#!/usr/bin/env python3
"""
杠杆资金流向分析
分析融资融券资金流向，识别杠杆资金偏好
"""

import akshare as ak
import argparse
import pandas as pd

def analyze_margin_flow():
    """分析融资融券资金流向"""
    try:
        # 获取深圳市场数据
        df_sz = ak.stock_margin_detail_szse(date="")
        # 获取上海市场数据
        df_sh = ak.stock_margin_detail_shse(date="")

        if df_sz.empty or df_sh.empty:
            print("暂无融资融券数据")
            return

        print("=" * 80)
        print("杠杆资金流向分析")
        print("=" * 80)

        # 计算净买入
        df_sz['融资净买入'] = df_sz['融资买入额'] - df_sz['融资偿还额']
        df_sh['融资净买入'] = df_sh['融资买入额'] - df_sh['融资偿还额']

        # 合并数据
        df_all = pd.concat([df_sz, df_sh], ignore_index=True)

        # 总体统计
        total_margin = df_all['融资融券余额'].sum()
        total_buy = df_all['融资买入额'].sum()
        total_repay = df_all['融资偿还额'].sum()
        net_buy = total_buy - total_repay

        print("\n【市场整体】")
        print(f"  融资融券总余额: {total_margin/1e12:.2f} 万亿元")
        print(f"  当日融资买入:   {total_buy/1e8:.2f} 亿元")
        print(f"  当日融资偿还:   {total_repay/1e8:.2f} 亿元")
        print(f"  融资净买入:     {net_buy/1e8:.2f} 亿元 ({'流入↑' if net_buy > 0 else '流出↓'})")

        # 净买入排行
        print("\n【融资净买入 TOP10】")
        df_net = df_all.sort_values('融资净买入', ascending=False).head(10)
        print(f"{'代码':<10} {'名称':<12} {'净买入(万)':<15} {'余额(亿)':<12}")
        print("-" * 60)
        for _, row in df_net.iterrows():
            print(f"{row['证券代码']:<10} {row['证券简称']:<12} "
                  f"{row['融资净买入']/1e4:<15.1f} {row['融资余额']/1e8:<12.2f}")

        # 净卖出排行
        print("\n【融资净卖出 TOP10】")
        df_net_sell = df_all.sort_values('融资净买入', ascending=True).head(10)
        print(f"{'代码':<10} {'名称':<12} {'净卖出(万)':<15} {'余额(亿)':<12}")
        print("-" * 60)
        for _, row in df_net_sell.iterrows():
            print(f"{row['证券代码']:<10} {row['证券简称']:<12} "
                  f"{abs(row['融资净买入'])/1e4:<15.1f} {row['融资余额']/1e8:<12.2f}")

        # 融券活跃度
        print("\n【融券卖出活跃 TOP10】")
        df_short = df_all.sort_values('融券卖出量', ascending=False).head(10)
        print(f"{'代码':<10} {'名称':<12} {'卖出量(万股)':<15} {'余额(万)':<12}")
        print("-" * 60)
        for _, row in df_short.iterrows():
            print(f"{row['证券代码']:<10} {row['证券简称']:<12} "
                  f"{row['融券卖出量']/1e4:<15.1f} {row['融券余额']/1e4:<12.1f}")

        print("=" * 80)

    except Exception as e:
        print(f"分析失败: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='杠杆资金流向分析')

    args = parser.parse_args()

    analyze_margin_flow()
