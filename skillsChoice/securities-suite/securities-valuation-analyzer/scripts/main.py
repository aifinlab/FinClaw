#!/usr/bin/env python3
"""券商股估值分析器 - 使用AkShare开源数据接口"""

import akshare as ak
import pandas as pd
import json
from datetime import datetime
import argparse


class SecuritiesValuationAnalyzer:
    """券商股估值分析器 - 使用AkShare获取实时行情"""
    
    SECURITIES_CODES = {
        "中信证券": "600030", "华泰证券": "601688", "海通证券": "600837",
        "国泰君安": "601211", "招商证券": "600999", "广发证券": "000776",
        "中国银河": "601881", "中信建投": "601066", "东方证券": "600958",
        "兴业证券": "601377", "东方财富": "300059", "申万宏源": "000166",
        "中金公司": "601995", "光大证券": "601788", "国信证券": "002736"
    }
    
    def _get_realtime_data(self, code: str) -> dict:
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
                "change_pct": float(stock_row['涨跌幅'].values[0]) if '涨跌幅' in stock_row.columns else None
            }
        except Exception:
            return None
    
    def analyze_valuation(self, name: str) -> dict:
        """分析券商估值 - 使用AkShare实时数据"""
        code = self.SECURITIES_CODES.get(name)
        if not code:
            return {
                "error": f"未找到券商: {name}",
                "available_securities": list(self.SECURITIES_CODES.keys())
            }
        
        result = {
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "securities_name": name,
            "stock_code": code
        }
        
        # 获取实时行情
        realtime = self._get_realtime_data(code)
        
        if realtime:
            result["valuation"] = {
                "股价": realtime.get("price"),
                "涨跌幅": f"{realtime.get('change_pct')}%" if realtime.get('change_pct') else None,
                "PB": realtime.get("pb"),
                "PE_TTM": realtime.get("pe"),
                "总市值_亿元": round(realtime.get("total_mv") / 1e8, 2) if realtime.get("total_mv") else None
            }
            
            # 估值评估
            pb = realtime.get("pb")
            result["assessment"] = self._assess_valuation(pb)
            
            result["data_source"] = "AkShare - 东方财富"
            result["data_quality"] = "实时行情"
        else:
            result["error"] = "无法获取实时行情数据"
        
        return result
    
    def compare_valuation(self) -> dict:
        """对比券商估值 - 使用AkShare实时数据"""
        results = []
        
        for name, code in self.SECURITIES_CODES.items():
            realtime = self._get_realtime_data(code)
            if realtime:
                results.append({
                    "name": name,
                    "code": code,
                    "price": realtime.get("price"),
                    "pb": realtime.get("pb"),
                    "pe": realtime.get("pe"),
                    "total_mv_yi": round(realtime.get("total_mv") / 1e8, 2) if realtime.get("total_mv") else None,
                    "change_pct": realtime.get("change_pct"),
                    "assessment": self._assess_valuation(realtime.get("pb"))
                })
        
        # 按PB排序
        results.sort(key=lambda x: x.get("pb") or 999)
        
        return {
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "valuation_ranking": results,
            "cheapest": results[0] if results else None,
            "most_expensive": results[-1] if results else None,
            "total_securities": len(results),
            "data_source": "AkShare - 东方财富",
            "data_quality": "实时行情"
        }
    
    def _assess_valuation(self, pb) -> str:
        """估值评估"""
        try:
            pb_val = float(pb) if pb else 0
            if pb_val < 1.0:
                return "深度破净，估值修复空间大"
            elif pb_val < 1.3:
                return "破净，关注基本面改善"
            elif pb_val > 2.0:
                return "估值溢价，质地优秀或成长性高"
            else:
                return "估值合理"
        except:
            return "数据不足"


def main():
    parser = argparse.ArgumentParser(description="券商股估值分析器")
    parser.add_argument("--securities", help="券商名称")
    parser.add_argument("--compare", action="store_true", help="对比估值")
    
    args = parser.parse_args()
    analyzer = SecuritiesValuationAnalyzer()
    
    if args.compare:
        result = analyzer.compare_valuation()
    elif args.securities:
        result = analyzer.analyze_valuation(args.securities)
    else:
        result = {
            "error": "请指定参数",
            "usage": "--securities 中信证券 或 --compare",
            "available_securities": list(analyzer.SECURITIES_CODES.keys())
        }
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
