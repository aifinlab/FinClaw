#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
期货板块监控 - AkShare
按板块分类监控期货行情
"""

import akshare as ak
import pandas as pd

def get_futures_board():
    """获取期货板块行情"""
    try:
        df = ak.futures_zh_spot(symbol='RB0,HC0,I0,J0,JM0', market="CF", adjust='0')
        return df
    except:
        return None

def get_futures_global():
    """获取外盘期货行情"""
    try:
        df = ak.futures_global_spot_em()
        return df
    except Exception as e:
        print(f"获取外盘期货失败: {e}")
        return None

def format_board_report():
    """格式化板块报告"""
    print("=" * 80)
    print("📊 期货板块监控")
    print("=" * 80)
    
    # 黑色系
    print("\n⬛ 黑色系")
    print("-" * 80)
    black_symbols = ['RB0', 'HC0', 'I0', 'J0', 'JM0']
    black_names = ['螺纹钢', '热卷', '铁矿石', '焦炭', '焦煤']
    
    for symbol, name in zip(black_symbols, black_names):
        try:
            df = ak.futures_zh_spot(symbol=symbol, market="CF", adjust='0')
            if df is not None and not df.empty:
                price = df.get('current_price', [0]).values[0]
                change = df.get('change_percent', [0]).values[0]
                trend = "🟢" if float(change) > 0 else "🔴" if float(change) < 0 else "➡️"
                print(f"   {name:<8} {symbol:<6} {price:>10} {change:>8}% {trend}")
        except:
            pass
    
    # 有色系
    print("\n🟨 有色系")
    print("-" * 80)
    metal_symbols = ['CU0', 'AL0', 'ZN0', 'NI0', 'AU0', 'AG0']
    metal_names = ['铜', '铝', '锌', '镍', '黄金', '白银']
    
    for symbol, name in zip(metal_symbols, metal_names):
        try:
            df = ak.futures_zh_spot(symbol=symbol, market="CF", adjust='0')
            if df is not None and not df.empty:
                price = df.get('current_price', [0]).values[0]
                change = df.get('change_percent', [0]).values[0]
                trend = "🟢" if float(change) > 0 else "🔴" if float(change) < 0 else "➡️"
                print(f"   {name:<8} {symbol:<6} {price:>10} {change:>8}% {trend}")
        except:
            pass
    
    # 农产品
    print("\n🌾 农产品")
    print("-" * 80)
    agri_symbols = ['M0', 'Y0', 'P0', 'C0', 'CS0', 'A0']
    agri_names = ['豆粕', '豆油', '棕榈油', '玉米', '淀粉', '豆一']
    
    for symbol, name in zip(agri_symbols, agri_names):
        try:
            df = ak.futures_zh_spot(symbol=symbol, market="CF", adjust='0')
            if df is not None and not df.empty:
                price = df.get('current_price', [0]).values[0]
                change = df.get('change_percent', [0]).values[0]
                trend = "🟢" if float(change) > 0 else "🔴" if float(change) < 0 else "➡️"
                print(f"   {name:<8} {symbol:<6} {price:>10} {change:>8}% {trend}")
        except:
            pass
    
    # 化工品
    print("\n⚗️ 化工品")
    print("-" * 80)
    chem_symbols = ['TA0', 'MA0', 'L0', 'PP0', 'V0', 'RU0']
    chem_names = ['PTA', '甲醇', '聚乙烯', '聚丙烯', 'PVC', '橡胶']
    
    for symbol, name in zip(chem_symbols, chem_names):
        try:
            df = ak.futures_zh_spot(symbol=symbol, market="CF", adjust='0')
            if df is not None and not df.empty:
                price = df.get('current_price', [0]).values[0]
                change = df.get('change_percent', [0]).values[0]
                trend = "🟢" if float(change) > 0 else "🔴" if float(change) < 0 else "➡️"
                print(f"   {name:<8} {symbol:<6} {price:>10} {change:>8}% {trend}")
        except:
            pass
    
    # 股指期货
    print("\n📈 股指期货")
    print("-" * 80)
    index_symbols = ['IF0', 'IC0', 'IH0']
    index_names = ['沪深300', '中证500', '上证50']
    
    for symbol, name in zip(index_symbols, index_names):
        try:
            df = ak.futures_zh_spot(symbol=symbol, market="CF", adjust='0')
            if df is not None and not df.empty:
                price = df.get('current_price', [0]).values[0]
                change = df.get('change_percent', [0]).values[0]
                trend = "🟢" if float(change) > 0 else "🔴" if float(change) < 0 else "➡️"
                print(f"   {name:<8} {symbol:<6} {price:>10} {change:>8}% {trend}")
        except:
            pass
    
    print("\n" + "=" * 80)
    print("💡 提示: 使用 futures_quote.py <代码> 获取详细行情")
    print("=" * 80)

if __name__ == "__main__":
    format_board_report()
