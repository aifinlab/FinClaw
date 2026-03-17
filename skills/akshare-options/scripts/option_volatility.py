#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
隐含波动率分析 - AkShare
"""

import akshare as ak

def get_option_volatility():
    """获取期权隐含波动率"""
    try:
        df = ak.option_value_analysis_em()
        return df
    except Exception as e:
        print(f"获取波动率失败: {e}")
        return None

def format_volatility_report():
    """格式化波动率报告"""
    print("=" * 80)
    print("📊 期权隐含波动率分析")
    print("=" * 80)
    
    df = get_option_volatility()
    if df is not None and not df.empty:
        print("\n📈 期权价值分析:")
        print(df.head(20).to_string(index=False))
        
        # 波动率统计
        if '隐含波动率' in df.columns:
            iv_mean = df['隐含波动率'].mean()
            iv_max = df['隐含波动率'].max()
            iv_min = df['隐含波动率'].min()
            
            print(f"\n💡 波动率统计:")
            print(f"   平均IV: {iv_mean:.2f}%")
            print(f"   最高IV: {iv_max:.2f}%")
            print(f"   最低IV: {iv_min:.2f}%")
            
            if iv_mean > 30:
                print("   判断: 🔴 波动率偏高，市场恐慌")
            elif iv_mean > 20:
                print("   判断: 🟡 波动率适中")
            else:
                print("   判断: 🟢 波动率偏低，市场平静")
    else:
        print("未获取到数据")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    format_volatility_report()
