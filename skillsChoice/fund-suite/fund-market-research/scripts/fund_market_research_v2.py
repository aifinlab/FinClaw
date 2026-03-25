#!/usr/bin/env python3
"""
基金市场研究核心模块（真实数据版）
Fund Market Research Core Module - Real Data Edition

功能：市场趋势分析、资金流向、情绪指标
数据源：AkShare / 同花顺iFinD
"""

import sys
sys.path.insert(0, '/root/.openclaw/workspace/finclaw/skills/fund-suite/fund-market-research/scripts')
sys.path.insert(0, '/root/.openclaw/workspace/finclaw/skills/fund-suite/data')

import json
import argparse
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta

# 导入数据适配器
try:
    from fund_data_adapter import get_fund_adapter
    DATA_ADAPTER_AVAILABLE = True
except ImportError as e:
    DATA_ADAPTER_AVAILABLE = False


class MarketResearcher:
    """市场研究员（真实数据版）"""
    
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
    
    def analyze_market_trend(self, fund_type: str = '混合型') -> Dict:
        """
        分析市场趋势
        
        Args:
            fund_type: 基金类型
        
        Returns:
            市场趋势报告
        """
# 尝试获取真实排行数据，如果没有真实数据则返回简化示例并发出警告
        if self.data_adapter:
            real_data = self._get_real_market_data(fund_type)
            if real_data:
                return real_data
        
        # 简化的模拟数据，带有明确警告
        import warnings
        warnings.warn(
            "⚠️ 正在使用示例数据！请传入真实数据或使用 --use-real-data 标志。\n"
            "   示例基金数据（000001, 000002）仅供演示，请勿用于生产环境。",
            UserWarning,
            stacklevel=2
        )
        
        return {
            'analysis_date': datetime.now().strftime('%Y-%m-%d'),
            'data_source': '示例数据（需替换）',
            'fund_type': fund_type,
            'market_sentiment': '中性（示例）',
            'trend': '震荡（示例）',
            'average_return_1y': 0.05,
            'top_performers': [
                {'code': 'EXAMPLE001', 'name': '示例基金A（需替换）', 'return_1y': 0.15, '_note': '示例数据'},
                {'code': 'EXAMPLE002', 'name': '示例基金B（需替换）', 'return_1y': 0.12, '_note': '示例数据'}
            ],
            'market_summary': '⚠️ 示例市场数据，请接入真实数据源（AkShare/同花顺iFinD）',
            '_warning': '此为示例数据，生产环境请使用真实数据源'
        }
    
    def _get_real_market_data(self, fund_type: str) -> Optional[Dict]:
        """获取真实市场数据"""
        try:
            import akshare as ak
            df = ak.fund_open_fund_rank_em()
            
            if df.empty:
                return None
            
            # 解析数据
            def parse_return(val):
                if val is None or val == '' or (isinstance(val, float) and val != val):  # nan check
                    return 0.0
                if isinstance(val, str):
                    return float(val.replace('%', '')) / 100
                return float(val) / 100 if val else 0.0
            
            # 计算平均收益
            returns_1y = []
            for _, row in df.head(100).iterrows():
                val = row.get('近1年', 0)
                returns_1y.append(parse_return(val))
            
            avg_return = sum(returns_1y) / len(returns_1y) if returns_1y else 0
            
            # 判断市场情绪
            if avg_return > 0.20:
                sentiment = '过热'
                trend = '强势上涨'
            elif avg_return > 0.10:
                sentiment = '乐观'
                trend = '上涨'
            elif avg_return > 0:
                sentiment = '中性偏多'
                trend = '震荡偏强'
            elif avg_return > -0.10:
                sentiment = '中性偏空'
                trend = '震荡偏弱'
            else:
                sentiment = '悲观'
                trend = '下跌'
            
            # 获取表现最好的基金
            top_performers = []
            for _, row in df.head(10).iterrows():
                top_performers.append({
                    'code': str(row.get('基金代码', '')),
                    'name': str(row.get('基金简称', '')),
                    'return_1y': parse_return(row.get('近1年')),
                    'return_ytd': parse_return(row.get('今年来'))
                })
            
            return {
                'analysis_date': datetime.now().strftime('%Y-%m-%d'),
                'data_source': 'AkShare',
                'fund_type': fund_type,
                'market_sentiment': sentiment,
                'trend': trend,
                'average_return_1y': round(avg_return, 4),
                'sample_size': len(df),
                'top_performers': top_performers,
                'market_summary': f"基于{len(df)}只基金统计，近1年平均收益{avg_return:.1%}，市场趋势{trend}"
            }
            
        except Exception as e:
            print(f"获取真实市场数据失败: {e}")
            return None
    
    def get_fund_flow(self) -> Dict:
        """
        获取资金流向
        
        Returns:
            资金流向报告
        """
        # 资金流向数据需要更专业的接口，这里提供结构
        return {
            'analysis_date': datetime.now().strftime('%Y-%m-%d'),
            'data_source': self.data_source,
            'note': '资金流向数据需通过专业数据终端获取',
            'north_bound_flow': None,  # 北向资金流向
            'south_bound_flow': None,  # 南向资金流向
            'sector_flow': []  # 板块资金流向
        }


def main():
    parser = argparse.ArgumentParser(description='基金市场研究')
    parser.add_argument('--fund-type', default='混合型', help='基金类型')
    parser.add_argument('--json', action='store_true', help='输出JSON格式')
    parser.add_argument('--use-real-data', action='store_true', default=True,
                       help='使用真实数据')
    parser.add_argument('--use-mock-data', action='store_true',
                       help='使用模拟数据')
    
    args = parser.parse_args()
    
    use_real = args.use_real_data and not args.use_mock_data
    researcher = MarketResearcher(use_real_data=use_real)
    
    result = researcher.analyze_market_trend(args.fund_type)
    
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("\n" + "=" * 60)
        print(f"📊 基金市场研究报告 ({result['data_source']})")
        print("=" * 60)
        print(f"分析日期: {result['analysis_date']}")
        print(f"基金类型: {result['fund_type']}")
        print(f"市场情绪: {result['market_sentiment']}")
        print(f"市场趋势: {result['trend']}")
        print(f"近1年平均收益: {result['average_return_1y']:.1%}")
        
        if 'top_performers' in result:
            print(f"\n表现前10基金:")
            for i, fund in enumerate(result['top_performers'][:5], 1):
                print(f"  {i}. {fund['name']} ({fund['code']})")
                print(f"     近1年收益: {fund['return_1y']:.1%}")
        
        if 'market_summary' in result:
            print(f"\n市场总结: {result['market_summary']}")


if __name__ == '__main__':
    main()
