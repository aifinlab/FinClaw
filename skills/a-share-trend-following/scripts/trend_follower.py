#!/usr/bin/env python3
"""
A股趋势跟踪策略分析工具 (A-Share Trend Following Analyzer)

支持策略: ma_cross(均线交叉), donchian(突破), turtle(海龟), all(综合)
输出: 趋势状态、交易信号、回测绩效

用法:
    python trend_follower.py --data kline.json --method ma_cross --fast 20 --slow 60
    python trend_follower.py --data kline.json --method turtle
    python trend_follower.py --data kline.json --method all --output result.json
"""

import argparse
import json
import sys
from typing import Optional

import numpy as np
import pandas as pd


# ── 指标计算 ──────────────────────────────────────────────────────────────

def calc_sma(series: pd.Series, period: int) -> pd.Series:
    """简单移动平均线"""
    return series.rolling(window=period, min_periods=period).mean()


def calc_ema(series: pd.Series, period: int) -> pd.Series:
    """指数移动平均线"""
    return series.ewm(span=period, adjust=False).mean()


def calc_atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """Average True Range"""
    prev_close = close.shift(1)
    tr = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low - prev_close).abs()
    ], axis=1).max(axis=1)
    return tr.rolling(window=period, min_periods=period).mean()


def calc_adx_dmi(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14):
    """
    计算 ADX, +DI, -DI
    返回: DataFrame with columns [plus_di, minus_di, adx]
    """
    prev_high = high.shift(1)
    prev_low = low.shift(1)

    # Directional Movement
    plus_dm = np.where((high - prev_high) > (prev_low - low), np.maximum(high - prev_high, 0), 0)
    minus_dm = np.where((prev_low - low) > (high - prev_high), np.maximum(prev_low - low, 0), 0)

    plus_dm = pd.Series(plus_dm, index=high.index, dtype=float)
    minus_dm = pd.Series(minus_dm, index=high.index, dtype=float)

    # True Range
    prev_close = close.shift(1)
    tr = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low - prev_close).abs()
    ], axis=1).max(axis=1)

    # Smoothed values (Wilder smoothing)
    smoothed_tr = tr.rolling(window=period, min_periods=period).sum()
    smoothed_plus_dm = plus_dm.rolling(window=period, min_periods=period).sum()
    smoothed_minus_dm = minus_dm.rolling(window=period, min_periods=period).sum()

    for i in range(period, len(tr)):
        smoothed_tr.iloc[i] = smoothed_tr.iloc[i - 1] - smoothed_tr.iloc[i - 1] / period + tr.iloc[i]
        smoothed_plus_dm.iloc[i] = smoothed_plus_dm.iloc[i - 1] - smoothed_plus_dm.iloc[i - 1] / period + plus_dm.iloc[i]
        smoothed_minus_dm.iloc[i] = smoothed_minus_dm.iloc[i - 1] - smoothed_minus_dm.iloc[i - 1] / period + minus_dm.iloc[i]

    plus_di = 100 * smoothed_plus_dm / smoothed_tr
    minus_di = 100 * smoothed_minus_dm / smoothed_tr

    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di)
    adx = dx.rolling(window=period, min_periods=period).mean()

    return pd.DataFrame({"plus_di": plus_di, "minus_di": minus_di, "adx": adx}, index=high.index)


def calc_donchian(high: pd.Series, low: pd.Series, period: int = 20):
    """Donchian Channel"""
    upper = high.rolling(window=period, min_periods=period).max()
    lower = low.rolling(window=period, min_periods=period).min()
    middle = (upper + lower) / 2
    return pd.DataFrame({"dc_upper": upper, "dc_lower": lower, "dc_middle": middle}, index=high.index)


def calc_atr_trailing_stop(close: pd.Series, atr: pd.Series, multiplier: float = 2.0) -> pd.Series:
    """ATR 跟踪止损线（多头）"""
    stop = close - multiplier * atr
    trailing_stop = stop.copy()
    for i in range(1, len(stop)):
        if pd.notna(stop.iloc[i]) and pd.notna(trailing_stop.iloc[i - 1]):
            if close.iloc[i] > trailing_stop.iloc[i - 1]:
                trailing_stop.iloc[i] = max(stop.iloc[i], trailing_stop.iloc[i - 1])
            else:
                trailing_stop.iloc[i] = stop.iloc[i]
    return trailing_stop


