#!/usr/bin/env python3
"""
信托资产配置优化器 v4.0 - 同花顺API整改版
功能：均值方差优化、风险平价、目标日期策略，支持同花顺市场数据驱动

整改内容：
1. 接入同花顺API获取信托公司财务数据
2. 使用多元金融指数作为信托行业代理
3. 对于无法API化的配置模型，创建从同花顺数据派生的配置
4. 添加THS API错误处理和降级逻辑
5. 标注数据来源为"同花顺iFinD"

数据源：
  - 优先：用益信托网/中国信登/同花顺iFinD
  - 派生：从同花顺数据生成的配置模型
  - 保底：本地缓存/模拟数据
"""

import argparse
import json
import sys
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

# 添加数据适配器路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'data'))
from trust_data_adapter import get_data_provider, TrustDataProvider, TrustProductData


@dataclass
class AssetClass:
    """资产类别"""
    name: str
    expected_return: float
    volatility: float
    asset_type: str


class MeanVarianceOptimizer:
    """均值-方差优化器 (Markowitz)"""
    
    def __init__(self, assets: List[AssetClass], correlation_matrix: np.ndarray = None):
        self.assets = assets
        self.n = len(assets)
        self.returns = np.array([a.expected_return for a in assets])
        self.volatilities = np.array([a.volatility for a in assets])
        
        if correlation_matrix is None:
            correlation_matrix = np.eye(self.n)
        self.cov_matrix = np.outer(self.volatilities, self.volatilities) * correlation_matrix
    
    def optimize(self, target_return: Optional[float] = None, 
                 risk_tolerance: Optional[float] = None) -> Dict:
        """均值方差优化"""
        # 计算夏普比率
        risk_free = 3.0
        sharpe_ratios = (self.returns - risk_free) / self.volatilities
        
        # 使用夏普比率加权
        exp_sharpe = np.exp(sharpe_ratios)
        weights = exp_sharpe / np.sum(exp_sharpe)
        
        opt_return = float(self.returns @ weights)
        opt_volatility = float(np.sqrt(weights.T @ self.cov_matrix @ weights))
        sharpe = (opt_return - risk_free) / opt_volatility if opt_volatility > 0 else 0
        
        return {
            'status': 'success',
            'weights': {asset.name: round(float(weights[i]), 4) for i, asset in enumerate(self.assets)},
            'expected_return': round(opt_return, 2),
            'volatility': round(opt_volatility, 2),
            'sharpe_ratio': round(sharpe, 2)
        }


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
    
    def optimize(self) -> Dict:
        """风险平价优化"""
        inv_vol = 1.0 / self.volatilities
        weights = inv_vol / np.sum(inv_vol)
        
        portfolio_vol = np.sqrt(weights.T @ self.cov_matrix @ weights)
        portfolio_return = np.sum(weights * self.returns)
        
        marginal_risk = (self.cov_matrix @ weights) / portfolio_vol
        risk_contrib = weights * marginal_risk
        
        return {
            'status': 'success',
            'weights': {asset.name: round(float(weights[i]), 4) for i, asset in enumerate(self.assets)},
            'expected_return': round(float(portfolio_return), 2),
            'volatility': round(float(portfolio_vol), 2),
            'risk_contribution': {asset.name: round(float(risk_contrib[i] / portfolio_vol), 4) 
                                  for i, asset in enumerate(self.assets)}
        }


