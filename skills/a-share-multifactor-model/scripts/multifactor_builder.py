# -*- coding: utf-8 -*-
"""多因子模型构建工具 - 截面回归/因子收益/协方差矩阵"""
import argparse
import json
import sys
import numpy as np
import pandas as pd


def winsorize_mad(series: pd.Series, n_mad: float = 3.0) -> pd.Series:
    """MAD 去极值"""
    median = series.median()
    mad = (series - median).abs().median() * 1.4826
    lower = median - n_mad * mad
    upper = median + n_mad * mad
    return series.clip(lower, upper)


def standardize(series: pd.Series) -> pd.Series:
    """Z-score 标准化"""
    std = series.std()
    if std == 0 or np.isnan(std):
        return series * 0
    return (series - series.mean()) / std


def cross_sectional_regression(returns: pd.Series, exposures: pd.DataFrame, weights: pd.Series = None):
    """单期截面回归 (WLS)"""
    valid = returns.dropna().index.intersection(exposures.dropna().index)
    if len(valid) < exposures.shape[1] + 5:
        return None, None, None

    y = returns.loc[valid].values
    X = exposures.loc[valid].values

    if weights is not None:
        w = np.sqrt(weights.loc[valid].values)
        W = np.diag(w)
        XtWX = X.T @ W @ W @ X
        XtWy = X.T @ W @ W @ y
    else:
        XtWX = X.T @ X
        XtWy = X.T @ y

    try:
        factor_returns = np.linalg.solve(XtWX, XtWy)
    except np.linalg.LinAlgError:
        factor_returns = np.linalg.lstsq(XtWX, XtWy, rcond=None)[0]

    residuals = y - X @ factor_returns
    n, k = X.shape
    mse = np.sum(residuals ** 2) / (n - k)
    try:
        se = np.sqrt(np.diag(mse * np.linalg.inv(XtWX)))
    except np.linalg.LinAlgError:
        se = np.full(k, np.nan)

    return factor_returns, se, residuals


def ewma_covariance(factor_returns_df: pd.DataFrame, halflife: int = 90) -> np.ndarray:
    """指数加权因子协方差矩阵"""
    n_obs = len(factor_returns_df)
    decay = 0.5 ** (1.0 / halflife)
    weights = np.array([decay ** (n_obs - 1 - i) for i in range(n_obs)])
    weights /= weights.sum()

    values = factor_returns_df.values
    means = (values * weights[:, None]).sum(axis=0)
    centered = values - means
    cov = (centered * weights[:, None]).T @ centered
    return cov


def main():
    parser = argparse.ArgumentParser(description="A股多因子模型构建工具")
    parser.add_argument("--returns", required=True, help="收益率 CSV (columns: date, code, return)")
    parser.add_argument("--exposures", required=True, help="因子暴露 CSV (columns: date, code, factor1, factor2, ...)")
    parser.add_argument("--factors", default=None, help="逗号分隔的因子列名（默认使用 exposures 中除 date/code 外所有列）")
    parser.add_argument("--halflife", type=int, default=90, help="协方差 EWMA 半衰期")
    parser.add_argument("--weight_col", default=None, help="WLS 权重列（如 market_cap）")
    args = parser.parse_args()

    # 加载数据
    ret_df = pd.read_csv(args.returns)
    exp_df = pd.read_csv(args.exposures)

    # 确定因子列
    meta_cols = {"date", "code", args.weight_col} if args.weight_col else {"date", "code"}
    if args.factors:
        factor_cols = [f.strip() for f in args.factors.split(",")]
    else:
        factor_cols = [c for c in exp_df.columns if c not in meta_cols]

    dates = sorted(ret_df["date"].unique())
    all_factor_returns = []

    for dt in dates:
        ret_slice = ret_df[ret_df["date"] == dt].set_index("code")["return"]
        exp_slice = exp_df[exp_df["date"] == dt].set_index("code")

        # 标准化因子暴露
        for col in factor_cols:
            if col in exp_slice.columns:
                exp_slice[col] = standardize(winsorize_mad(exp_slice[col]))

        weights = exp_slice[args.weight_col] if args.weight_col and args.weight_col in exp_slice.columns else None
        X = exp_slice[factor_cols]

        f_ret, f_se, residuals = cross_sectional_regression(ret_slice, X, weights)
        if f_ret is not None:
            record = {"date": dt}
            for i, col in enumerate(factor_cols):
                record[col] = round(float(f_ret[i]), 6)
                record[f"{col}_tstat"] = round(float(f_ret[i] / f_se[i]) if f_se[i] > 0 else 0, 4)
            all_factor_returns.append(record)

    fret_df = pd.DataFrame(all_factor_returns)

    # 因子收益统计
    factor_stats = {}
    for col in factor_cols:
        if col in fret_df.columns:
            vals = fret_df[col].dropna()
            factor_stats[col] = {
                "mean_return": round(float(vals.mean()), 6),
                "std": round(float(vals.std()), 6),
                "ir": round(float(vals.mean() / vals.std() * np.sqrt(252)) if vals.std() > 0 else 0, 4),
                "mean_tstat": round(float(fret_df[f"{col}_tstat"].mean()), 4),
                "pct_significant": round(float((fret_df[f"{col}_tstat"].abs() > 2).mean()), 4),
            }

    # 协方差矩阵
    cov_matrix = ewma_covariance(fret_df[factor_cols].dropna(), args.halflife)
    cov_dict = {}
    for i, fi in enumerate(factor_cols):
        for j, fj in enumerate(factor_cols):
            cov_dict[f"{fi}_{fj}"] = round(float(cov_matrix[i, j]), 8)

    result = {
        "ok": True,
        "n_dates": len(dates),
        "n_factors": len(factor_cols),
        "factors": factor_cols,
        "factor_stats": factor_stats,
        "covariance": cov_dict,
        "recent_factor_returns": fret_df.tail(20).to_dict(orient="records"),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
