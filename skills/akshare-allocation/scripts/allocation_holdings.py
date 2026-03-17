#!/usr/bin/env python3
"""
基金重仓股查询
查询基金重仓持股
"""

import akshare as ak
import pandas as pd
import argparse

def get_fund_holdings(code):
    """获取基金重仓股"""
    try:
        df = ak.fund_portfolio_hold_em(symbol=code)
        
        if df.empty:
            print(f"未找到基金 {code} 的持仓数据")
            return
        
        name = df.iloc[0].get('基金名称', code)
        
        print("=" * 90)
        print(f"{name} ({code}) 重仓持股")
        print("=" * 90)
        
        print(f"{'排名':<6} {'股票代码':<10} {'股票名称':<12} {'持仓占比%':<12} {'持仓股数(万股)':<15}")
        print("-" * 90)
        
        for i, (_, row) in enumerate(df.head(20).iterrows(), 1):
            print(f"{i:<6} {row.get('股票代码', '--'):<10} {row.get('股票名称', '--'):<12} "
                  f"{row.get('占净值比例', '--'):<12} {row.get('持仓股数', 0)/1e4:<15.2f}")
        
        print("=" * 90)
        
    except Exception as e:
        print(f"获取失败: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--code', type=str, required=True, help='基金代码')
    
    args = parser.parse_args()
    get_fund_holdings(args.code)
