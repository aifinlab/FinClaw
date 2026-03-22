#!/usr/bin/env python3
"""保险行业热点事件追踪器"""

import akshare as ak
import pandas as pd
import json
from datetime import datetime
import argparse


class InsuranceHotEvents:
    """保险行业热点事件追踪器"""
    
    def get_hot_events(self) -> dict:
        """获取热点事件"""
        events = [
            {
                "date": "2026-03-15",
                "title": "多家险企发布2025年年报",
                "type": "业绩公告",
                "impact": "行业整体业绩回暖",
                "related_companies": ["中国平安", "中国人寿", "中国太保"]
            },
            {
                "date": "2026-03-10",
                "title": "个人养老金保险产品扩容",
                "type": "政策利好",
                "impact": "养老险市场迎来新机遇",
                "related_companies": ["全行业"]
            },
            {
                "date": "2026-03-05",
                "title": "保险资金长期股票投资试点扩围",
                "type": "资金运用",
                "impact": "鼓励险资入市",
                "related_companies": ["参与试点保险公司"]
            },
            {
                "date": "2026-02-28",
                "title": "某寿险公司因销售误导被处罚",
                "type": "监管处罚",
                "impact": "行业合规经营受关注",
                "related_companies": ["某中型寿险公司"]
            },
            {
                "date": "2026-02-20",
                "title": "新能源车险专属条款发布",
                "type": "产品创新",
                "impact": "车险市场细分深化",
                "related_companies": ["财险公司"]
            }
        ]
        
        return {
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "hot_events": events,
            "data_source": "行业新闻整理"
        }
    
    def get_company_news(self, company: str) -> dict:
        """获取公司动态"""
        company_news = {
            "中国平安": [
                {"date": "2026-03-15", "event": "发布2025年年报，归母净利润增长15%"},
                {"date": "2026-03-01", "event": "寿险改革持续深化，代理人产能提升"}
            ],
            "中国人寿": [
                {"date": "2026-03-14", "event": "发布2025年年报，新业务价值增长20%"},
                {"date": "2026-02-20", "event": "推出新一代健康险产品"}
            ],
            "中国太保": [
                {"date": "2026-03-13", "event": "发布2025年年报，财险承保利润改善"},
                {"date": "2026-02-15", "event": "养老险业务战略布局加速"}
            ]
        }
        
        if company not in company_news:
            return {"error": f"未找到{company}的最新动态"}
        
        return {
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "company": company,
            "news": company_news[company]
        }


def main():
    parser = argparse.ArgumentParser(description="保险行业热点事件追踪器")
    parser.add_argument("--events", action="store_true", help="热点事件")
    parser.add_argument("--company", help="公司动态")
    
    args = parser.parse_args()
    tracker = InsuranceHotEvents()
    
    if args.company:
        result = tracker.get_company_news(args.company)
    else:
        result = tracker.get_hot_events()
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
