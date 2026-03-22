#!/usr/bin/env python3
"""
商业银行财务分析器
深度分析上市银行的财务报表和核心指标
"""

import os
import sys
import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime
import json
import argparse

# 添加common目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'common'))
from finance_api import FinanceDataAPI, get_stock_code


class BankFinancialAnalyzer:
    """商业银行财务分析器"""
    
    # A股上市银行代码映射
    BANK_CODES = {
        "工商银行": "601398", "农业银行": "601288", "中国银行": "601988",
        "建设银行": "601939", "交通银行": "601328", "邮储银行": "601658",
        "招商银行": "600036", "兴业银行": "601166", "浦发银行": "600000",
        "中信银行": "601998", "民生银行": "600016", "光大银行": "601818",
        "平安银行": "000001", "华夏银行": "600015", "浙商银行": "601916",
        "北京银行": "601169", "上海银行": "601229", "江苏银行": "600919",
        "南京银行": "601009", "宁波银行": "002142", "杭州银行": "600926",
        "成都银行": "601838",
    }
    
    def __init__(self):
        self.api = FinanceDataAPI()
    
    def get_bank_code(self, bank_name: str) -> str:
        """根据银行名称获取股票代码"""
        if bank_name in self.BANK_CODES:
            return self.BANK_CODES[bank_name]
        
        for name, code in self.BANK_CODES.items():
            if bank_name in name or name in bank_name:
                return code
        
        return get_stock_code(bank_name)
    
    def analyze_bank(self, bank_name: str) -> dict:
        """深度分析单家银行"""
        code = self.get_bank_code(bank_name)
        if not code:
            return {"error": f"未找到银行: {bank_name}"}
        
        result = {
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "bank_name": bank_name,
            "stock_code": code,
            "analysis": {}
        }
        
        try:
            # 获取实时行情
            result["realtime"] = self._get_realtime_quote(code)
            
            # 获取财务指标
            result["financial_indicators"] = self._get_financial_indicators(code)
            
            # 综合评价
            result["assessment"] = self._assess_bank(result)
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def _get_realtime_quote(self, code: str) -> dict:
        """获取实时行情"""
        # 首先尝试统一API
        try:
            api_result = self.api.get_realtime_quote([code])
            if api_result and 'data' in api_result:
                data = api_result['data'].get(code, {})
                if data:
                    return {
                        "price": data.get('price'),
                        "change_pct": data.get('change_percent'),
                        "volume": data.get('volume'),
                        "pb": data.get('pb'),
                        "pe": data.get('pe'),
                        "data_source": data.get('data_source', 'API')
                    }
        except Exception as e:
            print(f"统一API获取失败: {e}")
        
        # 回退到AkShare
        try:
            df = ak.stock_zh_a_spot_em()
            stock = df[df['代码'] == code]
            if not stock.empty:
                s = stock.iloc[0]
                return {
                    "price": s.get('最新价'),
                    "change_pct": s.get('涨跌幅'),
                    "volume": s.get('成交量'),
                    "market_cap": s.get('总市值'),
                    "pb": s.get('市净率'),
                    "pe": s.get('市盈率'),
                    "data_source": "AkShare"
                }
        except Exception as e:
            print(f"AkShare获取失败: {e}")
            return {}
    
    def _get_financial_indicators(self, code: str) -> dict:
        """获取财务指标"""
        # 首先尝试统一API
        try:
            api_result = self.api.get_financial_data(code)
            if api_result:
                return {
                    "roe": api_result.get('roe'),
                    "roa": api_result.get('roa'),
                    "eps": api_result.get('eps'),
                    "bvps": api_result.get('bvps'),
                    "report_date": datetime.now().strftime("%Y-%m-%d"),
                    "data_source": api_result.get('data_source', 'API')
                }
        except Exception as e:
            print(f"统一API获取失败: {e}")
        
        # 回退到AkShare
        try:
            df = ak.stock_financial_analysis_indicator(symbol=code)
            if df is not None and not df.empty:
                latest = df.iloc[0]
                return {
                    "roe": latest.get('净资产收益率'),
                    "roa": latest.get('总资产收益率'),
                    "eps": latest.get('基本每股收益'),
                    "bvps": latest.get('每股净资产'),
                    "report_date": latest.get('报告期'),
                    "data_source": "AkShare"
                }
        except Exception as e:
            print(f"AkShare获取失败: {e}")
            return {}
    
    def _assess_bank(self, analysis: dict) -> dict:
        """综合评价银行"""
        assessment = {
            "rating": "",
            "strengths": [],
            "concerns": []
        }
        
        indicators = analysis.get("financial_indicators", {})
        realtime = analysis.get("realtime", {})
        
        # ROE评价
        roe = indicators.get("roe")
        if roe and roe != 'N/A':
            try:
                roe_val = float(str(roe).replace('%', ''))
                if roe_val >= 15:
                    assessment["strengths"].append("ROE优秀，盈利能力强")
                elif roe_val >= 10:
                    assessment["rating"] = "良好"
                else:
                    assessment["concerns"].append("ROE偏低，盈利能力待提升")
            except:
                pass
        
        # PB评价
        pb = realtime.get("pb")
        if pb:
            try:
                pb_val = float(pb)
                if pb_val < 0.8:
                    assessment["concerns"].append("PB低于0.8，可能存在估值折价")
            except:
                pass
        
        if not assessment["rating"]:
            assessment["rating"] = "中等"
        
        return assessment


def main():
    parser = argparse.ArgumentParser(description="商业银行财务分析器")
    parser.add_argument("--bank", help="银行名称")
    parser.add_argument("--action", choices=["analyze"], default="analyze", help="操作类型")
    
    args = parser.parse_args()
    analyzer = BankFinancialAnalyzer()
    
    if args.action == "analyze" and args.bank:
        result = analyzer.analyze_bank(args.bank)
    else:
        result = {"error": "参数不足，请检查输入"}
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
