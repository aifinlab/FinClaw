#!/usr/bin/env python3
"""商品期货分析器"""

import akshare as ak
import pandas as pd
import json
from datetime import datetime
import argparse


class CommodityFuturesAnalyzer:
    """商品期货分析器"""
    
    # 商品板块分类
    SECTORS = {
        "有色金属": ["CU", "AL", "ZN", "PB", "NI", "SN"],
        "黑色金属": ["RB", "HC", "I", "J", "JM"],
        "能源化工": ["SC", "FU", "BU", "TA", "MA", "L", "PP", "EG", "PG"],
        "农产品": ["M", "Y", "P", "C", "SR", "CF", "RM", "OI"],
        "贵金属": ["AU", "AG"]
    }
    
    def analyze_sector(self, sector: str) -> dict:
        """分析商品板块"""
        if sector not in self.SECTORS:
            return {"error": f"未知板块: {sector}", "available_sectors": list(self.SECTORS.keys())}
        
        products = self.SECTORS[sector]
        
        return {
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "sector": sector,
            "products": products,
            "product_count": len(products),
            "note": "板块分析需要实时行情数据支持"
        }
    
    def get_seasonal_pattern(self, symbol: str) -> dict:
        """获取季节性规律"""
        try:
            df = ak.futures_zh_daily(symbol=symbol)
            
            if df is None or df.empty:
                return {"error": "数据不足"}
            
            df['date'] = pd.to_datetime(df['date'])
            df['month'] = df['date'].dt.month
            
            # 按月统计涨跌幅
            df['return'] = df['收盘'].pct_change()
            monthly_stats = df.groupby('month')['return'].agg(['mean', 'count']).to_dict()
            
            return {
                "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "symbol": symbol,
                "monthly_pattern": monthly_stats,
                "strongest_month": self._find_strongest_month(df),
                "weakest_month": self._find_weakest_month(df),
                "data_source": "AkShare"
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _find_strongest_month(self, df) -> int:
        """找出最强月份"""
        monthly_returns = df.groupby('month')['return'].mean()
        return int(monthly_returns.idxmax()) if not monthly_returns.empty else 0
    
    def _find_weakest_month(self, df) -> int:
        """找出最弱月份"""
        monthly_returns = df.groupby('month')['return'].mean()
        return int(monthly_returns.idxmin()) if not monthly_returns.empty else 0


def main():
    parser = argparse.ArgumentParser(description="商品期货分析器")
    parser.add_argument("--sector", help="板块名称(如有色金属/黑色金属等)")
    parser.add_argument("--seasonal", help="季节性分析合约代码")
    
    args = parser.parse_args()
    analyzer = CommodityFuturesAnalyzer()
    
    if args.sector:
        result = analyzer.analyze_sector(args.sector)
    elif args.seasonal:
        result = analyzer.get_seasonal_pattern(args.seasonal)
    else:
        result = {"available_sectors": list(analyzer.SECTORS.keys())}
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
