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
        df.columns = ['日期', 'LPR1Y(%)', 'LPR5Y(%)']
        return df.tail(12)
    except Exception as e:
        print(f"获取LPR数据失败: {e}")
        return None

def get_rmb_exchange():
    """获取人民币汇率数据"""
    try:
        df = ak.macro_china_rmb()
        df.columns = ['日期', '美元/人民币', '欧元/人民币', '日元/人民币', '港元/人民币']
        return df.tail(12)
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
    if lpr is not None:
        print("\n📈 LPR贷款市场报价利率（最近12期）")
        print(lpr.to_string(index=False))
        
        latest = lpr.iloc[-1]
        print(f"\n💡 最新LPR ({latest['日期']}):")
        print(f"   1年期LPR: {latest['LPR1Y(%)']}%")
        print(f"   5年期LPR: {latest['LPR5Y(%)']}%")
    
    # 汇率数据
    rmb = get_rmb_exchange()
    if rmb is not None:
        print("\n📈 人民币汇率（最近12期）")
        print(rmb.to_string(index=False))
        
        latest = rmb.iloc[-1]
        print(f"\n💡 最新汇率 ({latest['日期']}):")
        print(f"   美元/人民币: {latest['美元/人民币']}")
        print(f"   欧元/人民币: {latest['欧元/人民币']}")
        print(f"   日元/人民币: {latest['日元/人民币']}")
        print(f"   港元/人民币: {latest['港元/人民币']}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    format_rate_report()
