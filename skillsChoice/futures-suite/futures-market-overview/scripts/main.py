#!/usr/bin/env python3
"""
期货市场概览分析器
获取期货市场整体数据和统计信息
"""

import akshare as ak
import pandas as pd
import json
from datetime import datetime
import argparse


class FuturesMarketOverview:
    """期货市场概览分析器"""
    
    EXCHANGES = {
        "SHFE": "上海期货交易所",
        "DCE": "大连商品交易所",
        "CZCE": "郑州商品交易所",
        "CFFEX": "中国金融期货交易所",
        "INE": "上海国际能源交易中心"
    }
    
    def get_market_overview(self) -> dict:
        """获取期货市场概览"""
        result = {
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "market_overview": {}
        }
        
        try:
            # 获取期货品种列表和行情
            df = ak.futures_zh_realtime(symbol=""​")
            
            if df is not None and not df.empty:
                result["market_overview"]["total_contracts"] = len(df)
                result["market_overview"]["total_volume"] = df['成交量'].sum() if '成交量' in df.columns else 0
                result["market_overview"]["total_open_interest"] = df['持仓量'].sum() if '持仓量' in df.columns else 0
                
                # 最活跃品种
                if '成交量' in df.columns:
                    top_volume = df.nlargest(10, '成交量')[['名称', '成交量', '最新价']].to_dict('records')
                    result["market_overview"]["top_active_contracts"] = top_volume
                
                result["data_source"] = "AkShare - 期货实时行情"
            else:
                result["error"] = "无法获取期货数据"
                
        except Exception as e:
            result["error"] = str(e)
            result["suggestion"] = "请检查网络连接"
        
        return result
    
    def get_exchange_stats(self, exchange: str = None) -> dict:
        """获取交易所统计"""
        try:
            # 获取期货主力连续合约
            df = ak.futures_main_sina()
            
            if df is not None and not df.empty:
                # 按交易所分组统计
                stats = df.groupby('exchange').agg({
                    'volume': 'sum',
                    'open_interest': 'sum'
                }).to_dict()
                
                return {
                    "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "exchange_stats": stats,
                    "data_source": "AkShare"
                }
            else:
                return {"error": "无数据"}
                
        except Exception as e:
            return {"error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="期货市场概览分析器")
    parser.add_argument("--overview", action="store_true", help="市场概览")
    parser.add_argument("--exchange", help="交易所代码(SHFE/DCE/CZCE/CFFEX/INE)")
    
    args = parser.parse_args()
    analyzer = FuturesMarketOverview()
    
    if args.exchange:
        result = analyzer.get_exchange_stats(args.exchange)
    else:
        result = analyzer.get_market_overview()
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
