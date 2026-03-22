#!/usr/bin/env python3
"""银行股估值分析器 - 真实数据源"""

import akshare as ak
import pandas as pd
import json
from datetime import datetime
import argparse


class BankValuationAnalyzer:
    """银行股估值分析器"""
    
    BANK_CODES = {
        "招商银行": "600036", "工商银行": "601398", "建设银行": "601939",
        "农业银行": "601288", "中国银行": "601988", "交通银行": "601328",
        "邮储银行": "601658", "兴业银行": "601166", "浦发银行": "600000",
        "中信银行": "601998", "民生银行": "600016", "光大银行": "601818",
        "平安银行": "000001", "华夏银行": "600015", "浙商银行": "601916",
        "北京银行": "601169", "上海银行": "601229", "江苏银行": "600919",
        "南京银行": "601009", "宁波银行": "002142"
    }
    
    def analyze_valuation(self, bank_name: str) -> dict:
        """分析银行估值"""
        code = self.BANK_CODES.get(bank_name)
        if not code:
            return {"error": f"未找到银行: {bank_name}"}
        
        result = {
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "bank_name": bank_name,
            "stock_code": code,
            "valuation_metrics": {},
            "valuation_assessment": ""
        }
        
        try:
            # 获取实时行情
            df = ak.stock_zh_a_spot_em()
            stock = df[df['代码'] == code]
            
            if not stock.empty:
                s = stock.iloc[0]
                result["valuation_metrics"]["PB"] = s.get('市净率')
                result["valuation_metrics"]["PE_TTM"] = s.get('市盈率-动态')
                result["valuation_metrics"]["股息率"] = s.get('股息率')
                result["valuation_metrics"]["股价"] = s.get('最新价')
                result["valuation_metrics"]["总市值"] = s.get('总市值')
                
                # 估值评价
                pb = s.get('市净率', 0)
                if pb and float(pb) < 0.6:
                    result["valuation_assessment"] = "深度破净，存在估值修复空间"
                elif pb and float(pb) < 0.9:
                    result["valuation_assessment"] = "破净，关注基本面"
                elif pb and float(pb) > 1.2:
                    result["valuation_assessment"] = "估值溢价，质地优秀"
                else:
                    result["valuation_assessment"] = "估值合理"
                    
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def compare_valuation(self, bank_names: list = None) -> dict:
        """对比银行股估值"""
        if bank_names is None:
            bank_names = list(self.BANK_CODES.keys())[:10]
        
        results = []
        for name in bank_names:
            r = self.analyze_valuation(name)
            if "error" not in r:
                results.append({
                    "name": name,
                    "pb": r["valuation_metrics"].get("PB"),
                    "pe": r["valuation_metrics"].get("PE_TTM"),
                    "dividend": r["valuation_metrics"].get("股息率"),
                    "assessment": r.get("valuation_assessment")
                })
        
        # 按PB排序
        results.sort(key=lambda x: float(x.get("pb") or 999))
        
        return {
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "valuation_ranking": results,
            "cheapest": results[0] if results else None
        }


def main():
    parser = argparse.ArgumentParser(description="银行股估值分析器")
    parser.add_argument("--bank", help="银行名称")
    parser.add_argument("--compare", action="store_true", help="对比所有银行")
    
    args = parser.parse_args()
    analyzer = BankValuationAnalyzer()
    
    if args.compare:
        result = analyzer.compare_valuation()
    elif args.bank:
        result = analyzer.analyze_valuation(args.bank)
    else:
        result = {"error": "请指定--bank或--compare"}
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