def detect_limit(close: pd.Series, board_type: str = "main") -> pd.DataFrame:
    """检测涨跌停状态 (A股特殊处理)"""
    pct_change = close.pct_change()
    limits = {"main": 0.095, "gem": 0.195, "star": 0.195, "bse": 0.295, "st": 0.045}
    threshold = limits.get(board_type, 0.095)
    return pd.DataFrame({
        "limit_up": pct_change >= threshold,
        "limit_down": pct_change <= -threshold,
    }, index=close.index)


# ── 趋势状态判定 ─────────────────────────────────────────────────────────

def classify_trend_regime(close: pd.Series, ma_fast: pd.Series, ma_slow: pd.Series,
                          adx: pd.Series, plus_di: pd.Series, minus_di: pd.Series) -> pd.Series:
    """
    综合趋势状态分类
    返回: Series of regime labels
    """
    regime = pd.Series("震荡", index=close.index)

    for i in range(len(close)):
        if pd.isna(adx.iloc[i]) or pd.isna(ma_fast.iloc[i]) or pd.isna(ma_slow.iloc[i]):
            regime.iloc[i] = "数据不足"
            continue

        adx_val = adx.iloc[i]
        ma_bull = ma_fast.iloc[i] > ma_slow.iloc[i]
        price_above = close.iloc[i] > ma_slow.iloc[i]
        di_bull = plus_di.iloc[i] > minus_di.iloc[i]

        if adx_val >= 25:
            if ma_bull and price_above and di_bull:
                regime.iloc[i] = "强上升"
            elif not ma_bull and not price_above and not di_bull:
                regime.iloc[i] = "强下降"
            elif di_bull:
                regime.iloc[i] = "弱上升"
            else:
                regime.iloc[i] = "弱下降"
        elif adx_val >= 20:
            if ma_bull and price_above:
                regime.iloc[i] = "弱上升"
            elif not ma_bull and not price_above:
                regime.iloc[i] = "弱下降"
            else:
                regime.iloc[i] = "震荡"
        else:
            regime.iloc[i] = "震荡"

    return regime


# ── 策略信号生成 ─────────────────────────────────────────────────────────

def strategy_ma_cross(close: pd.Series, fast_period: int = 20, slow_period: int = 60,
                      use_ema: bool = False) -> pd.Series:
    """均线交叉策略信号: 1=买入, -1=卖出, 0=无信号"""
    calc = calc_ema if use_ema else calc_sma
    ma_fast = calc(close, fast_period)
    ma_slow = calc(close, slow_period)

    signal = pd.Series(0, index=close.index)
    prev_diff = ma_fast - ma_slow

    for i in range(1, len(close)):
        if pd.isna(prev_diff.iloc[i]) or pd.isna(prev_diff.iloc[i - 1]):
            continue
        if prev_diff.iloc[i] > 0 and prev_diff.iloc[i - 1] <= 0:
            signal.iloc[i] = 1  # 金叉
        elif prev_diff.iloc[i] < 0 and prev_diff.iloc[i - 1] >= 0:
            signal.iloc[i] = -1  # 死叉

    return signal


def strategy_donchian(high: pd.Series, low: pd.Series, close: pd.Series,
                      entry_period: int = 20, exit_period: int = 10) -> pd.Series:
    """Donchian 突破策略信号"""
    dc_entry = calc_donchian(high, low, entry_period)
    dc_exit = calc_donchian(high, low, exit_period)

    signal = pd.Series(0, index=close.index)
    position = 0

    for i in range(1, len(close)):
        if pd.isna(dc_entry["dc_upper"].iloc[i - 1]):
            continue
        if position == 0 and close.iloc[i] > dc_entry["dc_upper"].iloc[i - 1]:
            signal.iloc[i] = 1
            position = 1
        elif position == 1 and close.iloc[i] < dc_exit["dc_lower"].iloc[i - 1]:
            signal.iloc[i] = -1
            position = 0

    return signal


