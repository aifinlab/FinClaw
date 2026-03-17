#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
公司公告查询 - AkShare
获取上市公司公告
"""

import akshare as ak
import sys

def get_stock_announcement(stock="600519"):
    """获取公司公告"""
    try:
        df = ak.stock_notice_report()
        return df
    except Exception as e:
        print(f"获取公告失败: {e}")
        return None

def get_earnings_preview():
    """获取业绩预告"""
    try:
        df = ak.stock_yjyg_em()
        df.columns = ['股票代码', '股票简称', '业绩预告类型', '业绩预告内容', 
                      '变动幅度', '变动原因', '预告日期']
        return df
    except Exception as e:
        print(f"获取业绩预告失败: {e}")
        return None

def format_announcement_report(stock="600519"):
    """格式化公告报告"""
    print("=" * 80)
    print(f"📋 公司公告查询 | {stock}")
    print("=" * 80)
    
    # 公司公告
    df = get_stock_announcement(stock)
    if df is not None and not df.empty:
        print("\n📢 最新公告:")
        print("-" * 80)
        for i, row in df.head(10).iterrows():
            print(f"\n🔸 {row.get('公告标题', 'N/A')}")
            print(f"   时间: {row.get('公告日期', 'N/A')}")
    else:
        print("\n未获取到公告数据")
    
    print("\n" + "=" * 80)

def format_earnings_preview():
    """格式化业绩预告"""
    print("=" * 80)
    print("📊 业绩预告")
    print("=" * 80)
    
    df = get_earnings_preview()
    if df is not None and not df.empty:
        print("\n📈 最新业绩预告:")
        print("-" * 80)
        print(df.head(20).to_string(index=False))
    else:
        print("未获取到业绩预告数据")
    
    print("\n" + "=" * 80)

def show_usage():
    """显示用法"""
    print("\n📋 用法:")
    print("   python announcement.py [股票代码]")
    print("   python announcement.py --preview    # 业绩预告")
    print("\n示例:")
    print("   python announcement.py 600519")
    print("   python announcement.py 300750")
    print("   python announcement.py --preview")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--preview":
            format_earnings_preview()
        else:
            stock = sys.argv[1]
            format_announcement_report(stock)
    else:
        format_announcement_report("600519")
        show_usage()
