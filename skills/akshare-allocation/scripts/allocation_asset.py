#!/usr/bin/env python3
"""
基金资产配置查询
查询基金资产配置结构
"""

import akshare as ak
import argparse
import pandas as pd

def get_asset_allocation(code):
    """获取基金资产配置"""
    try:
        df = ak.fund_portfolio_hold_em(symbol=code)

        if df.empty:
            print(f"未找到基金 {code} 的配置数据")
            return

        # 获取基金名称
        name = df.iloc[0].get('基金名称', code)

        print("=" * 70)
        print(f"{name} ({code}) 资产配置")
        print("=" * 70)

        # 获取资产配置数据
        asset_df = ak.fund_portfolio_asset_allocation_em(symbol=code)

        if not asset_df.empty:
            latest = asset_df.iloc[0]

            print(f"\n【资产配置 - {latest.get('报告期', '--')}】")
            print(f"  股票占比: {latest.get('股票占净值比', '--')}%")
            print(f"  债券占比: {latest.get('债券占净值比', '--')}%")
            print(f"  现金占比: {latest.get('现金占净值比', '--')}%")
            print(f"  其他占比: {latest.get('其他占净值比', '--')}%")
            print(f"  基金净值: {latest.get('基金净值', '--')} 元")

        print("=" * 70)

    except Exception as e:
        print(f"获取失败: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--code', type=str, required=True, help='基金代码')

    args = parser.parse_args()
    get_asset_allocation(args.code)
