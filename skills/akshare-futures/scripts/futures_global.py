#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
外盘期货行情 - AkShare
获取全球期货行情数据
"""

import akshare as ak

def get_global_futures():
    """获取全球期货行情"""
    try:
        df = ak.futures_global_spot_em()
        return df
    except Exception as e:
        print(f"获取全球期货行情失败: {e}")
        return None

def get_foreign_commodity(symbol="CT"):
    """
    获取外盘商品期货
    symbol: CT(棉花), NID(镍), GC(黄金), SI(白银)等
    """
    try:
        df = ak.futures_foreign_commodity_realtime(symbol=symbol)
        return df
    except Exception as e:
        print(f"获取外盘商品失败: {e}")
        return None

def format_global_report():
    """格式化全球期货报告"""
    print("=" * 80)
    print("🌍 全球期货行情")
    print("=" * 80)
    
    df = get_global_futures()
    if df is not None and not df.empty:
        # 贵金属
        print("\n✨ 贵金属")
        print("-" * 80)
        metals = df[df['名称'].str.contains('金|银', na=False)]
        if not metals.empty:
            print(metals[['名称', '最新价', '涨跌额', '涨跌幅']].head(10).to_string(index=False))
        
        # 能源
        print("\n⚡ 能源")
        print("-" * 80)
        energy = df[df['名称'].str.contains('油|气', na=False)]
        if not energy.empty:
            print(energy[['名称', '最新价', '涨跌额', '涨跌幅']].head(10).to_string(index=False))
        
        # 农产品
        print("\n🌾 农产品")
        print("-" * 80)
        agri = df[df['名称'].str.contains('豆|麦|棉|糖|咖啡|可可', na=False)]
        if not agri.empty:
            print(agri[['名称', '最新价', '涨跌额', '涨跌幅']].head(10).to_string(index=False))
        
        # 有色金属
        print("\n🔶 有色金属")
        print("-" * 80)
        metals = df[df['名称'].str.contains('铜|铝|锌|镍|铅|锡', na=False)]
        if not metals.empty:
            print(metals[['名称', '最新价', '涨跌额', '涨跌幅']].head(10).to_string(index=False))
    else:
        print("未获取到数据")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    format_global_report()
