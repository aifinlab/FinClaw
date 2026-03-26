#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
财报数据获取 - AkShare
获取三大表数据
"""

import akshare as ak
import sys


def validate_input(data: dict) -> dict:
    """验证输入参数"""
    if not isinstance(data, dict):
        raise ValueError("输入必须是字典类型")
    
    required_fields = []  # 添加必填字段
    for field in required_fields:
        if field not in data:
            raise ValueError(f"缺少必填字段: {field}")
    
    return data



def get_balance_sheet(stock="600519"):
    """获取资产负债表"""
    try:
        df = ak.stock_balance_sheet_by_report_em(symbol=stock)
        return df
    except Exception as e:
        print(f"获取资产负债表失败: {e}")
        return None

def get_income_statement(stock="600519"):
    """获取利润表"""
    try:
        df = ak.stock_profit_sheet_by_report_em(symbol=stock)
        return df
    except Exception as e:
        print(f"获取利润表失败: {e}")
        return None

def get_cash_flow(stock="600519"):
    """获取现金流量表"""
    try:
        df = ak.stock_cash_flow_sheet_by_report_em(symbol=stock)
        return df
    except Exception as e:
        print(f"获取现金流量表失败: {e}")
        return None

def format_financial_report(stock):
    """格式化财报"""
    print("=" * 80)
    print(f"📊 三大表数据 | {stock}")
    print("=" * 80)
    
    # 资产负债表
    print("\n📋 资产负债表(最新):")
    bs = get_balance_sheet(stock)
    if bs is not None and not bs.empty:
        print(bs.iloc[0].to_string())
    
    print("\n📋 利润表(最新):")
    ic = get_income_statement(stock)
    if ic is not None and not ic.empty:
        print(ic.iloc[0].to_string())
    
    print("\n📋 现金流量表(最新):")
    cf = get_cash_flow(stock)
    if cf is not None and not cf.empty:
        print(cf.iloc[0].to_string())
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        stock = sys.argv[1]
        format_financial_report(stock)
    else:
        format_financial_report("600519")
