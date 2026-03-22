#!/usr/bin/env python3
"""银行信贷分析器 - 真实数据源"""

import akshare as ak
import pandas as pd
import json
from datetime import datetime
import argparse


class BankCreditAnalyzer:
    """银行信贷分析器"""
    
    def get_credit_overview(self) -> dict:
        """获取信贷概览"""
        try:
            # 获取金融机构人民币信贷收支表
            df = ak.macro_china_financial_institution_deposit()
            
            if df is not None and not df.empty:
                latest = df.iloc[-1]
                
                return {
                    "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "data_date": latest.get('月份'),
                    "total_loans": latest.get('各项贷款余额'),
                    "loan_yoy": latest.get('各项贷款同比增长'),
                    "loan_mom": latest.get('各项贷款环比增长'),
                    "corporate_loans": latest.get('非金融企业及其他部门贷款'),
                    "household_loans": latest.get('住户部门贷款'),
                    "bill_financing": latest.get('票据融资'),
                    "data_source": "中国人民银行",
                    "note": "全国金融机构人民币信贷数据"
                }
        except Exception as e:
            return {"error": f"获取信贷数据失败: {str(e)}"}
    
    def analyze_loan_structure(self) -> dict:
        """分析贷款结构"""
        overview = self.get_credit_overview()
        
        if "error" in overview:
            return overview
        
        try:
            total = float(overview.get("total_loans", 0))
            corporate = float(overview.get("corporate_loans", 0))
            household = float(overview.get("household_loans", 0))
            bill = float(overview.get("bill_financing", 0))
            
            if total > 0:
                structure = {
                    "对公贷款占比": f"{corporate/total*100:.1f}%",
                    "零售贷款占比": f"{household/total*100:.1f}%",
                    "票据融资占比": f"{bill/total*100:.1f}%"
                }
            else:
                structure = {}
            
            return {
                "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "loan_structure": structure,
                "assessment": self._assess_structure(structure)
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _assess_structure(self, structure: dict) -> str:
        """评估贷款结构"""
        try:
            retail_str = structure.get("零售贷款占比", "0%").replace("%", "")
            retail_pct = float(retail_str)
            
            if retail_pct > 40:
                return "零售转型成效显著"
            elif retail_pct > 30:
                return "零售占比适中"
            else:
                return "对公业务为主"
        except:
            return "评估数据不足"


def main():
    parser = argparse.ArgumentParser(description="银行信贷分析器")
    parser.add_argument("--overview", action="store_true", help="信贷概览")
    parser.add_argument("--structure", action="store_true", help="贷款结构")
    
    args = parser.parse_args()
    analyzer = BankCreditAnalyzer()
    
    if args.structure:
        result = analyzer.analyze_loan_structure()
    else:
        result = analyzer.get_credit_overview()
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
