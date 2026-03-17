#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
个股资金流向 - AkShare
"""

import akshare as ak
import sys

def get_capital_flow(stock="600519"):
    """获取个股资金流向"""
    try:
        df = ak.stock_individual_fund_flow(stock=stock, market="sh")
        return df
    except Exception as e:
        print(f"获取资金流向失败: {e}")
        return None

def format_capital_flow(stock):
    """格式化资金流向"""
    print("=" * 80)
    print(f"💰 资金流向 | {stock}")
    print("=" * 80)
    
    df = get_capital_flow(stock)
    if df is not None and not df.empty:
        print("\n📈 最近10日资金流向:")
        print(df.head(10).to_string(index=False))
        
        # 计算净流入
        if '主力净流入' in df.columns:
            total_main = df['主力净流入'].sum()
            print(f"\n💡 主力资金净流入: {total_main:.2f}万元")
            if total_main > 0:
                print("   🟢 主力净流入，看涨信号")
            else:
                print("   🔴 主力净流出，看跌信号")
    else:
        print("未获取到数据")
    
    print("\n" + "=" * 80)

def show_usage():
    print("\n📋 用法: python capital_flow.py <股票代码>")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        stock = sys.argv[1]
        format_capital_flow(stock)
    else:
        format_capital_flow("600519")
        show_usage()
