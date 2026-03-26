#!/usr/bin/env python3
"""
营业部追踪
追踪知名游资营业部交易动向
"""

from datetime import datetime, timedelta
import akshare as ak
import argparse
import pandas as pd

# 知名游资营业部列表
FAMOUS_DEALERS = {
    '中信证券上海溧阳路': '孙哥',
    '中信证券上海淮海中路': '游资',
    '国泰君安证券上海江苏路': '章盟主',
    '光大证券佛山绿景路': '佛山系',
    '国泰君安证券深圳益田路': '游资',
    '华泰证券深圳益田路荣超商务中心': '游资',
    '中信证券上海古北路': '游资',
    '中国银河证券绍兴': '赵老哥',
    '国金证券上海奉贤区金碧路': '游资',
    '东方财富证券拉萨团结路': '散户集中营',
    '东方财富证券拉萨东环路': '散户集中营',
    '招商证券深圳深南东路': '游资',
    '华鑫证券上海宛平南路': '炒股养家',
}

def get_dealer_activity(dealer_name=None, days=30):
    """
    追踪营业部交易活动

    Args:
        dealer_name: 营业部名称，默认显示知名游资
        days: 查询天数
    """
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

        if dealer_name:
            # 追踪指定营业部
            dealer_data = df[df['营业部名称'].str.contains(dealer_name, na=False)]

            if dealer_data.empty:
                print(f"未找到营业部 '{dealer_name}' 的交易记录")
                return

            print("=" * 90)
            print(f"营业部追踪: {dealer_name}")
            print(f"统计区间: {start_str} - {end_str}")
            print("=" * 90)

            # 统计交易情况
            print(f"\n【交易统计】")
            print(f"  上榜次数: {len(dealer_data)}")
            print(f"  涉及股票: {dealer_data['名称'].nunique()} 只")

            buy_data = dealer_data[dealer_data['买卖方向'] == '买入']
            sell_data = dealer_data[dealer_data['买卖方向'] == '卖出']

            print(f"  买入金额: {buy_data['成交额'].sum()/1e4:.1f} 万")
            print(f"  卖出金额: {sell_data['成交额'].sum()/1e4:.1f} 万")

            # 最近交易
            print(f"\n【最近交易】")
            print(f"{'日期':<12} {'代码':<10} {'名称':<12} {'方向':<6} {'金额(万)':<12}")
            print("-" * 90)

            for _, row in dealer_data.head(20).iterrows():
                print(f"{row['成交日期']:<12} {row['代码']:<10} {row['名称']:<12} "
                      f"{row['买卖方向']:<6} {row['成交额']/1e4:<12.1f}")
        else:
            # 显示知名游资统计
            print("=" * 90)
            print("知名游资营业部统计")
            print(f"统计区间: {start_str} - {end_str}")
            print("=" * 90)

            print(f"\n{'营业部':<35} {'昵称':<12} {'上榜次数':<10} {'买入(万)':<12} {'卖出(万)':<12}")
            print("-" * 90)

            for dealer, nickname in FAMOUS_DEALERS.items():
                dealer_data = df[df['营业部名称'].str.contains(dealer.split('证券')[1] if '证券' in dealer else dealer, na=False)]

                if not dealer_data.empty:
                    count = len(dealer_data)
                    buy_amount = dealer_data[dealer_data['买卖方向'] == '买入']['成交额'].sum() / 1e4
                    sell_amount = dealer_data[dealer_data['买卖方向'] == '卖出']['成交额'].sum() / 1e4

                    print(f"{dealer[:35]:<35} {nickname:<12} {count:<10} {buy_amount:<12.1f} {sell_amount:<12.1f}")

        print("=" * 90)

    except Exception as e:
        print(f"获取数据失败: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='营业部追踪')
    parser.add_argument('--name', type=str, help='营业部名称')
    parser.add_argument('--days', type=int, default=30, help='查询天数 (默认30)')

    args = parser.parse_args()

    get_dealer_activity(args.name, args.days)
