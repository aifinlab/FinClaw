#!/usr/bin/env python3
"""
全球宏观仪表盘
整合全球主要经济体数据
"""

import akshare as ak

def get_global_macro():
    """获取全球宏观数据"""
    print("=" * 70)
    print("全球宏观经济仪表盘")
    print("=" * 70)
    
    try:
        # 美国CPI
        us_cpi = ak.macro_usa_cpi_monthly()
        if not us_cpi.empty:
            print(f"\n🇺🇸 美国CPI同比: {us_cpi.iloc[0].get('同比', '--')}%")
    except:
        pass
    
    try:
        # 欧元区CPI
        eu_cpi = ak.macro_euro_cpi_monthly()
        if not eu_cpi.empty:
            print(f"🇪🇺 欧元区CPI同比: {eu_cpi.iloc[0].get('同比', '--')}%")
    except:
        pass
    
    try:
        # 日本CPI
        jp_cpi = ak.macro_japan_cpi_monthly()
        if not jp_cpi.empty:
            print(f"🇯🇵 日本CPI同比: {jp_cpi.iloc[0].get('同比', '--')}%")
    except:
        pass
    
    try:
        # 中国CPI
        cn_cpi = ak.macro_china_cpi_monthly()
        if not cn_cpi.empty:
            print(f"🇨🇳 中国CPI同比: {cn_cpi.iloc[0].get('同比', '--')}%")
    except:
        pass
    
    print("=" * 70)

if __name__ == "__main__":
    get_global_macro()
