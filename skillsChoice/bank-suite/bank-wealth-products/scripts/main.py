#!/usr/bin/env python3
"""银行理财产品分析器 - 真实数据源"""

import akshare as ak
import pandas as pd
import json
from datetime import datetime
import argparse


class BankWealthProducts:
    """银行理财产品分析器"""
    
    def get_products(self, bank_name: str = None, risk_level: str = None) -> dict:
        """获取理财产品列表"""
        try:
            # 使用AkShare获取理财产品数据
            df = ak.bank_wealth_product()
            
            if df is None or df.empty:
                return {"error": "无法获取理财产品数据"}
            
            # 筛选
            if bank_name:
                df = df[df['发行银行'].str.contains(bank_name, na=False)]
            if risk_level:
                df = df[df['风险等级'] == risk_level]
            
            products = df.head(50).to_dict('records')
            
            return {
                "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "count": len(products),
                "products": products,
                "data_source": "中国理财网/AkShare"
            }
            
        except Exception as e:
            return {"error": f"获取数据失败: {str(e)}"}
    
    def analyze_yields(self) -> dict:
        """分析理财产品收益率"""
        try:
            df = ak.bank_wealth_product()
            
            if df is None or df.empty:
                return {"error": "无数据"}
            
            # 按风险等级统计平均收益率
            yield_by_risk = df.groupby('风险等级')['预期收益率'].mean().to_dict()
            
            return {
                "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "avg_yield_by_risk": yield_by_risk,
                "data_source": "中国理财网"
            }
            
        except Exception as e:
            return {"error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="银行理财产品分析器")
    parser.add_argument("--bank", help="银行名称")
    parser.add_argument("--risk", help="风险等级(R1/R2/R3/R4)")
    parser.add_argument("--yields", action="store_true", help="分析收益率")
    
    args = parser.parse_args()
    analyzer = BankWealthProducts()
    
    if args.yields:
        result = analyzer.analyze_yields()
    else:
        result = analyzer.get_products(args.bank, args.risk)
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
