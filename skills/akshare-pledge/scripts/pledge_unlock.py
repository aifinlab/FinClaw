#!/usr/bin/env python3
"""
解禁股查询
查询即将解禁的股票
"""

from datetime import datetime, timedelta
import akshare as ak
import argparse
import pandas as pd


def get_unlock_stocks(days=30):
    """获取即将解禁的股票"""
    try:
        df = ak.stock_restricted_release_queue_em()

        if df.empty:
            print("暂无解禁数据")
            return

        # 筛选日期
        df['解禁日期'] = pd.to_datetime(df['解禁日期'])
        start = datetime.now()
        end = start + timedelta(days=days)

        upcoming = df[(df['解禁日期'] >= start) & (df['解禁日期'] <= end)]

        if upcoming.empty:
            print(f"未来{days}天无解禁股")
            return

        print("=" * 90)
        print(f"未来{days}天解禁股一览")
        print("=" * 90)

        print(f"\n{'代码':<10} {'名称':<12} {'解禁日期':<12} {'解禁数量(万股)':<15} {'解禁市值(万)':<15}")
        print("-" * 90)

        for _, row in upcoming.head(50).iterrows():
            print(f"{row['股票代码']:<10} {row['股票简称']:<12} "
                    f"{row['解禁日期'].strftime('%Y-%m-%d'):<12} "
                    f"{row.get('解禁数量(万股)', 0):<15.2f} "
                    f"{row.get('解禁市值(万)', 0):<15.2f}")

        print("=" * 90)

    except Exception as e:
        print(f"获取失败: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--days', type=int, default=30, help='天数')

    args = parser.parse_args()
    get_unlock_stocks(args.days)
