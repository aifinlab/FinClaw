#!/usr/bin/env python3
"""
微博财经热搜
查询微博财经热搜榜
"""

import akshare as ak
import pandas as pd

def get_weibo_hot():
    """获取微博热搜"""
    try:
        df = ak.weibo_hot_search()
        
        if df.empty:
            print("暂无数据")
            return
        
        print("=" * 90)
        print("微博热搜榜")
        print("=" * 90)
        
        # 筛选财经相关
        keywords = ['股', '基金', 'A股', '涨停', '跌', '涨', '币', '期货', '债']
        finance_df = df[df['标题'].str.contains('|'.join(keywords), na=False)]
        
        if finance_df.empty:
            finance_df = df.head(20)
        
        for i, (_, row) in enumerate(finance_df.head(20).iterrows(), 1):
            print(f"{i}. {row['标题']} ({row.get('热度', '--')})")
        
        print("=" * 90)
        
    except Exception as e:
        print(f"获取失败: {e}")

if __name__ == "__main__":
    get_weibo_hot()
