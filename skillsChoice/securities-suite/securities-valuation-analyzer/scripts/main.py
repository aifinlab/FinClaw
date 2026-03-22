#!/usr/bin/env python3
"""券商股估值分析器"""

import akshare as ak
import pandas as pd
import json
from datetime import datetime
import argparse


class SecuritiesValuationAnalyzer:
    """券商股估值分析器"""
    
    SECURITIES_CODES = {
        "中信证券": "600030", "华泰证券": "601688", "海通证券": "600837",
        "国泰君安": "601211", "招商证券": "600999", "广发证券": "000776",
        "中国银河": "601881", "中信建投": "601066", "东方证券": "600958",
        "兴业证券": "601377", "东方财富": "300059"
    }
    
    def analyze_valuation(self, name: str) -> dict:
        """分析券商估值"""
        code = self.SECURITIES_CODES.get(name)
        if not code:
            return {"error": f"未找到券商: {name}"}
        
        try:
            df = ak.stock_zh_a_spot_em()
            stock = df[df['代码'] == code]
            
            if stock.empty:
                return {"error": "无法获取行情"}
            
            s = stock.iloc[0]
            
            return {
                "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "securities_name": name,
                "stock_code": code,
                "valuation": {
                    "PB": s.get('市净率'),
                    "PE_TTM": s.get('市盈率-动态'),
                    "PE_LYR": s.get('市盈率-静态'),
                    "price": s.get('最新价'),
                    "market_cap": s.get('总市值')
                },
                "assessment": self._assess_valuation(s.get('市净率'))
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def compare_valuation(self) -> dict:
        """对比券商估值"""
        results = []
        
        for name, code in self.SECURITIES_CODES.items():
            r = self.analyze_valuation(name)
            if "error" not in r:
                results.append({
                    "name": name,
                    "pb": r["valuation"].get("PB"),
                    "pe": r["valuation"].get("PE_TTM"),
                    "assessment": r.get("assessment")
                })
        
        results.sort(key=lambda x: float(x.get("pb") or 999))
        
        return {
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "valuation_ranking": results,
            "cheapest": results[0] if results else None
        }
    
    def _assess_valuation(self, pb) -> str:
        """估值评估"""
        try:
            pb_val = float(pb) if pb else 0
            if pb_val < 1.0:
                return "深度破净，估值修复空间大"
            elif pb_val < 1.3:
                return "破净，关注基本面"
            elif pb_val > 2.0:
                return "估值溢价，质地优秀"
            else:
                return "估值合理"
        except:
            return "数据不足"


def main():
    parser = argparse.ArgumentParser(description="券商股估值分析器")
    parser.add_argument("--securities", help="券商名称")
    parser.add_argument("--compare", action="store_true", help="对比估值")
    
    args = parser.parse_args()
    analyzer = SecuritiesValuationAnalyzer()
    
    if args.compare:
        result = analyzer.compare_valuation()
    elif args.securities:
        result = analyzer.analyze_valuation(args.securities)
    else:
        result = {"error": "请指定参数"}
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
