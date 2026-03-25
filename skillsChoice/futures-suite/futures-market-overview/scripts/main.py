#!/usr/bin/env python3
"""期货市场概览分析器 - 使用AkShare开源数据接口

功能：获取期货市场整体数据
数据源：AkShare开源金融数据接口
说明：市场数据需参考各大交易所统计
"""

import akshare as ak
import json
from datetime import datetime
import argparse


class FuturesMarketOverview:
    """期货市场概览分析器 - 使用AkShare"""
    
    EXCHANGES = {
        "SHFE": "上海期货交易所",
        "DCE": "大连商品交易所",
        "CZCE": "郑州商品交易所",
        "CFFEX": "中国金融期货交易所",
        "INE": "上海国际能源交易中心"
    }
    
    def __init__(self):
        self.query_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _get_futures_data(self, symbol: str) -> dict:
        """获取期货行情 - 使用AkShare"""
        try:
            df = ak.futures_zh_realtime(symbol=symbol)
            if df is not None and not df.empty:
                latest = df.iloc[0]
                return {
                    "price": latest.get('最新价'),
                    "change_pct": latest.get('涨跌幅'),
                    "volume": latest.get('成交量')
                }
        except Exception:
            return None
    
    def get_market_overview(self) -> dict:
        """获取期货市场概览"""
        result = {
            "query_time": self.query_time,
            "exchanges": list(self.EXCHANGES.values()),
            "note": "详细市场数据参考各交易所统计月报"
        }
        
        # 尝试获取几个主力合约的行情
        main_contracts = ["RB", "I", "SC", "M", "IF"]
        quotes = []
        for symbol in main_contracts:
            data = self._get_futures_data(symbol)
            if data:
                quotes.append({
                    "symbol": symbol,
                    "price": data.get("price"),
                    "change_pct": data.get("change_pct")
                })
        
        if quotes:
            result["main_contracts_quotes"] = quotes
        
        result["market_structure"] = {
            "商品期货": "上海期货交易所、大连商品交易所、郑州商品交易所",
            "金融期货": "中国金融期货交易所",
            "能源期货": "上海国际能源交易中心"
        }
        
        result["data_source"] = "AkShare开源数据 + 交易所公告"
        result["data_quality"] = "实时行情 + 交易所统计"
        
        return result


def main():
    parser = argparse.ArgumentParser(description="期货市场概览分析器")
    parser.add_argument("--overview", action="store_true", help="获取市场概览")
    
    args = parser.parse_args()
    analyzer = FuturesMarketOverview()
    
    result = analyzer.get_market_overview()
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
