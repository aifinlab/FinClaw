#!/usr/bin/env python3
"""券商两融业务分析器"""

import akshare as ak
import pandas as pd
import json
from datetime import datetime
import argparse


class SecuritiesMarginAnalyzer:
    """券商两融业务分析器"""
    
    def get_margin_overview(self) -> dict:
        """获取两融市场概览"""
        try:
            # 获取融资融券汇总数据
            df = ak.stock_margin_szse()
            
            if df is not None and not df.empty:
                latest = df.iloc[-1]
                
                return {
                    "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "trade_date": latest.get('交易日期'),
                    "financing_balance": latest.get('融资余额'),
                    "securities_lending_balance": latest.get('融券余额'),
                    "total_balance": latest.get('融资融券余额'),
                    "financing_buy": latest.get('融资买入额'),
                    "financing_repay": latest.get('融资偿还额'),
                    "data_source": "深交所/AkShare",
                    "note": "深交所两融数据，沪市数据需单独获取"
                }
        except Exception as e:
            return {"error": f"获取两融数据失败: {str(e)}"}
    
    def get_margin_trend(self) -> dict:
        """获取两融趋势"""
        try:
            df = ak.stock_margin_szse()
            
            if df is not None and len(df) >= 5:
                recent = df.tail(5)
                trend = "上升" if float(recent.iloc[-1]['融资融券余额']) > float(recent.iloc[0]['融资融券余额']) else "下降"
                
                return {
                    "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "trend": trend,
                    "recent_5_days": recent[['交易日期', '融资融券余额']].to_dict('records'),
                    "data_source": "深交所"
                }
        except Exception as e:
            return {"error": str(e)}


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
