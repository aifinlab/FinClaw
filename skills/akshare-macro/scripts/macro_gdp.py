#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GDP数据获取 - AkShare
获取中国GDP季度及年度数据
"""

from datetime import datetime
import akshare as ak
import pandas as pd


def get_gdp_yearly():
    """获取GDP年度数据"""
    try:
        df = ak.macro_china_gdp()
        # 动态处理列名，避免硬编码导致的列数不匹配
        if df is not None and not df.empty:
            # 打印列名用于调试
            # print(f"[DEBUG] GDP年度数据列: {df.columns.tolist()}")
            return df.tail(10)
        return None
    except Exception as e:
        print(f"获取GDP年度数据失败: {e}")
        return None


def get_gdp_quarterly():
    """获取GDP季度数据"""
    try:
        df = ak.macro_china_gdp_yearly()
        # 动态处理列名
        if df is not None and not df.empty:
            # print(f"[DEBUG] GDP季度数据列: {df.columns.tolist()}")
            return df.tail(12)
        return None
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
    if yearly is not None and not yearly.empty:
        print("\n📈 GDP年度数据")
        print(yearly.to_string(index=False))
    else:
        print("\n⚠️ 未能获取GDP年度数据")

    # 季度数据
    quarterly = get_gdp_quarterly()
    if quarterly is not None and not quarterly.empty:
        print("\n📈 GDP季度数据（最近12个季度）")
        print(quarterly.to_string(index=False))
    else:
        print("\n⚠️ 未能获取GDP季度数据")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    format_gdp_report()
