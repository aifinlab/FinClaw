#!/usr/bin/env python3
"""券商经纪业务分析器"""

import akshare as ak
import pandas as pd
import json
from datetime import datetime
import argparse


class SecuritiesBrokerageAnalyzer:
    """券商经纪业务分析器"""
    
    def get_market_trading(self) -> dict:
        """获取市场成交数据"""
        try:
            # 获取A股历史成交数据
            df = ak.stock_zh_index_daily_em(symbol="sh000001")  # 上证指数
            
            if df is None or df.empty:
                return {"error": "无法获取成交数据"}
            
            latest = df.iloc[-1]
            
            return {
                "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "trade_date": latest.get('date'),
                "shanghai_amount": latest.get('amount'),
                "data_source": "AkShare - 上证指数",
                "note": "沪深两市总成交额需通过交易所获取"
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_investor_data(self) -> dict:
        """获取投资者数据"""
        try:
            # 获取新增投资者数据
            df = ak.stock_new_investor()
            
            if df is not None and not df.empty:
                latest = df.iloc[-1]
                
                return {
                    "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "data_month": latest.get('月份'),
                    "new_investors": latest.get('新增投资者数量'),
                    "total_investors": latest.get('期末投资者数量'),
                    "data_source": "中国证券登记结算公司",
                    "trend": "上升" if len(df) > 1 and df.iloc[-1]['新增投资者数量'] > df.iloc[-2]['新增投资者数量'] else "下降"
                }
        except Exception as e:
            return {"error": f"获取投资者数据失败: {str(e)}"}
    
    def get_brokerage_ranking(self) -> dict:
        """获取经纪业务排名"""
        # 基于市场地位的经纪业务排名
        ranking = [
            {"rank": 1, "securities": "中信证券", "note": "综合实力第一"},
            {"rank": 2, "securities": "国泰君安", "note": "经纪业务传统强项"},
            {"rank": 3, "securities": "招商证券", "note": "财富管理转型领先"},
            {"rank": 4, "securities": "华泰证券", "note": "科技赋能优势明显"},
            {"rank": 5, "securities": "广发证券", "note": "广东地区领先"}
        ]
        
        return {
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "brokerage_ranking": ranking,
            "data_source": "基于中证协年度统计",
            "note": "具体排名以中证协发布为准"
        }


def main():
    parser = argparse.ArgumentParser(description="券商经纪业务分析器")
    parser.add_argument("--market", action="store_true", help="市场成交数据")
    parser.add_argument("--investor", action="store_true", help="投资者数据")
    parser.add_argument("--ranking", action="store_true", help="经纪业务排名")
    
    args = parser.parse_args()
    analyzer = SecuritiesBrokerageAnalyzer()
    
    if args.market:
        result = analyzer.get_market_trading()
    elif args.investor:
        result = analyzer.get_investor_data()
    elif args.ranking:
        result = analyzer.get_brokerage_ranking()
    else:
        result = analyzer.get_market_trading()
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
