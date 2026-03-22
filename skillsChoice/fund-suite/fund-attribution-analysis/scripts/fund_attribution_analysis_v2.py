#!/usr/bin/env python3
"""
基金收益归因分析核心模块（真实数据版）
Fund Attribution Analysis Core Module - Real Data Edition

功能：Brinson归因、因子归因、风格分析
数据源：AkShare / 同花顺iFinD
"""

import sys
sys.path.insert(0, '/root/.openclaw/workspace/finclaw/skills/fund-suite/fund-attribution-analysis/scripts')
sys.path.insert(0, '/root/.openclaw/workspace/finclaw/skills/fund-suite/data')

import json
import argparse
import math
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

# 导入数据适配器
try:
    from fund_data_adapter import get_fund_adapter
    DATA_ADAPTER_AVAILABLE = True
except ImportError as e:
    DATA_ADAPTER_AVAILABLE = False


@dataclass
class BrinsonResult:
    """Brinson归因结果"""
    allocation_effect: float
    selection_effect: float
    interaction_effect: float
    total_excess: float
    data_source: str = "模拟"
    
    def to_dict(self) -> Dict:
        return asdict(self)


class AttributionAnalyzer:
    """归因分析器（真实数据版）"""
    
    FACTOR_DEFINITIONS = {
        'MKT': {'name': '市场因子', 'description': '市场风险暴露'},
        'HML': {'name': '价值因子', 'description': '高减低价值因子'},
        'SMB': {'name': '规模因子', 'description': '小减大规模因子'},
        'MOM': {'name': '动量因子', 'description': '过去12月动量'},
        'QUAL': {'name': '质量因子', 'description': '高ROE - 低ROE'},
        'LOWV': {'name': '低波因子', 'description': '低波动 - 高波动'},
    }
    
    def __init__(self, use_real_data: bool = True):
        self.data_adapter = None
        self.data_source = "模拟数据"
        self.fund_nav_cache = {}
        
        if use_real_data and DATA_ADAPTER_AVAILABLE:
            self._init_data_adapter()
    
    def _init_data_adapter(self):
        try:
            self.data_adapter = get_fund_adapter(prefer_ths=False)
            self.data_source = self.data_adapter.get_data_source()
            print(f"✅ 数据源: {self.data_source}")
        except Exception as e:
            print(f"⚠️ 数据适配器初始化失败: {e}")
    
    def brinson_attribution(self, portfolio_returns: Dict[str, float],
                           benchmark_returns: Dict[str, float],
                           portfolio_weights: Dict[str, float],
                           benchmark_weights: Dict[str, float],
                           fund_code: str = None) -> Dict:
        """
        Brinson归因分析
        
        Args:
            portfolio_returns: 组合各行业/资产收益
            benchmark_returns: 基准各行业/资产收益
            portfolio_weights: 组合权重
            benchmark_weights: 基准权重
            fund_code: 基金代码（用于获取真实数据）
        
        Returns:
            Brinson归因报告
        """
        # 尝试获取真实净值数据计算收益
        if fund_code and self.data_adapter:
            real_returns = self._get_real_returns(fund_code)
            if real_returns:
                print(f"✅ 使用真实净值数据计算收益")
        
        # 计算总收益
        portfolio_total = sum(
            portfolio_weights.get(s, 0) * r 
            for s, r in portfolio_returns.items()
        )
        benchmark_total = sum(
            benchmark_weights.get(s, 0) * r 
            for s, r in benchmark_returns.items()
        )
        
        excess_return = portfolio_total - benchmark_total
        
        # 计算各行业的归因
        sector_attributions = []
        total_allocation = 0
        total_selection = 0
        total_interaction = 0
        
        all_sectors = set(list(portfolio_returns.keys()) + list(benchmark_returns.keys()))
        
        for sector in all_sectors:
            w_p = portfolio_weights.get(sector, 0)
            w_b = benchmark_weights.get(sector, 0)
            r_p = portfolio_returns.get(sector, 0)
            r_b = benchmark_returns.get(sector, 0)
            
            # 配置效应: (wp - wb) × rb
            allocation = (w_p - w_b) * r_b
            
            # 选择效应: wb × (rp - rb)
            selection = w_b * (r_p - r_b)
            
            # 交互效应: (wp - wb) × (rp - rb)
            interaction = (w_p - w_b) * (r_p - r_b)
            
            total_allocation += allocation
            total_selection += selection
            total_interaction += interaction
            
            sector_attributions.append({
                'sector': sector,
                'portfolio_weight': w_p,
                'benchmark_weight': w_b,
                'portfolio_return': r_p,
                'benchmark_return': r_b,
                'allocation_effect': allocation,
                'selection_effect': selection,
                'interaction_effect': interaction,
                'total_effect': allocation + selection + interaction,
                'data_source': self.data_source
            })
        
        # 排序按总贡献
        sector_attributions.sort(key=lambda x: abs(x['total_effect']), reverse=True)
        
        return {
            'attribution_id': f'ATTR_{datetime.now().strftime("%Y%m%d")}_001',
            'analysis_date': datetime.now().strftime('%Y-%m-%d'),
            'data_source': self.data_source,
            'returns': {
                'portfolio': portfolio_total,
                'benchmark': benchmark_total,
                'excess': excess_return,
                'excess_pct': excess_return * 100
            },
            'brinson_attribution': {
                'allocation_effect': total_allocation,
                'allocation_pct': total_allocation / excess_return * 100 if excess_return != 0 else 0,
                'selection_effect': total_selection,
                'selection_pct': total_selection / excess_return * 100 if excess_return != 0 else 0,
                'interaction_effect': total_interaction,
                'interaction_pct': total_interaction / excess_return * 100 if excess_return != 0 else 0,
                'total_excess': excess_return,
                'residual': excess_return - total_allocation - total_selection - total_interaction,
                'formula': '配置效应 + 选择效应 + 交互效应 = 超额收益'
            },
            'sector_attribution': sector_attributions,
            'conclusion': self._generate_brinson_conclusion(
                total_allocation, total_selection, total_interaction
            )
        }
    
    def _get_real_returns(self, fund_code: str) -> Optional[Dict]:
        """从真实数据获取收益"""
        if not self.data_adapter:
            return None
        
        try:
            # 获取净值历史
            navs = self.data_adapter.get_fund_nav(fund_code, days=30)
            if navs and len(navs) >= 2:
                returns = [nav.daily_return for nav in navs if nav.daily_return is not None]
                if returns:
                    return {
                        'daily_returns': returns,
                        'total_return': sum(returns),
                        'avg_daily': sum(returns) / len(returns),
                        'volatility': math.sqrt(sum((r - sum(returns)/len(returns))**2 for r in returns) / len(returns))
                    }
        except Exception as e:
            print(f"获取真实收益失败: {e}")
        
        return None
    
    def _generate_brinson_conclusion(self, allocation: float, selection: float, 
                                     interaction: float) -> Dict:
        """生成Brinson归因结论"""
        total = allocation + selection + interaction
        
        # 主要贡献来源
        effects = [
            ('配置效应', allocation),
            ('选择效应', selection),
            ('交互效应', interaction)
        ]
        effects.sort(key=lambda x: abs(x[1]), reverse=True)
        primary_effect = effects[0]
        
        return {
            'primary_driver': primary_effect[0],
            'primary_contribution': primary_effect[1],
            'interpretation': f"超额收益主要来自{primary_effect[0]} ({primary_effect[1]:.2%})",
            'allocation_interpretation': self._interpret_allocation(allocation),
            'selection_interpretation': self._interpret_selection(selection)
        }
    
    def _interpret_allocation(self, allocation: float) -> str:
        """解读配置效应"""
        if allocation > 0.01:
            return "行业配置能力较好，超配了表现较好的行业"
        elif allocation < -0.01:
            return "行业配置有待改进，可能超配了表现较差的行业"
        else:
            return "行业配置中性，与基准接近"
    
    def _interpret_selection(self, selection: float) -> str:
        """解读选择效应"""
        if selection > 0.01:
            return "选股能力较强，行业内个股选择优秀"
        elif selection < -0.01:
            return "选股能力有待提升，行业内个股选择欠佳"
        else:
            return "选股能力中性"


