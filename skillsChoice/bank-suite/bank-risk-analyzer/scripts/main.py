#!/usr/bin/env python3
"""银行风险分析器 - 使用AkShare开源数据接口"""

import akshare as ak
import pandas as pd
import json
from datetime import datetime
import argparse


class BankRiskAnalyzer:
    """银行风险分析器 - 使用AkShare获取真实财务数据"""
    
    # 银行名称到股票代码映射
    BANK_CODES = {
        "招商银行": "600036", "工商银行": "601398", "农业银行": "601288",
        "中国银行": "601988", "建设银行": "601939", "交通银行": "601328",
        "邮储银行": "601658", "兴业银行": "601166", "浦发银行": "600000",
        "中信银行": "601998", "民生银行": "600016", "光大银行": "601818",
        "平安银行": "000001", "华夏银行": "600015", "北京银行": "601169",
        "上海银行": "601229", "江苏银行": "600919", "南京银行": "601009",
        "宁波银行": "002142", "杭州银行": "600926"
    }
    
    def _get_financial_data(self, code: str) -> dict:
        """从AkShare获取银行财务数据"""
        try:
            # 获取个股指标数据（包含财务指标）
            df = ak.stock_zh_a_spot_em()
            stock_row = df[df['代码'] == code]
            
            if stock_row.empty:
                return None
            
            return {
                "pb": stock_row['市净率'].values[0] if '市净率' in stock_row.columns else None,
                "pe": stock_row['市盈率-动态'].values[0] if '市盈率-动态' in stock_row.columns else None,
                "price": stock_row['最新价'].values[0] if '最新价' in stock_row.columns else None
            }
        except Exception as e:
            return None
    
    def analyze_risk(self, bank_name: str) -> dict:
        """分析银行风险指标 - 使用AkShare实时数据"""
        code = self.BANK_CODES.get(bank_name)
        if not code:
            return {
                "error": f"未找到银行: {bank_name}",
                "available_banks": list(self.BANK_CODES.keys())
            }
        
        result = {
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "bank_name": bank_name,
            "stock_code": code
        }
        
        # 获取实时财务数据
        fin_data = self._get_financial_data(code)
        
        if fin_data:
            result["realtime_data"] = {
                "股价": fin_data.get("price"),
                "市净率_PB": fin_data.get("pb"),
                "市盈率_PE": fin_data.get("pe")
            }
        
        # 尝试获取更详细的财务指标
        try:
            # 获取主要指标
            df_indicator = ak.stock_financial_analysis_indicator(symbol=code)
            if df_indicator is not None and not df_indicator.empty:
                latest = df_indicator.iloc[0]
                result["financial_indicators"] = {
                    "不良贷款率": latest.get('不良贷款率', 'N/A'),
                    "拨备覆盖率": latest.get('拨备覆盖率', 'N/A'),
                    "资本充足率": latest.get('资本充足率', 'N/A'),
                    "核心一级资本充足率": latest.get('核心一级资本充足率', 'N/A')
                }
        except Exception:
            result["financial_indicators"] = {
                "note": "详细财务指标需从年报获取",
                "数据来源": "建议查阅银行定期报告"
            }
        
        result["data_source"] = "AkShare开源数据"
        result["data_quality"] = "实时行情+财务指标"
        
        return result
    
    def compare_risk(self, bank_names: list = None) -> dict:
        """对比多家银行风险"""
        if bank_names is None:
            bank_names = ["招商银行", "工商银行", "建设银行", "农业银行", "中国银行"]
        
        results = []
        for name in bank_names:
            code = self.BANK_CODES.get(name.strip())
            if not code:
                continue
            
            fin_data = self._get_financial_data(code)
            if fin_data:
                results.append({
                    "name": name.strip(),
                    "code": code,
                    "pb": fin_data.get("pb"),
                    "pe": fin_data.get("pe"),
                    "price": fin_data.get("price")
                })
        
        # 按PB排序
        results.sort(key=lambda x: x.get("pb") or 999)
        
        return {
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "comparison": results,
            "total_banks": len(results),
            "data_source": "AkShare开源数据",
            "data_quality": "实时行情"
        }


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
        result = {
            "error": "参数不足",
            "usage": "--bank 招商银行 或 --banks '招商银行,工商银行' --action compare",
            "available_banks": list(analyzer.BANK_CODES.keys())
        }
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
