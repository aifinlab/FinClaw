# -*- coding: utf-8 -*-
"""配对交易分析工具 - 协整检验/价差分析/交易信号/回测"""
import argparse
import json
import numpy as np
import pandas as pd
import sys

HAS_STATSMODELS = True
try:
    from statsmodels.tsa.stattools import adfuller, coint
except ImportError:
    HAS_STATSMODELS = False


def load_prices(path: str) -> pd.Series:
    with open(path) as f:
        data = json.load(f)
    if isinstance(data, dict) and "data" in data:
        data = data["data"]
    df = pd.DataFrame(data)
    close_col = next(
        (c for c in [
            "close",
            "收盘",
            "收盘价"] if c in df.columns),
        None)
    date_col = next((c for c in ["date", "日期"] if c in df.columns), None)
    if not close_col or not date_col:
        raise ValueError(f"需要 date + close 列，当前列: {list(df.columns)}")
    df[date_col] = pd.to_datetime(df[date_col])
    return df.set_index(date_col)[close_col].astype(float).sort_index()


def adf_test(series):
    if not HAS_STATSMODELS:
        return {"error": "需要 statsmodels 库"}
    result = adfuller(series.dropna(), autolag="AIC")
    return {
        "adf_stat": round(
            result[0], 4), "p_value": round(
            result[1], 4), "critical_1pct": round(
                result[4]["1%"], 4), "critical_5pct": round(
                    result[4]["5%"], 4), "is_stationary": result[1] < 0.05}


def cointegration_test(s1, s2):
    if not HAS_STATSMODELS:
        return {"error": "需要 statsmodels 库"}
    score, p_value, _ = coint(s1, s2)
    return {
        "coint_stat": round(
            score, 4), "p_value": round(
            p_value, 4), "is_cointegrated": p_value < 0.05}


def calc_hedge_ratio(s1, s2):
    X = np.column_stack([s2.values, np.ones(len(s2))])
    beta, alpha = np.linalg.lstsq(X, s1.values, rcond=None)[0]
    return round(float(beta), 4), round(float(alpha), 4)


def calc_spread(s1, s2, beta, alpha):
    return s1 - beta * s2 - alpha


def calc_zscore(spread, window):
    mean = spread.rolling(window).mean()
    std = spread.rolling(window).std()
    return (spread - mean) / std


def calc_halflife(spread):
    spread_lag = spread.shift(1)
    delta = spread - spread_lag
    valid = pd.concat([delta, spread_lag], axis=1).dropna()
    valid.columns = ["delta", "lag"]
    X = np.column_stack([valid["lag"].values, np.ones(len(valid))])
    b, _ = np.linalg.lstsq(X, valid["delta"].values, rcond=None)[0]
    if b >= 0:
        return None
    return round(-np.log(2) / b, 1)


def backtest(zscore, spread, entry=2.0, exit_threshold=0.5, stop=3.0):
    position = 0
    trades = []
    entry_spread = 0
    for i in range(len(zscore)):
        z = zscore.iloc[i]
        if np.isnan(z):
            continue
        if position == 0:
            if z < -entry:
                position = 1
                entry_spread = spread.iloc[i]
            elif z > entry:
                position = -1
                entry_spread = spread.iloc[i]
        elif position == 1:
            if z > -exit_threshold or z < -stop:
                pnl = spread.iloc[i] - entry_spread
                trades.append({"pnl": float(pnl), "type": "long"})
                position = 0
        elif position == -1:
            if z < exit_threshold or z > stop:
                pnl = entry_spread - spread.iloc[i]
                trades.append({"pnl": float(pnl), "type": "short"})
                position = 0
    if not trades:
        return {"n_trades": 0}
    pnls = [t["pnl"] for t in trades]
    wins = [p for p in pnls if p > 0]
    return {
        "n_trades": len(trades),
        "total_pnl": round(sum(pnls), 4),
        "avg_pnl": round(np.mean(pnls), 4),
        "win_rate": round(len(wins) / len(pnls), 4),
        "max_win": round(max(pnls), 4),
        "max_loss": round(min(pnls), 4),
    }


def main():
    parser = argparse.ArgumentParser(description="A股配对交易分析工具")
    parser.add_argument("--stock1", required=True, help="股票1 K线 JSON")
    parser.add_argument("--stock2", required=True, help="股票2 K线 JSON")
    parser.add_argument("--window", type=int, default=60, help="Z-score 滚动窗口")
    parser.add_argument("--entry", type=float, default=2.0, help="开仓阈值")
    parser.add_argument("--exit", type=float, default=0.5, help="平仓阈值")
    parser.add_argument("--stop", type=float, default=3.0, help="止损阈值")
    args = parser.parse_args()

    s1 = load_prices(args.stock1)
    s2 = load_prices(args.stock2)
    common = s1.index.intersection(s2.index)
    s1, s2 = s1.loc[common], s2.loc[common]

    correlation = round(float(s1.corr(s2)), 4)
    adf1 = adf_test(s1)
    adf2 = adf_test(s2)
    coint_result = cointegration_test(s1, s2)
    beta, alpha = calc_hedge_ratio(s1, s2)
    spread = calc_spread(s1, s2, beta, alpha)
    zscore = calc_zscore(spread, args.window)
    halflife = calc_halflife(spread)
    bt = backtest(zscore, spread, args.entry, args.exit, args.stop)

    result = {"ok": True,
                "n_observations": len(common),
                "correlation": correlation,
                "adf_stock1": adf1,
                "adf_stock2": adf2,
                "cointegration": coint_result,
                "hedge_ratio": {"beta": beta,
                                "alpha": alpha},
                "halflife_days": halflife,
                "current_zscore": round(float(zscore.iloc[-1]),
                                        4) if len(zscore) > 0 and not np.isnan(zscore.iloc[-1]) else None,
                "spread_stats": {"mean": round(float(spread.mean()),
                                                4),
                                "std": round(float(spread.std()),
                                            4)},
                "backtest": bt,
                }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
