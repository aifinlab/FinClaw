#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
可转债数据 - AkShare
"""

import akshare as ak

def get_convertible_bond():
    """获取可转债数据"""
    try:
        df = ak.bond_zh_cov()
        return df
    except Exception as e:
        print(f"获取可转债失败: {e}")
        return None

def format_bond():
    """格式化债券数据"""
    print("=" * 80)
    print("📊 可转债数据")
    print("=" * 80)
    
    df = get_convertible_bond()
    if df is not None and not df.empty:
        print(df.head(20).to_string(index=False))
    else:
        print("未获取到数据")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    format_bond()
