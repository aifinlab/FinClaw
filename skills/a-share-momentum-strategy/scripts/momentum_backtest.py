#!/usr/bin/env python3
"""
A股动量策略回测脚本

功能：
  - 加载股票K线 JSON 数据
  - 计算多周期动量得分
  - 按动量排序分为 quintile 组合
  - 计算多空组合收益、年化收益率、Sharpe、最大回撤、换手率

用法：
  python momentum_backtest.py --data input.json --lookback 120 --holding 20
  python momentum_backtest.py --data input.json --lookback 120 --holding 20 --skip-month --groups 5

输入 JSON 格式：
  [
    {"code": "000001", "date": "2024-01-02", "close": 10.5, "volume": 123456},
    ...
  ]
  每条记录需包含 code(股票代码), date(日期), close(收盘价)，volume(成交量) 可选。
"""

from typing import Dict, List, Tuple
import argparse
import json
import numpy as np

import pandas as pd
import sys


def load_data(filepath: str) -> pd.DataFrame:
    """从 JSON 文件加载K线数据，返回 DataFrame"""
    with open(filepath, "r", encoding="utf-8") as f:
        raw = json.load(f)

    df = pd.DataFrame(raw)
    required_cols = {"code", "date", "close"}
    missing = required_cols - set(df.columns)
    if missing:
        print(f"[错误] 输入数据缺少必要字段: {missing}")
        sys.exit(1)

    df["date"] = pd.to_datetime(df["date"])
    df["close"] = df["close"].astype(float)
    df = df.sort_values(["code", "date"]).reset_index(drop=True)
    return df


def calc_momentum(df: pd.DataFrame, lookback: int, skip: int = 0) -> pd.DataFrame:
    """
    计算动量得分

    参数:
        df: 包含 code, date, close 的 DataFrame
        lookback: 回看天数（形成期）
        skip: 跳过最近 N 天（skip-month），避免短期反转干扰

    返回:
        每个 (code, date) 的动量得分
    """
    total_lag = lookback + skip

    def _momentum(group: pd.DataFrame) -> pd.DataFrame:
        g = group.copy()
        if skip > 0:
            past_price = g["close"].shift(total_lag)
            recent_price = g["close"].shift(skip)
            g["momentum"] = (recent_price / past_price - 1) * 100
        else:
            past_price = g["close"].shift(lookback)
            g["momentum"] = (g["close"] / past_price - 1) * 100
        return g

    result = df.groupby("code", group_keys=False).apply(_momentum)
    return result


def assign_quintiles(df: pd.DataFrame, n_groups: int = 5) -> pd.DataFrame:
    """
    按日期截面将股票分为 N 个 quintile 组

    Q1 = 最低动量（输家），Q5 = 最高动量（赢家）
    """

    def _assign(group: pd.DataFrame) -> pd.DataFrame:
        g = group.copy()
        valid = g["momentum"].notna()
        if valid.sum() < n_groups:
            g["quintile"] = np.nan
            return g
        g.loc[valid, "quintile"] = pd.qcut(
            g.loc[valid, "momentum"], q=n_groups, labels=False, duplicates="drop"
        )
        # 转为 1-based (Q1=输家, QN=赢家)
        g["quintile"] = g["quintile"] + 1
        return g

    result = df.groupby("date", group_keys=False).apply(_assign)
    return result


def calc_forward_returns(df: pd.DataFrame, holding: int) -> pd.DataFrame:
    """计算未来 holding 天的收益率"""

    def _forward(group: pd.DataFrame) -> pd.DataFrame:
        g = group.copy()
        future_price = g["close"].shift(-holding)
        g["fwd_return"] = (future_price / g["close"] - 1) * 100
        return g

    result = df.groupby("code", group_keys=False).apply(_forward)
    return result


def calc_portfolio_returns(
    df: pd.DataFrame, n_groups: int, holding: int
) -> pd.DataFrame:
    """
    按再平衡周期计算各 quintile 组合的等权收益

    返回每个再平衡日期各组的平均收益
    """
    # 只保留有动量分组和前瞻收益的记录
    valid = df.dropna(subset=["quintile", "fwd_return"]).copy()
    valid["quintile"] = valid["quintile"].astype(int)

    # 按日期+分组计算等权平均收益
    port_ret = (
        valid.groupby(["date", "quintile"])["fwd_return"].mean().unstack("quintile")
    )

    # 抽样：每 holding 天取一个再平衡日（避免重叠）
    dates = sorted(port_ret.index)
    rebalance_dates = dates[::holding]
    port_ret = port_ret.loc[port_ret.index.isin(rebalance_dates)]

    return port_ret


