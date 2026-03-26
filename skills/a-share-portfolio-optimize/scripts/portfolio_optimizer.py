#!/usr/bin/env python3
"""
A股组合优化器 — 支持多种优化方法
Usage:
    python portfolio_optimizer.py --returns_csv data.csv --method max_sharpe --rf 0.025 --long_only --max_weight 0.40
    python portfolio_optimizer.py --returns_csv data.csv --method risk_parity
    python portfolio_optimizer.py --returns_csv data.csv --method all --rf 0.025

CSV格式: 列为各资产日收益率，列名为股票代码，无日期列（或第一列为date会自动跳过）
"""

from scipy.optimize import minimize
import argparse
import json

import numpy as np
import pandas as pd
import sys


# ---------------------------------------------------------------------------
# 协方差估计
# ---------------------------------------------------------------------------

def sample_cov(returns: np.ndarray) -> np.ndarray:
    """样本协方差矩阵"""
    return np.cov(returns, rowvar=False)


def ledoit_wolf_shrink(returns: np.ndarray) -> np.ndarray:
    """Ledoit-Wolf 线性收缩估计（收缩到等方差-等相关目标）"""
    T, N = returns.shape
    S = np.cov(returns, rowvar=False)
    mean_var = np.trace(S) / N
    # 目标矩阵 F: 对角为样本方差均值，非对角为样本协方差均值
    avg_corr = (np.sum(S) - np.trace(S)) / (N * (N - 1)) if N > 1 else 0.0
    F = np.full((N, N), avg_corr)
    np.fill_diagonal(F, mean_var)

    # 估计最优收缩强度 (Ledoit & Wolf 2004 simplified)
    X = returns - returns.mean(axis=0)
    S2 = (X ** 2).T @ (X ** 2) / T - S ** 2
    delta = np.sum(S2) / T
    gamma = np.linalg.norm(S - F, 'fro') ** 2
    kappa = delta / gamma if gamma > 1e-10 else 1.0
    alpha = max(0.0, min(1.0, kappa))

    return alpha * F + (1 - alpha) * S


# ---------------------------------------------------------------------------
# 优化方法
# ---------------------------------------------------------------------------

def _portfolio_stats(w, mu, cov, rf=0.025):
    """计算组合统计指标"""
    ret = w @ mu
    vol = np.sqrt(w @ cov @ w)
    sharpe = (ret - rf) / vol if vol > 1e-10 else 0.0
    return ret, vol, sharpe


def optimize_min_var(mu, cov, long_only=True, max_weight=1.0):
    """最小方差组合"""
    n = len(mu)
    w0 = np.ones(n) / n
    bounds = [(0.0, max_weight)] * n if long_only else [(-max_weight, max_weight)] * n
    constraints = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0}]

    def obj(w):
        return w @ cov @ w

    result = minimize(obj, w0, method='SLSQP', bounds=bounds, constraints=constraints,
                      options={'maxiter': 1000, 'ftol': 1e-12})
    return result.x


def optimize_max_sharpe(mu, cov, rf=0.025, long_only=True, max_weight=1.0):
    """最大夏普比组合"""
    n = len(mu)
    w0 = np.ones(n) / n
    bounds = [(0.0, max_weight)] * n if long_only else [(-max_weight, max_weight)] * n
    constraints = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0}]

    def neg_sharpe(w):
        ret = w @ mu
        vol = np.sqrt(w @ cov @ w)
        return -(ret - rf) / vol if vol > 1e-10 else 0.0

    result = minimize(neg_sharpe, w0, method='SLSQP', bounds=bounds, constraints=constraints,
                      options={'maxiter': 1000, 'ftol': 1e-12})
    return result.x


