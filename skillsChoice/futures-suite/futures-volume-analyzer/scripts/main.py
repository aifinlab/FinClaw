#!/usr/bin/env python3
"""期货成交量持仓分析器 - 使用AkShare开源数据接口

功能：分析期货品种成交量、持仓量
数据源：AkShare开源金融数据接口
说明：成交持仓数据需参考交易所统计
"""

import akshare as ak
import json
from datetime import datetime
import argparse


class FuturesVolumeAnalyzer:
    """期货成交量持仓分析器 - 使用AkShare获取实时数据"""
    
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
                    "volume": latest.get('成交量'),
                    "open_interest": latest.get('持仓量')
                }
        except Exception:
            return None
    
    def _get_hist_data(self, symbol: str) -> list:
        """获取历史成交数据 - 使用AkShare"""
        try:
            df = ak.futures_zh_daily(symbol=symbol)
            if df is not None and not df.empty:
                return df.to_dict('records')
        except Exception:
            return []
        return []
    
    def analyze_volume(self, symbol: str) -> dict:
        """分析期货品种成交量持仓"""
        product_code = ''.join([c for c in symbol if c.isalpha()]).upper()
        
        result = {
            "query_time": self.query_time,
            "symbol": symbol,
            "product_code": product_code
        }
        
        # 获取实时行情
        quote = self._get_futures_data(symbol)
        if quote:
            result["realtime"] = {
                "price": quote.get("price"),
                "change_pct": quote.get("change_pct"),
                "volume": quote.get("volume"),
                "open_interest": quote.get("open_interest")
            }
        
        # 获取历史数据计算趋势
        hist_data = self._get_hist_data(symbol)
        if hist_data and len(hist_data) >= 5:
            recent_volume = [d.get('volume', 0) for d in hist_data[-5:] if d.get('volume')]
            if recent_volume:
                avg_volume = sum(recent_volume) / len(recent_volume)
                result["volume_analysis"] = {
                    "recent_5d_avg_volume": round(avg_volume, 0) if avg_volume else None,
                    "data_points": len(recent_volume)
                }
        
        result["analysis_note"] = "详细成交持仓排名参考各交易所统计"
        result["data_source"] = "AkShare开源数据"
        result["data_quality"] = "实时行情 + 历史数据"
        
        return result


def main():
    parser = argparse.ArgumentParser(description="期货成交量持仓分析器")
    parser.add_argument("--symbol", help="合约代码(如: RB, CU, SC)")
    
    args = parser.parse_args()
    analyzer = FuturesVolumeAnalyzer()
    
    if args.symbol:
        result = analyzer.analyze_volume(args.symbol)
    else:
        result = {
            "usage": "--symbol RB"
        }
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
