#!/usr/bin/env python3
"""证券行业宏观分析器 - 使用AkShare开源数据接口"""

import akshare as ak
import pandas as pd
import json
from datetime import datetime
import argparse


class SecuritiesIndustryAnalyzer:
    """证券行业宏观分析器 - 使用AkShare获取实时数据"""
    
    # 主要券商股票代码
    TOP_SECURITIES = {
        '600030': '中信证券', '601688': '华泰证券', '600837': '海通证券',
        '601211': '国泰君安', '600999': '招商证券', '000776': '广发证券',
        '601881': '中国银河', '601066': '中信建投', '600958': '东方证券',
        '601377': '兴业证券', '601108': '财通证券', '002736': '国信证券',
        '601878': '浙商证券', '600109': '国金证券', '601990': '南京证券'
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
                "total_mv": float(stock_row['总市值'].values[0]) if '总市值' in stock_row.columns else None
            }
        except Exception:
            return None
    
    def get_industry_overview(self) -> dict:
        """获取证券行业概览 - 使用AkShare实时数据"""
        result = {
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data_type": "证券行业概览"
        }
        
        # 获取主要券商实时行情
        securities_data = []
        for code, name in list(self.TOP_SECURITIES.items())[:10]:
            data = self._get_realtime_data(code)
            if data:
                securities_data.append({
                    "name": name,
                    "code": code,
                    "price": data.get("price"),
                    "pb": data.get("pb"),
                    "pe": data.get("pe"),
                    "total_mv_yi": round(data.get("total_mv") / 1e8, 2) if data.get("total_mv") else None
                })
        
        if securities_data:
            # 计算行业平均估值
            valid_pb = [s["pb"] for s in securities_data if s.get("pb")]
            valid_pe = [s["pe"] for s in securities_data if s.get("pe")]
            
            result["realtime_indicators"] = {
                "样本券商数": len(securities_data),
                "平均PB": round(sum(valid_pb) / len(valid_pb), 2) if valid_pb else None,
                "平均PE": round(sum(valid_pe) / len(valid_pe), 2) if valid_pe else None,
                "总市值合计_亿元": sum([s.get("total_mv_yi", 0) or 0 for s in securities_data])
            }
            result["top_securities"] = securities_data
        
        result["data_source"] = "AkShare - 东方财富"
        result["data_quality"] = "实时行情"
        
        return result
    
    def get_concentration_analysis(self) -> dict:
        """分析行业集中度 - 使用AkShare实时数据"""
        securities_list = []
        
        for code, name in self.TOP_SECURITIES.items():
            data = self._get_realtime_data(code)
            if data and data.get("total_mv"):
                securities_list.append({
                    'name': name,
                    'code': code,
                    'market_cap': data.get("total_mv"),
                    'pb': data.get("pb"),
                    'pe': data.get("pe")
                })
        
        if not securities_list:
            return {
                "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "error": "无法获取市值数据"
            }
        
        securities_list.sort(key=lambda x: x['market_cap'], reverse=True)
        
        # 计算集中度
        total_cap = sum([s['market_cap'] for s in securities_list])
        cr5_cap = sum([s['market_cap'] for s in securities_list[:5]])
        cr10_cap = sum([s['market_cap'] for s in securities_list[:10]])
        
        cr5_pct = cr5_cap/total_cap*100 if total_cap else 0
        
        return {
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "top_securities": securities_list[:10],
            "concentration": {
                "CR5": f"{cr5_pct:.1f}%",
                "CR10": f"{cr10_cap/total_cap*100:.1f}%" if total_cap else "N/A"
            },
            "assessment": "头部高度集中" if cr5_pct > 50 else "头部集中" if cr5_pct > 40 else "竞争分散",
            "data_source": "AkShare - 东方财富",
            "data_quality": "实时市值数据"
        }
    
    def get_policy_impact(self) -> dict:
        """分析政策影响"""
        return {
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "message": "政策数据需从证监会、交易所公告获取",
            "data_source": "需外部数据源",
            "note": "AkShare暂无政策数据接口，建议关注官方公告"
        }


def main():
    parser = argparse.ArgumentParser(description="证券行业宏观分析器")
    parser.add_argument("--action", choices=["overview", "concentration", "policy"],
                       default="overview")
    
    args = parser.parse_args()
    analyzer = SecuritiesIndustryAnalyzer()
    
    if args.action == "overview":
        result = analyzer.get_industry_overview()
    elif args.action == "concentration":
        result = analyzer.get_concentration_analysis()
    elif args.action == "policy":
        result = analyzer.get_policy_impact()
    else:
        result = {"error": "未知操作"}
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
