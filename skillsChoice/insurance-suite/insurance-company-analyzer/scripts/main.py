#!/usr/bin/env python3
"""保险公司分析器"""

import akshare as ak
import pandas as pd
import json
from datetime import datetime
import argparse


class InsuranceCompanyAnalyzer:
    """保险公司分析器"""
    
    # 上市保险公司映射
    COMPANIES = {
        "中国平安": {"code": "601318", "type": "综合保险"},
        "中国人寿": {"code": "601628", "type": "寿险"},
        "中国太保": {"code": "601601", "type": "综合保险"},
        "新华保险": {"code": "601336", "type": "寿险"},
        "中国人保": {"code": "601319", "type": "财险"}
    }
    
    def analyze_company(self, company_name: str) -> dict:
        """分析保险公司"""
        if company_name not in self.COMPANIES:
            return {
                "error": f"不支持的保险公司: {company_name}",
                "supported_companies": list(self.COMPANIES.keys())
            }
        
        info = self.COMPANIES[company_name]
        code = info["code"]
        
        result = {
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "company_name": company_name,
            "stock_code": code,
            "company_type": info["type"],
            "analysis": {}
        }
        
        try:
            # 获取实时行情
            df = ak.stock_zh_a_spot_em()
            stock_row = df[df['代码'] == code]
            
            if not stock_row.empty:
                result["realtime"] = {
                    "price": stock_row['最新价'].values[0],
                    "change_pct": stock_row['涨跌幅'].values[0],
                    "volume": stock_row['成交量'].values[0]
                }
        except Exception as e:
            result["realtime_error"] = str(e)
        
        try:
            # 获取财务指标
            df_fin = ak.stock_financial_analysis_indicator(symbol=code)
            if not df_fin.empty:
                latest = df_fin.iloc[0]
                result["financial_indicators"] = {
                    "roe": latest.get('净资产收益率', 'N/A'),
                    "eps": latest.get('每股收益', 'N/A'),
                    "bvps": latest.get('每股净资产', 'N/A'),
                    "report_date": latest.get('报告期', 'N/A')
                }
        except Exception as e:
            result["financial_error"] = str(e)
        
        return result
    
    def compare_companies(self) -> dict:
        """对比上市保险公司"""
        comparison = []
        
        for name, info in self.COMPANIES.items():
            comparison.append({
                "company": name,
                "code": info["code"],
                "type": info["type"]
            })
        
        return {
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "comparison": comparison,
            "total_companies": len(comparison)
        }


def main():
    parser = argparse.ArgumentParser(description="保险公司分析器")
    parser.add_argument("--company", help="保险公司名称")
    parser.add_argument("--compare", action="store_true", help="对比所有公司")
    
    args = parser.parse_args()
    analyzer = InsuranceCompanyAnalyzer()
    
    if args.compare:
        result = analyzer.compare_companies()
    elif args.company:
        result = analyzer.analyze_company(args.company)
    else:
        result = {"supported_companies": list(analyzer.COMPANIES.keys())}
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
