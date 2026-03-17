#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
期货主力合约获取 - AkShare
获取各交易所主力合约列表
"""

import akshare as ak
import sys

def get_main_contract(exchange="shfe"):
    """
    获取主力合约
    exchange: shfe(上期所), dce(大商所), zce(郑商所), cffex(中金所)
    """
    try:
        symbol = ak.match_main_contract(symbol=exchange)
        return symbol
    except Exception as e:
        print(f"获取主力合约失败: {e}")
        return None

def get_all_main_contracts():
    """获取所有交易所主力合约"""
    exchanges = {
        "shfe": "上海期货交易所",
        "dce": "大连商品交易所",
        "zce": "郑州商品交易所",
        "cffex": "中国金融期货交易所"
    }
    
    results = {}
    for code, name in exchanges.items():
        try:
            symbol = get_main_contract(code)
            results[name] = symbol
        except:
            results[name] = "N/A"
    
    return results

def format_main_contract_report():
    """格式化主力合约报告"""
    print("=" * 70)
    print("🎯 期货主力合约列表")
    print("=" * 70)
    
    contracts = get_all_main_contracts()
    
    print("\n📋 各交易所主力合约:")
    print("-" * 70)
    for exchange, symbol in contracts.items():
        print(f"   {exchange:<25} {symbol}")
    
    # 主力合约说明
    print("\n💡 主力合约说明:")
    print("   主力合约是指成交量和持仓量最大的合约")
    print("   通常在合约首次上市时确定，当其他合约持仓量")
    print("   超过当前主力合约1.1倍时切换")
    
    print("\n" + "=" * 70)

def show_usage():
    """显示用法"""
    print("\n📋 用法:")
    print("   python futures_main.py [交易所代码]")
    print("\n交易所代码:")
    print("   shfe  = 上海期货交易所")
    print("   dce   = 大连商品交易所")
    print("   zce   = 郑州商品交易所")
    print("   cffex = 中国金融期货交易所")
    print("\n示例:")
    print("   python futures_main.py shfe")
    print("   python futures_main.py cffex")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        exchange = sys.argv[1]
        symbol = get_main_contract(exchange)
        if symbol:
            print(f"\n✅ {exchange} 主力合约: {symbol}")
            # 获取行情
            import os
            os.system(f"python futures_quote.py {symbol}")
        else:
            print(f"❌ 无法获取 {exchange} 主力合约")
    else:
        format_main_contract_report()
        show_usage()
