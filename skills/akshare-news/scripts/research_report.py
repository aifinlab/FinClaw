#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
券商研报查询 - AkShare
获取券商研究报告
"""

import akshare as ak
import sys

def get_research_report(stock="600519"):
    """获取券商研报"""
    try:
        df = ak.stock_research_report_em(symbol=stock)
        return df
    except Exception as e:
        print(f"获取研报失败: {e}")
        return None

def format_report(symbol):
    """格式化研报报告"""
    print("=" * 80)
    print(f"📑 券商研报 | {symbol}")
    print("=" * 80)
    
    df = get_research_report(symbol)
    if df is not None and not df.empty:
        print(f"\n📈 最新研报 ({len(df)}篇):")
        print("-" * 80)
        
        for i, row in df.head(10).iterrows():
            title = row.get('报告标题', 'N/A')
            org = row.get('机构名称', 'N/A')
            author = row.get('分析师', 'N/A')
            rating = row.get('投资评级', 'N/A')
            date = row.get('发布日期', 'N/A')
            
            print(f"\n🔸 {title}")
            print(f"   机构: {org} | 分析师: {author}")
            print(f"   评级: {rating} | 日期: {date}")
    else:
        print("未获取到研报数据")
    
    print("\n" + "=" * 80)

def show_usage():
    """显示用法"""
    print("\n📋 用法:")
    print("   python research_report.py <股票代码>")
    print("\n示例:")
    print("   python research_report.py 600519")
    print("   python research_report.py 300750")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        symbol = sys.argv[1]
        format_report(symbol)
    else:
        format_report("600519")
        show_usage()
