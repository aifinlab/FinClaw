# -*- coding: utf-8 -*-
"""单因子分析工具 - IC/IR/分组回测/换手率分析"""
from scipy import stats
import argparse
import json
import numpy as np
import pandas as pd
import sys


def load_data(path: str) -> pd.DataFrame:
    """从 JSON 文件加载股票数据"""
    with open(path, "r") as f:
        data = json.load(f)
    if isinstance(data, dict) and "data" in data:
        data = data["data"]
    return pd.DataFrame(data)


def calc_forward_returns(df: pd.DataFrame, price_col: str, period: int, group_col: str = "date") -> pd.Series:
    """计算前瞻收益率"""
    df = df.sort_values([group_col, "code"])
    result = df.groupby("code")[price_col].pct_change(period).shift(-period)
    return result


def calc_ic_series(df: pd.DataFrame, factor_col: str, return_col: str, date_col: str = "date") -> pd.DataFrame:
    """计算每期 IC（Spearman rank correlation）"""
    records = []
    for dt, group in df.groupby(date_col):
        valid = group[[factor_col, return_col]].dropna()
        if len(valid) < 10:
            continue
        ic, p_value = stats.spearmanr(valid[factor_col], valid[return_col])
        records.append({"date": str(dt), "ic": ic, "p_value": p_value, "n_stocks": len(valid)})
    return pd.DataFrame(records)


def calc_quintile_returns(df: pd.DataFrame, factor_col: str, return_col: str, date_col: str = "date", n_groups: int = 5) -> dict:
    """分组回测：按因子值分N组，计算各组平均收益"""
    group_returns = {f"Q{i+1}": [] for i in range(n_groups)}

    for dt, group in df.groupby(date_col):
        valid = group[[factor_col, return_col]].dropna()
        if len(valid) < n_groups * 2:
            continue
        valid["quintile"] = pd.qcut(valid[factor_col], n_groups, labels=False, duplicates="drop")
        for q in range(n_groups):
            q_ret = valid[valid["quintile"] == q][return_col].mean()
            if not np.isnan(q_ret):
                group_returns[f"Q{q+1}"].append(q_ret)

    result = {}
    for q_name, rets in group_returns.items():
        if rets:
            arr = np.array(rets)
            result[q_name] = {
                "mean_return": round(float(np.mean(arr)), 6),
                "cumulative": round(float(np.prod(1 + arr) - 1), 4),
                "sharpe": round(float(np.mean(arr) / np.std(arr) * np.sqrt(12)) if np.std(arr) > 0 else 0, 4),
                "n_periods": len(rets),
            }
    if "Q1" in result and f"Q{n_groups}" in result:
        ls_rets = np.array(group_returns["Q1"]) - np.array(group_returns[f"Q{n_groups}"])
        result["long_short"] = {
            "mean_return": round(float(np.mean(ls_rets)), 6),
            "cumulative": round(float(np.prod(1 + ls_rets) - 1), 4),
            "sharpe": round(float(np.mean(ls_rets) / np.std(ls_rets) * np.sqrt(12)) if np.std(ls_rets) > 0 else 0, 4),
        }
    return result


def calc_turnover(df: pd.DataFrame, factor_col: str, date_col: str = "date", top_pct: float = 0.2) -> list:
    """计算因子换手率"""
    turnovers = []
    prev_stocks = None
    for dt, group in sorted(df.groupby(date_col)):
        valid = group[["code", factor_col]].dropna()
        if len(valid) < 5:
            continue
        n_top = max(1, int(len(valid) * top_pct))
        top_stocks = set(valid.nlargest(n_top, factor_col)["code"])
        if prev_stocks is not None:
            overlap = len(top_stocks & prev_stocks)
            turnover = 1 - overlap / len(top_stocks)
            turnovers.append({"date": str(dt), "turnover": round(turnover, 4)})
        prev_stocks = top_stocks
    return turnovers


def main():
    parser = argparse.ArgumentParser(description="A股单因子分析工具")
    parser.add_argument("--data", required=True, help="JSON 数据文件路径")
    parser.add_argument("--factor", required=True, help="因子列名")
    parser.add_argument("--period", type=int, default=20, help="前瞻收益周期（交易日）")
    parser.add_argument("--price_col", default="close", help="价格列名")
    parser.add_argument("--date_col", default="date", help="日期列名")
    parser.add_argument("--groups", type=int, default=5, help="分组数量")
    args = parser.parse_args()

    df = load_data(args.data)
    if args.factor not in df.columns:
        print(json.dumps({"ok": False, "error": f"因子列 '{args.factor}' 不存在，可用列: {list(df.columns)}"},
                         ensure_ascii=False))
        sys.exit(1)

    # 计算前瞻收益
    df["fwd_return"] = calc_forward_returns(df, args.price_col, args.period, args.date_col)

    # IC 序列
    ic_df = calc_ic_series(df, args.factor, "fwd_return", args.date_col)

    # IC 汇总
    ic_summary = {}
    if len(ic_df) > 0:
        ic_vals = ic_df["ic"].values
        ic_summary = {
            "mean_ic": round(float(np.mean(ic_vals)), 4),
            "std_ic": round(float(np.std(ic_vals)), 4),
            "ir": round(float(np.mean(ic_vals) / np.std(ic_vals)) if np.std(ic_vals) > 0 else 0, 4),
            "ic_positive_ratio": round(float(np.mean(ic_vals > 0)), 4),
            "abs_ic_gt_003": round(float(np.mean(np.abs(ic_vals) > 0.03)), 4),
            "n_periods": len(ic_vals),
        }

    # 分组回测
    quintile = calc_quintile_returns(df, args.factor, "fwd_return", args.date_col, args.groups)

    # 换手率
    turnover_list = calc_turnover(df, args.factor, args.date_col)
    avg_turnover = round(float(np.mean([t["turnover"] for t in turnover_list])), 4) if turnover_list else None

    result = {
        "ok": True,
        "factor": args.factor,
        "period": args.period,
        "ic_summary": ic_summary,
        "ic_series": ic_df.to_dict(orient="records") if len(ic_df) <= 120 else ic_df.tail(60).to_dict(orient="records"),
        "quintile_returns": quintile,
        "avg_turnover": avg_turnover,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
