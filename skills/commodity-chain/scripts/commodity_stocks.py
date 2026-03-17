#!/usr/bin/env python3
"""
商品产业链分析
分析大宗商品相关股票
"""

import akshare as ak

def get_commodity_stocks():
    """获取商品相关股票"""
    print("=" * 70)
    print("商品产业链相关股票")
    print("=" * 70)
    
    try:
        # 铜相关
        print("\n【铜产业链】")
        df = ak.stock_board_industry_name_ths()
        copper = df[df['行业名称'].str.contains('铜', na=False)]
        for _, row in copper.head(5).iterrows():
            print(f"  {row['行业名称']}")
    except:
        pass
    
    try:
        # 黄金相关
        print("\n【黄金产业链】")
        gold = df[df['行业名称'].str.contains('金', na=False)]
        for _, row in gold.head(5).iterrows():
            print(f"  {row['行业名称']}")
    except:
        pass
    
    print("=" * 70)

if __name__ == "__main__":
    get_commodity_stocks()
