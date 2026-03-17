#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
期货历史行情数据获取 - AkShare
"""

import akshare as ak
import sys

def get_futures_history_sina(symbol="RB0"):
    """
    获取期货历史数据（新浪财经）
    symbol: 合约代码，如 RB0、M0
    """
    try:
        df = ak.futures_zh_daily_sina(symbol=symbol)
        return df
    except Exception as e:
        print(f"获取历史数据失败: {e}")
        return None

def get_futures_history_em(symbol="热卷主连"):
    """
    获取期货历史数据（东方财富）
    symbol: 合约名称，如 "热卷主连"、"螺纹钢主连"
    """
    try:
        df = ak.futures_hist_em(symbol=symbol, period="daily")
        return df
    except Exception as e:
        print(f"获取历史数据失败: {e}")
        return None

def format_hist_report(symbol, days=30):
    """格式化历史数据报告"""
    print("=" * 70)
    print(f"📊 期货历史行情 | {symbol}")
    print("=" * 70)
    
    # 尝试获取新浪数据
    df = get_futures_history_sina(symbol)
    if df is not None and not df.empty:
        print(f"\n📈 最近{days}个交易日数据:")
        print(df.tail(days).to_string(index=False))
        
        # 计算统计指标
        if 'close' in df.columns:
            latest = df['close'].iloc[-1]
            prev = df['close'].iloc[-2]
            high_30d = df['high'].tail(30).max()
            low_30d = df['low'].tail(30).min()
            avg_30d = df['close'].tail(30).mean()
            
            print(f"\n💡 技术指标:")
            print(f"   最新收盘价: {latest}")
            print(f"   前日收盘价: {prev}")
            print(f"   30日最高价: {high_30d}")
            print(f"   30日最低价: {low_30d}")
            print(f"   30日均价: {avg_30d:.2f}")
    else:
        print("未获取到数据")
    
    print("\n" + "=" * 70)

def show_usage():
    """显示用法"""
    print("\n📋 用法:")
    print("   python futures_hist.py <合约代码> [天数]")
    print("\n示例:")
    print("   python futures_hist.py RB0")
    print("   python futures_hist.py M0 60")
    print("   python futures_hist.py IF0 20")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        symbol = sys.argv[1]
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        format_hist_report(symbol, days)
    else:
        format_hist_report("RB0")
        show_usage()
