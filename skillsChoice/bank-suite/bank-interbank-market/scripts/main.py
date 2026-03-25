#!/usr/bin/env python3
"""银行间市场分析器 - 使用AkShare开源数据接口

功能：获取Shibor、银行间回购利率、分析市场流动性
数据源：AkShare开源金融数据接口
"""

import akshare as ak
import json
from datetime import datetime
import argparse


class BankInterbankMarket:
    """银行间市场分析器 - 使用AkShare获取实时利率数据"""
    
    def __init__(self):
        self.query_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def get_shibor(self) -> dict:
        """获取Shibor报价 - 使用AkShare"""
        try:
            df = ak.macro_china_shibor_all()
            if df is not None and not df.empty:
                latest = df.iloc[-1]
                return {
                    "query_time": self.query_time,
                    "data_date": latest.get('日期', 'N/A'),
                    "shibor_overnight": latest.get('隔夜', 'N/A'),
                    "shibor_1w": latest.get('1周', 'N/A'),
                    "shibor_2w": latest.get('2周', 'N/A'),
                    "shibor_1m": latest.get('1个月', 'N/A'),
                    "shibor_3m": latest.get('3个月', 'N/A'),
                    "shibor_6m": latest.get('6个月', 'N/A'),
                    "shibor_1y": latest.get('1年', 'N/A'),
                    "data_source": "AkShare - 上海银行间同业拆放利率(Shibor)",
                    "data_quality": "实时利率数据",
                    "note": "Shibor反映银行间市场流动性状况"
                }
        except Exception as e:
            return {
                "query_time": self.query_time,
                "error": f"获取Shibor数据失败: {str(e)}",
                "data_source": "AkShare"
            }
    
    def get_repo_rates(self) -> dict:
        """获取银行间回购利率 - 使用AkShare"""
        try:
            df = ak.macro_china_interbank_rate()
            if df is not None and not df.empty:
                latest = df.iloc[-1]
                return {
                    "query_time": self.query_time,
                    "repo_rates": {
                        "R001": {"rate": latest.get('隔夜', 'N/A')},
                        "R007": {"rate": latest.get('7天', 'N/A')},
                        "R014": {"rate": latest.get('14天', 'N/A')},
                        "R1M": {"rate": latest.get('1个月', 'N/A')},
                        "R3M": {"rate": latest.get('3个月', 'N/A')}
                    },
                    "data_source": "AkShare - 银行间同业拆借利率",
                    "data_quality": "实时利率数据",
                    "note": "R为银行间质押式回购利率"
                }
        except Exception as e:
            return {
                "query_time": self.query_time,
                "error": f"获取回购利率失败: {str(e)}",
                "data_source": "AkShare"
            }
    
    def analyze_liquidity(self) -> dict:
        """分析流动性状况 - 基于Shibor数据"""
        result = {
            "query_time": self.query_time,
            "analysis_type": "银行间市场流动性分析"
        }
        
        # 获取Shibor数据
        shibor_data = self.get_shibor()
        if "error" not in shibor_data:
            overnight_str = shibor_data.get("shibor_overnight", "0%")
            try:
                overnight_rate = float(overnight_str.replace("%", ""))
            except:
                overnight_rate = 0
            
            # 判断流动性状况
            if overnight_rate < 1.5:
                status = "流动性充裕"
                color = "green"
            elif overnight_rate < 2.0:
                status = "流动性中性"
                color = "yellow"
            else:
                status = "流动性偏紧"
                color = "red"
            
            result["liquidity_status"] = status
            result["status_color"] = color
            result["shibor_overnight"] = shibor_data.get("shibor_overnight")
            result["assessment"] = self._get_liquidity_assessment(overnight_rate)
        
        # 获取回购利率
        repo_data = self.get_repo_rates()
        if "error" not in repo_data:
            result["repo_rates"] = repo_data.get("repo_rates")
        
        result["data_source"] = "AkShare开源数据"
        result["data_quality"] = "实时利率数据"
        
        return result
    
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
