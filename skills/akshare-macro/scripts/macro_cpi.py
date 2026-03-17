#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CPI通胀数据获取 - AkShare
获取消费者物价指数数据
"""

import akshare as ak
import pandas as pd

def get_cpi_monthly():
    """获取CPI月度数据"""
    try:
        df = ak.macro_china_cpi()
        df.columns = ['日期', '全国CPI同比(%)', '全国CPI环比(%)', '全国CPI定基(%)',
                      '城市CPI同比(%)', '农村CPI同比(%)']
        return df.tail(24)
    except Exception as e:
        print(f"获取CPI数据失败: {e}")
        return None

def format_cpi_report():
    """格式化CPI报告"""
    print("=" * 60)
    print("📊 CPI通胀数据报告")
    print("=" * 60)
    
    cpi = get_cpi_monthly()
    if cpi is not None:
        print("\n📈 CPI月度数据（最近24个月）")
        print(cpi.to_string(index=False))
        
        # 最新数据解读
        latest = cpi.iloc[-1]
        print(f"\n💡 最新数据解读 ({latest['日期']}):")
        print(f"   CPI同比: {latest['全国CPI同比(%)']}%", end="")
        if float(latest['全国CPI同比(%)']) > 3:
            print(" 🔴 通胀压力较大")
        elif float(latest['全国CPI同比(%)']) > 2:
            print(" 🟡 温和通胀")
        elif float(latest['全国CPI同比(%)']) > 0:
            print(" 🟢 低通胀")
        else:
            print(" ⚪ 通缩风险")
        print(f"   CPI环比: {latest['全国CPI环比(%)']}%")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    format_cpi_report()
