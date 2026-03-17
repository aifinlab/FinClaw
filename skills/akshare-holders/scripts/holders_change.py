#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股东增减持数据 - AkShare
"""

import akshare as ak
import sys

def get_holders_change(stock="600519"):
    """获取股东增减持"""
    try:
        df = ak.stock_gdfx_free_holding_change_em()
        return df
    except Exception as e:
        print(f"获取股东增减持失败: {e}")
        return None

def format_holders_change(stock):
    """格式化股东增减持"""
    print("=" * 80)
    print(f"👥 股东增减持 | {stock}")
    print("=" * 80)
    
    df = get_holders_change(stock)
    if df is not None and not df.empty:
        # 筛选特定股票
        stock_df = df[df['股票代码'] == stock]
        if not stock_df.empty:
            print(stock_df.to_string(index=False))
        else:
            print("该股票暂无增减持数据")
    else:
        print("未获取到数据")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        stock = sys.argv[1]
        format_holders_change(stock)
    else:
        format_holders_change("600519")
