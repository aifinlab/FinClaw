#!/usr/bin/env python3
"""期货持仓追踪器"""

import akshare as ak
import pandas as pd
import json
from datetime import datetime
import argparse


class FuturesPositionTracker:
    """期货持仓追踪器"""
    
    def get_position_ranking(self, symbol: str) -> dict:
        """获取持仓排名"""
        try:
            # 获取持仓排名数据
            df = ak.futures_zh_realtime(symbol=symbol)
            
            return {
                "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "symbol": symbol,
                "open_interest": df['持仓量'].iloc[0] if '持仓量' in df.columns else 0,
                "volume": df['成交量'].iloc[0] if '成交量' in df.columns else 0,
                "note": "详细持仓排名数据需通过交易所获取",
                "data_source": "AkShare"
            }
            
        except Exception as e:
            return {"error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="期货持仓追踪器")
    parser.add_argument("--symbol", required=True, help="合约代码")
    
    args = parser.parse_args()
    tracker = FuturesPositionTracker()
    result = tracker.get_position_ranking(args.symbol)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
