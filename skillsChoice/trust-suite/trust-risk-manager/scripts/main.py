#!/usr/bin/env python3
"""
信托风险管理与预警系统
Trust Risk Manager

功能：信用风险、市场风险、流动性风险监控与预警
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats


@dataclass
class RiskAsset:
    """风险资产"""
    asset_id: str
    asset_type: str
    exposure: float
    market_value: float
    credit_rating: Optional[str] = None
    counterparty: Optional[str] = None
    maturity_date: Optional[str] = None
    duration: Optional[float] = None
    volatility: Optional[float] = None


class CreditRiskAnalyzer:
    """信用风险分析器"""
    
    # 信用评级违约概率映射（简化版）
    PD_MAPPING = {
        'AAA': 0.0001, 'AA+': 0.0003, 'AA': 0.0005,
        'AA-': 0.001, 'A+': 0.002, 'A': 0.003,
        'A-': 0.005, 'BBB+': 0.01, 'BBB': 0.02,
        'BBB-': 0.03, 'BB+': 0.05, 'BB': 0.08,
        'BB-': 0.12, 'B+': 0.18, 'B': 0.25,
        'B-': 0.35, 'CCC': 0.50, 'CC': 0.70,
        'C': 0.90, 'D': 1.0
    }
    
    def __init__(self, assets: List[RiskAsset]):
        self.assets = [a for a in assets if a.asset_type in ['非标债权', '债券', '贷款']]
    
    def analyze(self) -> Dict:
        """信用风险分析"""
        if not self.assets:
            return {'score': 100, 'level': '无信用风险敞口', 'details': {}}
        
        total_exposure = sum(a.exposure for a in self.assets)
        
        # 按评级分布
        exposure_by_rating = {}
        for asset in self.assets:
            rating = asset.credit_rating or '未评级'
            exposure_by_rating[rating] = exposure_by_rating.get(rating, 0) + asset.exposure
        
        # 计算加权平均PD
        weighted_pd = 0
        for asset in self.assets:
            pd = self.PD_MAPPING.get(asset.credit_rating, 0.05)
            weighted_pd += pd * (asset.exposure / total_exposure)
        
        # 集中度风险
        max_single_exposure = max(a.exposure for a in self.assets) if self.assets else 0
        concentration_ratio = max_single_exposure / total_exposure if total_exposure > 0 else 0
        
        # 评分（0-100，越高越好）
        pd_score = max(0, 100 - weighted_pd * 1000)
        concentration_score = max(0, 100 - concentration_ratio * 100)
        score = (pd_score * 0.6 + concentration_score * 0.4)
        
        return {
            'score': round(score, 1),
            'level': self._score_to_level(score),
            'weighted_pd': round(weighted_pd * 100, 4),
            'exposure_by_rating': {k: round(v/total_exposure*100, 1) 
                                    for k, v in exposure_by_rating.items()},
            'concentration_ratio': round(concentration_ratio, 2),
            'total_exposure': total_exposure,
            'asset_count': len(self.assets)
        }
    
    def _score_to_level(self, score: float) -> str:
        if score >= 80: return '低信用风险'
        elif score >= 60: return '中等信用风险'
        elif score >= 40: return '较高信用风险'
        else: return '高信用风险'


class MarketRiskAnalyzer:
    """市场风险分析器"""
    
    def __init__(self, assets: List[RiskAsset], historical_prices: pd.DataFrame = None):
        self.assets = assets
        self.historical_prices = historical_prices
    
    def analyze(self, confidence_level: float = 0.95, time_horizon: int = 1) -> Dict:
        """市场风险分析"""
        total_value = sum(a.market_value for a in self.assets)
        
        # 计算组合波动率
        portfolio_vol = self._calculate_portfolio_volatility()
        
        # 计算VaR和CVaR
        var = self._calculate_var(portfolio_vol, confidence_level, time_horizon, total_value)
        cvar = self._calculate_cvar(portfolio_vol, confidence_level, time_horizon, total_value)
        
        # 久期和凸性（固收类）
        fixed_income_assets = [a for a in self.assets if a.asset_type in ['债券', '非标债权']]
        avg_duration = np.mean([a.duration for a in fixed_income_assets if a.duration]) if fixed_income_assets else 0
        
        # Beta（权益类）
        equity_assets = [a for a in self.assets if a.asset_type in ['股票', '基金']]
        avg_beta = np.mean([a.volatility for a in equity_assets if a.volatility]) if equity_assets else 0
        
        # 评分
        var_ratio = var / total_value if total_value > 0 else 0
        score = max(0, 100 - var_ratio * 1000 - avg_duration * 5)
        
        return {
            'score': round(score, 1),
            'level': self._score_to_level(score),
            'portfolio_volatility': round(portfolio_vol * 100, 2),
            f'var_{int(confidence_level*100)}': round(var, 2),
            f'cvar_{int(confidence_level*100)}': round(cvar, 2),
            'var_ratio': round(var_ratio * 100, 2),
            'average_duration': round(avg_duration, 2),
            'average_beta': round(avg_beta, 2),
            'total_market_value': total_value
        }
    
    def _calculate_portfolio_volatility(self) -> float:
        """计算组合波动率"""
        if self.historical_prices is not None and len(self.historical_prices) > 1:
            returns = self.historical_prices.pct_change().dropna()
            return returns.std() * np.sqrt(252)  # 年化波动率
        
        # 使用资产波动率加权
        total_value = sum(a.market_value for a in self.assets)
        if total_value == 0:
            return 0
        
        weighted_vol = sum(
            (a.market_value / total_value) * (a.volatility or 0.15)
            for a in self.assets
        )
        return weighted_vol
    
    def _calculate_var(self, volatility: float, confidence: float, 
                       horizon: int, portfolio_value: float) -> float:
        """计算VaR"""
        z_score = stats.norm.ppf(confidence)
        var = portfolio_value * volatility * z_score * np.sqrt(horizon / 252)
        return var
    
    def _calculate_cvar(self, volatility: float, confidence: float,
                        horizon: int, portfolio_value: float) -> float:
        """计算CVaR（条件VaR）"""
        z_score = stats.norm.ppf(confidence)
        cvar_multiplier = stats.norm.pdf(z_score) / (1 - confidence)
        cvar = portfolio_value * volatility * cvar_multiplier * np.sqrt(horizon / 252)
        return cvar
    
    def _score_to_level(self, score: float) -> str:
        if score >= 80: return '低市场风险'
        elif score >= 60: return '中等市场风险'
        elif score >= 40: return '较高市场风险'
        else: return '高市场风险'


class LiquidityRiskAnalyzer:
    """流动性风险分析器"""
    
    def __init__(self, assets: List[RiskAsset], liabilities: List[Dict] = None):
        self.assets = assets
        self.liabilities = liabilities or []
    
    def analyze(self) -> Dict:
        """流动性风险分析"""
        total_assets = sum(a.market_value for a in self.assets)
        
        # 资产流动性分类
        liquid_assets = sum(a.market_value for a in self.assets 
                           if a.asset_type in ['现金', '货币基金', '国债'])
        illiquid_assets = sum(a.market_value for a in self.assets 
                             if a.asset_type in ['非标债权', '私募股权', '房地产'])
        
        # 流动性比率
        liquidity_ratio = liquid_assets / total_assets if total_assets > 0 else 0
        
        # 期限错配（简化计算）
        avg_asset_maturity = self._calculate_avg_maturity(self.assets)
        avg_liability_maturity = self._calculate_avg_maturity_liabilities()
        maturity_mismatch = avg_asset_maturity - avg_liability_maturity
        
        # 评分
        score = (liquidity_ratio * 50 + 
                max(0, 50 - abs(maturity_mismatch) * 5))
        
        return {
            'score': round(score, 1),
            'level': self._score_to_level(score),
            'liquidity_ratio': round(liquidity_ratio, 2),
            'liquid_assets': liquid_assets,
            'illiquid_assets': illiquid_assets,
            'avg_asset_maturity': round(avg_asset_maturity, 1),
            'avg_liability_maturity': round(avg_liability_maturity, 1),
            'maturity_mismatch': round(maturity_mismatch, 1)
        }
    
    def _calculate_avg_maturity(self, assets: List[RiskAsset]) -> float:
        """计算平均资产期限"""
        total = sum(a.market_value for a in assets)
        if total == 0:
            return 0
        
        weighted_maturity = 0
        for asset in assets:
            if asset.maturity_date:
                maturity = datetime.strptime(asset.maturity_date, '%Y-%m-%d')
                days_to_maturity = (maturity - datetime.now()).days
                weighted_maturity += (asset.market_value / total) * (days_to_maturity / 365)
        
        return weighted_maturity
    
    def _calculate_avg_maturity_liabilities(self) -> float:
        """计算平均负债期限"""
        # 简化处理，假设负债平均期限
        return 0.5  # 6个月
    
    def _score_to_level(self, score: float) -> str:
        if score >= 80: return '流动性充足'
        elif score >= 60: return '流动性适中'
        elif score >= 40: return '流动性偏紧'
        else: return '流动性风险高'


class StressTester:
    """压力测试"""
    
    def __init__(self, assets: List[RiskAsset]):
        self.assets = assets
        self.total_value = sum(a.market_value for a in assets)
    
    def run_scenarios(self, scenarios: List[Dict]) -> Dict:
        """运行压力测试场景"""
        results = {}
        
        for scenario in scenarios:
            name = scenario['name']
            shocks = scenario['shocks']
            
            total_impact = 0
            asset_impacts = []
            
            for asset in self.assets:
                impact = self._calculate_impact(asset, shocks)
                total_impact += impact
                asset_impacts.append({
                    'asset_id': asset.asset_id,
                    'impact': round(impact, 2)
                })
            
            results[name] = {
                'portfolio_value_change': round(total_impact / self.total_value * 100, 2) if self.total_value else 0,
                'absolute_loss': round(total_impact, 2),
                'asset_impacts': asset_impacts
            }
        
        return results
    
    def _calculate_impact(self, asset: RiskAsset, shocks: Dict) -> float:
        """计算单资产冲击影响"""
        impact = 0
        
        if 'interest_rate_change' in shocks and asset.duration:
            # 利率冲击：-Duration * Δr * 市值
            rate_change = shocks['interest_rate_change'] / 100  # 转换为小数
            impact += -asset.duration * rate_change * asset.market_value
        
        if 'equity_shock' in shocks and asset.asset_type in ['股票', '基金']:
            equity_shock = shocks['equity_shock'] / 100
            impact += equity_shock * asset.market_value
        
        if 'credit_spread_widening' in shocks and asset.credit_rating:
            # 信用利差扩大影响
            spread_change = shocks['credit_spread_widening'] / 100
            # 简化处理：低评级资产受影响更大
            rating_factor = 1.0 if asset.credit_rating in ['AAA', 'AA+'] else 1.5
            impact += -spread_change * rating_factor * asset.market_value
        
        return impact


class EarlyWarningSystem:
    """风险预警系统"""
    
    def __init__(self, assets: List[RiskAsset]):
        self.assets = assets
        self.thresholds = {
            'single_concentration': 0.15,  # 单一集中度15%
            'var_limit': 0.05,             # VaR 5%
            'liquidity_ratio': 0.2,        # 流动性比率20%
            'avg_maturity': 5.0            # 平均期限5年
        }
    
    def check_warnings(self, risk_metrics: Dict) -> List[Dict]:
        """检查预警指标"""
        warnings = []
        
        # 集中度预警
        total = sum(a.market_value for a in self.assets)
        for asset in self.assets:
            concentration = asset.market_value / total if total > 0 else 0
            if concentration > self.thresholds['single_concentration']:
                warnings.append({
                    'level': 'yellow' if concentration < 0.20 else 'red',
                    'type': '集中度风险',
                    'indicator': f'{asset.asset_id}集中度',
                    'threshold': f"{self.thresholds['single_concentration']*100}%",
                    'current': f"{concentration*100:.1f}%",
                    'suggestion': '建议降低该资产配置比例或增加分散度'
                })
        
        # VaR预警
        if risk_metrics.get('var_ratio', 0) > self.thresholds['var_limit'] * 100:
            warnings.append({
                'level': 'red',
                'type': '市场风险',
                'indicator': 'VaR比率',
                'threshold': f"{self.thresholds['var_limit']*100}%",
                'current': f"{risk_metrics['var_ratio']:.2f}%",
                'suggestion': '建议降低组合波动率或对冲风险敞口'
            })
        
        # 流动性预警
        if risk_metrics.get('liquidity_ratio', 1) < self.thresholds['liquidity_ratio']:
            warnings.append({
                'level': 'yellow',
                'type': '流动性风险',
                'indicator': '流动性比率',
                'threshold': f"{self.thresholds['liquidity_ratio']*100}%",
                'current': f"{risk_metrics['liquidity_ratio']*100:.1f}%",
                'suggestion': '建议增加高流动性资产配置'
            })
        
        return warnings


class TrustRiskManager:
    """信托风险管理主类"""
    
    def __init__(self):
        self.assets = []
    
    def load_assets(self, assets_data: List[Dict]):
        """加载资产数据"""
        self.assets = [RiskAsset(**a) for a in assets_data]
    
    def analyze(self, risk_type: str = 'all', config: Dict = None) -> Dict:
        """执行风险分析"""
        config = config or {}
        confidence = config.get('confidence_level', 0.95)
        horizon = config.get('time_horizon', 1)
        
        result = {'status': 'success', 'risk_type': risk_type}
        
        if risk_type in ['all', 'credit']:
            credit_analyzer = CreditRiskAnalyzer(self.assets)
            result['credit_risk'] = credit_analyzer.analyze()
        
        if risk_type in ['all', 'market']:
            market_analyzer = MarketRiskAnalyzer(self.assets)
            result['market_risk'] = market_analyzer.analyze(confidence, horizon)
        
        if risk_type in ['all', 'liquidity']:
            liquidity_analyzer = LiquidityRiskAnalyzer(self.assets)
            result['liquidity_risk'] = liquidity_analyzer.analyze()
        
        # 综合评分
        scores = []
        if 'credit_risk' in result:
            scores.append(result['credit_risk']['score'])
        if 'market_risk' in result:
            scores.append(result['market_risk']['score'])
        if 'liquidity_risk' in result:
            scores.append(result['liquidity_risk']['score'])
        
        if scores:
            result['overall_risk_score'] = round(np.mean(scores), 1)
            result['overall_risk_level'] = self._score_to_level(result['overall_risk_score'])
        
        # 预警检查
        risk_metrics = {
            'var_ratio': result.get('market_risk', {}).get('var_ratio', 0),
            'liquidity_ratio': result.get('liquidity_risk', {}).get('liquidity_ratio', 1)
        }
        warning_system = EarlyWarningSystem(self.assets)
        result['early_warnings'] = warning_system.check_warnings(risk_metrics)
        
        result['metadata'] = {
            'source': 'trust-risk-manager',
            'version': '1.0.0',
            'timestamp': datetime.now().isoformat()
        }
        
        return result
    
    def stress_test(self, scenarios: List[Dict]) -> Dict:
        """执行压力测试"""
        tester = StressTester(self.assets)
        results = tester.run_scenarios(scenarios)
        
        return {
            'status': 'success',
            'stress_test': results,
            'metadata': {
                'source': 'trust-risk-manager',
                'version': '1.0.0',
                'timestamp': datetime.now().isoformat()
            }
        }
    
    def _score_to_level(self, score: float) -> str:
        if score >= 80: return '低风险'
        elif score >= 60: return '中等风险'
        elif score >= 40: return '较高风险'
        else: return '高风险'


def main():
    parser = argparse.ArgumentParser(description='信托风险管理与预警系统')
    parser.add_argument('--risk-type', default='all',
                       choices=['all', 'credit', 'market', 'liquidity'],
                       help='风险类型')
    parser.add_argument('--assets', required=True, help='资产数据文件')
    parser.add_argument('--stress-test', action='store_true', help='执行压力测试')
    parser.add_argument('--scenarios', help='压力测试场景文件')
    parser.add_argument('--confidence', type=float, default=0.95, help='置信水平')
    parser.add_argument('--output', default='json', choices=['json'], help='输出格式')
    
    args = parser.parse_args()
    
    # 加载资产数据
    with open(args.assets, 'r') as f:
        assets_data = json.load(f)
    
    # 执行分析
    manager = TrustRiskManager()
    manager.load_assets(assets_data)
    
    if args.stress_test:
        if not args.scenarios:
            print("错误：压力测试需要提供 --scenarios 参数", file=sys.stderr)
            sys.exit(1)
        
        with open(args.scenarios, 'r') as f:
            scenarios = json.load(f)
        
        result = manager.stress_test(scenarios)
    else:
        config = {'confidence_level': args.confidence}
        result = manager.analyze(args.risk_type, config)
    
    # 输出结果
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
