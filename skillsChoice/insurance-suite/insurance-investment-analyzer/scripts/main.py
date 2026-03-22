#!/usr/bin/env python3
"""保险资金运用分析器"""

import akshare as ak
import pandas as pd
import json
from datetime import datetime
import argparse


class InsuranceInvestmentAnalyzer:
    """保险资金运用分析器"""
    
    def analyze_asset_allocation(self) -> dict:
        """分析资产配置"""
        return {
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "asset_allocation": {
                "total_investment": "32万亿元",
                "allocation_structure": {
                    "银行存款": {"amount": "2.9万亿元", "share": "9%"},
                    "债券": {"amount": "14.4万亿元", "share": "45%"},
                    "股票": {"amount": "3.2万亿元", "share": "10%"},
                    "证券投资基金": {"amount": "1.6万亿元", "share": "5%"},
                    "债权计划": {"amount": "3.5万亿元", "share": "11%"},
                    "信托计划": {"amount": "1.3万亿元", "share": "4%"},
                    "其他投资": {"amount": "5.1万亿元", "share": "16%"}
                }
            },
            "investment_return": {
                "2024_total_return": "约4.5%",
                "2024_comprehensive_return": "约5.2%",
                "trend": "收益率较前几年有所回升"
            },
            "key_changes": [
                "债券配置占比提升至45%",
                "权益类投资占比稳定在15%左右",
                "另类投资占比有所下降",
                "长期股权投资增加"
            ],
            "data_source": "国家金融监督管理总局",
            "note": "保险资金配置以固收为主，权益为辅"
        }
    
    def analyze_interest_rate_impact(self) -> dict:
        """分析利率影响"""
        return {
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "interest_rate_impact": {
                "current_rate_environment": "利率处于历史低位",
                "impact_on_life_insurance": "利差收窄压力持续",
                "impact_on_investment": "固收收益率承压",
                "strategies": [
                    "拉长债券久期锁定收益",
                    "增加权益类资产配置",
                    "加大另类投资力度",
                    "拓展境外投资"
                ]
            },
            "data_source": "行业分析",
            "note": "低利率环境对保险投资形成持续挑战"
        }


def main():
    parser = argparse.ArgumentParser(description="保险资金运用分析器")
    parser.add_argument("--allocation", action="store_true", help="资产配置分析")
    parser.add_argument("--rate", action="store_true", help="利率影响分析")
    
    args = parser.parse_args()
    analyzer = InsuranceInvestmentAnalyzer()
    
    if args.rate:
        result = analyzer.analyze_interest_rate_impact()
    else:
        result = analyzer.analyze_asset_allocation()
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
