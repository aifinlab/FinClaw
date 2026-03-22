#!/usr/bin/env python3
"""
证券行业宏观分析器
获取证券行业整体运行数据
"""

import akshare as ak
import pandas as pd
import json
from datetime import datetime
import argparse


class SecuritiesIndustryAnalyzer:
    """证券行业宏观分析器"""
    
    def get_industry_overview(self) -> dict:
        """获取证券行业概览"""
        result = {
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data_type": "证券行业概览",
            "indicators": {}
        }
        
        try:
            # 获取券商行情数据（通过AkShare）
            df = ak.stock_zh_a_spot_em()
            
            # 筛选券商股
            securities_keywords = ['证券', '券商', '中信', '建投', '华泰', '海通', '国泰君安', '招商', '广发', '银河']
            mask = df['名称'].str.contains('|'.join(securities_keywords), na=False)
            securities_df = df[mask]
            
            if not securities_df.empty:
                result["indicators"]["上市券商数量"] = len(securities_df)
                result["indicators"]["总市值"] = f"{securities_df['总市值'].sum() / 1e8:.2f}亿元"
                result["indicators"]["平均PE"] = f"{securities_df['市盈率-动态'].mean():.2f}"
                result["indicators"]["平均PB"] = f"{securities_df['市净率'].mean():.2f}"
                
                # 今日表现
            result["indicators"]["平均涨跌幅"] = f"{securities_df['涨跌幅'].mean():.2f}%"
                
            result["data_source"] = "AkShare - 沪深A股实时行情"
            result["note"] = "数据基于上市券商股票行情"
            
        except Exception as e:
            result["error"] = str(e)
            result["suggestion"] = "请检查网络连接"
        
        return result
    
    def get_concentration_analysis(self) -> dict:
        """分析行业集中度"""
        try:
            df = ak.stock_zh_a_spot_em()
            
            # 主要券商代码映射
            top_securities = {
                '600030': '中信证券', '601688': '华泰证券', '600837': '海通证券',
                '601211': '国泰君安', '600999': '招商证券', '000776': '广发证券',
                '601881': '中国银河', '601066': '中信建投', '600958': '东方证券',
                '601377': '兴业证券'
            }
            
            securities_list = []
            for code, name in top_securities.items():
                stock = df[df['代码'] == code]
                if not stock.empty:
                    securities_list.append({
                        'name': name,
                        'code': code,
                        'market_cap': stock.iloc[0]['总市值'],
                        'pb': stock.iloc[0]['市净率']
                    })
            
            securities_list.sort(key=lambda x: x['market_cap'], reverse=True)
            
            # 计算集中度
            total_cap = sum([s['market_cap'] for s in securities_list])
            cr5_cap = sum([s['market_cap'] for s in securities_list[:5]])
            cr10_cap = sum([s['market_cap'] for s in securities_list[:10]])
            
            return {
                "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "top_securities": securities_list[:10],
                "concentration": {
                    "CR5": f"{cr5_cap/total_cap*100:.1f}%" if total_cap else "N/A",
                    "CR10": f"{cr10_cap/total_cap*100:.1f}%" if total_cap else "N/A"
                },
                "assessment": "头部集中" if cr5_cap/total_cap > 0.5 else "竞争分散"
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_policy_impact(self) -> dict:
        """分析政策影响"""
        return {
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "recent_policies": [
                {
                    "policy": "全面注册制改革",
                    "impact": "利好投行收入",
                    "status": "已实施"
                },
                {
                    "policy": "科创板做市商制度",
                    "impact": "增加自营业务机会",
                    "status": "实施中"
                },
                {
                    "policy": "两融标的扩容",
                    "impact": "利好信用业务收入",
                    "status": "已实施"
                }
            ],
            "data_source": "证监会公告整理"
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
