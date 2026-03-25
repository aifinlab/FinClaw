#!/usr/bin/env python3
"""
信托市场研究 - 接入数据适配器 v2.0
功能：信托市场研究、趋势分析、数据报告
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# 添加数据适配器路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'data'))
from trust_data_adapter import get_data_provider, TrustDataProvider


class TrustMarketResearch:
    """信托市场研究 - 接入真实数据源"""
    
    def __init__(self):
        self.data_provider = get_data_provider()
    
    def research(self, query: str = "market_overview") -> dict:
        """
        执行市场研究
        
        Args:
            query: 查询类型，支持 market_overview, yield_trend, product_analysis
        
        Returns:
            包含数据质量标注的研究结果
        """
        # 获取市场统计数据
        market_stats = self.data_provider.get_market_stats()
        
        # 获取产品数据
        products = self.data_provider.get_products()
        
        # 构建结果
        result = {
            'status': 'success',
            'query': query,
            'timestamp': datetime.now().isoformat()
        }
        
        # 添加数据质量信息
        data_quality = {
            'source_info': self.data_provider.get_data_source_info(),
            'market_stats_quality': market_stats.quality_label.to_dict() if market_stats and market_stats.quality_label else None,
            'products_count': len(products),
            'products_quality': products[0].quality_label.to_dict() if products and products[0].quality_label else None
        }
        result['data_quality'] = data_quality
        
        # 根据查询类型返回不同数据
        if query == "market_overview":
            result['market_overview'] = self._get_market_overview(market_stats)
        elif query == "yield_trend":
            result['yield_trend'] = self._get_yield_trend(market_stats)
        elif query == "product_analysis":
            result['product_analysis'] = self._get_product_analysis(products)
        else:
            result['market_overview'] = self._get_market_overview(market_stats)
            result['yield_trend'] = self._get_yield_trend(market_stats)
            result['product_analysis'] = self._get_product_analysis(products)
        
        return result
    
    def _get_market_overview(self, stats) -> dict:
        """获取市场概览"""
        if not stats:
            return {'error': '无法获取市场数据'}
        
        return {
            'total_issuance': stats.total_issuance,  # 亿元
            'avg_yield': stats.avg_yield,
            'product_count': stats.product_count,
            'stat_date': stats.stat_date,
            'data_source': stats.quality_label.source if stats.quality_label else 'unknown',
            'data_freshness_score': stats.quality_label.freshness_score if stats.quality_label else 0
        }
    
    def _get_yield_trend(self, stats) -> dict:
        """获取收益率趋势"""
        if not stats:
            return {'error': '无法获取收益率数据'}
        
        return {
            'avg_yield': stats.avg_yield,
            'yield_by_type': stats.yield_by_type,
            'yield_by_duration': stats.yield_by_duration,
            'trend_analysis': self._analyze_trend(stats),
            'data_source': stats.quality_label.source if stats.quality_label else 'unknown'
        }
    
    def _get_product_analysis(self, products) -> dict:
        """获取产品分析"""
        if not products:
            return {'error': '无法获取产品数据'}
        
        # 按类型统计
        by_type = {}
        by_risk = {}
        total_yield = 0
        
        for p in products:
            inv_type = p.investment_type
            by_type[inv_type] = by_type.get(inv_type, 0) + 1
            
            risk = p.risk_level
            by_risk[risk] = by_risk.get(risk, 0) + 1
            
            total_yield += p.expected_yield
        
        avg_yield = total_yield / len(products) if products else 0
        
        return {
            'total_products': len(products),
            'by_investment_type': by_type,
            'by_risk_level': by_risk,
            'avg_expected_yield': round(avg_yield, 2),
            'data_source': products[0].quality_label.source if products and products[0].quality_label else 'unknown'
        }
    
    def _analyze_trend(self, stats) -> str:
        """分析收益率趋势"""
        avg = stats.avg_yield
        if avg > 7.5:
            return "收益率处于高位，建议关注风险控制"
        elif avg > 6.5:
            return "收益率处于合理区间"
        else:
            return "收益率偏低，市场趋于保守"
    
    def generate_report(self) -> str:
        """生成市场研究报告"""
        result = self.research("all")
        
        report = []
        report.append("=" * 60)
        report.append("📊 信托市场研究报告")
        report.append("=" * 60)
        report.append(f"生成时间: {result['timestamp']}")
        report.append("")
        
        # 数据质量说明
        dq = result.get('data_quality', {})
        report.append("📋 数据质量说明")
        report.append("-" * 40)
        if dq.get('market_stats_quality'):
            ql = dq['market_stats_quality']
            report.append(f"  数据来源: {ql['source']}")
            report.append(f"  质量等级: {ql.get('freshness_score', 0)}分")
            report.append(f"  更新时间: {ql['update_time']}")
        report.append("")
        
        # 市场概览
        overview = result.get('market_overview', {})
        report.append("📈 市场概览")
        report.append("-" * 40)
        report.append(f"  统计日期: {overview.get('stat_date', 'N/A')}")
        report.append(f"  发行规模: {overview.get('total_issuance', 0)}亿元")
        report.append(f"  产品数量: {overview.get('product_count', 0)}个")
        report.append(f"  平均收益率: {overview.get('avg_yield', 0)}%")
        report.append("")
        
        # 收益率分布
        trend = result.get('yield_trend', {})
        report.append("📉 收益率分布")
        report.append("-" * 40)
        if 'yield_by_type' in trend:
            for type_name, yield_val in trend['yield_by_type'].items():
                report.append(f"  {type_name}: {yield_val}%")
        report.append("")
        
        report.append("=" * 60)
        
        return "\n".join(report)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='信托市场研究')
    parser.add_argument('--query', default='market_overview',
                       choices=['market_overview', 'yield_trend', 'product_analysis', 'all'],
                       help='查询类型')
    parser.add_argument('--report', action='store_true', help='生成完整报告')
    
    args = parser.parse_args()
    
    research = TrustMarketResearch()
    
    if args.report:
        print(research.generate_report())
    else:
        result = research.research(args.query)
        print(json.dumps(result, ensure_ascii=False, indent=2))
