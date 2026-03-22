#!/usr/bin/env python3
"""银行流动性分析器 - 真实数据源"""

import akshare as ak
import pandas as pd
import json
from datetime import datetime
import argparse


class BankLiquidityAnalyzer:
    """银行流动性分析器"""
    
    BANK_CODES = {
        "招商银行": "600036", "工商银行": "601398", "建设银行": "601939",
        "农业银行": "601288", "中国银行": "601988", "交通银行": "601328",
        "邮储银行": "601658", "兴业银行": "601166", "平安银行": "000001",
        "宁波银行": "002142", "南京银行": "601009", "江苏银行": "600919"
    }
    
    def analyze_liquidity(self, bank_name: str) -> dict:
        """分析银行流动性"""
        code = self.BANK_CODES.get(bank_name)
        if not code:
            return {"error": f"未找到银行: {bank_name}"}
        
        result = {
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "bank_name": bank_name,
            "stock_code": code,
            "liquidity_indicators": {},
            "assessment": {}
        }
        
        try:
            # 获取资产负债表
            df_bs = ak.stock_balance_sheet_by_report_em(symbol=code)
            if df_bs is not None and not df_bs.empty:
                latest = df_bs.iloc[0]
                
                deposits = self._to_float(latest.get('吸收存款'))
                loans = self._to_float(latest.get('发放贷款和垫款'))
                total_assets = self._to_float(latest.get('资产总计'))
                cash = self._to_float(latest.get('货币资金'))
                
                # 计算存贷比
                if deposits > 0:
                    loan_deposit_ratio = loans / deposits * 100
                    result["liquidity_indicators"]["存贷比"] = f"{loan_deposit_ratio:.2f}%"
                    result["assessment"]["存贷比评价"] = "正常" if loan_deposit_ratio < 75 else "偏高"
                
                # 现金资产占比
                if total_assets > 0:
                    cash_ratio = cash / total_assets * 100
                    result["liquidity_indicators"]["现金资产占比"] = f"{cash_ratio:.2f}%"
            
            # 获取财务指标（LCR、NSFR等）
            df_fi = ak.stock_financial_analysis_indicator(symbol=code)
            if df_fi is not None and not df_fi.empty:
                latest = df_fi.iloc[0]
                result["liquidity_indicators"]["流动性覆盖率"] = latest.get('流动性覆盖率', 'N/A')
                result["liquidity_indicators"]["净稳定资金比例"] = latest.get('净稳定资金比例', 'N/A')
                
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def _to_float(self, val) -> float:
        try:
            return float(val)
        except:
            return 0


def main():
    parser = argparse.ArgumentParser(description="银行流动性分析器")
    parser.add_argument("--bank", required=True, help="银行名称")
    args = parser.parse_args()
    
    analyzer = BankLiquidityAnalyzer()
    result = analyzer.analyze_liquidity(args.bank)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