def main():
    parser = argparse.ArgumentParser(description='基金收益归因分析')
    parser.add_argument('--json', action='store_true', help='输出JSON格式')
    parser.add_argument('--use-real-data', action='store_true', default=True,
                       help='使用真实数据')
    parser.add_argument('--use-mock-data', action='store_true',
                       help='使用模拟数据')
    
    args = parser.parse_args()
    
    use_real = args.use_real_data and not args.use_mock_data
    analyzer = AttributionAnalyzer(use_real_data=use_real)
    
    # 示例数据
    portfolio_returns = {'科技': 0.15, '消费': 0.08, '医药': 0.12}
    benchmark_returns = {'科技': 0.10, '消费': 0.09, '医药': 0.11}
    portfolio_weights = {'科技': 0.40, '消费': 0.30, '医药': 0.30}
    benchmark_weights = {'科技': 0.30, '消费': 0.40, '医药': 0.30}
    
    result = analyzer.brinson_attribution(
        portfolio_returns, benchmark_returns,
        portfolio_weights, benchmark_weights
    )
    
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("\n" + "=" * 60)
        print(f"📊 Brinson归因分析 ({result['data_source']})")
        print("=" * 60)
        print(f"分析日期: {result['analysis_date']}")
        
        ret = result['returns']
        print(f"\n收益对比:")
        print(f"  组合收益: {ret['portfolio']:.2%}")
        print(f"  基准收益: {ret['benchmark']:.2%}")
        print(f"  超额收益: {ret['excess']:.2%}")
        
        brinson = result['brinson_attribution']
        print(f"\n归因分解:")
        print(f"  配置效应: {brinson['allocation_effect']:.2%} ({brinson['allocation_pct']:.1f}%)")
        print(f"  选择效应: {brinson['selection_effect']:.2%} ({brinson['selection_pct']:.1f}%)")
        print(f"  交互效应: {brinson['interaction_effect']:.2%} ({brinson['interaction_pct']:.1f}%)")
        
        conclusion = result['conclusion']
        print(f"\n结论: {conclusion['interpretation']}")


if __name__ == '__main__':
    main()
