#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
汇率数据获取 - AkShare
"""

import akshare as ak

def get_forex_quote():
    """获取汇率行情"""
    try:
        df = ak.fx_quote_baidu()
        return df
    except Exception as e:
        print(f"获取汇率失败: {e}")
        return None

def format_forex():
    """格式化汇率"""
    print("=" * 80)
    print("💱 全球汇率行情")
    print("=" * 80)
    
    df = get_forex_quote()
    if df is not None and not df.empty:
        print(df.to_string(index=False))
    else:
        print("未获取到数据")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    format_forex()
