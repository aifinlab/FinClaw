#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
行业分类数据 - AkShare
"""

import akshare as ak

def get_industry_list():
    """获取行业列表"""
    try:
        df = ak.stock_board_industry_name_em()
        return df
    except Exception as e:
        print(f"获取行业列表失败: {e}")
        return None

def format_industry_list():
    """格式化行业列表"""
    print("=" * 80)
    print("🏭 申万行业分类")
    print("=" * 80)
    
    df = get_industry_list()
    if df is not None and not df.empty:
        print(df.to_string(index=False))
    else:
        print("未获取到数据")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    format_industry_list()
