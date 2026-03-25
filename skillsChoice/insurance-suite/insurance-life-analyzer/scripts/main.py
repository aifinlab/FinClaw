#!/usr/bin/env python3
"""寿险业务分析器 - 使用AkShare开源数据接口

功能：分析寿险股市场表现、保险公司估值
数据源：AkShare开源金融数据接口
"""

import akshare as ak
import json
from datetime import datetime
import argparse


class InsuranceLifeAnalyzer:
    """寿险业务分析器 - 使用AkShare获取上市险企数据"""
    
    # 主要寿险公司代码映射
    LIFE_INSURANCE_CODES = {
        "中国人寿": "601628",
        "中国平安": "601318",
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
    
    def analyze_life_market(self) -> dict:
        """分析寿险股市场表现"""
        result = {
            "query_time": self.query_time,
            "analysis_type": "上市寿险公司市场表现",
            "companies": []
        }
        
        for name, code in self.LIFE_INSURANCE_CODES.items():
            stock_data = self._get_stock_data(code)
            if stock_data:
                result["companies"].append({
                    "company": name,
                    "code": code,
                    "price": stock_data.get("price"),
                    "change_pct": f"{stock_data.get('change_pct')}%" if stock_data.get('change_pct') else None,
                    "pb": stock_data.get("pb"),
                    "pe": stock_data.get("pe"),
                    "market_cap_yi": round(stock_data.get("total_mv") / 1e8, 2) if stock_data.get("total_mv") else None
                })
        
        # 按市值排序
        result["companies"].sort(key=lambda x: x.get("market_cap_yi") or 0, reverse=True)
        
        # 计算行业平均估值
        valid_pb = [c["pb"] for c in result["companies"] if c.get("pb")]
        if valid_pb:
            result["industry_avg_pb"] = round(sum(valid_pb) / len(valid_pb), 2)
        
        result["market_analysis"] = {
            "整体评价": "寿险股估值处于历史低位，具备配置价值",
            "关注要点": [
                "NBV增速回暖情况",
                "代理人队伍质态改善",
                "利率环境对利差的冲击",
                "产品结构调整进展"
            ]
        }
        
        result["data_source"] = "AkShare - 东方财富"
        result["data_quality"] = "实时行情数据"
        
        return result
    
    def analyze_agent_channel(self) -> dict:
        """分析代理人渠道 - 基于上市险企数据推断"""
        result = {
            "query_time": self.query_time,
            "analysis_type": "代理人渠道分析",
            "note": "代理人数据需参考各公司定期报告披露"
        }
        
        # 获取上市险企行情作为参考
        companies_data = []
        for name, code in self.LIFE_INSURANCE_CODES.items():
            stock_data = self._get_stock_data(code)
            if stock_data:
                companies_data.append({
                    "company": name,
                    "code": code,
                    "price": stock_data.get("price"),
                    "change_pct": stock_data.get("change_pct")
                })
        
        result["companies"] = companies_data
        
        result["channel_analysis"] = {
            "行业趋势": [
                "代理人队伍规模趋于稳定",
                "人均产能提升成为重点",
                "绩优人力占比持续优化",
                "数字化赋能代理人展业"
            ],
            "渠道建议": [
                "关注各公司代理人数据披露",
                "分析人均产能变化趋势",
                "评估队伍质态改善成效",
                "跟踪MDRT等绩优人力占比"
            ],
            "数据来源说明": "代理人详细数据需查阅各公司年报/季报"
        }
        
        result["data_source"] = "AkShare实时行情 + 行业分析"
        result["data_quality"] = "实时市场数据 + 定性分析"
        
        return result


def main():
    parser = argparse.ArgumentParser(description="寿险业务分析器")
    parser.add_argument("--market", action="store_true", help="寿险市场分析")
    parser.add_argument("--agent", action="store_true", help="代理人渠道分析")
    
    args = parser.parse_args()
    analyzer = InsuranceLifeAnalyzer()
    
    if args.agent:
        result = analyzer.analyze_agent_channel()
    else:
        result = analyzer.analyze_life_market()
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
