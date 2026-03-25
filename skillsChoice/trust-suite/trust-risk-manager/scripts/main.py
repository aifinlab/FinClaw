#!/usr/bin/env python3
"""
信托风险管理与预警系统 v3.0
功能：信用风险、市场风险、流动性风险监控与预警
数据源：自动从数据适配器获取（用益信托网/中国信登/同花顺/本地缓存）

变更记录：
  v3.0 - 移除JSON文件加载，完全接入数据适配器
  v2.0 - 接入数据适配器
  v1.0 - 基础版本

数据更新机制：
  1. 优先使用实时数据源（用益信托网/中国信登/同花顺）
  2. 自动回退到本地缓存数据
  3. 定期运行 data/update_data.py 更新本地缓存
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

# 添加数据适配器路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'data'))
from trust_data_adapter import get_data_provider, TrustDataProvider, TrustProductData


def norm_ppf(p):
    """标准正态分布分位数函数"""
    if p <= 0 or p >= 1:
        return float('inf') if p >= 1 else float('-inf')
    
    a = 0.147
    sign = -1 if p < 0.5 else 1
    x = 2 * p - 1 if p < 0.5 else 2 * (1 - p) - 1
    ln = np.log(1 - x**2)
    sqrt_term = np.sqrt(ln / (ln - a * x**2))
    result = sign * sqrt_term * (2.515517 + 0.802853 * sqrt_term + 0.010328 * sqrt_term**2) / \
             (1 + 1.432788 * sqrt_term + 0.189269 * sqrt_term**2 + 0.001308 * sqrt_term**3)
    return -result if p < 0.5 else result


def norm_pdf(x):
    """标准正态分布概率密度函数"""
    return (1 / np.sqrt(2 * np.pi)) * np.exp(-0.5 * x**2)


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
        self.assets = [a for a in assets if a.asset_type in ['非标债权', '债券', '贷款', '固定收益类']]
    
    def analyze(self) -> Dict:
        """信用风险分析"""
        if not self.assets:
            return {
                'score': 100, 
                'level': '无信用风险敞口', 
                'details': {},
                'data_source_note': '无信用类资产'
            }
        
        total_exposure = sum(a.exposure for a in self.assets)
        
        exposure_by_rating = {}
        for asset in self.assets:
            rating = asset.credit_rating or '未评级'
            exposure_by_rating[rating] = exposure_by_rating.get(rating, 0) + asset.exposure
        
        weighted_pd = 0
        for asset in self.assets:
            pd = self.PD_MAPPING.get(asset.credit_rating, 0.05)
            weighted_pd += pd * (asset.exposure / total_exposure)
        
        max_single_exposure = max(a.exposure for a in self.assets) if self.assets else 0
        concentration_ratio = max_single_exposure / total_exposure if total_exposure > 0 else 0
        
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
            'asset_count': len(self.assets),
            'data_source_note': '基于实时数据源计算'
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
        
        portfolio_vol = self._calculate_portfolio_volatility()
        
        var = self._calculate_var(portfolio_vol, confidence_level, time_horizon, total_value)
        cvar = self._calculate_cvar(portfolio_vol, confidence_level, time_horizon, total_value)
        
        fixed_income_assets = [a for a in self.assets if a.asset_type in ['债券', '非标债权', '固定收益类']]
        avg_duration = np.mean([a.duration for a in fixed_income_assets if a.duration]) if fixed_income_assets else 0
        
        equity_assets = [a for a in self.assets if a.asset_type in ['股票', '基金', '权益类']]
        avg_beta = np.mean([a.volatility for a in equity_assets if a.volatility]) if equity_assets else 0
        
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
            'total_market_value': total_value,
            'data_source_note': '基于实时市场数据计算'
        }
    
    def _calculate_portfolio_volatility(self) -> float:
        """计算组合波动率"""
        if self.historical_prices is not None and len(self.historical_prices) > 1:
            returns = self.historical_prices.pct_change().dropna()
            return returns.std() * np.sqrt(252)
        
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
        z_score = norm_ppf(confidence)
        var = portfolio_value * volatility * z_score * np.sqrt(horizon / 252)
        return var
    
    def _calculate_cvar(self, volatility: float, confidence: float,
                        horizon: int, portfolio_value: float) -> float:
        """计算CVaR"""
        z_score = norm_ppf(confidence)
        cvar_multiplier = norm_pdf(z_score) / (1 - confidence)
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
        
        liquid_assets = sum(a.market_value for a in self.assets 
                           if a.asset_type in ['现金', '货币基金', '国债', '现金管理'])
        illiquid_assets = sum(a.market_value for a in self.assets 
                             if a.asset_type in ['非标债权', '私募股权', '房地产', '另类投资'])
        
        liquidity_ratio = liquid_assets / total_assets if total_assets > 0 else 0
        
        avg_asset_maturity = self._calculate_avg_maturity(self.assets)
        avg_liability_maturity = self._calculate_avg_maturity_liabilities()
        maturity_mismatch = avg_asset_maturity - avg_liability_maturity
        
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
            'maturity_mismatch': round(maturity_mismatch, 1),
            'data_source_note': '基于实时资产数据计算'
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
            elif asset.duration:
                weighted_maturity += (asset.market_value / total) * (asset.duration / 12)
        
        return weighted_maturity
    
    def _calculate_avg_maturity_liabilities(self) -> float:
        """计算平均负债期限"""
        return 0.5
    
    def _score_to_level(self, score: float) -> str:
        if score >= 80: return '流动性充足'
        elif score >= 60: return '流动性适中'
        elif score >= 40: return '流动性偏紧'
        else: return '流动性风险高'


class EarlyWarningSystem:
    """风险预警系统"""
    
    def __init__(self, assets: List[RiskAsset]):
        self.assets = assets
        self.thresholds = {
            'single_concentration': 0.15,
            'var_limit': 0.05,
            'liquidity_ratio': 0.2,
            'avg_maturity': 5.0
        }
    
    def check_warnings(self, risk_metrics: Dict) -> List[Dict]:
        """检查预警指标"""
        warnings = []
        
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
        
        if risk_metrics.get('var_ratio', 0) > self.thresholds['var_limit'] * 100:
            warnings.append({
                'level': 'red',
                'type': '市场风险',
                'indicator': 'VaR比率',
                'threshold': f"{self.thresholds['var_limit']*100}%",
                'current': f"{risk_metrics['var_ratio']:.2f}%",
                'suggestion': '建议降低组合波动率或对冲风险敞口'
            })
        
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
    """信托风险管理主类 v3.0 - 完全接入数据适配器"""
    
    def __init__(self):
        self.assets = []
        self.data_provider = get_data_provider()
    
    def load_assets(self, assets_data: List[Dict]):
        """加载资产数据"""
        self.assets = [RiskAsset(**a) for a in assets_data]
    
    def load_from_data_source(self, **filters) -> int:
        """从数据源加载产品作为风险资产"""
        products = self.data_provider.get_products(**filters)
        
        if not products:
            print("⚠️ 未从数据源获取到产品，尝试运行 data/update_data.py 更新数据")
            return 0
        
        assets_data = []
        for p in products:
            # 将产品数据转换为风险资产
            asset = RiskAsset(
                asset_id=p.product_code,
                asset_type=p.investment_type,
                exposure=p.issue_scale * 10000 if p.issue_scale else 1000000,  # 转换为元
                market_value=p.issue_scale * 10000 if p.issue_scale else 1000000,
                credit_rating='AA',  # 默认评级
                duration=p.duration / 12 if p.duration else 2,  # 转换为年
                volatility=0.15 if '固收' in p.investment_type else 0.25
            )
            assets_data.append(asset)
        
        self.load_assets([{
            'asset_id': a.asset_id,
            'asset_type': a.asset_type,
            'exposure': a.exposure,
            'market_value': a.market_value,
            'credit_rating': a.credit_rating,
            'duration': a.duration,
            'volatility': a.volatility
        } for a in assets_data])
        
        return len(assets_data)
    
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
        
        # 添加数据源信息
        data_source_info = self.data_provider.get_data_source_info()
        result['data_source'] = {
            'last_used_adapter': data_source_info.get('last_used'),
            'available_adapters': [a['name'] for a in data_source_info.get('adapters', []) if a['available']],
            'timestamp': datetime.now().isoformat()
        }
        
        # 添加数据更新建议
        result['data_update_note'] = '建议定期运行: python data/update_data.py'
        
        result['metadata'] = {
            'source': 'trust-risk-manager',
            'version': '3.0.0',
            'data_source_version': 'auto_adapter',
            'timestamp': datetime.now().isoformat()
        }
        
        return result
    
    def _score_to_level(self, score: float) -> str:
        if score >= 80: return '低风险'
        elif score >= 60: return '中等风险'
        elif score >= 40: return '较高风险'
        else: return '高风险'


def main():
    parser = argparse.ArgumentParser(description='信托风险管理与预警系统 v3.0')
    parser.add_argument('--risk-type', default='all',
                       choices=['all', 'credit', 'market', 'liquidity'],
                       help='风险类型')
    parser.add_argument('--from-data-source', action='store_true',
                       help='从数据源加载资产（推荐）', default=True)
    parser.add_argument('--min-yield', type=float, help='筛选收益率')
    parser.add_argument('--confidence', type=float, default=0.95, help='置信水平')
    parser.add_argument('--update-data', action='store_true',
                       help='先运行数据更新脚本')
    
    args = parser.parse_args()
    
    # 如果需要，先更新数据
    if args.update_data:
        print("🔄 正在更新数据...")
        import subprocess
        data_dir = Path(__file__).parent.parent / 'data'
        subprocess.run(['python', str(data_dir / 'update_data.py'), '--force'])
        print()
    
    manager = TrustRiskManager()
    
    # 加载资产数据
    if args.from_data_source:
        filters = {}
        if args.min_yield:
            filters['min_yield'] = args.min_yield
        count = manager.load_from_data_source(**filters)
        print(f"✅ 从数据源加载了 {count} 个资产")
        if count == 0:
            print("⚠️ 警告: 未加载到任何资产，风险分析可能不准确")
    
    # 执行分析
    config = {'confidence_level': args.confidence}
    result = manager.analyze(args.risk_type, config)
    
    # 输出结果
    print("\n" + "=" * 60)
    print("📊 风险分析报告")
    print("=" * 60)
    
    # 综合评分
    if 'overall_risk_score' in result:
        print(f"\n综合风险评分: {result['overall_risk_score']}")
        print(f"风险等级: {result['overall_risk_level']}")
    
    # 各维度风险
    for risk_type in ['credit_risk', 'market_risk', 'liquidity_risk']:
        if risk_type in result:
            data = result[risk_type]
            print(f"\n{risk_type.replace('_', ' ').title()}:")
            print(f"  评分: {data.get('score')}")
            print(f"  等级: {data.get('level')}")
    
    # 预警
    if result.get('early_warnings'):
        print(f"\n⚠️ 风险预警 ({len(result['early_warnings'])}条):")
        for w in result['early_warnings'][:5]:
            emoji = "🔴" if w['level'] == 'red' else "🟡"
            print(f"  {emoji} [{w['type']}] {w['indicator']}: {w['current']}")
    
    # 数据源信息
    if 'data_source' in result:
        print(f"\n📡 数据源: {result['data_source'].get('last_used_adapter', 'N/A')}")
        print(f"   可用适配器: {', '.join(result['data_source'].get('available_adapters', []))}")
    
    print("\n" + "=" * 60)
    
    # 输出完整JSON
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
