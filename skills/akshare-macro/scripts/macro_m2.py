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
        if df is not None and not df.empty:
            return df.tail(24)
        return None
    except Exception as e:
        print(f"获取M2数据失败: {e}")
        return None


def format_m2_report():
    """格式化M2报告"""
    print("=" * 60)
    print("💰 M2货币供应量报告")
    print("=" * 60)
    
    m2 = get_m2_monthly()
    if m2 is not None and not m2.empty:
        print("\n📈 M2月度数据（最近24个月）")
        print(m2.to_string(index=False))
        
        # 最新数据解读
        try:
            latest = m2.iloc[-1]
            date_col = m2.columns[0]
            print(f"\n💡 最新数据 ({latest[date_col]}):")
            
            # 动态查找列
            m2_cols = [c for c in m2.columns if 'M2' in c]
            m1_cols = [c for c in m2.columns if 'M1' in c]
            
            if m2_cols:
                print(f"   M2数据: {latest[m2_cols[0]]}")
            if m1_cols:
                print(f"   M1数据: {latest[m1_cols[0]]}")
                
            # 尝试计算M1-M2剪刀差
            try:
                m1_growth = float(latest[m1_cols[0]])
                m2_growth = float(latest[m2_cols[0]])
                scissors = m1_growth - m2_growth
                print(f"\n   M1-M2剪刀差: {scissors:.2f}%", end="")
                if scissors > 0:
                    print(" 🟢 资金活化程度高")
                elif scissors > -5:
                    print(" 🟡 资金活化程度一般")
                else:
                    print(" 🔴 资金活化程度低")
            except:
                pass
        except Exception as e:
            print(f"\n💡 数据解读失败: {e}")
    else:
        print("\n⚠️ 未能获取M2数据")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    format_m2_report()
