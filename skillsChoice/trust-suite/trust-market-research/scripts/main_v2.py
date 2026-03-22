#!/usr/bin/env python3
"""
更新版：信托市场研究（集成数据对接层）
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'data'))

try:
    from trust_data_adapter import get_data_provider
    DATA_ADAPTER_AVAILABLE = True
except ImportError:
    DATA_ADAPTER_AVAILABLE = False

import argparse
import json
from datetime import datetime
import pandas as pd


class TrustMarketResearch:
    """信托市场研究（更新版）"""
    
    def __init__(self):
        self.use_adapter = DATA_ADAPTER_AVAILABLE
        if self.use_adapter:
            self.provider = get_data_provider()
    
    def research(self, query: str = 'market_overview') -> dict:
        """市场研究"""
        if query == 'market_overview':
            return self._get_market_overview()
        elif query == 'yield_trend':
            return self._get_yield_trend()
        elif query == 'company_rankings':
            return self._get_company_rankings()
        else:
            return {'status': 'error', 'message': f'未知查询类型: {query}'}
    
    def _get_market_overview(self) -> dict:
        """获取市场概览"""
        if self.use_adapter:
            try:
                stats = self.provider.get_market_stats()
                if stats:
                    return {
                        'status': 'success',
                        'query': 'market_overview',
                        'data_source': '数据对接层',
                        'market_overview': {
                            'total_issuance': stats.total_issuance,
                            'product_count': stats.product_count,
                            'avg_yield': stats.avg_yield,
                            'yield_by_type': stats.yield_by_type,
                            'yield_by_duration': stats.yield_by_duration
                        },
                        'timestamp': datetime.now().isoformat()
                    }
            except Exception as e:
                print(f"数据对接层获取失败: {e}")
        
        # 回退到模拟数据
        return {
            'status': 'success',
            'query': 'market_overview',
            'data_source': '模拟数据',
            'market_overview': {
                'total_issuance': 1250.5,
                'product_count': 186,
                'avg_yield': 6.85,
                'yield_by_type': {
                    '固定收益类': 6.52,
                    '混合类': 7.25,
                    '权益类': 8.10,
                    '另类投资': 7.80
                },
                'yield_by_duration': {
                    '1年内': 6.20,
                    '1-2年': 6.85,
                    '2-3年': 7.35,
                    '3年以上': 7.80
                }
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_yield_trend(self) -> dict:
        """获取收益率趋势"""
        if self.use_adapter:
            try:
                curve = self.provider.get_yield_curve()
                if not curve.empty:
                    return {
                        'status': 'success',
                        'query': 'yield_trend',
                        'data_source': '数据对接层',
                        'yield_curve': curve.to_dict('records'),
                        'timestamp': datetime.now().isoformat()
                    }
            except Exception as e:
                print(f"数据对接层获取失败: {e}")
        
        return {
            'status': 'success',
            'query': 'yield_trend',
            'data_source': '模拟数据',
            'yield_curve': [
                {'期限': '1年内', '收益率': 6.20},
                {'期限': '1-2年', '收益率': 6.85},
                {'期限': '2-3年', '收益率': 7.35},
                {'期限': '3年以上', '收益率': 7.80}
            ],
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_company_rankings(self) -> dict:
        """获取信托公司排名"""
        # 模拟数据
        return {
            'status': 'success',
            'query': 'company_rankings',
            'data_source': '模拟数据',
            'rankings': [
                {'rank': 1, 'company': '平安信托', 'aum': 4500, 'issuance': 120},
                {'rank': 2, 'company': '中信信托', 'aum': 4200, 'issuance': 110},
                {'rank': 3, 'company': '五矿信托', 'aum': 3800, 'issuance': 95}
            ],
            'timestamp': datetime.now().isoformat()
        }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='信托市场研究 v1.1（集成数据对接）')
    parser.add_argument('--query', default='market_overview',
                       choices=['market_overview', 'yield_trend', 'company_rankings'])
    
    args = parser.parse_args()
    
    research = TrustMarketResearch()
    print(json.dumps(research.research(args.query), ensure_ascii=False, indent=2))
