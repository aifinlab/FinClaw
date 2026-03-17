#!/usr/bin/env python3
"""
涨跌停预警
监控涨跌停股票
"""

import akshare as ak
import pandas as pd

def check_limit_alert():
    """检查涨跌停股票"""
    try:
        df = ak.stock_zh_a_spot_em()
        
        if df.empty:
            print("暂无数据")
            return
        
        # 涨停股票 (涨幅接近10%或20%)
        limit_up = df[df['涨跌幅'] >= 9.5]
        # 跌停股票
        limit_down = df[df['涨跌幅'] <= -9.5]
        
        print("=" * 90)
        print("涨跌停监控")
        print("=" * 90)
        
        print(f"\n【涨停股票 ({len(limit_up)} 只)】")
        if not limit_up.empty:
            print(f"{'代码':<10} {'名称':<12} {'涨跌幅%':<10} {'成交额(万)':<12}")
            print("-" * 60)
            for _, row in limit_up.head(20).iterrows():
                print(f"{row['代码']:<10} {row['名称']:<12} "
                      f"{row['涨跌幅']:<10.2f} {row['成交额']/1e4:<12.1f}")
        
        print(f"\n【跌停股票 ({len(limit_down)} 只)】")
        if not limit_down.empty:
            print(f"{'代码':<10} {'名称':<12} {'涨跌幅%':<10} {'成交额(万)':<12}")
            print("-" * 60)
            for _, row in limit_down.head(20).iterrows():
                print(f"{row['代码']:<10} {row['名称']:<12} "
                      f"{row['涨跌幅']:<10.2f} {row['成交额']/1e4:<12.1f}")
        
        print("=" * 90)
        
    except Exception as e:
        print(f"检查失败: {e}")

if __name__ == "__main__":
    check_limit_alert()
