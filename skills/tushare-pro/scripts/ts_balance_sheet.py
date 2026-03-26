#!/usr/bin/env python3
"""
Get balance sheet data via Tushare Pro.

Usage:
    python ts_balance_sheet.py <ts_code> [year]
    
    python ts_balance_sheet.py 600519.SH 2023
    python ts_balance_sheet.py 000001.SZ 2022

Environment:
    TUSHARE_TOKEN - Your Tushare API token
"""

import tushare as ts
import json
import os
import sys


def get_balance_sheet(ts_code, year=2023):
    """获取资产负债表数据"""
    try:
        token = os.environ.get('TUSHARE_TOKEN')
        if not token:
            print(json.dumps({"ok": False, "error": "Missing TUSHARE_TOKEN"}))
            return
        
        pro = ts.pro_api(token)
        df = pro.balancesheet(ts_code=ts_code, period=f"{year}1231")
        
        if df is None or df.empty:
            print(json.dumps({"ok": False, "error": "No data found"}))
            return
        
        # 转换为字典
        data = df.to_dict(orient='records')
        
        result = {
            "ok": True,
            "data": data,
            "code": ts_code,
            "year": year
        }
        print(json.dumps(result, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e)}))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ts_balance_sheet.py <ts_code> [year]")
        print("Example: python ts_balance_sheet.py 600519.SH 2023")
        sys.exit(1)
    
    ts_code = sys.argv[1]
    year = int(sys.argv[2]) if len(sys.argv) > 2 else 2023
    
    get_balance_sheet(ts_code, year)