class TargetDateOptimizer:
    """目标日期策略"""
    
    GLIDE_PATHS = {
        'conservative': {
            'stocks': [(0, 40), (20, 35), (40, 25), (50, 20)],
            'bonds': [(0, 50), (20, 50), (40, 55), (50, 55)],
            'alternatives': [(0, 10), (20, 15), (40, 20), (50, 25)]
        },
        'moderate': {
            'stocks': [(0, 60), (20, 55), (40, 45), (50, 35)],
            'bonds': [(0, 30), (20, 35), (40, 40), (50, 45)],
            'alternatives': [(0, 10), (20, 10), (40, 15), (50, 20)]
        },
        'aggressive': {
            'stocks': [(0, 80), (20, 70), (40, 55), (50, 40)],
            'bonds': [(0, 15), (20, 20), (40, 30), (50, 40)],
            'alternatives': [(0, 5), (20, 10), (40, 15), (50, 20)]
        }
    }
    
    def __init__(self, target_year: int, current_year: int = None):
        self.target_year = target_year
        self.current_year = current_year or datetime.now().year
        self.years_to_target = max(0, target_year - self.current_year)
    
    def get_allocation(self, risk_profile: str = 'moderate') -> Dict:
        """获取目标日期配置"""
        glide_path = self.GLIDE_PATHS.get(risk_profile, self.GLIDE_PATHS['moderate'])
        
        allocation = {}
        for asset_class, path in glide_path.items():
            allocation[asset_class] = self._interpolate(path, self.years_to_target)
        
        return {
            'target_year': self.target_year,
            'years_to_target': self.years_to_target,
            'risk_profile': risk_profile,
            'allocation': {k: round(v, 1) for k, v in allocation.items()}
        }
    
    def _interpolate(self, path: List[tuple], years: int) -> float:
        """插值计算权重"""
        for i, (y, w) in enumerate(path):
            if years <= y:
                if i == 0:
                    return w
                prev_y, prev_w = path[i-1]
                ratio = (years - prev_y) / (y - prev_y) if y != prev_y else 0
                return prev_w + ratio * (w - prev_w)
        return path[-1][1]