def calc_long_short(port_ret: pd.DataFrame, n_groups: int) -> pd.Series:
    """计算 Long-Short (Q_max - Q1) 收益序列"""
    q_max = max(port_ret.columns)
    q_min = min(port_ret.columns)
    ls = port_ret[q_max] - port_ret[q_min]
    return ls


def annualized_return(returns: pd.Series, holding: int) -> float:
    """将持有期收益序列转为年化收益率"""
    periods_per_year = 250 / holding
    mean_ret = returns.mean() / 100  # 百分比→小数
    ann = (1 + mean_ret) ** periods_per_year - 1
    return ann * 100


def sharpe_ratio(returns: pd.Series, holding: int, rf_annual: float = 2.0) -> float:
    """计算 Sharpe ratio (年化)"""
    periods_per_year = 250 / holding
    mean_ret = returns.mean() / 100
    std_ret = returns.std() / 100
    if std_ret == 0:
        return 0.0
    rf_per_period = (1 + rf_annual / 100) ** (1 / periods_per_year) - 1
    sharpe = (mean_ret - rf_per_period) / std_ret * np.sqrt(periods_per_year)
    return sharpe


def max_drawdown(returns: pd.Series) -> float:
    """计算最大回撤 (%)，基于累计净值"""
    cum = (1 + returns / 100).cumprod()
    peak = cum.cummax()
    dd = (cum - peak) / peak * 100
    return dd.min()


def calc_turnover(df: pd.DataFrame, n_groups: int, holding: int) -> float:
    """
    估算换手率：相邻再平衡日赢家组合的成分变化比例
    """
    q_max = n_groups
    valid = df.dropna(subset=["quintile"]).copy()
    valid["quintile"] = valid["quintile"].astype(int)

    dates = sorted(valid["date"].unique())
    rebalance_dates = dates[::holding]

    turnovers = []
    prev_stocks = None
    for d in rebalance_dates:
        day_data = valid[(valid["date"] == d) & (valid["quintile"] == q_max)]
        curr_stocks = set(day_data["code"].values)
        if prev_stocks is not None and len(prev_stocks) > 0 and len(curr_stocks) > 0:
            union = prev_stocks | curr_stocks
            changed = len(union - (prev_stocks & curr_stocks))
            turnover = changed / max(len(prev_stocks), len(curr_stocks)) * 100
            turnovers.append(turnover)
        prev_stocks = curr_stocks

    return np.mean(turnovers) if turnovers else 0.0


