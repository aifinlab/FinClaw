#!/usr/bin/env python3
"""
价格预警
设置价格突破或跌破预警
"""

import akshare as ak
import argparse
import pandas as pd

def check_price_alert(code, above=None, below=None):
    """检查价格预警"""
    try:
        # 获取实时行情
        df = ak.stock_zh_a_spot_em()
        stock = df[df['代码'] == code]

        if stock.empty:
            print(f"未找到股票: {code}")
            return

        name = stock.iloc[0]['名称']
        price = stock.iloc[0]['最新价']
        change = stock.iloc[0]['涨跌幅']

        print("=" * 70)
        print(f"价格预警检查 - {name} ({code})")
        print("=" * 70)

        print(f"\n当前价格: {price} (涨跌幅: {change}%)")

        alerts = []

        if above and price >= above:
            alerts.append(f"🚨 突破预警价 {above}！当前 {price}")

        if below and price <= below:
            alerts.append(f"🚨 跌破预警价 {below}！当前 {price}")

        if alerts:
            print("\n【预警触发】")
            for alert in alerts:
                print(f"  {alert}")
        else:
            print("\n✅ 价格正常，未触发预警")
            if above:
                print(f"  距离上方预警价 {above}: {(above-price)/price*100:.2f}%")
            if below:
                print(f"  距离下方预警价 {below}: {(price-below)/price*100:.2f}%")

        print("=" * 70)

    except Exception as e:
        print(f"检查失败: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--code', type=str, required=True, help='股票代码')
    parser.add_argument('--above', type=float, help='突破预警价')
    parser.add_argument('--below', type=float, help='跌破预警价')

    args = parser.parse_args()

    check_price_alert(args.code, args.above, args.below)
