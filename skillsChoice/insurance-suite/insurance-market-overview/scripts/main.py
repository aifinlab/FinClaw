#!/usr/bin/env python3
"""保险市场概览分析器 - 使用AkShare开源数据接口

功能：获取中国保险行业整体数据、上市险企市场表现
数据源：AkShare开源金融数据接口
"""

import akshare as ak
import json
from datetime import datetime
import argparse


class InsuranceMarketOverview:
    """保险市场概览分析器 - 基于上市险企数据"""
    
    # 主要上市保险公司代码映射
    COMPANIES = {
        "中国平安": "601318",
        "中国人寿": "601628",
        "中国太保": "601601",
        "新华保险": "601336",
        "中国人保": "601319"
    }
    
    def __init__(self):
        self.query_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _get_stock_data(self, code: str) -> dict:
        """获取股票实时数据 - 使用AkShare"""
        try:
            df = ak.stock_zh_a_spot_em()
            stock_row = df[df['代码'] == code]
            
            if stock_row.empty:
                return None
            
            return {
                "price": float(stock_row['最新价'].values[0]) if '最新价' in stock_row.columns else None,
                "change_pct": float(stock_row['涨跌幅'].values[0]) if '涨跌幅' in stock_row.columns else None,
                "pb": float(stock_row['市净率'].values[0]) if '市净率' in stock_row.columns else None,
                "pe": float(stock_row['市盈率-动态'].values[0]) if '市盈率-动态' in stock_row.columns else None,
                "total_mv": float(stock_row['总市值'].values[0]) if '总市值' in stock_row.columns else None
            }
        except Exception:
            return None
    
    def get_industry_overview(self) -> dict:
        """获取保险行业概览 - 基于上市险企市场表现"""
        result = {
            "query_time": self.query_time,
            "analysis_type": "保险行业市场表现概览",
            "note": "行业保费数据需参考金融监管总局公告"
        }
        
        companies = []
        total_mv = 0
        
        for name, code in self.COMPANIES.items():
            stock_data = self._get_stock_data(code)
            if stock_data:
                mv = stock_data.get("total_mv", 0) or 0
                total_mv += mv
                companies.append({
                    "company": name,
                    "code": code,
                    "price": stock_data.get("price"),
                    "change_pct": f"{stock_data.get('change_pct')}%" if stock_data.get('change_pct') else None,
                    "pb": stock_data.get("pb"),
                    "pe": stock_data.get("pe"),
                    "market_cap_yi": round(mv / 1e8, 2) if mv else None
                })
        
        companies.sort(key=lambda x: x.get("market_cap_yi") or 0, reverse=True)
        result["listed_companies"] = companies
        result["total_market_cap_yi"] = round(total_mv / 1e8, 2) if total_mv else None
        
        # 计算行业平均估值
        valid_pb = [c["pb"] for c in companies if c.get("pb")]
        if valid_pb:
            result["industry_avg_pb"] = round(sum(valid_pb) / len(valid_pb), 2)
        
        result["industry_trends"] = [
            "人身险业务逐步复苏",
            "财产险非车险增长迅速",
            "健康险保持较快增长",
            "保险资金运用收益率承压"
        ]
        
        result["data_source"] = "AkShare - 东方财富"
        result["data_quality"] = "实时行情数据"
        
        return result
    
    def get_structure_analysis(self) -> dict:
        """获取保险业务结构分析 - 基于行业趋势"""
        result = {
            "query_time": self.query_time,
            "analysis_type": "保险业务结构分析",
            "note": "详细结构数据需参考行业统计报告"
        }
        
        # 获取上市险企数据作为参考
        companies = []
        for name, code in self.COMPANIES.items():
            stock_data = self._get_stock_data(code)
            if stock_data:
                companies.append({
                    "company": name,
                    "code": code,
                    "change_pct": stock_data.get("change_pct")
                })
        
        result["companies_performance"] = companies
        
        result["business_structure_analysis"] = {
            "人身险": {
                "description": "寿险、健康险、意外险",
                "trend": "寿险转型深化，健康险快速增长"
            },
            "财产险": {
                "description": "车险、非车险",
                "trend": "车险综改深化，非车险占比提升"
            },
            "关注要点": [
                "各险种保费增速",
                "新业务价值(NBV)变化",
                "综合成本率走势",
                "代理人队伍质态"
            ],
            "数据来源说明": "业务结构数据参考国家金融监督管理总局公告"
        }
        
        result["data_source"] = "AkShare实时行情 + 行业分析"
        result["data_quality"] = "实时市场数据 + 定性分析"
        
        return result


def main():
    parser = argparse.ArgumentParser(description="保险市场概览分析器")
    parser.add_argument("--overview", action="store_true", help="行业概览")
    parser.add_argument("--structure", action="store_true", help="业务结构")
    
    args = parser.parse_args()
    analyzer = InsuranceMarketOverview()
    
    if args.structure:
        result = analyzer.get_structure_analysis()
    else:
        result = analyzer.get_industry_overview()
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
