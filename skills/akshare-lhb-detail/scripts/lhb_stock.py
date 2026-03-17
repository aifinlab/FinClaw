#!/usr/bin/env python3
"""
龙虎榜个股查询
查询指定股票的历史龙虎榜记录
"""

import akshare as ak
import pandas as pd
import argparse

def get_stock_lhb_history(code, limit=10):
    """获取个股龙虎榜历史"""
    try:
        # 获取龙虎榜数据
        df = ak.stock_lhb_detail_daily_sina()
        
        # 筛选指定股票
        stock_data = df[df['代码'] == code]
        
        if stock_data.empty:
            print(f"未找到股票 {code} 的龙虎榜数据")
            return
        
        stock_name = stock_data.iloc[0]['名称']
        
        # 获取股票历史数据
        dates = stock_data['日期'].unique()[:limit]
        
        print("=" * 90)
        print(f"{stock_name} ({code}) 龙虎榜历史 (最近{len(dates)}次)")
        print("=" * 90)
        
        for d in dates:
            day_data = stock_data[stock_data['日期'] == d]
            
            print(f"\n【{d}】")
            
            # 买入营业部
            buy_data = day_data[day_data['买卖方向'] == '买入'].sort_values('成交额', ascending=False)
            if not buy_data.empty:
                total_buy = buy_data['成交额'].sum()
                print(f"  买入前五 (合计 {total_buy/1e4:.1f} 万):")
                for _, row in buy_data.head(5).iterrows():
                    dealer = row['营业部名称']
                    if len(dealer) > 28:
                        dealer = dealer[:28] + "..."
                    print(f"    {dealer:<32} {row['成交额']/1e4:>8.1f}万")
            
            # 卖出营业部
            sell_data = day_data[day_data['买卖方向'] == '卖出'].sort_values('成交额', ascending=False)
            if not sell_data.empty:
                total_sell = sell_data['成交额'].sum()
                print(f"  卖出前五 (合计 {total_sell/1e4:.1f} 万):")
                for _, row in sell_data.head(5).iterrows():
                    dealer = row['营业部名称']
                    if len(dealer) > 28:
                        dealer = dealer[:28] + "..."
                    print(f"    {dealer:<32} {row['成交额']/1e4:>8.1f}万")
            
            # 计算净额
            net = buy_data['成交额'].sum() - sell_data['成交额'].sum()
            print(f"  龙虎榜净额: {net/1e4:.1f} 万 ({'净流入' if net > 0 else '净流出'})")
        
        print("=" * 90)
        
    except Exception as e:
        print(f"获取数据失败: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='龙虎榜个股查询')
    parser.add_argument('--code', type=str, required=True, help='股票代码')
    parser.add_argument('--limit', type=int, default=10, help='查询条数 (默认10)')
    
    args = parser.parse_args()
    
    get_stock_lhb_history(args.code, args.limit)