def strategy_turtle(high: pd.Series, low: pd.Series, close: pd.Series,
                    atr: pd.Series, capital: float = 1_000_000) -> pd.Series:
    """
    海龟交易法则（简化版）
    System 2: 55日突破入场, 20日突破出场
    """
    dc_entry = calc_donchian(high, low, 55)
    dc_exit = calc_donchian(high, low, 20)

    signal = pd.Series(0, index=close.index)
    position = 0

    for i in range(1, len(close)):
        if pd.isna(dc_entry["dc_upper"].iloc[i - 1]) or pd.isna(atr.iloc[i]):
            continue
        if position == 0 and close.iloc[i] > dc_entry["dc_upper"].iloc[i - 1]:
            signal.iloc[i] = 1
            position = 1
        elif position == 1:
            # 止损: 2*ATR
            if pd.notna(atr.iloc[i]):
                entry_idx = signal[signal == 1].index[-1] if len(signal[signal == 1]) > 0 else None
                if entry_idx is not None:
                    entry_price = close.loc[entry_idx]
                    if close.iloc[i] < entry_price - 2 * atr.iloc[i]:
                        signal.iloc[i] = -1
                        position = 0
                        continue
            # 出场: 跌破 20 日下轨
            if close.iloc[i] < dc_exit["dc_lower"].iloc[i - 1]:
                signal.iloc[i] = -1
                position = 0

    return signal


# ── 回测引擎 ─────────────────────────────────────────────────────────────

def backtest(close: pd.Series, signal: pd.Series, commission: float = 0.00025,
             stamp_tax: float = 0.0005, slippage: float = 0.001,
             t_plus_1: bool = True) -> dict:
    """
    回测引擎（考虑 A 股 T+1）

    Args:
        close: 收盘价序列
        signal: 信号序列 (1=买, -1=卖, 0=无)
        commission: 佣金率（单边）
        stamp_tax: 印花税率（仅卖出）
        slippage: 滑点
        t_plus_1: 是否T+1延迟执行

    Returns:
        回测绩效字典
    """
    if t_plus_1:
        # T+1: 信号延迟一日执行，使用次日开盘价（近似为次日收盘价）
        exec_price = close.shift(-1)
    else:
        exec_price = close

    position = 0
    entry_price = 0.0
    trades = []
    equity = [1.0]

    for i in range(len(close)):
        if pd.isna(exec_price.iloc[i]):
            equity.append(equity[-1])
            continue

        if signal.iloc[i] == 1 and position == 0:
            entry_price = exec_price.iloc[i] * (1 + slippage)
            cost = entry_price * commission
            entry_price += cost
            position = 1

        elif signal.iloc[i] == -1 and position == 1:
            exit_price = exec_price.iloc[i] * (1 - slippage)
            exit_cost = exit_price * (commission + stamp_tax)
            exit_price -= exit_cost
            pnl = (exit_price - entry_price) / entry_price
            trades.append(pnl)
            position = 0

        # 更新权益曲线
        if position == 1:
            daily_ret = close.pct_change().iloc[i] if i > 0 else 0
            equity.append(equity[-1] * (1 + daily_ret))
        else:
            equity.append(equity[-1])

    equity_series = pd.Series(equity[1:], index=close.index)

    # 计算绩效指标
    if len(trades) == 0:
        return {
            "total_trades": 0,
            "message": "无交易信号产生，请检查数据长度或参数设置"
        }

    trades_arr = np.array(trades)
    wins = trades_arr[trades_arr > 0]
    losses = trades_arr[trades_arr <= 0]

    total_return = equity_series.iloc[-1] / equity_series.iloc[0] - 1
    trading_days = len(close)
    annual_return = (1 + total_return) ** (252 / max(trading_days, 1)) - 1

    daily_returns = equity_series.pct_change().dropna()
    annual_vol = daily_returns.std() * np.sqrt(252) if len(daily_returns) > 0 else 0
    risk_free = 0.02
    sharpe = (annual_return - risk_free) / annual_vol if annual_vol > 0 else 0

    # 最大回撤
    cummax = equity_series.cummax()
    drawdown = (equity_series - cummax) / cummax
    max_drawdown = drawdown.min()

    win_rate = len(wins) / len(trades_arr) * 100
    avg_win = wins.mean() * 100 if len(wins) > 0 else 0
    avg_loss = abs(losses.mean()) * 100 if len(losses) > 0 else 0
    profit_loss_ratio = (wins.mean() / abs(losses.mean())) if len(wins) > 0 and len(losses) > 0 else float("inf")
    profit_factor = (wins.sum() / abs(losses.sum())) if len(losses) > 0 and losses.sum() != 0 else float("inf")

    calmar = annual_return / abs(max_drawdown) if max_drawdown != 0 else float("inf")

    return {
        "total_trades": len(trades_arr),
        "win_trades": len(wins),
        "loss_trades": len(losses),
        "win_rate_pct": round(win_rate, 2),
        "total_return_pct": round(total_return * 100, 2),
        "annual_return_pct": round(annual_return * 100, 2),
        "annual_volatility_pct": round(annual_vol * 100, 2),
        "sharpe_ratio": round(sharpe, 3),
        "max_drawdown_pct": round(max_drawdown * 100, 2),
        "avg_win_pct": round(avg_win, 2),
        "avg_loss_pct": round(avg_loss, 2),
        "profit_loss_ratio": round(profit_loss_ratio, 2),
        "profit_factor": round(profit_factor, 2),
        "calmar_ratio": round(calmar, 2),
    }


