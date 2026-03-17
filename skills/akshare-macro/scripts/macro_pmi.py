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
        df.columns = ['日期', '制造业PMI', '非制造业PMI', '综合PMI',
                      '制造业PMI生产', '制造业PMI新订单', '制造业PMI原材料库存',
                      '制造业PMI从业人员', '制造业PMI供应商配送时间']
        return df.tail(24)
    except Exception as e:
        print(f"获取PMI数据失败: {e}")
        return None

def format_pmi_report():
    """格式化PMI报告"""
    print("=" * 60)
    print("🏭 PMI采购经理指数报告")
    print("=" * 60)
    
    pmi = get_pmi_monthly()
    if pmi is not None:
        print("\n📈 PMI月度数据（最近24个月）")
        print(pmi[['日期', '制造业PMI', '非制造业PMI', '综合PMI']].to_string(index=False))
        
        # 最新数据解读
        latest = pmi.iloc[-1]
        manufacturing_pmi = float(latest['制造业PMI'])
        
        print(f"\n💡 最新数据解读 ({latest['日期']}):")
        print(f"   制造业PMI: {manufacturing_pmi}", end="")
        if manufacturing_pmi > 50:
            print(" 🟢 扩张区间（经济景气）")
        else:
            print(" 🔴 收缩区间（经济承压）")
        
        print(f"   非制造业PMI: {latest['非制造业PMI']}", end="")
        if float(latest['非制造业PMI']) > 50:
            print(" 🟢 扩张区间")
        else:
            print(" 🔴 收缩区间")
        
        # 分项指标
        print(f"\n   生产指数: {latest['制造业PMI生产']}")
        print(f"   新订单指数: {latest['制造业PMI新订单']}")
        print(f"   原材料库存: {latest['制造业PMI原材料库存']}")
        print(f"   从业人员: {latest['制造业PMI从业人员']}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    format_pmi_report()
