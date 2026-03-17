#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
宏观经济概览仪表盘 - AkShare
整合GDP、CPI、PPI、M2、PMI、利率等核心指标
"""

import akshare as ak
import pandas as pd

def get_latest_indicators():
    """获取最新宏观指标"""
    indicators = {}
    
    try:
        # GDP - 使用正确的字段名
        gdp_df = ak.macro_china_gdp_yearly()
        indicators['gdp_quarter'] = gdp_df.iloc[-1]['日期']
        indicators['gdp_yoy'] = str(gdp_df.iloc[-1]['今值'])
    except Exception as e:
        indicators['gdp_yoy'] = 'N/A'
    
    try:
        # CPI - 使用正确的字段名
        cpi_df = ak.macro_china_cpi()
        indicators['cpi_date'] = cpi_df.iloc[-1]['月份']
        indicators['cpi_yoy'] = str(cpi_df.iloc[-1]['全国-同比增长'])
    except Exception as e:
        indicators['cpi_yoy'] = 'N/A'
    
    try:
        # PPI
        ppi_df = ak.macro_china_ppi()
        indicators['ppi_yoy'] = str(ppi_df.iloc[-1].iloc[2])  # 第三列是同比
    except Exception as e:
        indicators['ppi_yoy'] = 'N/A'
    
    try:
        # M2
        m2_df = ak.macro_china_m2()
        indicators['m2_yoy'] = str(m2_df.iloc[-1].iloc[2])  # M2同比
        indicators['m1_yoy'] = str(m2_df.iloc[-1].iloc[4])  # M1同比
    except Exception as e:
        indicators['m2_yoy'] = 'N/A'
        indicators['m1_yoy'] = 'N/A'
    
    try:
        # PMI
        pmi_df = ak.macro_china_pmi()
        indicators['pmi'] = str(pmi_df.iloc[-1].iloc[1])  # 制造业PMI
        indicators['pmi_date'] = str(pmi_df.iloc[-1].iloc[0])  # 日期
    except Exception as e:
        indicators['pmi'] = 'N/A'
    
    try:
        # LPR
        lpr_df = ak.macro_china_lpr()
        indicators['lpr_1y'] = str(lpr_df.iloc[-1].iloc[1])  # 1年期
        indicators['lpr_5y'] = str(lpr_df.iloc[-1].iloc[2])  # 5年期
    except Exception as e:
        indicators['lpr_1y'] = 'N/A'
        indicators['lpr_5y'] = 'N/A'
    
    try:
        # 汇率
        rmb_df = ak.macro_china_rmb()
        indicators['usd_cny'] = str(rmb_df.iloc[-1].iloc[1])  # 美元/人民币
    except Exception as e:
        indicators['usd_cny'] = 'N/A'
    
    return indicators

def judge_economic_cycle(gdp, cpi, pmi):
    """判断经济周期阶段"""
    try:
        gdp_val = float(gdp) if gdp != 'N/A' else 0
        cpi_val = float(cpi) if cpi != 'N/A' else 0
        pmi_val = float(pmi) if pmi != 'N/A' else 50
        
        if gdp_val > 5 and cpi_val < 2 and pmi_val > 50:
            return "复苏期", "🟢 GDP增长+CPI低位+PMI扩张，经济向好"
        elif gdp_val > 5 and cpi_val > 3 and pmi_val > 50:
            return "过热期", "🔴 GDP高增+CPI高位+PMI扩张，警惕通胀"
        elif gdp_val < 5 and cpi_val > 3 and pmi_val < 50:
            return "滞胀期", "🟡 GDP放缓+CPI高位+PMI收缩，经济滞胀"
        elif gdp_val < 5 and cpi_val < 2 and pmi_val < 50:
            return "衰退期", "⚪ GDP低增+CPI低位+PMI收缩，经济承压"
        else:
            return "过渡期", "➡️ 经济方向不明，观望为主"
    except:
        return "未知", "无法判断"

def format_summary_report():
    """格式化宏观概览报告"""
    indicators = get_latest_indicators()
    
    print("=" * 70)
    print("🌍 宏观经济概览仪表盘")
    print("=" * 70)
    
    # 核心指标表
    print("\n📊 核心宏观指标")
    print("-" * 70)
    print(f"{'指标':<15} {'最新值':<15} {'趋势判断':<20}")
    print("-" * 70)
    
    # GDP
    gdp_val = indicators.get('gdp_yoy', 'N/A')
    gdp_trend = "🟢 稳健增长" if gdp_val != 'N/A' and float(gdp_val) > 5 else "🟡 温和增长" if gdp_val != 'N/A' and float(gdp_val) > 0 else "🔴 增长放缓"
    print(f"{'GDP增速':<15} {gdp_val + '%':<15} {gdp_trend:<20}")
    
    # CPI
    cpi_val = indicators.get('cpi_yoy', 'N/A')
    if cpi_val != 'N/A':
        cpi_f = float(cpi_val)
        cpi_trend = "🔴 通胀压力" if cpi_f > 3 else "🟡 温和通胀" if cpi_f > 2 else "🟢 低通胀" if cpi_f > 0 else "⚪ 通缩风险"
    else:
        cpi_trend = "N/A"
    print(f"{'CPI同比':<15} {cpi_val + '%':<15} {cpi_trend:<20}")
    
    # PPI
    ppi_val = indicators.get('ppi_yoy', 'N/A')
    if ppi_val != 'N/A':
        ppi_f = float(ppi_val)
        ppi_trend = "🔴 工业通胀" if ppi_f > 5 else "🟡 温和上涨" if ppi_f > 0 else "🟢 价格下跌" if ppi_f > -2 else "⚪ 工业通缩"
    else:
        ppi_trend = "N/A"
    print(f"{'PPI同比':<15} {ppi_val + '%':<15} {ppi_trend:<20}")
    
    # M2
    m2_val = indicators.get('m2_yoy', 'N/A')
    print(f"{'M2同比':<15} {m2_val + '%':<15} {'➡️ 货币供应':<20}")
    
    # PMI
    pmi_val = indicators.get('pmi', 'N/A')
    if pmi_val != 'N/A':
        pmi_f = float(pmi_val)
        pmi_trend = "🟢 扩张区间" if pmi_f > 50 else "🔴 收缩区间"
    else:
        pmi_trend = "N/A"
    print(f"{'制造业PMI':<15} {pmi_val:<15} {pmi_trend:<20}")
    
    # LPR
    lpr_1y = indicators.get('lpr_1y', 'N/A')
    lpr_5y = indicators.get('lpr_5y', 'N/A')
    print(f"{'1年期LPR':<15} {lpr_1y + '%':<15} {'➡️ 政策利率':<20}")
    print(f"{'5年期LPR':<15} {lpr_5y + '%':<15} {'➡️ 房贷利率':<20}")
    
    # 汇率
    usd_cny = indicators.get('usd_cny', 'N/A')
    print(f"{'美元/人民币':<15} {usd_cny:<15} {'➡️ 汇率水平':<20}")
    
    # 经济周期判断
    print("\n" + "-" * 70)
    cycle, desc = judge_economic_cycle(gdp_val, cpi_val, pmi_val)
    print(f"\n🔄 经济周期判断: {cycle}")
    print(f"   {desc}")
    
    # 资产配置建议
    print("\n💰 资产配置建议")
    print("-" * 70)
    if cycle == "复苏期":
        print("   股票: 50% 🟢")
        print("   债券: 30% 🟡")
        print("   商品: 10% 🟡")
        print("   现金: 10% ⚪")
    elif cycle == "过热期":
        print("   股票: 40% 🟡")
        print("   债券: 20% 🔴")
        print("   商品: 30% 🟢")
        print("   现金: 10% ⚪")
    elif cycle == "滞胀期":
        print("   股票: 20% 🔴")
        print("   债券: 30% 🟡")
        print("   商品: 30% 🟢")
        print("   现金: 20% 🟡")
    elif cycle == "衰退期":
        print("   股票: 20% 🔴")
        print("   债券: 50% 🟢")
        print("   商品: 10% 🔴")
        print("   现金: 20% 🟡")
    else:
        print("   股票: 40% 🟡")
        print("   债券: 40% 🟡")
        print("   商品: 10% ⚪")
        print("   现金: 10% ⚪")
    
    print("\n" + "=" * 70)
    print("📌 数据来源: AkShare | 更新时间:", pd.Timestamp.now().strftime('%Y-%m-%d %H:%M'))
    print("=" * 70)

if __name__ == "__main__":
    format_summary_report()
