#!/usr/bin/env python3
"""券商财务分析器 - 使用AkShare开源数据接口"""

import akshare as ak
import pandas as pd
import json
from datetime import datetime
import argparse


class SecuritiesFinancialAnalyzer:
    """券商财务分析器 - 使用AkShare获取实时行情和财务数据"""
    
    # 主要上市券商代码映射
    SECURITIES_CODES = {
        "中信证券": "600030", "华泰证券": "601688", "海通证券": "600837",
        "国泰君安": "601211", "招商证券": "600999", "广发证券": "000776",
        "中国银河": "601881", "中信建投": "601066", "东方证券": "600958",
        "兴业证券": "601377", "光大证券": "601788", "国信证券": "002736",
        "东方财富": "300059", "申万宏源": "000166", "中金公司": "601995",
        "浙商证券": "601878", "方正证券": "601901", "国金证券": "600109",
        "东吴证券": "601555", "财通证券": "601108", "长城证券": "002939",
        "国联证券": "601456", "南京证券": "601990", "红塔证券": "601236",
        "中银证券": "601696", "华安证券": "600909"
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
        """分析单家券商 - 使用AkShare实时数据"""
        code = self.get_securities_code(name)
        if not code:
            return {
                "error": f"未找到券商: {name}",
                "available_securities": list(self.SECURITIES_CODES.keys())[:20]
            }
        
        result = {
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "securities_name": name,
            "stock_code": code
        }
        
        # 获取实时行情
        realtime = self._get_realtime_data(code)
        
        if realtime:
            result["realtime_data"] = {
                "股价": realtime.get("price"),
                "涨跌幅": f"{realtime.get('change_pct')}%" if realtime.get('change_pct') else None,
                "市净率_PB": realtime.get("pb"),
                "市盈率_PE": realtime.get("pe"),
                "总市值_亿元": round(realtime.get("total_mv") / 1e8, 2) if realtime.get("total_mv") else None
            }
            
            # 业绩评价基于PB
            pb = realtime.get("pb")
            if pb:
                if pb > 1.5:
                    result["assessment"] = "估值溢价，市场认可度高"
                    result["rating"] = "优秀"
                elif pb > 1.0:
                    result["assessment"] = "估值合理"
                    result["rating"] = "良好"
                elif pb > 0.8:
                    result["assessment"] = "估值偏低，关注基本面"
                    result["rating"] = "中等"
                else:
                    result["assessment"] = "估值偏低，或存在经营压力"
                    result["rating"] = "关注"
            
            result["data_source"] = "AkShare - 东方财富"
            result["data_quality"] = "实时行情"
        else:
            result["error"] = "无法获取实时行情数据"
        
        # 尝试获取财务指标
        try:
            df_fin = ak.stock_financial_analysis_indicator(symbol=code)
            if df_fin is not None and not df_fin.empty:
                latest = df_fin.iloc[0]
                result["financial_indicators"] = {
                    "ROE": latest.get('净资产收益率', 'N/A'),
                    "ROA": latest.get('总资产报酬率', 'N/A'),
                    "净利率": latest.get('销售净利率', 'N/A')
                }
        except Exception:
            result["financial_note"] = "详细财务指标需从定期报告获取"
        
        return result
    
    def compare_securities(self, names: list = None) -> dict:
        """对比多家券商 - 使用AkShare实时数据"""
        if names is None:
            names = ["中信证券", "华泰证券", "国泰君安", "海通证券", "招商证券"]
        
        results = []
        for name in names:
            code = self.get_securities_code(name.strip())
            if not code:
                continue
            
            realtime = self._get_realtime_data(code)
            if realtime:
                results.append({
                    "name": name,
                    "code": code,
                    "price": realtime.get("price"),
                    "pb": realtime.get("pb"),
                    "pe": realtime.get("pe"),
                    "total_mv_yi": round(realtime.get("total_mv") / 1e8, 2) if realtime.get("total_mv") else None,
                    "change_pct": realtime.get("change_pct")
                })
        
        # 按PB排序
        results.sort(key=lambda x: x.get("pb") or 999)
        
        return {
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "comparison": results,
            "top_performer": results[0] if results else None,
            "total_securities": len(results),
            "data_source": "AkShare - 东方财富",
            "data_quality": "实时行情"
        }


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
        result = {
            "error": "参数不足",
            "usage": "--securities 中信证券 或 --securities-list '中信证券,华泰证券' --action compare",
            "available_securities": list(analyzer.SECURITIES_CODES.keys())[:10]
        }
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
