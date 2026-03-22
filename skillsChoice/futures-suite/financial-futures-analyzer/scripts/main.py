#!/usr/bin/env python3
"""金融期货分析器"""

import akshare as ak
import pandas as pd
import json
from datetime import datetime
import argparse


class FinancialFuturesAnalyzer:
    """金融期货分析器"""
    
    # 股指期货映射
    INDEX_FUTURES = {
        "IF": {"name": "沪深300", "index_code": "sh000300", "multiplier": 300},
        "IC": {"name": "中证500", "index_code": "sh000905", "multiplier": 200},
        "IH": {"name": "上证50", "index_code": "sh000016", "multiplier": 300},
        "IM": {"name": "中证1000", "index_code": "sh000852", "multiplier": 200}
    }
    
    def analyze_basis(self, symbol: str) -> dict:
        """分析股指期货基差"""
        try:
            # 获取期货价格
            futures_df = ak.futures_zh_daily(symbol=symbol)
            if futures_df is None or futures_df.empty:
                return {"error": "无法获取期货数据"}
            
            futures_price = futures_df.iloc[-1]['收盘']
            
            # 获取对应现货指数
            product_code = ''.join([c for c in symbol if c.isalpha()]).upper()
            if product_code not in self.INDEX_FUTURES:
                return {"error": "不支持的品种"}
            
            index_info = self.INDEX_FUTURES[product_code]
            
            # 获取指数数据
            index_df = ak.index_zh_a_hist(symbol=index_info['index_code'])
            if index_df is None or index_df.empty:
                return {"error": "无法获取指数数据"}
            
            spot_price = index_df.iloc[-1]['收盘']
            
            # 计算基差和贴水率
            basis = futures_price - spot_price
            discount_rate = basis / spot_price * 100
            
            return {
                "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "symbol": symbol,
                "futures_price": futures_price,
                "spot_price": spot_price,
                "basis": basis,
                "discount_rate": f"{discount_rate:.2f}%",
                "basis_status": "贴水" if basis < 0 else "升水",
                "data_source": "AkShare"
            }
            
        except Exception as e:
            return {"error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="金融期货分析器")
    parser.add_argument("--symbol", required=True, help="合约代码(如: IF2503)")
    
    args = parser.parse_args()
    analyzer = FinancialFuturesAnalyzer()
    result = analyzer.analyze_basis(args.symbol)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
