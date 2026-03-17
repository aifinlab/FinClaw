#!/usr/bin/env python3
"""
碳中和相关股票
查询碳中和概念股
"""

import akshare as ak
import pandas as pd

def get_carbon_stocks():
    """获取碳中和相关股票"""
    try:
        # 获取碳中和板块
        df = ak.stock_board_industry_name_ths()
        
        # 筛选碳中和相关
        carbon_keywords = ['碳', '新能源', '光伏', '风电', '储能', '环保']
        carbon_df = df[df['行业名称'].str.contains('|'.join(carbon_keywords), na=False)]
        
        if carbon_df.empty:
            print("暂无碳中和板块数据")
            return
        
        print("=" * 70)
        print("碳中和相关板块")
        print("=" * 70)
        
        for _, row in carbon_df.head(20).iterrows():
            print(f"{row['行业名称']}")
        
        print("=" * 70)
        
    except Exception as e:
        print(f"获取失败: {e}")

if __name__ == "__main__":
    get_carbon_stocks()
