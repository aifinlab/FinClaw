#!/usr/bin/env python3
"""
信托资产配置优化器
Trust Asset Allocation Optimizer

支持：均值方差优化、风险平价、Black-Litterman、目标日期策略
"""

import argparse
import json
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.optimize import minimize
import cvxpy as cp


@dataclass
class AssetClass:
    """资产类别"""
    name: str
    expected_return: float  # 年化预期收益 %
    volatility: float       # 年化波动率 %
    asset_type: str         # 资产类型


class MeanVarianceOptimizer:
    """均值-方差优化器 (Markowitz)"""
    
    def __init__(self, assets: List[AssetClass], correlation_matrix: np.ndarray = None):
        self.assets = assets
        self.n = len(assets)
        self.returns = np.array([a.expected_return for a in assets])
        self.volatilities = np.array([a.volatility for a in assets])
        
        # 构建协方差矩阵
        if correlation_matrix is None:
            # 默认单位矩阵（资产间无相关性）
            correlation_matrix = np.eye(self.n)
        self.cov_matrix = np.outer(self.volatilities, self.volatilities) * correlation_matrix
    
    def optimize(self, target_return: Optional[float] = None, 
                 risk_tolerance: Optional[float] = None,
                 constraints: Dict = None) -> Dict:
        """
        均值方差优化
        
        Args:
            target_return: 目标收益率（%）
            risk_tolerance: 风险容忍度（最大波动率%）
            constraints: 约束条件
        """
        w = cp.Variable(self.n)
        
        # 组合收益和方差
        portfolio_return = self.returns @ w
        portfolio_variance = cp.quad_form(w, self.cov_matrix)
        
        # 约束条件
        constraint_list = [cp.sum(w) == 1, w >= 0]  # 权重和为1，非负
        
        if constraints:
            # 最小权重约束
            if 'min_weights' in constraints:
                for i, asset in enumerate(self.assets):
                    min_w = constraints['min_weights'].get(asset.name, 0)
                    constraint_list.append(w[i] >= min_w)
            
            # 最大权重约束
            if 'max_weights' in constraints:
                for i, asset in enumerate(self.assets):
                    max_w = constraints['max_weights'].get(asset.name, 1)
                    constraint_list.append(w[i] <= max_w)
        
        # 目标函数
        if target_return is not None:
            # 给定目标收益，最小化风险
            constraint_list.append(portfolio_return >= target_return)
            objective = cp.Minimize(portfolio_variance)
        elif risk_tolerance is not None:
            # 给定风险上限，最大化收益
            constraint_list.append(cp.sqrt(portfolio_variance) <= risk_tolerance)
            objective = cp.Maximize(portfolio_return)
        else:
            # 默认：最大化夏普比率（假设无风险利率3%）
            risk_free_rate = 3.0
            objective = cp.Maximize((portfolio_return - risk_free_rate) / cp.sqrt(portfolio_variance))
        
        # 求解
        problem = cp.Problem(objective, constraint_list)
        problem.solve()
        
        if w.value is None:
            return {'status': 'error', 'message': '优化问题无解'}
        
        weights = w.value
        opt_return = float(self.returns @ weights)
        opt_volatility = float(np.sqrt(weights.T @ self.cov_matrix @ weights))
        sharpe = (opt_return - 3.0) / opt_volatility if opt_volatility > 0 else 0
        
        return {
            'status': 'success',
            'weights': {asset.name: round(float(weights[i]), 4) for i, asset in enumerate(self.assets)},
            'expected_return': round(opt_return, 2),
            'volatility': round(opt_volatility, 2),
            'sharpe_ratio': round(sharpe, 2),
            'diversification_ratio': round(self._calculate_diversification_ratio(weights), 2)
        }
    
    def generate_efficient_frontier(self, num_points: int = 50) -> List[Dict]:
        """生成有效前沿"""
        min_return = np.min(self.returns)
        max_return = np.max(self.returns)
        target_returns = np.linspace(min_return, max_return, num_points)
        
        frontier = []
        for target in target_returns:
            result = self.optimize(target_return=target)
            if result['status'] == 'success':
                frontier.append({
                    'return': result['expected_return'],
                    'volatility': result['volatility'],
                    'sharpe': result['sharpe_ratio']
                })
        
        return frontier
    
    def _calculate_diversification_ratio(self, weights: np.ndarray) -> float:
        """计算分散化比率"""
        portfolio_vol = np.sqrt(weights.T @ self.cov_matrix @ weights)
        weighted_vol = np.sum(weights * self.volatilities)
        return weighted_vol / portfolio_vol if portfolio_vol > 0 else 1.0


