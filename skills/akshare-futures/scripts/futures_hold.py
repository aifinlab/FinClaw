#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
期货持仓龙虎榜 - AkShare
获取期货合约的成交量和持仓量龙虎榜
"""

import akshare as ak
import sys

def get_hold_ranking(symbol="OI2501", indicator="成交量", date=None):
    """
    获取持仓龙虎榜
    symbol: 合约代码，如 OI2501(菜油2501)、RB2501(螺纹2501)
    indicator: "成交量" 或 "多单持仓" 或 "空单持仓"
    date: 日期，如 "20240115"
    """
    try:
        if date is None:
            # 获取最新日期
            import pandas as pd
            date = pd.Timestamp.now().strftime('%Y%m%d')
        
        df = ak.futures_hold_pos_sina(symbol=indicator, contract=symbol, date=date)
        return df
    except Exception as e:
        print(f"获取持仓数据失败: {e}")
        return None

def format_hold_report(symbol):
    """格式化持仓报告"""
    print("=" * 70)
    print(f"🏆 期货持仓龙虎榜 | {symbol}")
    print("=" * 70)
    
    # 成交量排行
    print("\n📊 成交量龙虎榜:")
    df_vol = get_hold_ranking(symbol, "成交量")
    if df_vol is not None and not df_vol.empty:
        print(df_vol.head(10).to_string(index=False))
    else:
        print("暂无数据")
    
    # 多单持仓排行
    print("\n📈 多单持仓龙虎榜:")
    df_long = get_hold_ranking(symbol, "多单持仓")
    if df_long is not None and not df_long.empty:
        print(df_long.head(10).to_string(index=False))
    else:
        print("暂无数据")
    
    # 空单持仓排行
    print("\n📉 空单持仓龙虎榜:")
    df_short = get_hold_ranking(symbol, "空单持仓")
    if df_short is not None and not df_short.empty:
        print(df_short.head(10).to_string(index=False))
    else:
        print("暂无数据")
    
    # 分析
    print("\n💡 持仓分析:")
    if df_long is not None and df_short is not None:
        top_long = df_long.iloc[0] if not df_long.empty else None
        top_short = df_short.iloc[0] if not df_short.empty else None
        
        if top_long is not None and top_short is not None:
            print(f"   多头龙头: {top_long.get('会员简称', 'N/A')}")
            print(f"   空头龙头: {top_short.get('会员简称', 'N/A')}")
            
            # 计算持仓比
            total_long = df_long['多单持仓'].sum() if '多单持仓' in df_long.columns else 0
            total_short = df_short['空单持仓'].sum() if '空单持仓' in df_short.columns else 0
            if total_short > 0:
                ratio = total_long / total_short
                print(f"   多空持仓比: {ratio:.2f}", end="")
                if ratio > 1.2:
                    print(" 🟢 多头占优")
                elif ratio < 0.8:
                    print(" 🔴 空头占优")
                else:
                    print(" ➡️ 多空均衡")
    
    print("\n" + "=" * 70)

def show_usage():
    """显示用法"""
    print("\n📋 用法:")
    print("   python futures_hold.py <合约代码>")
    print("\n示例:")
    print("   python futures_hold.py OI2501    # 菜油2501")
    print("   python futures_hold.py RB2501    # 螺纹2501")
    print("   python futures_hold.py M2501     # 豆粕2501")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        symbol = sys.argv[1]
        format_hold_report(symbol)
    else:
        format_hold_report("OI2501")
        show_usage()
