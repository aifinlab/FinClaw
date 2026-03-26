#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PMI采购经理指数数据获取 - AkShare
"""

import akshare as ak


def get_pmi_monthly():
    """获取PMI月度数据"""
    try:
        df = ak.macro_china_pmi()
        if df is not None and not df.empty:
            return df.tail(24)
        return None
    except Exception as e:
        print(f"获取PMI数据失败: {e}")
        return None


def format_pmi_report():
    """格式化PMI报告"""
    print("=" * 60)
    print("🏭 PMI采购经理指数报告")
    print("=" * 60)
    
    pmi = get_pmi_monthly()
    if pmi is not None and not pmi.empty:
        print("\n📈 PMI月度数据（最近24个月）")
        # 动态选择列显示
        display_cols = [c for c in pmi.columns if 'PMI' in c or '日期' in c][:5]
        if display_cols:
            print(pmi[display_cols].to_string(index=False))
        else:
            print(pmi.to_string(index=False))
        
        # 最新数据解读
        try:
            latest = pmi.iloc[-1]
            date_col = pmi.columns[0]
            print(f"\n💡 最新数据 ({latest[date_col]}):")
            
            # 查找制造业PMI列
            m_pmi_cols = [c for c in pmi.columns if '制造业' in c or '制造' in c]
            if m_pmi_cols:
                manufacturing_pmi = float(latest[m_pmi_cols[0]])
                print(f"   制造业PMI: {manufacturing_pmi}", end="")
                if manufacturing_pmi > 50:
                    print(" 🟢 扩张区间")
                else:
                    print(" 🔴 收缩区间")
        except Exception as e:
            print(f"\n💡 数据解读失败: {e}")
    else:
        print("\n⚠️ 未能获取PMI数据")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    format_pmi_report()
