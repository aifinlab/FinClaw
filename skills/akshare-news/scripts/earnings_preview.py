#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
业绩预告查询 - AkShare
获取上市公司业绩预告
"""

import akshare as ak

def get_earnings_preview():
    """获取业绩预告"""
    try:
        df = ak.stock_yjyg_em()
        return df
    except Exception as e:
        print(f"获取业绩预告失败: {e}")
        return None

def format_earnings_report():
    """格式化业绩预告报告"""
    print("=" * 80)
    print("📊 上市公司业绩预告")
    print("=" * 80)
    
    df = get_earnings_preview()
    if df is not None and not df.empty:
        print(f"\n📈 最新业绩预告 ({len(df)}条):")
        print("-" * 80)
        
        for i, row in df.head(30).iterrows():
            code = row.get('股票代码', 'N/A')
            name = row.get('股票简称', 'N/A')
            preview_type = row.get('业绩预告类型', 'N/A')
            content = row.get('业绩预告内容', 'N/A')[:50] + "..."
            change = row.get('变动幅度', 'N/A')
            date = row.get('预告日期', 'N/A')
            
            # 根据类型显示不同图标
            if '增' in preview_type or '盈' in preview_type:
                icon = "🟢"
            elif '减' in preview_type or '亏' in preview_type:
                icon = "🔴"
            else:
                icon = "➡️"
            
            print(f"\n{icon} {name}({code}) - {preview_type}")
            print(f"   变动: {change}")
            print(f"   内容: {content}")
            print(f"   日期: {date}")
    else:
        print("未获取到业绩预告数据")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    format_earnings_report()