class RiskParityOptimizer:
    """风险平价优化器"""
    
    def __init__(self, assets: List[AssetClass], correlation_matrix: np.ndarray = None):
        self.assets = assets
        self.n = len(assets)
        self.returns = np.array([a.expected_return for a in assets])
        self.volatilities = np.array([a.volatility for a in assets])
        
        if correlation_matrix is None:
            correlation_matrix = np.eye(self.n)
        self.cov_matrix = np.outer(self.volatilities, self.volatilities) * correlation_matrix
    
    def optimize(self, target_risk: Optional[float] = None) -> Dict:
        """
        风险平价优化
        使各资产对组合风险的贡献相等
        """
        def risk_parity_objective(w):
            w = np.array(w)
            portfolio_vol = np.sqrt(w.T @ self.cov_matrix @ w)
            marginal_risk = (self.cov_matrix @ w) / portfolio_vol
            risk_contrib = w * marginal_risk
            target = portfolio_vol / self.n
            return np.sum((risk_contrib - target) ** 2)
        
        # 初始权重
        w0 = np.ones(self.n) / self.n
        
        # 约束
        constraints = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}]
        bounds = [(0, 1) for _ in range(self.n)]
        
        # 求解
        result = minimize(risk_parity_objective, w0, method='SLSQP',
                         bounds=bounds, constraints=constraints)
        
        if not result.success:
            return {'status': 'error', 'message': result.message}
        
        weights = result.x
        portfolio_vol = np.sqrt(weights.T @ self.cov_matrix @ weights)
        portfolio_return = np.sum(weights * self.returns)
        
        # 计算风险贡献
        marginal_risk = (self.cov_matrix @ weights) / portfolio_vol
        risk_contrib = weights * marginal_risk
        
        return {
            'status': 'success',
            'weights': {asset.name: round(float(weights[i]), 4) for i, asset in enumerate(self.assets)},
            'expected_return': round(float(portfolio_return), 2),
            'volatility': round(float(portfolio_vol), 2),
            'risk_contribution': {asset.name: round(float(risk_contrib[i] / portfolio_vol), 4) 
                                  for i, asset in enumerate(self.assets)},
            'sharpe_ratio': round(float((portfolio_return - 3.0) / portfolio_vol), 2)
        }


class BlackLittermanOptimizer:
    """Black-Litterman资产配置"""
    
    def __init__(self, assets: List[AssetClass], market_weights: np.ndarray = None,
                 correlation_matrix: np.ndarray = None, tau: float = 0.05):
        self.assets = assets
        self.n = len(assets)
        self.returns = np.array([a.expected_return for a in assets])
        self.volatilities = np.array([a.volatility for a in assets])
        self.tau = tau  # 不确定性参数
        
        if correlation_matrix is None:
            correlation_matrix = np.eye(self.n)
        self.cov_matrix = np.outer(self.volatilities, self.volatilities) * correlation_matrix
        
        # 市场均衡权重（默认等权）
        if market_weights is None:
            market_weights = np.ones(self.n) / self.n
        self.market_weights = market_weights
        
        # 计算均衡收益（逆向优化）
        self.pi = self._calculate_equilibrium_returns()
    
    def _calculate_equilibrium_returns(self) -> np.ndarray:
        """通过逆向优化计算均衡收益"""
        # 假设风险厌恶系数 lambda = 2.5
        lam = 2.5
        pi = lam * self.cov_matrix @ self.market_weights
        return pi
    
    def optimize(self, views: List[Dict], view_confidences: List[float] = None) -> Dict:
        """
        Black-Litterman优化
        
        Args:
            views: 投资者观点列表
                [{'assets': ['权益类'], 'return': 12.0, 'certainty': 0.6}, ...]
            view_confidences: 观点置信度
        """
        if not views:
            # 无观点时使用均衡收益
            bl_returns = self.pi
        else:
            # 构建观点矩阵 P 和观点收益 Q
            P = np.zeros((len(views), self.n))
            Q = np.zeros(len(views))
            Omega = np.zeros((len(views), len(views)))
            
            for i, view in enumerate(views):
                assets = view['assets']
                ret = view['return']
                certainty = view.get('certainty', 0.5)
                
                # 设置观点权重
                for asset_name in assets:
                    for j, asset in enumerate(self.assets):
                        if asset.name == asset_name:
                            P[i, j] = 1.0 / len(assets)
                
                Q[i] = ret
                Omega[i, i] = self.tau * certainty
            
            # 计算后验收益
            # E(R) = [(τΣ)^-1 + P^T * Ω^-1 * P]^-1 * [(τΣ)^-1 * Π + P^T * Ω^-1 * Q]
            tau_sigma_inv = np.linalg.inv(self.tau * self.cov_matrix)
            omega_inv = np.linalg.inv(Omega)
            
            M = tau_sigma_inv + P.T @ omega_inv @ P
            M_inv = np.linalg.inv(M)
            
            bl_returns = M_inv @ (tau_sigma_inv @ self.pi + P.T @ omega_inv @ Q)
        
        # 使用调整后的收益进行均值方差优化
        w = cp.Variable(self.n)
        portfolio_return = bl_returns @ w
        portfolio_variance = cp.quad_form(w, self.cov_matrix)
        
        constraints = [cp.sum(w) == 1, w >= 0]
        
        # 最大化夏普比率
        risk_free = 3.0
        objective = cp.Maximize((portfolio_return - risk_free) / cp.sqrt(portfolio_variance))
        
        problem = cp.Problem(objective, constraints)
        problem.solve()
        
        if w.value is None:
            return {'status': 'error', 'message': '优化失败'}
        
        weights = w.value
        opt_return = float(bl_returns @ weights)
        opt_vol = float(np.sqrt(weights.T @ self.cov_matrix @ weights))
        
        return {
            'status': 'success',
            'weights': {asset.name: round(float(weights[i]), 4) for i, asset in enumerate(self.assets)},
            'expected_return': round(opt_return, 2),
            'volatility': round(opt_vol, 2),
            'equilibrium_returns': {asset.name: round(float(self.pi[i]), 2) for i, asset in enumerate(self.assets)},
            'adjusted_returns': {asset.name: round(float(bl_returns[i]), 2) for i, asset in enumerate(self.assets)},
            'sharpe_ratio': round((opt_return - 3.0) / opt_vol, 2)
        }


