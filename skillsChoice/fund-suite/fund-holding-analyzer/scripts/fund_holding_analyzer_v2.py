#!/usr/bin/env python3
"""
基金持仓分析核心模块（真实数据版）
Fund Holding Analyzer Core Module - Real Data Edition

功能：持仓集中度分析、FOF穿透、风格暴露
数据源：AkShare / 同花顺iFinD
"""

import sys
sys.path.insert(0, '/root/.openclaw/workspace/finclaw/skills/fund-suite/fund-holding-analyzer/scripts')
sys.path.insert(0, '/root/.openclaw/workspace/finclaw/skills/fund-suite/data')

import json
import argparse
import math
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

# 导入数据适配器
try:
    from fund_data_adapter import get_fund_adapter
    DATA_ADAPTER_AVAILABLE = True
except ImportError as e:
    DATA_ADAPTER_AVAILABLE = False


class HoldingAnalyzer:
    """持仓分析器（真实数据版）"""
    
    def __init__(self, use_real_data: bool = True):
        self.data_adapter = None
        self.data_source = "模拟数据"
        
        if use_real_data and DATA_ADAPTER_AVAILABLE:
            self._init_data_adapter()
    
    def _init_data_adapter(self):
        try:
            self.data_adapter = get_fund_adapter(prefer_ths=False)
            self.data_source = self.data_adapter.get_data_source()
            print(f"✅ 数据源: {self.data_source}")
        except Exception as e:
            print(f"⚠️ 数据适配器初始化失败: {e}")
    
    def analyze_concentration(self, holdings: List[Dict], fund_code: str = None) -> Dict:
        """
        分析持仓集中度
        
        Args:
            holdings: 持仓列表 [{'stock_code': '000001', 'stock_name': '平安银行', 'weight': 0.08}]
            fund_code: 基金代码（用于获取真实持仓）
        
        Returns:
            集中度分析报告
        """
        # 尝试获取真实持仓数据
        if fund_code and self.data_adapter:
            real_holdings = self._get_real_holdings(fund_code)
            if real_holdings:
                holdings = real_holdings
                print(f"✅ 使用真实持仓数据 ({len(holdings)} 只股票)")
        
        if not holdings:
            return {'error': '无持仓数据'}
        
        # 按权重排序
        sorted_holdings = sorted(holdings, key=lambda x: x.get('weight', 0), reverse=True)
        weights = [h.get('weight', 0) for h in sorted_holdings]
        
        # CR5: 前5大持仓占比
        cr5 = sum(weights[:5])
        
        # CR10: 前10大持仓占比
        cr10 = sum(weights[:10]) if len(weights) >= 10 else sum(weights)
        
        # HHI: 赫芬达尔指数
        hhi = sum(w ** 2 for w in weights)
        
        # 有效持仓数
        effective_n = 1 / hhi if hhi > 0 else len(weights)
        
        # 集中度评级
        if cr5 <= 0.30:
            concentration_level = "分散"
            risk = "低"
        elif cr5 <= 0.50:
            concentration_level = "适中"
            risk = "中"
        else:
            concentration_level = "集中"
            risk = "高"
        
        return {
            'analysis_date': datetime.now().strftime('%Y-%m-%d'),
            'data_source': self.data_source,
            'fund_code': fund_code,
            'concentration_metrics': {
                'cr5': round(cr5, 4),
                'cr10': round(cr10, 4),
                'hhi': round(hhi, 4),
                'effective_n': round(effective_n, 1)
            },
            'concentration_level': concentration_level,
            'risk_level': risk,
            'top_holdings': sorted_holdings[:10],
            'interpretation': self._interpret_concentration(cr5, hhi),
            'recommendations': self._generate_concentration_recommendations(cr5, effective_n)
        }
    
    def _get_real_holdings(self, fund_code: str) -> Optional[List[Dict]]:
        """从真实数据获取持仓"""
        if not self.data_adapter:
            return None
        
        try:
            # 获取最新季度持仓
            holdings = self.data_adapter.get_fund_holdings(fund_code)
            if holdings:
                return [{
                    'stock_code': h.stock_code,
                    'stock_name': h.stock_name,
                    'weight': h.weight,
                    'sector': h.sector
                } for h in holdings]
        except Exception as e:
            print(f"获取真实持仓失败: {e}")
        
        return None
    
    def _interpret_concentration(self, cr5: float, hhi: float) -> str:
        """解读集中度"""
        interpretations = []
        
        if cr5 <= 0.30:
            interpretations.append("前5大持仓占比低于30%，持仓较为分散")
        elif cr5 <= 0.50:
            interpretations.append("前5大持仓占比30%-50%，持仓集中度适中")
        else:
            interpretations.append("前5大持仓占比超过50%，持仓高度集中，个股风险较高")
        
        if hhi <= 0.01:
            interpretations.append("HHI指数低于0.01，组合分散度良好")
        elif hhi <= 0.05:
            interpretations.append("HHI指数适中")
        else:
            interpretations.append("HHI指数较高，头部持仓权重过大")
        
        return "；".join(interpretations)
    
    def _generate_concentration_recommendations(self, cr5: float, effective_n: float) -> List[str]:
        """生成集中度建议"""
        recommendations = []
        
        if cr5 > 0.50:
            recommendations.append("⚠️ 持仓高度集中，建议关注头部个股风险")
            recommendations.append("建议分散投资，降低单一股票波动对组合的影响")
        elif cr5 > 0.40:
            recommendations.append("持仓集中度较高，关注前5大持仓的动态")
        
        if effective_n < 20:
            recommendations.append(f"有效持仓数仅{effective_n:.0f}只，实际分散度有限")
        
        if not recommendations:
            recommendations.append("✅ 持仓集中度适中，风险分散良好")
        
        return recommendations