def print_report(
    port_ret: pd.DataFrame,
    ls_returns: pd.Series,
    n_groups: int,
    lookback: int,
    holding: int,
    turnover: float,
):
    """输出回测报告"""
    print("=" * 70)
    print(f"  A股动量策略回测报告")
    print(f"  形成期 (lookback): {lookback} 交易日")
    print(f"  持有期 (holding):  {holding} 交易日")
    print(f"  分组数:            {n_groups}")
    print(f"  再平衡次数:        {len(port_ret)}")
    print("=" * 70)

    print(f"\n{'组合':<10} {'平均收益%':<12} {'年化收益%':<12} {'Sharpe':<10} {'最大回撤%':<12}")
    print("-" * 56)

    for q in sorted(port_ret.columns):
        ret_series = port_ret[q]
        avg = ret_series.mean()
        ann = annualized_return(ret_series, holding)
        sr = sharpe_ratio(ret_series, holding)
        mdd = max_drawdown(ret_series)
        label = f"Q{q}"
        if q == min(port_ret.columns):
            label += "(输家)"
        elif q == max(port_ret.columns):
            label += "(赢家)"
        print(f"{label:<10} {avg:<12.2f} {ann:<12.2f} {sr:<10.2f} {mdd:<12.2f}")

    # Long-Short
    avg_ls = ls_returns.mean()
    ann_ls = annualized_return(ls_returns, holding)
    sr_ls = sharpe_ratio(ls_returns, holding, rf_annual=0)
    mdd_ls = max_drawdown(ls_returns)
    print(f"{'L-S':<10} {avg_ls:<12.2f} {ann_ls:<12.2f} {sr_ls:<10.2f} {mdd_ls:<12.2f}")

    print(f"\n赢家组合平均换手率: {turnover:.1f}%")

    # 动量分布统计
    print(f"\nLong-Short 收益统计:")
    print(f"  胜率: {(ls_returns > 0).mean() * 100:.1f}%")
    print(f"  盈亏比: {ls_returns[ls_returns > 0].mean() / abs(ls_returns[ls_returns < 0].mean()):.2f}" if (ls_returns < 0).any() and (ls_returns > 0).any() else "  盈亏比: N/A")
    print(f"  最佳单期: +{ls_returns.max():.2f}%")
    print(f"  最差单期: {ls_returns.min():.2f}%")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="A股动量策略回测",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python momentum_backtest.py --data kline.json --lookback 120 --holding 20
  python momentum_backtest.py --data kline.json --lookback 250 --holding 20 --skip-month --groups 10
        """,
    )
    parser.add_argument("--data", required=True, help="输入K线 JSON 文件路径")
    parser.add_argument(
        "--lookback", type=int, default=120, help="动量形成期天数 (默认 120，即 6 个月)"
    )
    parser.add_argument(
        "--holding", type=int, default=20, help="持有期天数 (默认 20，即 1 个月)"
    )
    parser.add_argument(
        "--skip-month",
        action="store_true",
        help="是否跳过最近 1 个月 (21 天)，用于 12M 动量",
    )
    parser.add_argument(
        "--groups", type=int, default=5, help="分组数量 (默认 5，quintile)"
    )
    parser.add_argument(
        "--output", type=str, default=None, help="输出结果 JSON 文件路径 (可选)"
    )

    args = parser.parse_args()

    # 1. 加载数据
    print(f"[1/5] 加载数据: {args.data}")
    df = load_data(args.data)
    n_stocks = df["code"].nunique()
    n_dates = df["date"].nunique()
    print(f"      股票数: {n_stocks}，交易日数: {n_dates}")

    # 2. 计算动量
    skip = 21 if args.skip_month else 0
    print(f"[2/5] 计算动量 (lookback={args.lookback}, skip={skip})")
    df = calc_momentum(df, args.lookback, skip)
    valid_mom = df["momentum"].notna().sum()
    print(f"      有效动量记录: {valid_mom}")

    # 3. 分组
    print(f"[3/5] 按截面分为 {args.groups} 组")
    df = assign_quintiles(df, args.groups)

    # 4. 计算前瞻收益
    print(f"[4/5] 计算持有期 ({args.holding} 天) 收益")
    df = calc_forward_returns(df, args.holding)

    # 5. 组合收益与统计
    print(f"[5/5] 生成回测报告\n")
    port_ret = calc_portfolio_returns(df, args.groups, args.holding)

    if port_ret.empty:
        print("[错误] 无法计算组合收益，请检查数据量是否足够")
        sys.exit(1)

    ls_returns = calc_long_short(port_ret, args.groups)
    turnover = calc_turnover(df, args.groups, args.holding)

    print_report(port_ret, ls_returns, args.groups, args.lookback, args.holding, turnover)

    # 可选：输出 JSON
    if args.output:
        result = {
            "params": {
                "lookback": args.lookback,
                "holding": args.holding,
                "skip_month": args.skip_month,
                "groups": args.groups,
            },
            "summary": {},
        }
        for q in sorted(port_ret.columns):
            ret_s = port_ret[q]
            result["summary"][f"Q{q}"] = {
                "avg_return": round(ret_s.mean(), 4),
                "ann_return": round(annualized_return(ret_s, args.holding), 4),
                "sharpe": round(sharpe_ratio(ret_s, args.holding), 4),
                "max_drawdown": round(max_drawdown(ret_s), 4),
            }
        result["summary"]["long_short"] = {
            "avg_return": round(ls_returns.mean(), 4),
            "ann_return": round(annualized_return(ls_returns, args.holding), 4),
            "sharpe": round(sharpe_ratio(ls_returns, args.holding, rf_annual=0), 4),
            "max_drawdown": round(max_drawdown(ls_returns), 4),
            "win_rate": round((ls_returns > 0).mean() * 100, 2),
        }
        result["summary"]["turnover"] = round(turnover, 2)

        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n结果已保存至: {args.output}")


if __name__ == "__main__":
    main()
