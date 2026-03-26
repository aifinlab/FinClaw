#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
指数行情数据 - AkShare
"""

import akshare as ak
import sys
import time


def get_index_quote(symbol="000300", max_retries=3):
    """获取指数行情，带重试机制"""
    for attempt in range(max_retries):
        try:
            df = ak.index_zh_a_hist(symbol=symbol, period="daily")
            return df
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"[WARN] 第{attempt + 1}次尝试失败，1秒后重试...")
                time.sleep(1)
            else:
                print(f"[ERROR] 获取指数行情失败（已重试{max_retries}次）: {e}")
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
        print(f"   收盘: {latest.get('收盘', 'N/A')}")
        print(f"   涨跌: {latest.get('涨跌幅', 'N/A')}%")
    else:
        print("⚠️ 未获取到数据，请检查网络连接或指数代码")
    
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
