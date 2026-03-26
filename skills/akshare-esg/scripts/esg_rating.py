#!/usr/bin/env python3
"""
ESG评级查询
查询个股ESG评级
"""

import akshare as ak
import argparse
import pandas as pd


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

        print("\n【行业对比】")
        industry = row.get('行业', '未知')
        print(f"  所属行业: {industry}")
        print(f"  行业排名: {row.get('行业排名', '--')}")

        print("=" * 70)

    except Exception as e:
        print(f"获取ESG评级失败: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--code', type=str, required=True, help='股票代码')

    args = parser.parse_args()
    get_esg_rating(args.code)
