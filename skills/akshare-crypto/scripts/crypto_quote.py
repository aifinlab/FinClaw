#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
加密货币行情 - AkShare
"""

import akshare as ak

def get_crypto_quote():
    """获取加密货币行情"""
    try:
        df = ak.crypto_bitcoin_cme()
        return df
    except Exception as e:
        print(f"获取加密货币失败: {e}")
        return None

def format_crypto():
    """格式化加密货币"""
    print("=" * 80)
    print("₿ 加密货币行情")
    print("=" * 80)
    
    df = get_crypto_quote()
    if df is not None and not df.empty:
        print(df.tail(10).to_string(index=False))
    else:
        print("未获取到数据")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    format_crypto()
