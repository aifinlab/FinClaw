#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大宗商品/石油价格查询
获取国内外原油及相关大宗商品价格走势
"""

from datetime import datetime, timedelta
import akshare as ak
import pandas as pd

def get_commodity_oil():
    """获取大宗商品石油相关价格"""
    print("=" * 80)
    print("🛢️  大宗商品 - 石油价格走势")
    print("=" * 80)
    print(f"更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # 1. 国内原油期货 (上海国际能源交易中心)
    print("📍 国内原油期货 (INE)")
    print("-" * 80)
    try:
        df = ak.futures_zh_spot(symbol="SC0", market="CF", adjust='0')
        if df is not None and not df.empty:
            row = df.iloc[0]
            current = float(row['current_price']) if pd.notna(row['current_price']) else 0
            last_close = float(row['last_settle_price']) if pd.notna(row['last_settle_price']) else 0
            change = current - last_close
            change_pct = (change / last_close * 100) if last_close else 0

            print(f"   合约: 原油连续 (SC0)")
            print(f"   最新价: ¥{current:.2f}/桶")
            print(f"   涨跌额: {change:+.2f}")
            print(f"   涨跌幅: {change_pct:+.2f}%")
            print(f"   成交量: {row['volume']}")
            print(f"   持仓量: {row['hold']}")
    except Exception as e:
        print(f"   获取失败: {e}")

    print()

    # 2. 全球期货行情 - 原油相关
    print("🌍 国际原油期货市场")
    print("-" * 80)
    try:
        df = ak.futures_global_spot_em()
        if df is not None and not df.empty:
            # 筛选原油相关
            oil_keywords = ['原油', 'Oil', '布伦特', 'Brent', 'WTI', '汽油', '燃油']
            mask = df['名称'].str.contains('|'.join(oil_keywords), na=False, case=False)
            oil_df = df[mask]

            if not oil_df.empty:
                for _, row in oil_df.head(15).iterrows():
                    name = row['名称']
                    price = row['最新价']
                    change = row['涨跌额']
                    change_pct = row['涨跌幅']

                    # 格式化输出
                    symbol = "📈" if change_pct and change_pct > 0 else "📉" if change_pct and change_pct < 0 else "➖"
                    print(f"   {symbol} {name:20s} 价格: {price:>12}  涨跌: {change:>+8.2f} ({change_pct:>+.2f}%)")
            else:
                print("   暂未获取到原油相关数据")
    except Exception as e:
        print(f"   获取失败: {e}")

    print()

    # 3. 外盘商品期货 - 原油
    print("🌐 外盘原油主力合约")
    print("-" * 80)
    try:
        # WTI原油
        df_wti = ak.futures_foreign_commodity_realtime(symbol="CL")
        if df is not None and not df.empty:
            print("   🛢️ WTI原油:")
            for _, row in df_wti.head(5).iterrows():
                print(f"      {row['名称']:20s} 价格: ${row['最新价']:>8}  涨跌: {row['涨跌额']:>+8.2f}")
    except Exception as e:
        print(f"   WTI获取失败: {e}")

    try:
        # 布伦特原油
        df_brent = ak.futures_foreign_commodity_realtime(symbol="BZ")
        if df is not None and not df.empty:
            print("   🛢️ 布伦特原油:")
            for _, row in df_brent.head(5).iterrows():
                print(f"      {row['名称']:20s} 价格: ${row['最新价']:>8}  涨跌: {row['涨跌额']:>+8.2f}")
    except Exception as e:
        print(f"   布伦特获取失败: {e}")

    print()
    print("=" * 80)

    # 4. 其他大宗商品概览
    print("📊 其他大宗商品概览")
    print("-" * 80)
    try:
        df = ak.futures_global_spot_em()
        if df is not None and not df.empty:
            # 黄金
            print("\n   ✨ 贵金属:")
            gold = df[df['名称'].str.contains('黄金|Gold', na=False, case=False)]
            for _, row in gold.head(3).iterrows():
                print(f"      {row['名称']:20s} 价格: {row['最新价']:>10}  涨跌: {row['涨跌幅']:>+6.2f}%")

            # 有色金属
            print("\n   🔶 有色金属:")
            metals = df[df['名称'].str.contains('铜|Copper|铝|Aluminum|锌|Zinc', na=False, case=False)]
            for _, row in metals.head(5).iterrows():
                print(f"      {row['名称']:20s} 价格: {row['最新价']:>10}  涨跌: {row['涨跌幅']:>+6.2f}%")

            # 农产品
            print("\n   🌾 农产品:")
            agri = df[df['名称'].str.contains('大豆|Soybean|玉米|Corn|小麦|Wheat', na=False, case=False)]
            for _, row in agri.head(4).iterrows():
                print(f"      {row['名称']:20s} 价格: {row['最新价']:>10}  涨跌: {row['涨跌幅']:>+6.2f}%")
    except Exception as e:
        print(f"   获取失败: {e}")

    print()
    print("=" * 80)
    print("💡 提示: 国内原油代码 SC0 | 国际WTI代码 CL | 布伦特代码 BZ")
    print("=" * 80)

if __name__ == "__main__":
    get_commodity_oil()