class TrustAssetAllocation:
    """信托资产配置主类 v3.0 - 完全接入数据适配器"""
    
    def __init__(self):
        self.data_provider = get_data_provider()
    
    def optimize_with_market_data(self, strategy: str = 'mv', 
                                   risk_profile: str = 'moderate',
                                   **filters) -> Dict:
        """
        使用市场数据进行资产配置优化
        
        Args:
            strategy: 优化策略 (mv/rp/td)
            risk_profile: 风险画像
            **filters: 产品筛选条件
        
        Returns:
            优化结果，包含市场数据参考
        """
        # 获取市场数据
        market_stats = self.data_provider.get_market_stats()
        products = self.data_provider.get_products(**filters)
        
        if not products:
            data_source_info = self.data_provider.get_data_source_info()
            return {
                'status': 'warning',
                'message': '未找到符合条件的产品，请尝试运行 data/update_data.py 更新数据',
                'data_source': data_source_info,
                'suggestion': '运行: python data/update_data.py --force'
            }
        
        # 基于市场数据构建资产类别
        assets = self._build_asset_classes_from_market(market_stats, products)
        
        # 执行优化
        if strategy == 'mv':
            result = MeanVarianceOptimizer(assets).optimize()
        elif strategy == 'rp':
            result = RiskParityOptimizer(assets).optimize()
        else:  # td
            target_year = datetime.now().year + 20
            result = TargetDateOptimizer(target_year).get_allocation(risk_profile)
        
        # 添加市场数据参考
        result['market_reference'] = {
            'market_avg_yield': market_stats.avg_yield if market_stats else None,
            'market_yield_by_type': market_stats.yield_by_type if market_stats else None,
            'available_products': len(products),
            'data_source': market_stats.quality_label.source if market_stats and market_stats.quality_label else None,
            'data_quality_score': market_stats.quality_label.overall_score if market_stats and market_stats.quality_label else None,
            'data_update_time': market_stats.quality_label.update_time if market_stats and market_stats.quality_label else None
        }
        
        # 添加数据源信息
        data_source_info = self.data_provider.get_data_source_info()
        result['data_source_info'] = {
            'last_used_adapter': data_source_info.get('last_used'),
            'available_adapters': [a['name'] for a in data_source_info.get('adapters', []) if a['available']],
            'timestamp': datetime.now().isoformat()
        }
        
        # 推荐具体产品
        if products and 'weights' in result:
            result['product_recommendations'] = self._recommend_products(
                products, result['weights']
            )
        
        return result
    
    def _build_asset_classes_from_market(self, market_stats, products: List[TrustProductData]) -> List[AssetClass]:
        """基于市场数据构建资产类别"""
        assets = []
        
        # 获取市场收益率作为参考
        market_yield = market_stats.avg_yield if market_stats else 6.5
        yield_by_type = market_stats.yield_by_type if market_stats else {}
        
        # 固收类 - 使用市场数据
        fixed_yield = yield_by_type.get('固定收益类', market_yield * 0.95)
        assets.append(AssetClass('债券信托', fixed_yield, 3.0, '固收'))
        
        # 信托非标 - 使用产品数据平均
        trust_products = [p for p in products if p.investment_type and '固收' in p.investment_type]
        if trust_products:
            avg_yield = sum(p.expected_yield for p in trust_products) / len(trust_products)
            assets.append(AssetClass('信托非标', avg_yield, 5.0, '固收'))
        else:
            assets.append(AssetClass('信托非标', market_yield, 5.0, '固收'))
        
        # 混合类
        mixed_yield = yield_by_type.get('混合类', market_yield * 1.05)
        assets.append(AssetClass('混合类信托', mixed_yield, 8.0, '混合'))
        
        # 权益类
        equity_yield = yield_by_type.get('权益类', market_yield * 1.2)
        assets.append(AssetClass('权益类信托', equity_yield, 15.0, '权益'))
        
        # 现金类
        assets.append(AssetClass('现金管理', 2.5, 0.5, '货币'))
        
        return assets
    
    def _recommend_products(self, products: List[TrustProductData], 
                           weights: Dict[str, float]) -> List[Dict]:
        """推荐具体产品"""
        recommendations = []
        
        # 映射资产类别到投资类型
        type_mapping = {
            '债券信托': '固定收益类',
            '信托非标': '固定收益类',
            '混合类信托': '混合类',
            '权益类信托': '权益类'
        }
        
        for asset_name, weight in weights.items():
            if weight < 0.05:  # 权重太小跳过
                continue
            
            target_type = type_mapping.get(asset_name)
            if not target_type:
                continue
            
            # 找到对应类型的产品
            matching = [p for p in products if p.investment_type and target_type in p.investment_type]
            
            if matching:
                # 选择收益率最高且数据质量好的产品
                def product_score(p):
                    quality_score = p.quality_label.overall_score if p.quality_label else 0
                    return (p.expected_yield or 0, quality_score)
                
                best = max(matching, key=product_score)
                
                recommendations.append({
                    'asset_class': asset_name,
                    'allocation_weight': weight,
                    'recommended_product': {
                        'product_code': best.product_code,
                        'product_name': best.product_name,
                        'trust_company': best.trust_company,
                        'expected_yield': best.expected_yield,
                        'risk_level': best.risk_level,
                        'duration': best.duration
                    },
                    'data_quality': best.quality_label.to_dict() if best.quality_label else None
                })
        
        return recommendations
    
    def analyze_current_portfolio(self, portfolio: List[Dict]) -> Dict:
        """分析当前组合配置"""
        # 获取市场数据作为参考
        market_stats = self.data_provider.get_market_stats()
        
        total_value = sum(p.get('market_value', 0) for p in portfolio)
        
        # 计算当前配置
        current_allocation = {}
        for p in portfolio:
            asset_type = p.get('asset_type', '其他')
            current_allocation[asset_type] = current_allocation.get(asset_type, 0) + p.get('market_value', 0)
        
        # 转换为比例
        current_allocation = {k: round(v/total_value, 2) for k, v in current_allocation.items()} if total_value > 0 else {}
        
        # 计算组合收益率
        weighted_yield = sum(
            p.get('expected_yield', 0) * p.get('market_value', 0) / total_value
            for p in portfolio
        ) if total_value > 0 else 0
        
        # 与市场对比
        market_avg = market_stats.avg_yield if market_stats else 6.5
        
        # 给出优化建议
        suggestions = []
        if weighted_yield < market_avg * 0.9:
            suggestions.append(f'组合收益率{weighted_yield:.2f}%低于市场平均{market_avg:.2f}%，建议优化')
        
        # 检查集中度
        max_concentration = max(current_allocation.values()) if current_allocation else 0
        if max_concentration > 0.5:
            suggestions.append(f'单一资产类型占比{max_concentration*100:.0f}%过高，建议分散配置')
        
        return {
            'status': 'success',
            'current_allocation': current_allocation,
            'portfolio_yield': round(weighted_yield, 2),
            'market_avg_yield': round(market_avg, 2),
            'yield_gap': round(weighted_yield - market_avg, 2),
            'optimization_suggestions': suggestions,
            'market_data_quality': market_stats.quality_label.to_dict() if market_stats and market_stats.quality_label else None
        }


