#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
期权行情数据获取 - AkShare
获取ETF期权、股指期权行情
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



# 支持的期权品种映射
OPTION_SYMBOLS = {
    "50ETF": "华夏上证50ETF期权",
    "300ETF": "华泰柏瑞沪深300ETF期权", 
    "500ETF": "南方中证500ETF期权",
    "创业板ETF": "易方达创业板ETF期权",
    "沪深300股指": "沪深300股指期权",
    "中证1000股指": "中证1000股指期权",
    "上证50股指": "上证50股指期权",
    "科创50ETF": "华夏科创50ETF期权",
}

def get_option_quote(symbol="华夏上证50ETF期权"):
    """获取期权行情"""
    try:
        # 尝试获取行情
        df = ak.option_finance_board(symbol=symbol, end_month="")
        if df is None or df.empty:
            return None
        return df
    except Exception as e:
        # 非交易日或数据源问题
        return None

def get_option_underlying():
    """获取期权标的行情（50ETF等）"""
    try:
        # 尝试获取50ETF行情作为参考
        df = ak.fund_etf_spot_em()
        if df is not None and not df.empty:
            # 筛选主要ETF期权标的
            etf_codes = ['510050', '510300', '510500', '159915', '588000']
            etf_df = df[df['代码'].isin(etf_codes)]
            return etf_df
        return None
    except Exception as e:
        return None

def format_option_quote(symbol):
    """格式化期权行情"""
    print("=" * 80)
    print(f"📊 期权行情 | {symbol}")
    print("=" * 80)
    
    df = get_option_quote(symbol)
    if df is not None and not df.empty:
        print("\n📈 期权合约列表:")
        print(df.head(20).to_string(index=False))
        
        # 统计
        print(f"\n💡 统计信息:")
        print(f"   合约数量: {len(df)}")
        if '当前价' in df.columns:
            print(f"   最高价格: {df['当前价'].max()}")
            print(f"   最低价格: {df['当前价'].min()}")
    else:
        print("\n⚠️ 未获取到期权合约数据")
        print("   可能原因：")
        print("   1. 当前为非交易日（周末/节假日）")
        print("   2. 期权市场已收盘")
        print("   3. 数据源暂时不可用")
        
        # 显示标的行情
        print("\n📊 期权标的ETF行情（供参考）:")
        etf_df = get_option_underlying()
        if etf_df is not None and not etf_df.empty:
            print(etf_df[['代码', '名称', '最新价', '涨跌幅']].to_string(index=False))
    
    print("\n" + "=" * 80)

def show_usage():
    """显示用法"""
    print("\n📋 支持的期权品种:")
    for code, name in OPTION_SYMBOLS.items():
        print(f"   {code:12s} - {name}")
    print("\n💡 使用方法:")
    print("   python option_quote.py [品种代码]")
    print("   示例: python option_quote.py 50ETF")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        symbol_input = sys.argv[1]
        # 支持代码或全称
        symbol = OPTION_SYMBOLS.get(symbol_input, symbol_input)
        format_option_quote(symbol)
    else:
        format_option_quote("华夏上证50ETF期权")
        show_usage()
