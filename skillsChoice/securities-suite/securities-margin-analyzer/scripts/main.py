#!/usr/bin/env python3
"""券商两融业务分析器 - 使用AkShare开源数据接口

功能：分析两融市场概况、趋势、标的扩容
数据源：AkShare开源金融数据接口
说明：详细两融数据需参考交易所公告
"""

import akshare as ak
import json
from datetime import datetime
import argparse


class SecuritiesMarginAnalyzer:
    """券商两融业务分析器 - 基于市场数据"""
    
    def __init__(self):
        self.query_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _get_stock_market_data(self) -> dict:
        """获取股票市场数据 - 使用AkShare"""
        try:
            df = ak.stock_zh_a_spot_em()
            if df is not None and not df.empty:
                # 计算市场成交额
                total_amount = df['成交额'].sum() if '成交额' in df.columns else 0
                # 计算上涨下跌家数
                up_count = len(df[df['涨跌幅'] > 0]) if '涨跌幅' in df.columns else 0
                down_count = len(df[df['涨跌幅'] < 0]) if '涨跌幅' in df.columns else 0
                
                return {
                    "当日总成交额_亿元": round(total_amount / 1e8, 2) if total_amount else None,
                    "上涨家数": up_count,
                    "下跌家数": down_count,
                    "data_source": "AkShare - 东方财富"
                }
        except Exception:
            return None
        return None
    
    def _get_index_data(self) -> dict:
        """获取市场指数数据 - 使用AkShare"""
        try:
            df = ak.index_zh_a_hist(symbol="000300", period="daily",
                                   start_date="20240101", end_date=datetime.now().strftime("%Y%m%d"))
            if df is not None and not df.empty:
                latest = df.iloc[-1]
                return {
                    "沪深300点位": latest.get('收盘'),
                    "data_source": "AkShare - 东方财富"
                }
        except Exception:
            return None
        return None
    
    def get_margin_overview(self) -> dict:
        """获取两融市场概览 - 基于市场环境分析"""
        result = {
            "query_time": self.query_time,
            "analysis_type": "两融业务市场分析",
            "note": "详细两融数据需参考沪深交易所公告"
        }
        
        # 获取市场数据
        market_data = self._get_stock_market_data()
        if market_data:
            result["market_environment"] = market_data
        
        # 获取指数数据
        index_data = self._get_index_data()
        if index_data:
            result["index_data"] = index_data
        
        result["margin_analysis"] = {
            "两融余额影响因素": [
                "A股市场整体走势",
                "投资者风险偏好",
                "两融标的扩容",
                "保证金比例调整"
            ],
            "风险指标说明": {
                "维持担保比例": "客户担保物价值/融资融券债务",
                "警戒线": "通常为150%，低于需追加担保",
                "平仓线": "通常为130%，低于可能强制平仓"
            },
            "关注要点": [
                "两融余额变化趋势",
                "融资买入额/偿还额",
                "融券卖出量",
                "维持担保比例分布"
            ],
            "业务影响": "两融余额与市场情绪高度相关，影响券商利息收入"
        }
        
        result["data_source"] = "AkShare开源数据 + 行业分析"
        result["data_quality"] = "实时市场数据 + 定性分析"
        
        return result
    
    def get_margin_trend(self) -> dict:
        """获取两融趋势 - 基于市场趋势分析"""
        result = {
            "query_time": self.query_time,
            "analysis_type": "两融趋势分析",
            "note": "历史两融数据需参考交易所统计"
        }
        
        # 获取市场数据
        market_data = self._get_stock_market_data()
        if market_data:
            result["market_environment"] = market_data
        
        # 获取指数数据
        index_data = self._get_index_data()
        if index_data:
            result["index_data"] = index_data
        
        result["trend_analysis"] = {
            "趋势判断": "两融余额与市场走势高度相关",
            "影响因素": [
                "市场行情（牛市融资增加，熊市减少）",
                "投资者情绪",
                "政策变化（标的扩容、保证金调整）",
                "利率环境"
            ],
            "关注指标": [
                "融资余额变化",
                "融券余额变化",
                "融资买入额",
                "融资偿还额"
            ],
            "数据来源说明": "详细历史数据参考沪深交易所统计月报"
        }
        
        result["data_source"] = "AkShare开源数据 + 行业分析"
        result["data_quality"] = "实时市场数据 + 定性分析"
        
        return result


def main():
    parser = argparse.ArgumentParser(description="券商两融业务分析器")
    parser.add_argument("--overview", action="store_true", help="两融概览")
    parser.add_argument("--trend", action="store_true", help="两融趋势")
    
    args = parser.parse_args()
    analyzer = SecuritiesMarginAnalyzer()
    
    if args.trend:
        result = analyzer.get_margin_trend()
    else:
        result = analyzer.get_margin_overview()
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