# ── 数据加载 ─────────────────────────────────────────────────────────────

def load_kline(filepath: str) -> pd.DataFrame:
    """
    加载K线 JSON 数据
    预期字段: date, open, high, low, close, volume
    """
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict):
        # 处理 cn-stock-data 格式: {"data": [...]}
        data = data.get("data", data.get("kline", data))

    df = pd.DataFrame(data)

    # 标准化列名
    col_map = {}
    for col in df.columns:
        cl = col.lower()
        if cl in ("date", "trade_date", "datetime", "日期"):
            col_map[col] = "date"
        elif cl in ("open", "开盘价", "开盘"):
            col_map[col] = "open"
        elif cl in ("high", "最高价", "最高"):
            col_map[col] = "high"
        elif cl in ("low", "最低价", "最低"):
            col_map[col] = "low"
        elif cl in ("close", "收盘价", "收盘"):
            col_map[col] = "close"
        elif cl in ("volume", "vol", "成交量"):
            col_map[col] = "volume"

    df = df.rename(columns=col_map)

    required = ["date", "open", "high", "low", "close"]
    for col in required:
        if col not in df.columns:
            print(f"错误: 缺少必要字段 '{col}'", file=sys.stderr)
            sys.exit(1)

    df["date"] = pd.to_datetime(df["date"])
    for col in ["open", "high", "low", "close"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    if "volume" in df.columns:
        df["volume"] = pd.to_numeric(df["volume"], errors="coerce")

    df = df.sort_values("date").reset_index(drop=True)
    df = df.set_index("date")
    return df


# ── 主分析流程 ───────────────────────────────────────────────────────────

def analyze(df: pd.DataFrame, method: str = "all", fast: int = 20, slow: int = 60,
            use_ema: bool = False, atr_multiplier: float = 2.0,
            board_type: str = "main") -> dict:
    """运行完整趋势跟踪分析"""

    close = df["close"]
    high = df["high"]
    low = df["low"]

    # 计算基础指标
    ma_fast = (calc_ema if use_ema else calc_sma)(close, fast)
    ma_slow = (calc_ema if use_ema else calc_sma)(close, slow)
    atr = calc_atr(high, low, close, 14)
    dmi = calc_adx_dmi(high, low, close, 14)
    dc = calc_donchian(high, low, 20)
    trailing_stop = calc_atr_trailing_stop(close, atr, atr_multiplier)
    limits = detect_limit(close, board_type)

    # 趋势状态
    regime = classify_trend_regime(close, ma_fast, ma_slow, dmi["adx"], dmi["plus_di"], dmi["minus_di"])
    current_regime = regime.iloc[-1] if len(regime) > 0 else "数据不足"

    # 当前指标快照
    latest = {
        "date": str(df.index[-1].date()),
        "close": round(close.iloc[-1], 2),
        "ma_fast": round(ma_fast.iloc[-1], 2) if pd.notna(ma_fast.iloc[-1]) else None,
        "ma_slow": round(ma_slow.iloc[-1], 2) if pd.notna(ma_slow.iloc[-1]) else None,
        "adx": round(dmi["adx"].iloc[-1], 2) if pd.notna(dmi["adx"].iloc[-1]) else None,
        "plus_di": round(dmi["plus_di"].iloc[-1], 2) if pd.notna(dmi["plus_di"].iloc[-1]) else None,
        "minus_di": round(dmi["minus_di"].iloc[-1], 2) if pd.notna(dmi["minus_di"].iloc[-1]) else None,
        "dc_upper": round(dc["dc_upper"].iloc[-1], 2) if pd.notna(dc["dc_upper"].iloc[-1]) else None,
        "dc_lower": round(dc["dc_lower"].iloc[-1], 2) if pd.notna(dc["dc_lower"].iloc[-1]) else None,
        "atr": round(atr.iloc[-1], 2) if pd.notna(atr.iloc[-1]) else None,
        "trailing_stop": round(trailing_stop.iloc[-1], 2) if pd.notna(trailing_stop.iloc[-1]) else None,
        "trend_regime": current_regime,
    }

    # 生成信号与回测
    results = {"indicators": latest, "strategies": {}}

    strategies_to_run = {
        "ma_cross": lambda: strategy_ma_cross(close, fast, slow, use_ema),
        "donchian": lambda: strategy_donchian(high, low, close, 20, 10),
        "turtle": lambda: strategy_turtle(high, low, close, atr),
    }

    if method == "all":
        run_methods = strategies_to_run.keys()
    elif method in strategies_to_run:
        run_methods = [method]
    else:
        print(f"错误: 未知策略 '{method}'，可选: ma_cross, donchian, turtle, all", file=sys.stderr)
        sys.exit(1)

    for m in run_methods:
        signal = strategies_to_run[m]()
        bt = backtest(close, signal)

        # 当前信号状态
        last_signal_idx = signal[signal != 0].index[-1] if len(signal[signal != 0]) > 0 else None
        if last_signal_idx is not None:
            last_signal = "买入" if signal.loc[last_signal_idx] == 1 else "卖出"
            last_signal_date = str(last_signal_idx.date()) if hasattr(last_signal_idx, "date") else str(last_signal_idx)
        else:
            last_signal = "无信号"
            last_signal_date = None

        results["strategies"][m] = {
            "current_signal": last_signal,
            "signal_date": last_signal_date,
            "backtest": bt,
        }

    # 涨跌停统计
    results["limit_stats"] = {
        "limit_up_days": int(limits["limit_up"].sum()),
        "limit_down_days": int(limits["limit_down"].sum()),
    }

    return results


# ── CLI 入口 ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="A股趋势跟踪策略分析工具")
    parser.add_argument("--data", required=True, help="K线数据 JSON 文件路径")
    parser.add_argument("--method", default="all", choices=["ma_cross", "donchian", "turtle", "all"],
                        help="策略方法 (默认: all)")
    parser.add_argument("--fast", type=int, default=20, help="快速均线周期 (默认: 20)")
    parser.add_argument("--slow", type=int, default=60, help="慢速均线周期 (默认: 60)")
    parser.add_argument("--ema", action="store_true", help="使用 EMA 代替 SMA")
    parser.add_argument("--atr-mult", type=float, default=2.0, help="ATR 止损倍数 (默认: 2.0)")
    parser.add_argument("--board", default="main", choices=["main", "gem", "star", "bse", "st"],
                        help="板块类型，决定涨跌停阈值 (默认: main)")
    parser.add_argument("--output", help="输出 JSON 文件路径 (不指定则打印到终端)")
    args = parser.parse_args()

    # 加载数据
    df = load_kline(args.data)
    print(f"已加载 {len(df)} 条K线数据 ({df.index[0].date()} ~ {df.index[-1].date()})", file=sys.stderr)

    # 分析
    results = analyze(df, method=args.method, fast=args.fast, slow=args.slow,
                      use_ema=args.ema, atr_multiplier=args.atr_mult, board_type=args.board)

    # 输出
    output_json = json.dumps(results, ensure_ascii=False, indent=2, default=str)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_json)
        print(f"结果已保存至 {args.output}", file=sys.stderr)
    else:
        print(output_json)


if __name__ == "__main__":
    main()