def main():
    parser = argparse.ArgumentParser(description='基金持仓分析')
    parser.add_argument('--fund-code', help='基金代码')
    parser.add_argument('--json', action='store_true', help='输出JSON格式')
    parser.add_argument('--use-real-data', action='store_true', default=True,
                       help='使用真实数据')
    parser.add_argument('--use-mock-data', action='store_true',
                       help='使用模拟数据')
    
    args = parser.parse_args()
    
    use_real = args.use_real_data and not args.use_mock_data
    analyzer = HoldingAnalyzer(use_real_data=use_real)
    
    # 示例持仓数据
    holdings = [
        {'stock_code': '000001', 'stock_name': '平安银行', 'weight': 0.08},
        {'stock_code': '000002', 'stock_name': '万科A', 'weight': 0.07},
        {'stock_code': '000858', 'stock_name': '五粮液', 'weight': 0.06},
        {'stock_code': '000568', 'stock_name': '泸州老窖', 'weight': 0.05},
        {'stock_code': '002415', 'stock_name': '海康威视', 'weight': 0.04},
    ]
    
    result = analyzer.analyze_concentration(holdings, args.fund_code)
    
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("\n" + "=" * 60)
        print(f"📊 持仓集中度分析 ({result.get('data_source', '模拟数据')})")
        print("=" * 60)
        
        if 'error' in result:
            print(f"错误: {result['error']}")
            return
        
        metrics = result['concentration_metrics']
        print(f"\n集中度指标:")
        print(f"  CR5 (前5大持仓): {metrics['cr5']:.1%}")
        print(f"  CR10 (前10大持仓): {metrics['cr10']:.1%}")
        print(f"  HHI (赫芬达尔指数): {metrics['hhi']:.4f}")
        print(f"  有效持仓数: {metrics['effective_n']:.1f}")
        
        print(f"\n风险评级: {result['risk_level']} ({result['concentration_level']})")
        print(f"\n解读: {result['interpretation']}")
        
        print(f"\n建议:")
        for rec in result['recommendations']:
            print(f"  {rec}")


if __name__ == '__main__':
    main()