def optimize_risk_parity(cov, long_only=True, max_weight=1.0):
    """风险平价（等风险贡献）组合"""
    n = cov.shape[0]
    w0 = np.ones(n) / n
    bounds = [(1e-6, max_weight)] * n  # 风险平价要求正权重
    constraints = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0}]

    def risk_parity_obj(w):
        sigma_p = np.sqrt(w @ cov @ w)
        if sigma_p < 1e-10:
            return 0.0
        marginal = cov @ w
        rc = w * marginal / sigma_p  # 各资产风险贡献
        target = sigma_p / n
        return np.sum((rc - target) ** 2)

    result = minimize(risk_parity_obj, w0, method='SLSQP', bounds=bounds, constraints=constraints,
                      options={'maxiter': 2000, 'ftol': 1e-14})
    return result.x


def equal_weight(n):
    """等权组合"""
    return np.ones(n) / n


def optimize_black_litterman(mu_eq, cov, P, Q, omega=None, tau=0.025,
                             rf=0.025, long_only=True, max_weight=1.0):
    """
    Black-Litterman 模型
    mu_eq: 均衡收益 (N,)
    cov: 协方差矩阵 (N,N)
    P: 观点矩阵 (K,N)
    Q: 观点收益 (K,)
    omega: 观点不确定性 (K,K), 默认 diag(P @ tau*cov @ P^T)
    """
    N = len(mu_eq)
    tau_cov = tau * cov
    tau_cov_inv = np.linalg.inv(tau_cov)

    if omega is None:
        omega = np.diag(np.diag(P @ tau_cov @ P.T))

    omega_inv = np.linalg.inv(omega)
    M = np.linalg.inv(tau_cov_inv + P.T @ omega_inv @ P)
    mu_bl = M @ (tau_cov_inv @ mu_eq + P.T @ omega_inv @ Q)

    # 基于 BL 预期收益做最大夏普
    return optimize_max_sharpe(mu_bl, cov, rf, long_only, max_weight), mu_bl


# ---------------------------------------------------------------------------
# 有效前沿
# ---------------------------------------------------------------------------

def efficient_frontier(mu, cov, rf=0.025, long_only=True, max_weight=1.0, n_points=20):
    """计算有效前沿上的点"""
    # 找收益率范围
    w_minvar = optimize_min_var(mu, cov, long_only, max_weight)
    ret_min = w_minvar @ mu
    ret_max = np.max(mu)

    target_rets = np.linspace(ret_min, ret_max, n_points)
    frontier = []
    n = len(mu)

    for target in target_rets:
        w0 = np.ones(n) / n
        bounds = [(0.0, max_weight)] * n if long_only else [(-max_weight, max_weight)] * n
        constraints = [
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0},
            {'type': 'ineq', 'fun': lambda w, t=target: w @ mu - t},
        ]

        def obj(w):
            return w @ cov @ w

        result = minimize(obj, w0, method='SLSQP', bounds=bounds, constraints=constraints,
                          options={'maxiter': 1000, 'ftol': 1e-12})
        if result.success:
            r, v, s = _portfolio_stats(result.x, mu, cov, rf)
            frontier.append({'return': round(r * 100, 2), 'volatility': round(v * 100, 2),
                             'sharpe': round(s, 3)})

    return frontier


# ---------------------------------------------------------------------------
# 风险分解
# ---------------------------------------------------------------------------

def risk_contribution(w, cov):
    """计算各资产的风险贡献"""
    sigma_p = np.sqrt(w @ cov @ w)
    if sigma_p < 1e-10:
        return np.zeros_like(w)
    marginal = cov @ w
    rc = w * marginal / sigma_p
    return rc


