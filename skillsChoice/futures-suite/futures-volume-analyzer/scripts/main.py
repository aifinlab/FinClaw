#!/usr/bin/env python3
"""期货成交量持仓分析器"""

import akshare as ak
import pandas as pd
import json
from datetime import datetime
import argparse


class FuturesVolumeAnalyzer:
    """期货成交量持仓分析器"""
    
    def analyze_volume(self, symbol: str) -> dict:
        """分析期货品种成交量持仓"""
        try:
            # 获取期货历史行情
            df = ak.futures_zh_daily(symbol=symbol)
            
            if df is None or df.empty:
                return {"error": f"无法获取{symbol}数据"}
            
            # 计算指标
            df['volume_change'] = df['成交量'].pct_change()
            df['oi_change'] = df['持仓量'].pct_change()
            
            latest = df.iloc[-1]
            prev = df.iloc[-2] if len(df) > 1 else latest
            
            return {
                "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "symbol": symbol,
                "latest_data": {
                    "date": latest.get('date'),
                    "close": latest.get('收盘'),
                    "volume": latest.get('成交量'),
                    "open_interest": latest.get('持仓量'),
                    "volume_change_pct": f"{latest.get('volume_change', 0)*100:.2f}%",
                    "oi_change_pct": f"{latest.get('oi_change', 0)*100:.2f}%"
                },
                "analysis": self._analyze_signal(latest, prev),
                "data_source": "AkShare"
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _analyze_signal(self, latest, prev) -> dict:
        """分析交易信号"""
        signal = {}
        
        volume_change = latest.get('volume_change', 0)
        price_change = (latest.get('收盘', 0) - prev.get('收盘', 0)) / prev.get('收盘', 1) if prev.get('收盘') else 0
        
        # 量价关系
        if volume_change > 0.5 and price_change > 0:
            signal["volume_price"] = "放量上涨，多头强势"
        elif volume_change > 0.5 and price_change < 0:
            signal["volume_price"] = "放量下跌，空头强势"
        elif volume_change < -0.2 and price_change > 0:
            signal["volume_price"] = "缩量上涨，动能减弱"
        elif volume_change < -0.2 and price_change < 0:
            signal["volume_price"] = "缩量下跌，可能企稳"
        else:
            signal["volume_price"] = "量价正常"
        
        return signal


def main():
    parser = argparse.ArgumentParser(description="期货成交量持仓分析器")
    parser.add_argument("--symbol", required=True, help="期货合约代码(如: RB2501)")
    
    args = parser.parse_args()
    analyzer = FuturesVolumeAnalyzer()
    result = analyzer.analyze_volume(args.symbol)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
