#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PPI生产者物价指数数据获取 - AkShare
"""

import akshare as ak

def get_ppi_monthly():
    """获取PPI月度数据"""
    try:
        df = ak.macro_china_ppi()
        df.columns = ['日期', 'PPI全部工业品同比(%)', 'PPI全部工业品环比(%)',
                      'PPI生产资料同比(%)', 'PPI生活资料同比(%)']
        return df.tail(24)
    except Exception as e:
        print(f"获取PPI数据失败: {e}")
        return None

def format_ppi_report():
    """格式化PPI报告"""
    print("=" * 60)
    print("📊 PPI生产者物价指数报告")
    print("=" * 60)
    
    ppi = get_ppi_monthly()
    if ppi is not None:
        print("\n📈 PPI月度数据（最近24个月）")
        print(ppi.to_string(index=False))
        
        # 最新数据解读
        latest = ppi.iloc[-1]
        print(f"\n💡 最新数据解读 ({latest['日期']}):")
        print(f"   PPI同比: {latest['PPI全部工业品同比(%)']}%", end="")
        ppi_val = float(latest['PPI全部工业品同比(%)'])
        if ppi_val > 5:
            print(" 🔴 工业通胀压力较大")
        elif ppi_val > 0:
            print(" 🟡 工业价格温和上涨")
        elif ppi_val > -2:
            print(" 🟢 工业价格小幅下跌")
        else:
            print(" ⚪ 工业通缩风险")
        
        # PPI-CPI剪刀差分析
        print(f"\n   PPI生产资料: {latest['PPI生产资料同比(%)']}%")
        print(f"   PPI生活资料: {latest['PPI生活资料同比(%)']}%")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    format_ppi_report()
