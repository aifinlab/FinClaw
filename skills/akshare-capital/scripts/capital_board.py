#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
板块资金流向 - AkShare
"""

import akshare as ak

def get_sector_capital():
    """获取板块资金流向"""
    try:
        df = ak.stock_sector_fund_flow_rank()
        return df
    except Exception as e:
        print(f"获取板块资金失败: {e}")
        return None

def format_sector_capital():
    """格式化板块资金"""
    print("=" * 80)
    print("💰 板块资金流向排行")
    print("=" * 80)
    
    df = get_sector_capital()
    if df is not None and not df.empty:
        print("\n📈 主力净流入排行:")
        print(df.head(20).to_string(index=False))
    else:
        print("未获取到数据")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    format_sector_capital()
