#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
利率与汇率数据获取 - AkShare
LPR利率、人民币汇率
"""

import akshare as ak


def get_lpr():
    """获取LPR利率数据"""
    try:
        df = ak.macro_china_lpr()
        if df is not None and not df.empty:
            return df.tail(12)
        return None
    except Exception as e:
        print(f"获取LPR数据失败: {e}")
        return None


def get_rmb_exchange():
    """获取人民币汇率数据"""
    try:
        df = ak.macro_china_rmb()
        if df is not None and not df.empty:
            return df.tail(12)
        return None
    except Exception as e:
        print(f"获取汇率数据失败: {e}")
        return None


def format_rate_report():
    """格式化利率汇率报告"""
    print("=" * 60)
    print("💱 利率与汇率报告")
    print("=" * 60)
    
    # LPR数据
    lpr = get_lpr()
    if lpr is not None and not lpr.empty:
        print("\n📈 LPR贷款市场报价利率（最近12期）")
        print(lpr.to_string(index=False))
        
        try:
            latest = lpr.iloc[-1]
            date_col = lpr.columns[0]
            print(f"\n💡 最新LPR ({latest[date_col]}):")
            for col in lpr.columns[1:3]:  # 显示前两个利率列
                print(f"   {col}: {latest[col]}%")
        except Exception as e:
            print(f"\n💡 LPR数据解读失败: {e}")
    else:
        print("\n⚠️ 未能获取LPR数据")
    
    # 汇率数据
    rmb = get_rmb_exchange()
    if rmb is not None and not rmb.empty:
        print("\n📈 人民币汇率（最近12期）")
        print(rmb.to_string(index=False))
        
        try:
            latest = rmb.iloc[-1]
            date_col = rmb.columns[0]
            print(f"\n💡 最新汇率 ({latest[date_col]}):")
            for col in rmb.columns[1:5]:  # 显示前四个汇率列
                print(f"   {col}: {latest[col]}")
        except Exception as e:
            print(f"\n💡 汇率数据解读失败: {e}")
    else:
        print("\n⚠️ 未能获取汇率数据")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    format_rate_report()
