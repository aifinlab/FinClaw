#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
M2货币供应量数据获取 - AkShare
"""

import akshare as ak

def get_m2_monthly():
    """获取M2货币供应量数据"""
    try:
        df = ak.macro_china_m2()
        df.columns = ['日期', 'M2余额(亿元)', 'M2同比增长(%)', 'M1余额(亿元)',
                      'M1同比增长(%)', 'M0余额(亿元)', 'M0同比增长(%)']
        return df.tail(24)
    except Exception as e:
        print(f"获取M2数据失败: {e}")
        return None

def format_m2_report():
    """格式化M2报告"""
    print("=" * 60)
    print("💰 M2货币供应量报告")
    print("=" * 60)
    
    m2 = get_m2_monthly()
    if m2 is not None:
        print("\n📈 M2月度数据（最近24个月）")
        print(m2.to_string(index=False))
        
        # 最新数据解读
        latest = m2.iloc[-1]
        print(f"\n💡 最新数据解读 ({latest['日期']}):")
        print(f"   M2余额: {latest['M2余额(亿元)']}亿元")
        print(f"   M2同比增长: {latest['M2同比增长(%)']}%")
        print(f"   M1同比增长: {latest['M1同比增长(%)']}%")
        
        # M1-M2剪刀差分析
        m1_growth = float(latest['M1同比增长(%)'])
        m2_growth = float(latest['M2同比增长(%)'])
        scissors = m1_growth - m2_growth
        print(f"\n   M1-M2剪刀差: {scissors:.2f}%", end="")
        if scissors > 0:
            print(" 🟢 资金活化程度高（企业投资意愿强）")
        elif scissors > -5:
            print(" 🟡 资金活化程度一般")
        else:
            print(" 🔴 资金活化程度低（企业投资意愿弱）")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    format_m2_report()
