#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
北向资金流向 - AkShare
"""

import akshare as ak

def get_northbound_flow():
    """获取北向资金流向"""
    try:
        df = ak.stock_hsgt_hist_em(symbol="沪股通")
        return df
    except Exception as e:
        print(f"获取北向资金失败: {e}")
        return None

def format_northbound():
    """格式化北向资金"""
    print("=" * 80)
    print("💰 北向资金流向")
    print("=" * 80)
    
    df = get_northbound_flow()
    if df is not None and not df.empty:
        print("\n📈 最近10日北向资金:")
        print(df.head(10).to_string(index=False))
        
        # 计算净流入
        if '净买入额' in df.columns:
            total = df['净买入额'].sum()
            print(f"\n💡 累计净流入: {total:.2f}亿元")
    else:
        print("未获取到数据")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    format_northbound()
