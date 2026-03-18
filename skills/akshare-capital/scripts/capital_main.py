#!/usr/bin/env python3
"""
主力资金排行 - Capital Main Flow
获取主力资金净流入/流出排行（带限流保护）
"""

import sys
sys.path.insert(0, '.')

import akshare as ak
import pandas as pd
from datetime import datetime
from akshare_utils import safe_ak_call

def get_main_capital_rank(days=1, top=20):
    """
    获取主力资金排行
    
    Args:
        days: 统计天数 (1=当日, 5=5日, 10=10日)
        top: 返回前N名
        
    Returns:
        DataFrame with columns: 名称, 最新价, 涨跌幅, 主力净流入, 主力净占比
    """
    try:
        # 使用安全调用方式（带延迟和重试）
        df = safe_ak_call(ak.stock_individual_fund_flow_rank, indicator="今日")
        
        if df is None or df.empty:
            print("获取数据失败或被限流")
            return pd.DataFrame()
        
        # 选择需要的列
        columns = ['名称', '最新价', '涨跌幅', '主力净流入-净额', '主力净流入-净占比']
        if all(col in df.columns for col in columns):
            result = df[columns].copy()
            result.columns = ['名称', '最新价', '涨跌幅', '主力净流入', '主力净占比']
            
            # 转换为数值
            result['最新价'] = pd.to_numeric(result['最新价'], errors='coerce')
            result['涨跌幅'] = pd.to_numeric(result['涨跌幅'], errors='coerce')
            result['主力净流入'] = pd.to_numeric(result['主力净流入'], errors='coerce')
            result['主力净占比'] = pd.to_numeric(result['主力净占比'], errors='coerce')
            
            # 按主力净流入排序
            result = result.sort_values('主力净流入', ascending=False)
            
            return result.head(top)
        else:
            print(f"列名不匹配，可用列: {df.columns.tolist()}")
            return df.head(top)
            
    except Exception as e:
        print(f"获取主力资金排行失败: {e}")
        return pd.DataFrame()

def get_sector_capital_rank():
    """
    获取行业板块资金流向排行
    
    Returns:
        DataFrame with sector capital flow
    """
    try:
        df = safe_ak_call(ak.stock_sector_fund_flow_rank, indicator="今日", sector_type="行业资金流")
        
        if df is None or df.empty:
            print("获取板块资金流向失败或被限流")
            return pd.DataFrame()
        
        return df.head(10)
        
    except Exception as e:
        print(f"获取板块资金流向失败: {e}")
        return pd.DataFrame()

def format_output(df, title="主力资金排行"):
    """格式化输出"""
    print(f"\n=== {title} ===")
    print(f"更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    if df.empty:
        print("暂无数据（可能被限流，请稍后重试）")
        return
    
    print(f"{'排名':<4} {'名称':<10} {'最新价':<10} {'涨跌幅':<8} {'主力净流入(万)':<15} {'主力净占比':<10}")
    print("-" * 70)
    
    for i, (_, row) in enumerate(df.iterrows(), 1):
        name = row.get('名称', 'N/A')[:8]
        price = row.get('最新价', 0)
        change = row.get('涨跌幅', 0)
        main_flow = row.get('主力净流入', 0) / 10000  # 转为万
        main_pct = row.get('主力净占比', 0)
        
        change_str = f"{change:+.2f}%" if change else "N/A"
        print(f"{i:<4} {name:<10} {price:<10.2f} {change_str:<8} {main_flow:<15.1f} {main_pct:<10.2f}%")

if __name__ == "__main__":
    print("正在获取数据，请稍候（含限流保护延迟）...")
    
    # 获取主力资金流入排行
    df_in = get_main_capital_rank(days=1, top=10)
    format_output(df_in, "主力资金流入 TOP10")
    
    # 获取主力资金流出排行
    if not df_in.empty:
        df_out = df_in.tail(10).sort_values('主力净流入')
        format_output(df_out, "主力资金流出 TOP10")
    
    # 获取板块资金流向
    df_sector = get_sector_capital_rank()
    if not df_sector.empty:
        print(f"\n=== 行业板块资金流向 TOP10 ===")
        print(df_sector.to_string())
