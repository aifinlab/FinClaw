#!/usr/bin/env python3
"""银行间市场分析器 - 真实数据源"""

import akshare as ak
import pandas as pd
import json
from datetime import datetime
import argparse


class BankInterbankMarket:
    """银行间市场分析器"""
    
    def get_shibor(self) -> dict:
        """获取Shibor报价"""
        try:
            df = ak.macro_china_shibor_all()
            
            if df is not None and not df.empty:
                latest = df.iloc[-1]
                return {
                    "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "data_date": latest.get('日期'),
                    "shibor_overnight": latest.get('隔夜'),
                    "shibor_1w": latest.get('1周'),
                    "shibor_2w": latest.get('2周'),
                    "shibor_1m": latest.get('1月'),
                    "shibor_3m": latest.get('3月'),
                    "shibor_6m": latest.get('6月'),
                    "shibor_1y": latest.get('1年'),
                    "data_source": "上海银行间同业拆放利率",
                    "note": "Shibor反映银行间市场流动性状况"
                }
        except Exception as e:
            return {"error": f"获取Shibor失败: {str(e)}"}
    
    def get_repo_rates(self) -> dict:
        """获取银行间回购利率"""
        try:
            df = ak.bond_repo_zh_tick()
            
            if df is not None and not df.empty:
                return {
                    "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "repo_rates": df.head(10).to_dict('records'),
                    "data_source": "中国货币网"
                }
        except Exception as e:
            return {"error": f"获取回购利率失败: {str(e)}"}
    
    def analyze_liquidity(self) -> dict:
        """分析流动性状况"""
        shibor = self.get_shibor()
        
        if "error" in shibor:
            return shibor
        
        overnight = shibor.get("shibor_overnight", 0)
        try:
            overnight_rate = float(overnight) if overnight else 0
        except:
            overnight_rate = 0
        
        if overnight_rate < 1.5:
            status = "流动性充裕"
        elif overnight_rate < 2.0:
            status = "流动性中性"
        else:
            status = "流动性偏紧"
        
        return {
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "liquidity_status": status,
            "shibor_overnight": overnight,
            "assessment": self._get_liquidity_assessment(overnight_rate)
        }
    
    def _get_liquidity_assessment(self, rate: float) -> str:
        """流动性评估"""
        if rate < 1.0:
            return "资金极度宽松，可能面临资产荒"
        elif rate < 1.5:
            return "资金充裕，有利于债券牛市"
        elif rate < 2.0:
            return "资金平衡，货币政策中性"
        elif rate < 2.5:
            return "资金偏紧，关注央行操作"
        else:
            return "资金紧张，警惕流动性风险"


def main():
    parser = argparse.ArgumentParser(description="银行间市场分析器")
    parser.add_argument("--shibor", action="store_true", help="查询Shibor")
    parser.add_argument("--repo", action="store_true", help="查询回购利率")
    parser.add_argument("--liquidity", action="store_true", help="流动性分析")
    
    args = parser.parse_args()
    analyzer = BankInterbankMarket()
    
    if args.shibor:
        result = analyzer.get_shibor()
    elif args.repo:
        result = analyzer.get_repo_rates()
    elif args.liquidity:
        result = analyzer.analyze_liquidity()
    else:
        result = analyzer.get_shibor()
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
