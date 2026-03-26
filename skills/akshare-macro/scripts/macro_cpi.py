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
        if df is not None and not df.empty:
            return df.tail(24)
        return None
    except Exception as e:
        print(f"获取CPI数据失败: {e}")
        return None


def format_cpi_report():
    """格式化CPI报告"""
    print("=" * 60)
    print("📊 CPI通胀数据报告")
    print("=" * 60)
    
    cpi = get_cpi_monthly()
    if cpi is not None and not cpi.empty:
        print("\n📈 CPI月度数据（最近24个月）")
        print(cpi.to_string(index=False))
        
        # 最新数据解读
        try:
            latest = cpi.iloc[-1]
            date_col = cpi.columns[0]  # 第一列通常是日期
            cpi_col = [c for c in cpi.columns if '同比' in c or 'CPI' in c]
            
            if cpi_col:
                cpi_value = latest[cpi_col[0]]
                print(f"\n💡 最新数据解读 ({latest[date_col]}):")
                print(f"   CPI同比: {cpi_value}%", end="")
                
                try:
                    cpi_float = float(cpi_value)
                    if cpi_float > 3:
                        print(" 🔴 通胀压力较大")
                    elif cpi_float > 2:
                        print(" 🟡 温和通胀")
                    elif cpi_float > 0:
                        print(" 🟢 低通胀")
                    else:
                        print(" ⚪ 通缩风险")
                except:
                    print("")
        except Exception as e:
            print(f"\n💡 数据解读失败: {e}")
    else:
        print("\n⚠️ 未能获取CPI数据")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    format_cpi_report()
