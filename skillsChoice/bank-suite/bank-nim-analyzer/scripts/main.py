#!/usr/bin/env python3
"""银行净息差(NIM)分析器 - 真实数据源"""

import akshare as ak
import pandas as pd
import json
from datetime import datetime
import argparse


class BankNIMAnalyzer:
    """银行净息差分析器"""
    
    BANK_CODES = {
        "招商银行": "600036", "工商银行": "601398", "建设银行": "601939",
        "农业银行": "601288", "中国银行": "601988", "交通银行": "601328",
        "邮储银行": "601658", "兴业银行": "601166", "平安银行": "000001",
        "宁波银行": "002142", "南京银行": "601009", "江苏银行": "600919"
    }
    
    def analyze_nim(self, bank_name: str) -> dict:
        """分析银行净息差"""
        code = self.BANK_CODES.get(bank_name)
        if not code:
            return {"error": f"未找到银行: {bank_name}"}
        
        result = {
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "bank_name": bank_name,
            "stock_code": code,
            "nim_data": {}
        }
        
        try:
            # 获取财务分析指标
            df = ak.stock_financial_analysis_indicator(symbol=code)
            if df is not None and not df.empty:
                latest = df.iloc[0]
                
                result["nim_data"]["净息差_NIM"] = latest.get('净息差')
                result["nim_data"]["净利差"] = latest.get('净利差')
                result["nim_data"]["生息资产收益率"] = latest.get('生息资产收益率')
                result["nim_data"]["计息负债成本率"] = latest.get('计息负债成本率')
                result["nim_data"]["报告期"] = latest.get('报告期')
                
                # NIM评估
                nim_str = latest.get('净息差', '0%').replace('%', '')
                try:
                    nim = float(nim_str)
                    if nim >= 2.5:
                        result["assessment"] = "NIM优秀，盈利能力强劲"
                    elif nim >= 2.0:
                        result["assessment"] = "NIM良好"
                    elif nim >= 1.8:
                        result["assessment"] = "NIM中等，关注息差压力"
                    else:
                        result["assessment"] = "NIM偏低，面临息差收窄压力"
                except:
                    result["assessment"] = "数据不足"
                    
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def compare_nim(self, bank_names: list = None) -> dict:
        """对比银行NIM"""
        if bank_names is None:
            bank_names = list(self.BANK_CODES.keys())[:8]
        
        results = []
        for name in bank_names:
            r = self.analyze_nim(name)
            if "error" not in r:
                nim_val = r["nim_data"].get("净息差_NIM", "0%").replace("%", "")
                try:
                    nim_float = float(nim_val)
                except:
                    nim_float = 0
                results.append({
                    "name": name,
                    "nim": r["nim_data"].get("净息差_NIM"),
                    "nim_float": nim_float,
                    "asset_yield": r["nim_data"].get("生息资产收益率"),
                    "liability_cost": r["nim_data"].get("计息负债成本率")
                })
        
        results.sort(key=lambda x: x["nim_float"], reverse=True)
        
        return {
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "nim_ranking": results,
            "highest_nim": results[0] if results else None
        }


def main():
    parser = argparse.ArgumentParser(description="银行NIM分析器")
    parser.add_argument("--bank", help="银行名称")
    parser.add_argument("--compare", action="store_true", help="对比NIM")
    
    args = parser.parse_args()
    analyzer = BankNIMAnalyzer()
    
    if args.compare:
        result = analyzer.compare_nim()
    elif args.bank:
        result = analyzer.analyze_nim(args.bank)
    else:
        result = {"error": "请指定--bank或--compare"}
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
