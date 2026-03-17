#!/usr/bin/env python3
"""
AI选股
智能选股系统
"""

import akshare as ak
import pandas as pd

def ai_pick_stocks():
    """AI选股"""
    print("=" * 70)
    print("AI智能选股")
    print("=" * 70)
    
    try:
        df = ak.stock_zh_a_spot_em()
        
        # 简单筛选条件：低PE+高换手+放量上涨
        filtered = df[
            (df['市盈率'] > 0) & 
            (df['市盈率'] < 30) &
            (df['换手率'] > 3) &
            (df['涨跌幅'] > 2)
        ]
        
        filtered = filtered.sort_values('涨跌幅', ascending=False)
        
        print("\n【AI精选股票】")
        print(f"{'代码':<10} {'名称':<12} {'PE':<8} {'换手%':<8} {'涨幅%':<8}")
        print("-" * 60)
        
        for _, row in filtered.head(20).iterrows():
            print(f"{row['代码']:<10} {row['名称']:<12} {row['市盈率']:<8.1f} "
                  f"{row['换手率']:<8.2f} {row['涨跌幅']:<8.2f}")
        
        print("=" * 70)
        
    except Exception as e:
        print(f"选股失败: {e}")

if __name__ == "__main__":
    ai_pick_stocks()
