#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
关键词监控 - AkShare
监控财经新闻中的关键词
"""

import akshare as ak
import sys

def monitor_news(keyword="增持"):
    """监控新闻关键词"""
    try:
        df = ak.stock_news_em()
        
        # 过滤包含关键词的新闻
        filtered = df[df['标题'].str.contains(keyword, na=False, case=False)]
        return filtered
    except Exception as e:
        print(f"监控失败: {e}")
        return None

def format_monitor_report(keyword):
    """格式化监控报告"""
    print("=" * 80)
    print(f"🔍 关键词监控 | '{keyword}'")
    print("=" * 80)
    
    df = monitor_news(keyword)
    if df is not None and not df.empty:
        print(f"\n📢 找到 {len(df)} 条相关新闻:")
        print("-" * 80)
        
        for i, row in df.head(20).iterrows():
            title = row.get('标题', 'N/A')
            source = row.get('来源', 'N/A')
            time = row.get('时间', 'N/A')
            
            print(f"\n🔸 {title}")
            print(f"   来源: {source} | 时间: {time}")
    else:
        print(f"\n未找到包含 '{keyword}' 的新闻")
    
    print("\n" + "=" * 80)

def show_usage():
    """显示用法"""
    print("\n📋 用法:")
    print("   python news_monitor.py <关键词>")
    print("\n示例:")
    print("   python news_monitor.py 增持")
    print("   python news_monitor.py 回购")
    print("   python news_monitor.py 订单")
    print("   python news_monitor.py 预增")
    print("   python news_monitor.py 减持")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        keyword = sys.argv[1]
        format_monitor_report(keyword)
    else:
        format_monitor_report("增持")
        show_usage()
