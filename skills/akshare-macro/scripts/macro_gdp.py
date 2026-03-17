#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GDP数据获取 - AkShare
获取中国GDP季度及年度数据
"""

import akshare as ak
import pandas as pd
from datetime import datetime

def get_gdp_yearly():
    """获取GDP年度数据"""
    try:
        df = ak.macro_china_gdp()
        df.columns = ['年份', 'GDP绝对值(亿元)', 'GDP同比增长(%)', '第一产业(亿元)', 
                      '第二产业(亿元)', '第三产业(亿元)']
        return df.tail(10)
    except Exception as e:
        print(f"获取GDP年度数据失败: {e}")
        return None

def get_gdp_quarterly():
    """获取GDP季度数据"""
    try:
        df = ak.macro_china_gdp_yearly()
        df.columns = ['季度', 'GDP累计值(亿元)', 'GDP累计增长(%)']
        return df.tail(12)
    except Exception as e:
        print(f"获取GDP季度数据失败: {e}")
        return None

def format_gdp_report():
    """格式化GDP报告"""
    print("=" * 60)
    print("📊 中国GDP数据报告")
    print("=" * 60)
    
    # 年度数据
    yearly = get_gdp_yearly()
    if yearly is not None:
        print("\n📈 GDP年度数据")
        print(yearly.to_string(index=False))
    
    # 季度数据
    quarterly = get_gdp_quarterly()
    if quarterly is not None:
        print("\n📈 GDP季度数据（最近12个季度）")
        print(quarterly.to_string(index=False))
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    format_gdp_report()
