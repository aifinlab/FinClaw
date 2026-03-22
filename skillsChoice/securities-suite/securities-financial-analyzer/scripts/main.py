#!/usr/bin/env python3
"""
券商财务分析器
深度分析上市券商的财务报表和核心指标
"""

import akshare as ak
import pandas as pd
import json
from datetime import datetime
import argparse


class SecuritiesFinancialAnalyzer:
    """券商财务分析器"""
    
    # 主要上市券商代码映射
    SECURITIES_CODES = {
        "中信证券": "600030", "华泰证券": "601688", "海通证券": "600837",
        "国泰君安": "601211", "招商证券": "600999", "广发证券": "000776",
        "中国银河": "601881", "中信建投": "601066", "东方证券": "600958",
        "兴业证券": "601377", "光大证券": "601788", "国信证券": "002736",
        "东方财富": "300059", "申万宏源": "000166", "中国中金": "601995",
        "浙商证券": "601878", "方正证券": "601901", "国金证券": "600109",
        "东吴证券": "601555", "财通证券": "601108", "长城证券": "002939",
        "国联证券": "601456", "南京证券": "601990", "红塔证券": "601236",
        "中银证券": "601696", "华安证券": "600909", "华鑫股份": "600621",
        "山西证券": "002500", "西部证券": "002673", "第一创业": "002797",
        "西南证券": "600369", "国海证券": "000750", "中原证券": "601375",
        "华林证券": "002945", "锦龙股份": "000712", "哈投股份": "600864"
    }
    
    def __init__(self):
        pass
    
    def get_securities_code(self, name: str) -> str:
        """获取券商代码"""
        if name in self.SECURITIES_CODES:
            return self.SECURITIES_CODES[name]
        
        # 模糊匹配
        for k, v in self.SECURITIES_CODES.items():
            if name in k or k in name:
                return v
        return None
    
    def analyze_securities(self, name: str) -> dict:
        """分析单家券商财务"""
        code = self.get_securities_code(name)
        if not code:
            return {"error": f"未找到券商: {name}"}
        
        result = {
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "securities_name": name,
            "stock_code": code,
            "financial_analysis": {}
        }
        
        try:
            # 获取实时行情
            result["realtime"] = self._get_realtime(code)
            
            # 获取财务指标
            result["financial_indicators"] = self._get_financial_indicators(code)
            
            # 获取资产负债表摘要
            result["balance_sheet"] = self._get_balance_sheet(code)
            
            # 获取利润表摘要
            result["income_statement"] = self._get_income_statement(code)
            
            # 计算核心指标
            result["core_metrics"] = self._calculate_metrics(result)
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def compare_securities(self, names: list) -> dict:
        """对比多家券商"""
        results = []
        for name in names:
            analysis = self.analyze_securities(name.strip())
            if "error" not in analysis:
                results.append({
                    "name": name,
                    "code": analysis.get("stock_code"),
                    "metrics": analysis.get("core_metrics", {}),
                    "realtime": analysis.get("realtime", {})
                })
        
        return {
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "securities": [r["name"] for r in results],
            "comparison": results
        }
    
    def _get_realtime(self, code: str) -> dict:
        """获取实时行情"""
        try:
            df = ak.stock_zh_a_spot_em()
            stock = df[df['代码'] == code]
            if not stock.empty:
                s = stock.iloc[0]
                return {
                    "price": s.get('最新价'),
                    "change_pct": s.get('涨跌幅'),
                    "market_cap": s.get('总市值'),
                    "pb": s.get('市净率'),
                    "pe": s.get('市盈率-动态')
                }
        except:
            pass
        return {}
    
    def _get_financial_indicators(self, code: str) -> dict:
        """获取财务指标"""
        try:
            df = ak.stock_financial_analysis_indicator(symbol=code)
            if df is not None and not df.empty:
                latest = df.iloc[0]
                return {
                    "roe": latest.get('净资产收益率'),
                    "roa": latest.get('总资产收益率'),
                    "eps": latest.get('基本每股收益'),
                    "bvps": latest.get('每股净资产')
                }
        except:
            pass
        return {}
    
    def _get_balance_sheet(self, code: str) -> dict:
        """获取资产负债表"""
        try:
            df = ak.stock_balance_sheet_by_report_em(symbol=code)
            if df is not None and not df.empty:
                latest = df.iloc[0]
                total_assets = float(latest.get('资产总计', 0))
                total_equity = float(latest.get('所有者权益合计', 0))
                
                leverage = total_assets / total_equity if total_equity > 0 else 0
                
                return {
                    "total_assets": total_assets,
                    "total_equity": total_equity,
                    "leverage": f"{leverage:.2f}x"
                }
        except:
            pass
        return {}
    
    def _get_income_statement(self, code: str) -> dict:
        """获取利润表"""
        try:
            df = ak.stock_profit_sheet_by_report_em(symbol=code)
            if df is not None and not df.empty:
                latest = df.iloc[0]
                return {
                    "total_revenue": latest.get('营业总收入'),
                    "net_profit": latest.get('净利润'),
                    "operating_profit": latest.get('营业利润')
                }
        except:
            pass
        return {}
    
    def _calculate_metrics(self, analysis: dict) -> dict:
        """计算核心指标"""
        metrics = {}
        
        indicators = analysis.get("financial_indicators", {})
        realtime = analysis.get("realtime", {})
        
        if indicators.get("roe"):
            metrics["ROE"] = indicators["roe"]
        if indicators.get("roa"):
            metrics["ROA"] = indicators["roa"]
        if realtime.get("pb"):
            metrics["PB"] = realtime["pb"]
        
        bs = analysis.get("balance_sheet", {})
        if bs.get("leverage"):
            metrics["杠杆率"] = bs["leverage"]
        
        return metrics


def main():
    parser = argparse.ArgumentParser(description="券商财务分析器")
    parser.add_argument("--securities", help="券商名称")
    parser.add_argument("--securities-list", help="多家券商逗号分隔")
    parser.add_argument("--action", choices=["analyze", "compare"], default="analyze")
    
    args = parser.parse_args()
    analyzer = SecuritiesFinancialAnalyzer()
    
    if args.action == "analyze" and args.securities:
        result = analyzer.analyze_securities(args.securities)
    elif args.action == "compare" and args.securities_list:
        result = analyzer.compare_securities(args.securities_list.split(","))
    else:
        result = {"error": "参数不足"}
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