# ---------------------------------------------------------------------------
# 主函数
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description='A股组合优化器')
    parser.add_argument('--returns_csv', required=True, help='日收益率CSV文件路径')
    parser.add_argument('--method', default='max_sharpe',
                        choices=['min_var', 'max_sharpe', 'risk_parity', 'equal_weight', 'all'],
                        help='优化方法')
    parser.add_argument('--rf', type=float, default=0.025, help='无风险年化利率 (默认0.025)')
    parser.add_argument('--long_only', action='store_true', default=True, help='做多约束')
    parser.add_argument('--max_weight', type=float, default=0.40, help='单资产权重上限')
    parser.add_argument('--cov_method', default='sample', choices=['sample', 'shrink'],
                        help='协方差估计方法')
    parser.add_argument('--annualize', type=int, default=250, help='年化因子(交易日数)')
    parser.add_argument('--frontier', action='store_true', help='输出有效前沿')
    parser.add_argument('--frontier_points', type=int, default=15, help='有效前沿点数')

    args = parser.parse_args()

    # 读取数据
    df = pd.read_csv(args.returns_csv)
    # 如果第一列是日期，跳过
    if df.columns[0].lower() in ('date', 'trade_date', '日期'):
        df = df.iloc[:, 1:]

    assets = list(df.columns)
    returns = df.values  # T x N
    N = len(assets)
    T = len(returns)

    # 年化收益率和协方差
    mu_daily = returns.mean(axis=0)
    mu = mu_daily * args.annualize

    if args.cov_method == 'shrink':
        cov_daily = ledoit_wolf_shrink(returns)
    else:
        cov_daily = sample_cov(returns)
    cov = cov_daily * args.annualize

    # 个股统计
    vols = np.sqrt(np.diag(cov))
    sharpes = (mu - args.rf) / vols
    # 最大回撤（近似：基于累计收益）
    cum = (1 + returns).cumprod(axis=0)
    running_max = np.maximum.accumulate(cum, axis=0)
    drawdowns = (cum - running_max) / running_max
    max_dd = drawdowns.min(axis=0)

    asset_stats = []
    for i, name in enumerate(assets):
        asset_stats.append({
            'asset': name,
            'annual_return_pct': round(mu[i] * 100, 2),
            'annual_vol_pct': round(vols[i] * 100, 2),
            'sharpe': round(sharpes[i], 3),
            'max_drawdown_pct': round(max_dd[i] * 100, 2),
        })

    # 相关系数矩阵
    corr = np.corrcoef(returns, rowvar=False)
    corr_list = {assets[i]: {assets[j]: round(corr[i, j], 3) for j in range(N)} for i in range(N)}

    # 执行优化
    methods_to_run = ['min_var', 'max_sharpe', 'risk_parity', 'equal_weight'] if args.method == 'all' else [args.method]
    results = {}

    for method in methods_to_run:
        if method == 'min_var':
            w = optimize_min_var(mu, cov, args.long_only, args.max_weight)
        elif method == 'max_sharpe':
            w = optimize_max_sharpe(mu, cov, args.rf, args.long_only, args.max_weight)
        elif method == 'risk_parity':
            w = optimize_risk_parity(cov, args.long_only, args.max_weight)
        elif method == 'equal_weight':
            w = equal_weight(N)
        else:
            continue

        ret, vol, sharpe = _portfolio_stats(w, mu, cov, args.rf)
        rc = risk_contribution(w, cov)
        rc_pct = rc / rc.sum() * 100 if rc.sum() > 1e-10 else np.zeros(N)

        weights = {}
        risk_contribs = {}
        for i, name in enumerate(assets):
            if w[i] > 1e-4:
                weights[name] = round(w[i] * 100, 2)
                risk_contribs[name] = round(rc_pct[i], 2)

        results[method] = {
            'weights_pct': weights,
            'risk_contribution_pct': risk_contribs,
            'expected_return_pct': round(ret * 100, 2),
            'expected_volatility_pct': round(vol * 100, 2),
            'sharpe_ratio': round(sharpe, 3),
        }

    # 有效前沿
    frontier_data = None
    if args.frontier:
        frontier_data = efficient_frontier(mu, cov, args.rf, args.long_only, args.max_weight,
                                           args.frontier_points)

    # 输出
    output = {
        'data_info': {
            'assets': assets,
            'n_assets': N,
            'n_observations': T,
            'cov_method': args.cov_method,
            'risk_free_rate': args.rf,
            'max_weight': args.max_weight,
        },
        'asset_statistics': asset_stats,
        'correlation_matrix': corr_list,
        'optimization_results': results,
    }
    if frontier_data:
        output['efficient_frontier'] = frontier_data

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