class TargetDateAllocator:
    """目标日期资产配置"""
    
    def __init__(self, target_year: int, current_age: Optional[int] = None,
                 retirement_age: int = 65):
        self.target_year = target_year
        self.current_age = current_age
        self.retirement_age = retirement_age
        
        if current_age:
            self.years_to_target = retirement_age - current_age
        else:
            self.years_to_target = target_year - datetime.now().year
    
    def calculate_glide_path(self) -> Dict:
        """
        计算下滑轨道（Glide Path）
        随着年龄增长，逐步降低权益类资产比例
        """
        # 经典下滑轨道公式
        # 权益类比例 = max(20%, min(80%, 100 - age))
        # 随着年龄增长，权益类比例从约80%逐步降至20%
        
        if self.current_age:
            equity_ratio = max(0.20, min(0.80, (100 - self.current_age) / 100))
        else:
            # 基于目标日期计算
            years_remaining = max(1, self.years_to_target)
            equity_ratio = max(0.20, min(0.80, years_remaining / 40))
        
        # 资产配置
        allocation = {
            '权益类': round(equity_ratio, 2),
            '固收类': round(0.60 - equity_ratio * 0.4, 2),
            '现金管理类': round(0.15 + equity_ratio * 0.1, 2),
            '另类投资': 0.10
        }
        
        # 调整确保总和为1
        total = sum(allocation.values())
        if abs(total - 1.0) > 0.01:
            allocation['固收类'] += round(1.0 - total, 2)
        
        # 未来调整计划
        rebalancing_schedule = []
        for year in range(1, min(6, self.years_to_target + 1)):
            future_age = (self.current_age or 35) + year
            future_equity = max(0.20, min(0.80, (100 - future_age) / 100))
            rebalancing_schedule.append({
                'year': datetime.now().year + year,
                'equity_target': round(future_equity, 2),
                'adjustment': round(future_equity - equity_ratio, 2)
            })
        
        return {
            'status': 'success',
            'target_year': self.target_year,
            'years_to_target': self.years_to_target,
            'current_allocation': allocation,
            'glide_path': rebalancing_schedule,
            'risk_profile': self._get_risk_profile(equity_ratio)
        }
    
    def _get_risk_profile(self, equity_ratio: float) -> str:
        if equity_ratio >= 0.60:
            return "进取型"
        elif equity_ratio >= 0.40:
            return "平衡型"
        elif equity_ratio >= 0.25:
            return "稳健型"
        else:
            return "保守型"


