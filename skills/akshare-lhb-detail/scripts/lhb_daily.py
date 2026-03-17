#!/usr/bin/env python3
"""
每日龙虎榜数据查询
获取当日龙虎榜上榜股票及交易明细
"""

import akshare as ak
import pandas as pd
from datetime import datetime
import argparse

def get_daily_lhb(date=None):
    """
    获取每日龙虎榜数据
    
    Args:
        date: 日期格式 YYYYMMDD，默认最新
    """
    try:
        # 获取龙虎榜数据
        if date:
            df = ak.stock_lhb_detail_em(start_date=date, end_date=date)
        else:
            # 获取最近交易日数据
            from datetime import datetime, timedelta
            end = datetime.now()
            start = end - timedelta(days=7)
            df = ak.stock_lhb_detail_em(start_date=start.strftime('%Y%m%d'), end_date=end.strftime('%Y%m%d'))
        
        if df.empty:
            print("暂无龙虎榜数据")
            return
        
        # 获取日期
        trade_date = df['成交日期'].iloc[0] if '成交日期' in df.columns else '最新'
        
        print("=" * 90)
        print(f"龙虎榜数据 | 日期: {trade_date}")
        print("=" * 90)
        
        # 按股票分组统计
        stock_summary = df.groupby(['代码', '名称']).agg({
            '成交额': 'sum',
            '营业部名称': 'count'
        }).reset_index()
        stock_summary.columns = ['代码', '名称', '总成交额', '上榜次数']
        stock_summary = stock_summary.sort_values('总成交额', ascending=False)
        
        print(f"\n【上榜股票】共 {len(stock_summary)} 只")
        print(f"{'代码':<10} {'名称':<12} {'总成交额(万)':<15} {'上榜次数':<10}")
        print("-" * 90)
        
        for _, row in stock_summary.head(30).iterrows():
            print(f"{row['代码']:<10} {row['名称']:<12} "
                  f"{row['总成交额']/1e4:<15.1f} {row['上榜次数']:<10.0f}")
        
        print("=" * 90)
        
    except Exception as e:
        print(f"获取数据失败: {e}")

def get_lhb_detail(code, date=None):
    """获取个股龙虎榜明细"""
    try:
        from datetime import datetime, timedelta
        end = datetime.now()
        start = end - timedelta(days=30)
        
        df = ak.stock_lhb_detail_em(start_date=start.strftime('%Y%m%d'), end_date=end.strftime('%Y%m%d'))
        
        # 筛选指定股票
        stock_data = df[df['代码'] == code]
        
        if stock_data.empty:
            print(f"未找到股票 {code} 的龙虎榜数据")
            return
        
        stock_name = stock_data.iloc[0]['名称']
        
        print("=" * 90)
        print(f"{stock_name} ({code}) 龙虎榜明细")
        print("=" * 90)
        
        # 按日期分组
        dates = stock_data['日期'].unique()
        
        for d in dates[:5]:  # 最近5天
            day_data = stock_data[stock_data['日期'] == d]
            print(f"\n【{d}】")
            
            # 买入营业部
            buy_data = day_data[day_data['买卖方向'] == '买入']
            if not buy_data.empty:
                print(f"  买入金额: {buy_data['成交额'].sum()/1e4:.1f} 万")
                print("  买入营业部:")
                for _, row in buy_data.head(5).iterrows():
                    print(f"    {row['营业部名称'][:30]:<32} {row['成交额']/1e4:>8.1f}万")
            
            # 卖出营业部
            sell_data = day_data[day_data['买卖方向'] == '卖出']
            if not sell_data.empty:
                print(f"  卖出金额: {sell_data['成交额'].sum()/1e4:.1f} 万")
                    
        print("=" * 90)
        
    except Exception as e:
        print(f"获取明细失败: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='龙虎榜数据查询')
    parser.add_argument('--date', type=str, help='日期 (格式: YYYYMMDD)')
    parser.add_argument('--code', type=str, help='股票代码')
    
    args = parser.parse_args()
    
    if args.code:
        get_lhb_detail(args.code, args.date)
    else:
        get_daily_lhb(args.date)
