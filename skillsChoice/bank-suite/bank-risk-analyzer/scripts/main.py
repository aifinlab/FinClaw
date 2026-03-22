#!/usr/bin/env python3
"""银行风险分析器 - 真实数据源"""

import akshare as ak
import pandas as pd
import json
from datetime import datetime
import argparse


class BankRiskAnalyzer:
    """银行风险分析器"""
    
    BANK_CODES = {
        "招商银行": "600036", "工商银行": "601398", "农业银行": "601288",
        "中国银行": "601988", "建设银行": "601939", "交通银行": "601328",
        "邮储银行": "601658", "兴业银行": "601166", "浦发银行": "600000",
        "中信银行": "601998", "民生银行": "600016", "光大银行": "601818",
        "平安银行": "000001", "华夏银行": "600015", "北京银行": "601169",
        "上海银行": "601229", "江苏银行": "600919", "南京银行": "601009",
        "宁波银行": "002142", "杭州银行": "600926"
    }
    
    def analyze_risk(self, bank_name: str) -> dict:
        """分析银行风险指标"""
        code = self.BANK_CODES.get(bank_name)
        if not code:
            return {"error": f"未找到银行: {bank_name}"}
        
        result = {
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "bank_name": bank_name,
            "stock_code": code,
            "risk_indicators": {},
            "risk_level": "",
            "warnings": []
        }
        
        try:
            # 获取财务分析指标
            df = ak.stock_financial_analysis_indicator(symbol=code)
            if df is not None and not df.empty:
                latest = df.iloc[0]
                
                # 风险指标
                result["risk_indicators"]["不良贷款率"] = latest.get('不良贷款率', 'N/A')
                result["risk_indicators"]["拨备覆盖率"] = latest.get('拨备覆盖率', 'N/A')
                result["risk_indicators"]["资本充足率"] = latest.get('资本充足率', 'N/A')
                result["risk_indicators"]["核心一级资本充足率"] = latest.get('核心一级资本充足率', 'N/A')
                result["risk_indicators"]["流动性覆盖率"] = latest.get('流动性覆盖率', 'N/A')
                
                # 风险评级
                npl = self._parse_pct(latest.get('不良贷款率', '0'))
                provision = self._parse_pct(latest.get('拨备覆盖率', '0'))
                
                if npl < 1 and provision > 300:
                    result["risk_level"] = "低风险"
                elif npl < 1.5 and provision > 200:
                    result["risk_level"] = "中低风险"
                elif npl < 2 and provision > 150:
                    result["risk_level"] = "中等风险"
                else:
                    result["risk_level"] = "需关注"
                    result["warnings"].append("资产质量或拨备覆盖率需关注")
                
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def compare_risk(self, bank_names: list) -> dict:
        """对比多家银行风险"""
        results = []
        for name in bank_names:
            r = self.analyze_risk(name.strip())
            if "error" not in r:
                results.append({
                    "name": name,
                    "level": r.get("risk_level"),
                    "npl": r["risk_indicators"].get("不良贷款率"),
                    "provision": r["risk_indicators"].get("拨备覆盖率")
                })
        
        return {
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "comparison": sorted(results, key=lambda x: self._parse_pct(x.get("npl", "100%")))
        }
    
    def _parse_pct(self, val) -> float:
        """解析百分比"""
        try:
            return float(str(val).replace('%', ''))
        except:
            return 0


def main():
    parser = argparse.ArgumentParser(description="银行风险分析器")
    parser.add_argument("--bank", help="银行名称")
    parser.add_argument("--banks", help="多家银行逗号分隔")
    parser.add_argument("--action", choices=["analyze", "compare"], default="analyze")
    
    args = parser.parse_args()
    analyzer = BankRiskAnalyzer()
    
    if args.action == "analyze" and args.bank:
        result = analyzer.analyze_risk(args.bank)
    elif args.action == "compare" and args.banks:
        result = analyzer.compare_risk(args.banks.split(","))
    else:
        result = {"error": "参数不足"}
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
