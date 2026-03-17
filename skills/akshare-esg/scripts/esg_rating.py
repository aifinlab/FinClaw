#!/usr/bin/env python3
"""
ESG评级查询
查询个股ESG评级
"""

import akshare as ak
import pandas as pd
import argparse

def get_esg_rating(code):
    """获取ESG评级"""
    try:
        df = ak.stock_esg_hz_sina()
        
        stock = df[df['股票代码'] == code]
        
        if stock.empty:
            print(f"未找到 {code} 的ESG数据")
            return
        
        print("=" * 70)
        print(f"ESG评级 - {stock.iloc[0].get('股票简称', code)} ({code})")
        print("=" * 70)
        
        row = stock.iloc[0]
        print(f"\n【华证ESG评级】")
        print(f"  ESG评级: {row.get('ESG评级', '--')}")
        print(f"  环境(E): {row.get('环境', '--')}")
        print(f"  社会(S): {row.get('社会', '--')}")
        print(f"  治理(G): {row.get('治理', '--')}")
        print(f"  评级日期: {row.get('评级日期', '--')}")
        print(f"  行业排名: {row.get('行业排名', '--')}/{row.get('行业总数', '--')}")
        
        print("=" * 70)
        
    except Exception as e:
        print(f"获取失败: {e}")

def get_esg_rank():
    """获取ESG排行"""
    try:
        df = ak.stock_esg_hz_sina()
        
        if df.empty:
            print("暂无数据")
            return
        
        print("=" * 90)
        print("ESG评级排行")
        print("=" * 90)
        
        # 按ESG评分排序（假设有评分列，这里用行业排名）
        df_sorted = df.sort_values('行业排名').head(30)
        
        print(f"{'代码':<10} {'名称':<12} {'ESG评级':<10} {'行业排名':<12}")
        print("-" * 60)
        
        for _, row in df_sorted.iterrows():
            print(f"{row['股票代码']:<10} {row.get('股票简称', '--'):<12} "
                  f"{row.get('ESG评级', '--'):<10} {row.get('行业排名', '--'):<12}")
        
        print("=" * 90)
        
    except Exception as e:
        print(f"获取失败: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--code', type=str, help='股票代码')
    
    args = parser.parse_args()
    
    if args.code:
        get_esg_rating(args.code)
    else:
        get_esg_rank()
