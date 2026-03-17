#!/usr/bin/env python3
"""
A股波动率分析器
功能：多窗口历史波动率、波动率锥、GARCH(1,1)预测、EWMA备选
用法：python volatility_analyzer.py --code 000001 --start 2024-03-16
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

# ── 配置 ──────────────────────────────────────────────────
CN_STOCK_SCRIPT = Path(__file__).resolve().parent.parent.parent / "cn-stock-data" / "scripts" / "cn_stock_data.py"
HV_WINDOWS = [5, 10, 20, 60, 120]
PERCENTILES = [5, 25, 50, 75, 95]
TRADING_DAYS_PER_YEAR = 252
EWMA_LAMBDA = 0.94  # RiskMetrics standard


def fetch_kline(code: str, start: str) -> pd.DataFrame:
    """通过 cn-stock-data 获取日线数据"""
    cmd = [
        sys.executable, str(CN_STOCK_SCRIPT),
        "kline", "--code", code, "--freq", "daily", "--start", start
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        print(f"[ERROR] 获取K线失败: {result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)

    lines = result.stdout.strip().split("\n")
    # 尝试解析为 CSV 或 JSON
    try:
        from io import StringIO
        df = pd.read_csv(StringIO(result.stdout))
    except Exception:
        try:
            data = json.loads(result.stdout)
            df = pd.DataFrame(data)
        except Exception:
            print(f"[ERROR] 无法解析K线数据，前3行: {lines[:3]}", file=sys.stderr)
            sys.exit(1)

    # 标准化列名
    col_map = {}
    for c in df.columns:
        cl = c.lower().strip()
        if cl in ("close", "收盘", "收盘价"):
            col_map[c] = "close"
        elif cl in ("high", "最高", "最高价"):
            col_map[c] = "high"
        elif cl in ("low", "最低", "最低价"):
            col_map[c] = "low"
        elif cl in ("open", "开盘", "开盘价"):
            col_map[c] = "open"
        elif cl in ("date", "日期", "trade_date"):
            col_map[c] = "date"
    df.rename(columns=col_map, inplace=True)

    if "close" not in df.columns:
        print(f"[ERROR] 数据中无收盘价列。列名: {list(df.columns)}", file=sys.stderr)
        sys.exit(1)

    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    df.dropna(subset=["close"], inplace=True)

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
        df.sort_values("date", inplace=True)
        df.set_index("date", inplace=True)

    return df


def compute_log_returns(df: pd.DataFrame) -> pd.Series:
    """计算对数收益率"""
    return np.log(df["close"] / df["close"].shift(1)).dropna()


def compute_hv_close_to_close(returns: pd.Series, window: int) -> pd.Series:
    """Close-to-Close 历史波动率（年化，百分比）"""
    return returns.rolling(window=window).std() * np.sqrt(TRADING_DAYS_PER_YEAR) * 100


def compute_hv_parkinson(df: pd.DataFrame, window: int) -> pd.Series | None:
    """Parkinson 波动率（年化，百分比）"""
    if "high" not in df.columns or "low" not in df.columns:
        return None
    hl = np.log(df["high"] / df["low"])
    hl_sq = hl ** 2
    factor = 1.0 / (4.0 * np.log(2))
    return np.sqrt(hl_sq.rolling(window=window).mean() * factor) * np.sqrt(TRADING_DAYS_PER_YEAR) * 100


def compute_hv_yang_zhang(df: pd.DataFrame, window: int) -> pd.Series | None:
    """Yang-Zhang 波动率（年化，百分比）"""
    required = {"open", "high", "low", "close"}
    if not required.issubset(df.columns):
        return None

    log_oc = np.log(df["open"] / df["close"].shift(1)).dropna()  # overnight
    log_co = np.log(df["close"] / df["open"]).dropna()  # open-to-close
    log_hl = np.log(df["high"] / df["low"]).dropna()

    n = window
    k = 0.34 / (1.34 + (n + 1) / (n - 1)) if n > 1 else 0.34

    var_overnight = log_oc.rolling(window=n).var()
    var_close_open = log_co.rolling(window=n).var()
    # Rogers-Satchell
    log_ho = np.log(df["high"] / df["open"])
    log_hc = np.log(df["high"] / df["close"])
    log_lo = np.log(df["low"] / df["open"])
    log_lc = np.log(df["low"] / df["close"])
    rs = (log_ho * log_hc + log_lo * log_lc).rolling(window=n).mean()

    var_yz = var_overnight + k * var_close_open + (1 - k) * rs
    # 防止负数
    var_yz = var_yz.clip(lower=0)
    return np.sqrt(var_yz) * np.sqrt(TRADING_DAYS_PER_YEAR) * 100


def build_volatility_cone(returns: pd.Series, windows: list[int], percentiles: list[int]) -> dict:
    """构建波动率锥"""
    cone = {}
    for w in windows:
        hv_series = compute_hv_close_to_close(returns, w).dropna()
        if len(hv_series) == 0:
            continue
        pcts = np.percentile(hv_series, percentiles)
        current = hv_series.iloc[-1]
        # 当前值所处的百分位
        current_pct = (hv_series < current).sum() / len(hv_series) * 100
        cone[f"HV{w}"] = {
            "current": round(float(current), 2),
            "current_percentile": round(float(current_pct), 1),
            "percentiles": {f"P{p}": round(float(v), 2) for p, v in zip(percentiles, pcts)},
            "mean": round(float(hv_series.mean()), 2),
            "count": len(hv_series),
        }
    return cone


def fit_garch(returns: pd.Series) -> dict | None:
    """拟合 GARCH(1,1) 模型，返回参数和预测"""
    try:
        from arch import arch_model
    except ImportError:
        return None

    # arch 库要求百分比收益率
    ret_pct = returns * 100
    ret_pct = ret_pct.dropna()

    if len(ret_pct) < 250:
        return {"error": f"数据量不足: {len(ret_pct)} < 250"}

    try:
        model = arch_model(ret_pct, vol="Garch", p=1, q=1, mean="Constant", dist="Normal")
        res = model.fit(disp="off", show_warning=False)
    except Exception as e:
        return {"error": f"GARCH 拟合失败: {str(e)}"}

    omega = float(res.params.get("omega", 0))
    alpha = float(res.params.get("alpha[1]", 0))
    beta = float(res.params.get("beta[1]", 0))
    persistence = alpha + beta

    # 长期波动率（年化百分比）
    if persistence < 1 and (1 - persistence) > 0:
        long_run_var = omega / (1 - persistence)
        long_run_vol = np.sqrt(long_run_var * TRADING_DAYS_PER_YEAR)
    else:
        long_run_vol = None

    # 半衰期
    if 0 < persistence < 1:
        half_life = np.log(2) / (-np.log(persistence))
    else:
        half_life = None

    # 预测未来 N 步
    forecasts = res.forecast(horizon=20)
    fcast_var = forecasts.variance.iloc[-1]  # 最后一个观测点的预测
    fcast_vol = {}
    for h in [5, 10, 20]:
        col = f"h.{h}"
        if col in fcast_var.index:
            fcast_vol[f"{h}d"] = round(float(np.sqrt(fcast_var[col] * TRADING_DAYS_PER_YEAR)), 2)

    return {
        "model": "GARCH(1,1)",
        "omega": round(omega, 6),
        "alpha": round(alpha, 4),
        "beta": round(beta, 4),
        "persistence": round(persistence, 4),
        "long_run_vol_annualized": round(float(long_run_vol), 2) if long_run_vol else None,
        "half_life_days": round(float(half_life), 1) if half_life else None,
        "forecast_vol_annualized": fcast_vol,
        "log_likelihood": round(float(res.loglikelihood), 2),
        "aic": round(float(res.aic), 2),
        "bic": round(float(res.bic), 2),
    }


def compute_ewma(returns: pd.Series, lam: float = EWMA_LAMBDA) -> dict:
    """EWMA 波动率估计"""
    ret = returns.dropna()
    if len(ret) < 20:
        return {"error": "数据量不足"}

    var_t = ret.iloc[:20].var()  # 初始方差
    ewma_vars = [var_t]

    for r in ret.iloc[20:]:
        var_t = lam * var_t + (1 - lam) * r ** 2
        ewma_vars.append(var_t)

    current_vol = np.sqrt(ewma_vars[-1] * TRADING_DAYS_PER_YEAR) * 100

    # EWMA 预测（所有未来步数相同，等于当前条件方差）
    forecast_vol = round(float(current_vol), 2)

    return {
        "model": "EWMA",
        "lambda": lam,
        "current_vol_annualized": forecast_vol,
        "forecast_vol_5d": forecast_vol,
        "forecast_vol_10d": forecast_vol,
        "forecast_vol_20d": forecast_vol,
        "note": "EWMA预测所有期限相同（无均值回归）",
    }


def analyze(code: str, start: str) -> dict:
    """主分析流程"""
    print(f"[INFO] 获取 {code} K线数据 (from {start})...", file=sys.stderr)
    df = fetch_kline(code, start)
    print(f"[INFO] 获取到 {len(df)} 条K线数据", file=sys.stderr)

    returns = compute_log_returns(df)
    print(f"[INFO] 计算收益率序列: {len(returns)} 条", file=sys.stderr)

    result = {
        "code": code,
        "data_range": {
            "start": str(df.index[0].date()) if hasattr(df.index[0], "date") else str(df.index[0]),
            "end": str(df.index[-1].date()) if hasattr(df.index[-1], "date") else str(df.index[-1]),
            "trading_days": len(df),
        },
        "current_price": round(float(df["close"].iloc[-1]), 2),
    }

    # 1. 多窗口 HV（Close-to-Close）
    print("[INFO] 计算多窗口历史波动率...", file=sys.stderr)
    hv_current = {}
    for w in HV_WINDOWS:
        hv = compute_hv_close_to_close(returns, w).dropna()
        if len(hv) > 0:
            hv_current[f"HV{w}"] = round(float(hv.iloc[-1]), 2)
    result["hv_close_to_close"] = hv_current

    # 2. Parkinson HV
    hv_park = compute_hv_parkinson(df, 20)
    if hv_park is not None and len(hv_park.dropna()) > 0:
        result["hv_parkinson_20"] = round(float(hv_park.dropna().iloc[-1]), 2)

    # 3. Yang-Zhang HV
    hv_yz = compute_hv_yang_zhang(df, 20)
    if hv_yz is not None and len(hv_yz.dropna()) > 0:
        result["hv_yang_zhang_20"] = round(float(hv_yz.dropna().iloc[-1]), 2)

    # 4. 波动率锥
    print("[INFO] 构建波动率锥...", file=sys.stderr)
    result["volatility_cone"] = build_volatility_cone(returns, HV_WINDOWS, PERCENTILES)

    # 5. GARCH(1,1)
    print("[INFO] 拟合 GARCH(1,1)...", file=sys.stderr)
    garch_result = fit_garch(returns)
    if garch_result is not None:
        result["garch"] = garch_result
        if "error" not in garch_result:
            print("[INFO] GARCH(1,1) 拟合成功", file=sys.stderr)
        else:
            print(f"[INFO] GARCH: {garch_result['error']}", file=sys.stderr)
    else:
        print("[INFO] arch 库未安装，使用 EWMA 替代", file=sys.stderr)

    # 6. EWMA（始终计算，作为备选或对比）
    print("[INFO] 计算 EWMA 波动率...", file=sys.stderr)
    result["ewma"] = compute_ewma(returns)

    # 7. 波动率统计摘要
    hv20_series = compute_hv_close_to_close(returns, 20).dropna()
    if len(hv20_series) > 0:
        current_hv20 = hv20_series.iloc[-1]
        pct_rank = (hv20_series < current_hv20).sum() / len(hv20_series) * 100
        if pct_rank >= 75:
            level = "偏高"
        elif pct_rank <= 25:
            level = "偏低"
        else:
            level = "正常"

        result["summary"] = {
            "current_hv20": round(float(current_hv20), 2),
            "hv20_percentile": round(float(pct_rank), 1),
            "level": level,
            "hv20_mean": round(float(hv20_series.mean()), 2),
            "hv20_min": round(float(hv20_series.min()), 2),
            "hv20_max": round(float(hv20_series.max()), 2),
        }

    return result


def main():
    parser = argparse.ArgumentParser(description="A股波动率分析器")
    parser.add_argument("--code", required=True, help="股票代码，如 000001 / 600519")
    parser.add_argument("--start", required=True, help="起始日期，如 2024-03-16")
    args = parser.parse_args()

    result = analyze(args.code, args.start)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
