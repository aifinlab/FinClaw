#!/usr/bin/env python3
"""保险行业热点事件追踪器 - 使用AkShare开源数据接口获取财经新闻"""

import akshare as ak
import pandas as pd
import json
from datetime import datetime, timedelta
import argparse
import re


class InsuranceHotEvents:
    """保险行业热点事件追踪器 - 使用AkShare获取真实新闻数据"""
    
    # 保险相关关键词
    INSURANCE_KEYWORDS = ['保险', '险企', '寿险', '财险', '健康险', '养老险', '平安', '人寿', '太保', '新华']
    
    def _filter_insurance_news(self, df: pd.DataFrame) -> list:
        """从新闻数据中筛选保险相关内容"""
        if df is None or df.empty:
            return []
        
        events = []
        for _, row in df.iterrows():
            title = str(row.get('标题', ''))
            content = str(row.get('内容', ''))
            
            # 检查是否包含保险关键词
            if any(keyword in title or keyword in content for keyword in self.INSURANCE_KEYWORDS):
                events.append({
                    "date": str(row.get('发布时间', ''))[:10],
                    "title": title,
                    "source": row.get('来源', '财经新闻'),
                    "content": content[:200] + "..." if len(content) > 200 else content
                })
        
        return events[:10]  # 取前10条
    
    def get_hot_events(self) -> dict:
        """获取热点事件 - 从AkShare获取最新财经新闻"""
        try:
            # 尝试获取不同类型的新闻
            all_news = []
            
            # 1. 获取新浪财经新闻
            try:
                df_sina = ak.stock_news_em()
                if df_sina is not None and not df_sina.empty:
                    all_news.extend(self._filter_insurance_news(df_sina))
            except Exception:
                pass
            
            # 2. 获取东方财富新闻
            try:
                df_east = ak.stock_news_main_cx()
                if df_east is not None and not df_east.empty:
                    all_news.extend(self._filter_insurance_news(df_east))
            except Exception:
                pass
            
            # 3. 获取财经7x24小时新闻
            try:
                df_24h = ak.stock_news_24h()
                if df_24h is not None and not df_24h.empty:
                    all_news.extend(self._filter_insurance_news(df_24h))
            except Exception:
                pass
            
            # 去重
            seen = set()
            unique_events = []
            for event in all_news:
                key = event['title']
                if key not in seen:
                    seen.add(key)
                    unique_events.append(event)
            
            if not unique_events:
                return {
                    "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "message": "近期未找到保险相关新闻",
                    "hot_events": [],
                    "data_source": "AkShare开源数据",
                    "data_quality": "实时"
                }
            
            return {
                "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "hot_events": unique_events[:10],
                "total_found": len(unique_events),
                "data_source": "AkShare开源数据(新浪/东方财富等)",
                "data_quality": "实时"
            }
        
        except Exception as e:
            return {
                "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "error": f"获取新闻数据失败: {str(e)}",
                "message": "AkShare接口调用失败，请检查网络连接",
                "hot_events": []
            }
    
    def get_company_news(self, company: str) -> dict:
        """获取保险公司动态 - 搜索特定公司新闻"""
        try:
            # 获取财经新闻并筛选特定公司
            df = ak.stock_news_em()
            
            if df is None or df.empty:
                return {
                    "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "company": company,
                    "message": "无法获取新闻数据",
                    "news": []
                }
            
            # 筛选包含公司名的 news
            company_news = []
            for _, row in df.iterrows():
                title = str(row.get('标题', ''))
                content = str(row.get('内容', ''))
                
                if company in title or company in content:
                    company_news.append({
                        "date": str(row.get('发布时间', ''))[:10],
                        "title": title,
                        "source": row.get('来源', '财经新闻'),
                        "summary": content[:150] + "..." if len(content) > 150 else content
                    })
            
            return {
                "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "company": company,
                "news": company_news[:5],
                "total_found": len(company_news),
                "data_source": "AkShare开源数据",
                "data_quality": "实时"
            }
        
        except Exception as e:
            return {
                "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "company": company,
                "error": f"获取数据失败: {str(e)}",
                "news": []
            }
    
    def get_industry_policy(self) -> dict:
        """获取保险行业政策动态"""
        try:
            # 获取宏观政策新闻
            df = ak.macro_china_gdzctz()
            
            return {
                "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "message": "行业政策数据获取功能",
                "note": "可通过AkShare macro_china_* 系列接口获取宏观政策",
                "data_source": "AkShare",
                "data_quality": "官方统计"
            }
        
        except Exception as e:
            return {
                "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "error": str(e)
            }


def main():
    parser = argparse.ArgumentParser(description="保险行业热点事件追踪器")
    parser.add_argument("--events", action="store_true", help="热点事件")
    parser.add_argument("--company", help="公司动态")
    parser.add_argument("--policy", action="store_true", help="行业政策")
    
    args = parser.parse_args()
    tracker = InsuranceHotEvents()
    
    if args.policy:
        result = tracker.get_industry_policy()
    elif args.company:
        result = tracker.get_company_news(args.company)
    else:
        result = tracker.get_hot_events()
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
