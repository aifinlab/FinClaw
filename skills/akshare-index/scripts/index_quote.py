#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
指数行情数据 - AkShare
"""

import akshare as ak
import sys

def get_index_quote(symbol="000300"):
    """获取指数行情"""
    try:
        df = ak.index_zh_a_hist(symbol=symbol, period="daily")
        return df
    except Exception as e:
        print(f"获取指数行情失败: {e}")
        return None

def format_index(symbol):
    """格式化指数"""
    print("=" * 80)
    print(f"📈 指数行情 | {symbol}")
    print("=" * 80)
    
    df = get_index_quote(symbol)
    if df is not None and not df.empty:
        print(df.tail(10).to_string(index=False))
        
        latest = df.iloc[-1]
        print(f"\n💡 最新数据:")
        print(f"   收盘: {latest['收盘']}")
        print(f"   涨跌: {latest['涨跌幅']}%")
    else:
        print("未获取到数据")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        symbol = sys.argv[1]
        format_index(symbol)
    else:
        format_index("000300")
        print("\n常用指数代码:")
        print("   000001 - 上证指数")
        print("   000300 - 沪深300")
        print("   000905 - 中证500")
        print("   000016 - 上证50")
