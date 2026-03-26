#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PPI生产者物价指数数据获取 - AkShare
"""

import akshare as ak


def get_ppi_monthly():
    """获取PPI月度数据"""
    try:
        df = ak.macro_china_ppi()
        if df is not None and not df.empty:
            return df.tail(24)
        return None
    except Exception as e:
        print(f"获取PPI数据失败: {e}")
        return None


def format_ppi_report():
    """格式化PPI报告"""
    print("=" * 60)
    print("📊 PPI生产者物价指数报告")
    print("=" * 60)
    
    ppi = get_ppi_monthly()
    if ppi is not None and not ppi.empty:
        print("\n📈 PPI月度数据（最近24个月）")
        print(ppi.to_string(index=False))
        
        # 最新数据解读
        try:
            latest = ppi.iloc[-1]
            date_col = ppi.columns[0]
            print(f"\n💡 最新数据 ({latest[date_col]}):")
            
            # 尝试找到PPI同比列
            ppi_cols = [c for c in ppi.columns if '同比' in c or 'PPI' in c]
            if ppi_cols:
                ppi_val = latest[ppi_cols[0]]
                print(f"   PPI同比: {ppi_val}%", end="")
                try:
                    ppi_float = float(ppi_val)
                    if ppi_float > 5:
                        print(" 🔴 工业通胀压力较大")
                    elif ppi_float > 0:
                        print(" 🟡 工业价格温和上涨")
                    elif ppi_float > -2:
                        print(" 🟢 工业价格小幅下跌")
                    else:
                        print(" ⚪ 工业通缩风险")
                except:
                    print("")
        except Exception as e:
            print(f"\n💡 数据解读失败: {e}")
    else:
        print("\n⚠️ 未能获取PPI数据")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    format_ppi_report()
