#!/usr/bin/env python3
"""券商资管业务分析器 - 使用AkShare开源数据接口

功能：分析券商资管业务市场、上市券商表现
数据源：AkShare开源金融数据接口
说明：详细资管数据需参考中国证券投资基金业协会
"""

import akshare as ak
import json
from datetime import datetime
import argparse


class SecuritiesAMAnalyzer:
    """券商资管业务分析器 - 基于上市券商行情"""
    
    # 主要上市券商代码映射
    SECURITIES_CODES = {
        "中信证券": "600030", "华泰证券": "601688", "海通证券": "600837",
        "国泰君安": "601211", "招商证券": "600999", "广发证券": "000776",
        "中国银河": "601881", "中信建投": "601066", "东方证券": "600958",
        "兴业证券": "601377", "中金公司": "601995"
    }
    
    def __init__(self):
        self.query_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _get_realtime_data(self, code: str) -> dict:
        """获取实时行情 - 使用AkShare"""
        try:
            df = ak.stock_zh_a_spot_em()
            stock_row = df[df['代码'] == code]
            
            if stock_row.empty:
                return None
            
            return {
                "price": float(stock_row['最新价'].values[0]) if '最新价' in stock_row.columns else None,
                "change_pct": float(stock_row['涨跌幅'].values[0]) if '涨跌幅' in stock_row.columns else None,
                "pb": float(stock_row['市净率'].values[0]) if '市净率' in stock_row.columns else None,
                "total_mv": float(stock_row['总市值'].values[0]) if '总市值' in stock_row.columns else None
            }
        except Exception:
            return None
    
    def get_am_overview(self) -> dict:
        """获取资管业务概览 - 基于市场环境分析"""
        result = {
            "query_time": self.query_time,
            "analysis_type": "券商资管业务分析",
            "note": "详细资管数据需参考中国证券投资基金业协会"
        }
        
        # 获取主要券商行情
        securities = []
        for name, code in list(self.SECURITIES_CODES.items())[:8]:
            stock_data = self._get_realtime_data(code)
            if stock_data:
                securities.append({
                    "name": name,
                    "code": code,
                    "price": stock_data.get("price"),
                    "pb": stock_data.get("pb")
                })
        
        result["securities"] = securities
        
        result["am_analysis"] = {
            "业务类型": {
                "定向资管": "一对一专户业务",
                "集合资管": "一对多理财产品",
                "专项资管": "ABS等专项计划"
            },
            "行业趋势": [
                "资管新规后去通道化",
                "主动管理能力成为核心",
                "公募化转型加速",
                "财富管理协同发展"
            ],
            "关注要点": [
                "资管规模变化",
                "主动管理占比",
                "产品收益率表现",
                "费率水平"
            ],
            "数据来源说明": "详细数据参考中国证券投资基金业协会、各公司年报"
        }
        
        result["data_source"] = "AkShare开源数据 + 行业分析"
        result["data_quality"] = "实时行情 + 定性分析"
        
        return result
    
    def get_am_ranking(self) -> dict:
        """获取资管业务排名 - 基于券商市值排名"""
        result = {
            "query_time": self.query_time,
            "analysis_type": "券商资管业务分析",
            "note": "详细排名数据需参考中国证券投资基金业协会"
        }
        
        # 获取所有券商行情并按市值排序
        securities = []
        for name, code in self.SECURITIES_CODES.items():
            stock_data = self._get_realtime_data(code)
            if stock_data:
                securities.append({
                    "name": name,
                    "code": code,
                    "price": stock_data.get("price"),
                    "pb": stock_data.get("pb"),
                    "market_cap_yi": round(stock_data.get("total_mv") / 1e8, 2) if stock_data.get("total_mv") else None
                })
        
        securities.sort(key=lambda x: x.get("market_cap_yi") or 0, reverse=True)
        result["securities_by_market_cap"] = securities
        
        result["ranking_analysis"] = {
            "行业特点": [
                "头部券商资管优势明显",
                "主动管理能力分化",
                "公募牌照价值凸显",
                "财富管理协同效应"
            ],
            "竞争格局": "行业集中度较高，CR5约占50%",
            "关注要点": [
                "资管规模排名",
                "主动管理规模占比",
                "产品业绩表现",
                "费率竞争力"
            ],
            "数据来源说明": "详细排名参考中国证券投资基金业协会季度数据"
        }
        
        result["data_source"] = "AkShare开源数据 + 行业分析"
        result["data_quality"] = "实时行情 + 定性分析"
        
        return result


def main():
    parser = argparse.ArgumentParser(description="券商资管业务分析器")
    parser.add_argument("--overview", action="store_true", help="资管概览")
    parser.add_argument("--ranking", action="store_true", help="资管排名")
    
    args = parser.parse_args()
    analyzer = SecuritiesAMAnalyzer()
    
    if args.ranking:
        result = analyzer.get_am_ranking()
    else:
        result = analyzer.get_am_overview()
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
