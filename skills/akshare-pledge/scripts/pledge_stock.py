#!/usr/bin/env python3
"""
个股股权质押查询
查询指定股票的股权质押情况
"""

import akshare as ak
import pandas as pd
import argparse

def get_stock_pledge(code):
    """获取个股股权质押数据"""
    try:
        # 获取股权质押数据
        df = ak.stock_gpzy_pledge_ratio_detail_em()
        
        # 筛选指定股票
        stock_data = df[df['股票代码'] == code]
        
        if stock_data.empty:
            print(f"未找到 {code} 的质押数据")
            return
        
        name = stock_data.iloc[0]['股票名称']
        ratio = stock_data.iloc[0]['质押比例']
        
        print("=" * 70)
        print(f"{name} ({code}) 股权质押情况")
        print("=" * 70)
        
        print(f"\n【质押概况】")
        print(f"  质押比例: {ratio}%")
        
        if ratio >= 50:
            risk = "极高风险"
        elif ratio >= 30:
            risk = "高风险"
        elif ratio >= 20:
            risk = "中等风险"
        else:
            risk = "低风险"
        
        print(f"  风险等级: {risk}")
        
        # 获取详细质押信息
        df_detail = ak.stock_gpzy_profile_em()
        detail = df_detail[df_detail['股票代码'] == code]
        
        if not detail.empty:
            d = detail.iloc[0]
            print(f"\n【详细数据】")
            print(f"  质押总股数: {d.get('质押总股数', '--')} 股")
            print(f"  质押总市值: {d.get('质押总市值', '--')} 元")
            print(f"  质押笔数: {d.get('质押笔数', '--')} 笔")
        
        print("=" * 70)
        
    except Exception as e:
        print(f"获取失败: {e}")

def get_high_pledge(limit=50):
    """获取高质押比例股票"""
    try:
        df = ak.stock_gpzy_pledge_ratio_em()
        
        if df.empty:
            print("暂无数据")
            return
        
        print("=" * 70)
        print(f"股权质押比例排行 TOP{limit}")
        print("=" * 70)
        
        print(f"{'代码':<10} {'名称':<12} {'质押比例%':<12} {'风险等级':<12}")
        print("-" * 70)
        
        for _, row in df.head(limit).iterrows():
            ratio = row['质押比例']
            if ratio >= 50:
                risk = "🔴 极高"
            elif ratio >= 30:
                risk = "🟠 高"
            elif ratio >= 20:
                risk = "🟡 中"
            else:
                risk = "🟢 低"
            
            print(f"{row['股票代码']:<10} {row['股票简称']:<12} "
                  f"{ratio:<12.2f} {risk:<12}")
        
        print("=" * 70)
        
    except Exception as e:
        print(f"获取失败: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--code', type=str, help='股票代码')
    parser.add_argument('--high', action='store_true', help='高质押排行')
    parser.add_argument('--limit', type=int, default=50, help='数量')
    
    args = parser.parse_args()
    
    if args.high:
        get_high_pledge(args.limit)
    elif args.code:
        get_stock_pledge(args.code)
    else:
        get_high_pledge(50)
