#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
热点财经新闻 - AkShare
获取实时财经新闻
"""

import akshare as ak
import pandas as pd

def get_hot_news():
    """获取热点财经新闻"""
    try:
        df = ak.stock_news_em()
        return df
    except Exception as e:
        print(f"获取新闻失败: {e}")
        return None

def get_stock_news(stock="600519"):
    """获取个股新闻"""
    try:
        df = ak.stock_news_main_stock()
        return df
    except Exception as e:
        print(f"获取个股新闻失败: {e}")
        return None

def format_hot_news():
    """格式化热点新闻"""
    print("=" * 80)
    print("📰 热点财经新闻")
    print("=" * 80)
    
    df = get_hot_news()
    if df is not None and not df.empty:
        print("\n📢 最新财经资讯:")
        print("-" * 80)
        
        for i, row in df.head(20).iterrows():
            title = row.get('标题', 'N/A')
            source = row.get('来源', 'N/A')
            time = row.get('时间', 'N/A')
            
            print(f"\n🔸 {title}")
            print(f"   来源: {source} | 时间: {time}")
    else:
        print("未获取到新闻数据")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    format_hot_news()
