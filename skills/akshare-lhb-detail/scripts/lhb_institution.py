#!/usr/bin/env python3
"""
机构席位分析
分析机构专用席位的交易动向
"""

import akshare as ak
import pandas as pd
import argparse
from datetime import datetime, timedelta

def get_institution_activity(days=30):
    """获取机构席位交易活动"""
    try:
        # 计算日期范围
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        start_str = start_date.strftime('%Y%m%d')
        end_str = end_date.strftime('%Y%m%d')
        
        # 获取龙虎榜数据
        df = ak.stock_lhb_daily_detail(start_date=start_str, end_date=end_str)
        
        if df.empty:
            print("暂无龙虎榜数据")
            return
        
        # 筛选机构席位
        institution_data = df[df['营业部名称'].str.contains('机构专用', na=False)]
        
        if institution_data.empty:
            print("暂无机构席位数据")
            return
        
        print("=" * 90)
        print("机构专用席位分析")
        print(f"统计区间: {start_str} - {end_str}")
        print("=" * 90)
        
        # 总体统计
        print(f"\n【总体统计】")
        print(f"  机构上榜次数: {len(institution_data)}")
        print(f"  涉及股票数: {institution_data['名称'].nunique()} 只")
        
        buy_data = institution_data[institution_data['买卖方向'] == '买入']
        sell_data = institution_data[institution_data['买卖方向'] == '卖出']
        
        total_buy = buy_data['成交额'].sum()
        total_sell = sell_data['成交额'].sum()
        
        print(f"  机构买入金额: {total_buy/1e8:.2f} 亿元")
        print(f"  机构卖出金额: {total_sell/1e8:.2f} 亿元")
        print(f"  净流向: {(total_buy - total_sell)/1e8:.2f} 亿元 ({'净流入↑' if total_buy > total_sell else '净流出↓'})")
        
        # 机构买入排行
        print(f"\n【机构买入金额 TOP15】")
        inst_buy = institution_data[institution_data['买卖方向'] == '买入']
        stock_buy = inst_buy.groupby(['代码', '名称'])['成交额'].sum().sort_values(ascending=False).head(15)
        
        print(f"{'排名':<6} {'代码':<10} {'名称':<12} {'买入金额(万)':<15}")
        print("-" * 60)
        for i, ((code, name), amount) in enumerate(stock_buy.items(), 1):
            print(f"{i:<6} {code:<10} {name:<12} {amount/1e4:<15.1f}")
        
        # 机构卖出排行
        print(f"\n【机构卖出金额 TOP15】")
        inst_sell = institution_data[institution_data['买卖方向'] == '卖出']
        stock_sell = inst_sell.groupby(['代码', '名称'])['成交额'].sum().sort_values(ascending=False).head(15)
        
        print(f"{'排名':<6} {'代码':<10} {'名称':<12} {'卖出金额(万)':<15}")
        print("-" * 60)
        for i, ((code, name), amount) in enumerate(stock_sell.items(), 1):
            print(f"{i:<6} {code:<10} {name:<12} {amount/1e4:<15.1f}")
        
        # 机构净买入排行
        print(f"\n【机构净买入 TOP15】")
        inst_net = institution_data.groupby(['代码', '名称', '买卖方向'])['成交额'].sum().unstack(fill_value=0)
        if '买入' in inst_net.columns and '卖出' in inst_net.columns:
            inst_net['净买入'] = inst_net['买入'] - inst_net['卖出']
            net_buy = inst_net.sort_values('净买入', ascending=False).head(15)
            
            print(f"{'排名':<6} {'代码':<10} {'名称':<12} {'净买入(万)':<15}")
            print("-" * 60)
            for i, ((code, name), row) in enumerate(net_buy.iterrows(), 1):
                print(f"{i:<6} {code:<10} {name:<12} {row['净买入']/1e4:<15.1f}")
        
        print("=" * 90)
        
    except Exception as e:
        print(f"获取数据失败: {e}")

def get_stock_institution(code):
    """获取个股机构交易明细"""
    try:
        # 获取龙虎榜数据
        df = ak.stock_lhb_detail_daily_sina()
        
        # 筛选指定股票
        stock_data = df[df['代码'] == code]
        institution_data = stock_data[stock_data['营业部名称'].str.contains('机构专用', na=False)]
        
        if institution_data.empty:
            print(f"股票 {code} 暂无机构交易记录")
            return
        
        stock_name = institution_data.iloc[0]['名称']
        
        print("=" * 90)
        print(f"{stock_name} ({code}) 机构交易明细")
        print("=" * 90)
        
        # 按日期分组
        dates = institution_data['日期'].unique()
        
        for d in dates[:10]:
            day_data = institution_data[institution_data['日期'] == d]
            buy_data = day_data[day_data['买卖方向'] == '买入']
            sell_data = day_data[day_data['买卖方向'] == '卖出']
            
            buy_amount = buy_data['成交额'].sum() if not buy_data.empty else 0
            sell_amount = sell_data['成交额'].sum() if not sell_data.empty else 0
            
            print(f"\n【{d}】")
            print(f"  机构买入: {buy_amount/1e4:.1f} 万 ({len(buy_data)} 笔)")
            print(f"  机构卖出: {sell_amount/1e4:.1f} 万 ({len(sell_data)} 笔)")
            print(f"  机构净额: {(buy_amount - sell_amount)/1e4:.1f} 万")
        
        print("=" * 90)
        
    except Exception as e:
        print(f"获取数据失败: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='机构席位分析')
    parser.add_argument('--days', type=int, default=30, help='查询天数 (默认30)')
    parser.add_argument('--code', type=str, help='股票代码')
    
    args = parser.parse_args()
    
    if args.code:
        get_stock_institution(args.code)
    else:
        get_institution_activity(args.days)