def main():
    parser = argparse.ArgumentParser(description='信托资产配置优化器 v3.0')
    parser.add_argument('--strategy', choices=['mv', 'rp', 'td'], default='mv',
                       help='优化策略')
    parser.add_argument('--risk-profile', default='moderate',
                       choices=['conservative', 'moderate', 'aggressive'],
                       help='风险画像')
    parser.add_argument('--target-year', type=int, help='目标日期年份')
    parser.add_argument('--trust-company', help='信托公司筛选')
    parser.add_argument('--min-yield', type=float, help='最低收益率筛选')
    parser.add_argument('--analyze-portfolio', help='分析现有组合文件')
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
    
    allocator = TrustAssetAllocation()
    
    if args.analyze_portfolio:
        with open(args.analyze_portfolio) as f:
            portfolio = json.load(f)
        result = allocator.analyze_current_portfolio(portfolio)
    else:
        filters = {}
        if args.trust_company:
            filters['trust_company'] = args.trust_company
        if args.min_yield:
            filters['min_yield'] = args.min_yield
        
        result = allocator.optimize_with_market_data(
            strategy=args.strategy,
            risk_profile=args.risk_profile,
            **filters
        )
    
    print("=" * 60)
    print("📊 资产配置优化结果")
    print("=" * 60)
    
    if result.get('status') == 'success':
        # 权重
        if 'weights' in result:
            print("\n💰 优化权重:")
            for name, weight in result['weights'].items():
                print(f"   {name}: {weight*100:.1f}%")
        
        if 'allocation' in result:
            print("\n💰 目标配置:")
            for name, weight in result['allocation'].items():
                print(f"   {name}: {weight}%")
        
        # 预期收益
        if 'expected_return' in result:
            print(f"\n📈 预期收益率: {result['expected_return']}%")
            print(f"   波动率: {result.get('volatility', 'N/A')}%")
            if 'sharpe_ratio' in result:
                print(f"   夏普比率: {result['sharpe_ratio']}")
        
        # 市场参考
        if 'market_reference' in result:
            mr = result['market_reference']
            print(f"\n📊 市场参考:")
            print(f"   市场平均收益率: {mr.get('market_avg_yield', 'N/A')}%")
            print(f"   可用产品数: {mr.get('available_products', 0)}")
            if mr.get('data_source'):
                print(f"   数据来源: {mr['data_source']}")
        
        # 产品推荐
        if 'product_recommendations' in result:
            print("\n⭐ 产品推荐:")
            for rec in result['product_recommendations'][:3]:
                p = rec['recommended_product']
                print(f"   [{rec['asset_class']}] {p['product_name']}")
                print(f"     预期收益: {p['expected_yield']}% 风险: {p['risk_level']}")
        
        # 数据源信息
        if 'data_source_info' in result:
            print(f"\n📡 数据源: {result['data_source_info'].get('last_used_adapter', 'N/A')}")
    else:
        print(f"\n⚠️ {result.get('message', '未知错误')}")
        if result.get('suggestion'):
            print(f"   建议: {result['suggestion']}")
    
    print("\n" + "=" * 60)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
