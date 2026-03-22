#!/usr/bin/env python3
"""券商自营业务分析器"""

import akshare as ak
import pandas as pd
import json
from datetime import datetime
import argparse


class SecuritiesProprietaryAnalyzer:
    """券商自营业务分析器"""
    
    SECURITIES_CODES = {
        "中信证券": "600030", "华泰证券": "601688", "海通证券": "600837",
        "国泰君安": "601211", "招商证券": "600999", "广发证券": "000776"
    }
    
    def analyze_proprietary(self, name: str) -> dict:
        """分析券商自营业务"""
        code = self.SECURITIES_CODES.get(name)
        if not code:
            return {"error": f"未找到券商: {name}"}
        
        try:
            # 获取利润表
            df = ak.stock_profit_sheet_by_report_em(symbol=code)
            
            if df is None or df.empty:
                return {"error": "无法获取财务数据"}
            
            latest = df.iloc[0]
            
            # 提取自营相关收入
            investment_income = latest.get('投资收益', 0)
            fair_value_change = latest.get('公允价值变动收益', 0)
            total_revenue = latest.get('营业总收入', 1)
            
            proprietary_income = float(investment_income) + float(fair_value_change)
            proprietary_ratio = proprietary_income / float(total_revenue) * 100 if total_revenue else 0
            
            return {
                "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "securities_name": name,
                "stock_code": code,
                "proprietary_income": proprietary_income,
                "investment_income": investment_income,
                "fair_value_change": fair_value_change,
                "proprietary_ratio": f"{proprietary_ratio:.2f}%",
                "report_period": latest.get('报告期'),
                "data_source": "AkShare - 利润表"
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def compare_proprietary(self) -> dict:
        """对比券商自营业务"""
        results = []
        for name in self.SECURITIES_CODES.keys():
            r = self.analyze_proprietary(name)
            if "error" not in r:
                results.append({
                    "name": name,
                    "income": r.get("proprietary_income"),
                    "ratio": r.get("proprietary_ratio")
                })
        
        results.sort(key=lambda x: float(x.get("income") or 0), reverse=True)
        
        return {
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "comparison": results
        }


def main():
    parser = argparse.ArgumentParser(description="券商自营业务分析器")
    parser.add_argument("--securities", help="券商名称")
    parser.add_argument("--compare", action="store_true", help="对比")
    
    args = parser.parse_args()
    analyzer = SecuritiesProprietaryAnalyzer()
    
    if args.compare:
        result = analyzer.compare_proprietary()
    elif args.securities:
        result = analyzer.analyze_proprietary(args.securities)
    else:
        result = {"error": "请指定参数"}
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
