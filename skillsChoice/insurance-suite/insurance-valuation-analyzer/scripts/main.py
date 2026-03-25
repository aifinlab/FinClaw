#!/usr/bin/env python3
"""保险股估值分析器 - 使用AkShare开源数据接口"""

import akshare as ak
import pandas as pd
import json
from datetime import datetime
import argparse


class InsuranceValuationAnalyzer:
    """保险股估值分析器 - 使用AkShare获取实时行情"""
    
    # 保险公司名称到股票代码映射
    COMPANY_CODES = {
        "中国平安": "601318",
        "中国人寿": "601628",
        "中国太保": "601601",
        "新华保险": "601336",
        "中国人保": "601319"
    }
    
    def _get_realtime_quote(self, code: str) -> dict:
        """从AkShare获取实时行情"""
        try:
            df = ak.stock_zh_a_spot_em()
            stock_row = df[df['代码'] == code]
            
            if stock_row.empty:
                return None
            
            return {
                "price": float(stock_row['最新价'].values[0]) if '最新价' in stock_row.columns else None,
                "pb": float(stock_row['市净率'].values[0]) if '市净率' in stock_row.columns else None,
                "pe": float(stock_row['市盈率-动态'].values[0]) if '市盈率-动态' in stock_row.columns else None,
                "total_mv": float(stock_row['总市值'].values[0]) if '总市值' in stock_row.columns else None,
                "circ_mv": float(stock_row['流通市值'].values[0]) if '流通市值' in stock_row.columns else None
            }
        except Exception:
            return None
    
    def analyze_valuation(self, company: str = None) -> dict:
        """分析保险股估值 - 使用AkShare实时数据"""
        try:
            result = {
                "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "valuation_data": []
            }
            
            for name, code in self.COMPANY_CODES.items():
                if company and name != company:
                    continue
                
                realtime = self._get_realtime_quote(code)
                
                if realtime:
                    result["valuation_data"].append({
                        "company": name,
                        "code": code,
                        "price": realtime.get("price"),
                        "pb": realtime.get("pb"),
                        "pe": realtime.get("pe"),
                        "total_mv_yi": round(realtime.get("total_mv") / 1e8, 2) if realtime.get("total_mv") else None,
                        "data_source": "AkShare实时行情"
                    })
            
            if not result["valuation_data"]:
                result["error"] = "无法获取估值数据"
                return result
            
            # 估值判断
            result["valuation_assessment"] = self._assess_valuation(result["valuation_data"])
            result["data_source"] = "AkShare - 东方财富"
            result["data_quality"] = "实时行情"
            
            return result
            
        except Exception as e:
            return {
                "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "error": f"获取数据失败: {str(e)}"
            }
    
    def _assess_valuation(self, data: list) -> dict:
        """估值判断"""
        avg_pb = sum([d.get("pb", 0) for d in data if d.get("pb")]) / len(data) if data else 0
        
        if avg_pb < 0.8:
            return {
                "level": "历史低位",
                "description": "保险股整体估值处于历史低位，具备长期配置价值",
                "avg_pb": round(avg_pb, 2)
            }
        elif avg_pb < 1.0:
            return {
                "level": "偏低",
                "description": "保险股估值偏低，关注基本面改善",
                "avg_pb": round(avg_pb, 2)
            }
        else:
            return {
                "level": "合理",
                "description": "保险股估值处于合理区间",
                "avg_pb": round(avg_pb, 2)
            }
    
    def compare_all(self) -> dict:
        """对比所有保险股"""
        return self.analyze_valuation()


def main():
    parser = argparse.ArgumentParser(description="保险股估值分析器")
    parser.add_argument("--company", help="保险公司名称")
    parser.add_argument("--all", action="store_true", help="对比所有保险公司")
    
    args = parser.parse_args()
    analyzer = InsuranceValuationAnalyzer()
    
    if args.all or not args.company:
        result = analyzer.analyze_valuation()
    else:
        result = analyzer.analyze_valuation(args.company)
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
