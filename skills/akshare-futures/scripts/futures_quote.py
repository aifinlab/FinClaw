#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
期货实时行情获取 - AkShare
获取国内期货主力合约实时行情
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



def get_futures_quote(symbol="RB0"):
    """
    获取期货实时行情
    symbol: 合约代码，如 RB0(螺纹钢主力)、M0(豆粕主力)、IF0(沪深300期指)
    """
    try:
        df = ak.futures_zh_spot(symbol=symbol, market="CF", adjust='0')
        return df
    except Exception as e:
        print(f"获取期货行情失败: {e}")
        return None

def get_futures_realtime(symbol="螺纹钢"):
    """获取期货品种实时行情（按名称）"""
    try:
        df = ak.futures_zh_realtime(symbol=symbol)
        return df
    except Exception as e:
        print(f"获取期货行情失败: {e}")
        return None

def format_quote(symbol):
    """格式化行情输出"""
    print("=" * 70)
    print(f"📊 期货实时行情 | {symbol}")
    print("=" * 70)
    
    # 获取行情
    df = get_futures_quote(symbol)
    if df is not None and not df.empty:
        print("\n📈 行情数据:")
        print(df.to_string(index=False))
        
        # 提取关键信息
        if 'current_price' in df.columns:
            price = df['current_price'].iloc[0] if not df['current_price'].empty else 'N/A'
            
            # 安全获取字段值
            def safe_get(col, default='N/A'):
                if col in df.columns and not df[col].empty:
                    return df[col].iloc[0]
                return default
            
            change = safe_get('change')
            change_pct = safe_get('change_percent')
            volume = safe_get('volume')
            
            print(f"\n💡 关键信息:")
            print(f"   最新价: {price}")
            print(f"   涨跌额: {change}")
            print(f"   涨跌幅: {change_pct}%")
            print(f"   成交量: {volume}")
    else:
        # 尝试另一种方式
        df = get_futures_realtime(symbol)
        if df is not None and not df.empty:
            print("\n📈 行情数据:")
            print(df.head(5).to_string(index=False))
    
    print("\n" + "=" * 70)

def show_common_symbols():
    """显示常见合约代码"""
    print("\n📋 常见合约代码:")
    print("-" * 50)
    print("黑色系:")
    print("   RB0 = 螺纹钢主力")
    print("   HC0 = 热卷主力")
    print("   I0  = 铁矿石主力")
    print("   J0  = 焦炭主力")
    print("   JM0 = 焦煤主力")
    print("\n有色系:")
    print("   CU0 = 铜主力")
    print("   AL0 = 铝主力")
    print("   ZN0 = 锌主力")
    print("   NI0 = 镍主力")
    print("\n农产品:")
    print("   M0  = 豆粕主力")
    print("   Y0  = 豆油主力")
    print("   P0  = 棕榈油主力")
    print("   C0  = 玉米主力")
    print("\n化工品:")
    print("   TA0 = PTA主力")
    print("   MA0 = 甲醇主力")
    print("   L0  = 聚乙烯主力")
    print("   PP0 = 聚丙烯主力")
    print("\n股指期货:")
    print("   IF0 = 沪深300期指主力")
    print("   IC0 = 中证500期指主力")
    print("   IH0 = 上证50期指主力")
    print("   T0  = 10年期国债主力")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        symbol = sys.argv[1]
        format_quote(symbol)
    else:
        format_quote("RB0")
        show_common_symbols()
