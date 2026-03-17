#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PCR情绪指标 - AkShare
Put-Call Ratio 分析市场情绪
"""

import akshare as ak

def get_option_risk():
    """获取期权风险指标（含PCR）"""
    try:
        df = ak.option_risk_analysis_em()
        return df
    except Exception as e:
        print(f"获取PCR失败: {e}")
        return None

def calculate_pcr():
    """计算PCR指标"""
    try:
        # 通过风险分析数据估算PCR
        df = get_option_risk()
        if df is not None:
            # 统计认购/认沽数量
            call_count = df[df['期权名称'].str.contains('购', na=False)].shape[0]
            put_count = df[df['期权名称'].str.contains('沽', na=False)].shape[0]
            
            if call_count > 0:
                pcr = put_count / call_count
                return pcr, put_count, call_count
        return None, 0, 0
    except:
        return None, 0, 0

def format_pcr_report():
    """格式化PCR报告"""
    print("=" * 80)
    print("📊 PCR情绪指标分析")
    print("=" * 80)
    
    pcr, put_count, call_count = calculate_pcr()
    
    print(f"\n📈 PCR数据:")
    print(f"   认沽期权数量: {put_count}")
    print(f"   认购期权数量: {call_count}")
    
    if pcr is not None:
        print(f"   PCR值: {pcr:.2f}")
        
        print(f"\n💡 情绪判断:")
        if pcr > 1.0:
            print("   🔴 PCR > 1.0: 看跌情绪浓厚，可能见底")
        elif pcr > 0.8:
            print("   🟡 PCR 0.8-1.0: 偏空情绪")
        elif pcr > 0.7:
            print("   ➡️ PCR 0.7-0.8: 情绪中性")
        else:
            print("   🟢 PCR < 0.7: 看涨情绪浓厚，可能见顶")
    else:
        print("   无法计算PCR")
    
    # 希腊字母
    df = get_option_risk()
    if df is not None and not df.empty:
        print(f"\n📊 希腊字母示例:")
        print(df[['期权名称', 'Delta', 'Gamma', 'Theta', 'Vega']].head(10).to_string(index=False))
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    format_pcr_report()