class TrustAssetAllocation:
    """信托资产配置主类"""
    
    def __init__(self):
        self.mv_optimizer = None
        self.rp_optimizer = None
        self.bl_optimizer = None
        self.td_allocator = None
    
    def optimize(self, config: Dict) -> Dict:
        """执行资产配置优化"""
        strategy = config.get('strategy', 'mean_variance')
        assets = [AssetClass(**a) for a in config.get('asset_classes', [])]
        
        if not assets:
            return {'status': 'error', 'message': '未提供资产类别'}
        
        # 构建相关性矩阵
        corr_matrix = config.get('correlation_matrix')
        if corr_matrix:
            corr_matrix = np.array(corr_matrix)
        
        result = {'strategy': strategy}
        
        if strategy == 'mean_variance':
            optimizer = MeanVarianceOptimizer(assets, corr_matrix)
            result['optimization'] = optimizer.optimize(
                target_return=config.get('target_return'),
                risk_tolerance=config.get('risk_tolerance'),
                constraints=config.get('constraints')
            )
            result['efficient_frontier'] = optimizer.generate_efficient_frontier(20)
        
        elif strategy == 'risk_parity':
            optimizer = RiskParityOptimizer(assets, corr_matrix)
            result['optimization'] = optimizer.optimize()
        
        elif strategy == 'black_litterman':
            market_weights = config.get('market_weights')
            if market_weights:
                market_weights = np.array(list(market_weights.values()))
            
            optimizer = BlackLittermanOptimizer(
                assets, market_weights, corr_matrix,
                tau=config.get('tau', 0.05)
            )
            result['optimization'] = optimizer.optimize(
                views=config.get('views', [])
            )
        
        elif strategy == 'target_date':
            allocator = TargetDateAllocator(
                target_year=config.get('target_year', 2045),
                current_age=config.get('current_age'),
                retirement_age=config.get('retirement_age', 65)
            )
            result['optimization'] = allocator.calculate_glide_path()
        
        else:
            return {'status': 'error', 'message': f'未知的策略类型: {strategy}'}
        
        # 添加元数据
        result['metadata'] = {
            'source': 'trust-asset-allocation',
            'version': '1.0.0',
            'timestamp': datetime.now().isoformat()
        }
        
        return result
    
    def backtest(self, config: Dict, historical_returns: pd.DataFrame) -> Dict:
        """回测资产配置策略"""
        # 简化的回测逻辑
        opt_result = self.optimize(config)
        
        if opt_result['optimization']['status'] != 'success':
            return opt_result
        
        weights = opt_result['optimization']['weights']
        weight_array = np.array(list(weights.values()))
        
        # 计算组合历史收益
        portfolio_returns = historical_returns @ weight_array
        
        # 计算回测指标
        total_return = (1 + portfolio_returns).prod() - 1
        annual_return = portfolio_returns.mean() * 252
        annual_vol = portfolio_returns.std() * np.sqrt(252)
        sharpe = (annual_return - 0.03) / annual_vol if annual_vol > 0 else 0
        max_dd = self._calculate_max_drawdown(portfolio_returns)
        
        return {
            'status': 'success',
            'backtest_metrics': {
                'total_return': round(total_return * 100, 2),
                'annual_return': round(annual_return * 100, 2),
                'annual_volatility': round(annual_vol * 100, 2),
                'sharpe_ratio': round(sharpe, 2),
                'max_drawdown': round(max_dd * 100, 2),
                'calmar_ratio': round(annual_return / abs(max_dd), 2) if max_dd != 0 else 0
            },
            'allocation': weights
        }
    
    def _calculate_max_drawdown(self, returns: pd.Series) -> float:
        """计算最大回撤"""
        cum_returns = (1 + returns).cumprod()
        rolling_max = cum_returns.expanding().max()
        drawdown = (cum_returns - rolling_max) / rolling_max
        return drawdown.min()


def main():
    parser = argparse.ArgumentParser(description='信托资产配置优化器')
    parser.add_argument('--strategy', required=True,
                       choices=['mean_variance', 'risk_parity', 'black_litterman', 'target_date'],
                       help='优化策略')
    parser.add_argument('--config', help='配置文件路径')
    parser.add_argument('--target-return', type=float, help='目标收益率(%)')
    parser.add_argument('--risk-tolerance', type=float, help='风险容忍度(%)')
    parser.add_argument('--target-year', type=int, help='目标日期(年)')
    parser.add_argument('--current-age', type=int, help='当前年龄')
    parser.add_argument('--output', default='json', choices=['json'],
                       help='输出格式')
    
    args = parser.parse_args()
    
    # 加载配置
    if args.config:
        with open(args.config, 'r') as f:
            config = json.load(f)
    else:
        config = {'strategy': args.strategy}
        
        if args.target_return:
            config['target_return'] = args.target_return
        if args.risk_tolerance:
            config['risk_tolerance'] = args.risk_tolerance
        if args.target_year:
            config['target_year'] = args.target_year
        if args.current_age:
            config['current_age'] = args.current_age
        
        # 默认资产类别
        config['asset_classes'] = [
            {'name': '现金管理类', 'expected_return': 3.0, 'volatility': 1.0, 'asset_type': '货币'},
            {'name': '固收类', 'expected_return': 5.5, 'volatility': 4.0, 'asset_type': '债券'},
            {'name': '权益类', 'expected_return': 10.0, 'volatility': 18.0, 'asset_type': '股票'},
            {'name': '另类投资', 'expected_return': 8.0, 'volatility': 12.0, 'asset_type': '另类'}
        ]
    
    # 执行优化
    allocator = TrustAssetAllocation()
    result = allocator.optimize(config)
    
    # 输出结果
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
