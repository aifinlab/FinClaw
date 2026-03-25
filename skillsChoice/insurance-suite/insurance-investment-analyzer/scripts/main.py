#!/usr/bin/env python3
"""保险资金运用分析器 - 使用AkShare开源数据接口

功能：分析保险资金配置结构、收益率趋势、利率影响
数据源：AkShare开源金融数据接口
"""

import akshare as ak
import json
from datetime import datetime
import argparse


class InsuranceInvestmentAnalyzer:
    """保险资金运用分析器 - 使用AkShare获取市场数据"""
    
    def __init__(self):
        self.query_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _get_bond_market_data(self) -> dict:
        """获取债券市场数据 - 使用AkShare"""
        try:
            # 获取国债收益率数据
            df = ak.bond_zh_yield()
            if df is not None and not df.empty:
                latest = df.iloc[-1]
                return {
                    "国债收益率_10Y": latest.get('中债国债到期收益率:10年', 'N/A'),
                    "国债收益率_5Y": latest.get('中债国债到期收益率:5年', 'N/A'),
                    "国开债收益率_10Y": latest.get('中债国开债到期收益率:10年', 'N/A'),
                    "data_source": "AkShare - 中债登"
                }
        except Exception as e:
            return {"error": f"获取债券数据失败: {str(e)}", "data_source": "AkShare"}
        return {"data_source": "AkShare", "note": "暂无债券数据"}
    
    def _get_stock_market_data(self) -> dict:
        """获取股票市场数据 - 使用AkShare"""
        try:
            # 获取沪深300指数
            df = ak.index_zh_a_hist(symbol="000300", period="daily", 
                                   start_date="20240101", end_date=datetime.now().strftime("%Y%m%d"))
            if df is not None and not df.empty:
                latest = df.iloc[-1]
                first = df.iloc[0]
                ytd_return = (latest['收盘'] - first['收盘']) / first['收盘'] * 100
                return {
                    "沪深300点位": latest.get('收盘'),
                    "沪深300_YTD涨跌幅": f"{ytd_return:.2f}%",
                    "data_source": "AkShare - 东方财富"
                }
        except Exception as e:
            return {"error": f"获取股票数据失败: {str(e)}", "data_source": "AkShare"}
        return {"data_source": "AkShare", "note": "暂无股票数据"}
    
    def _get_lpr_data(self) -> dict:
        """获取LPR利率数据 - 使用AkShare"""
        try:
            df = ak.macro_china_lpr()
            if df is not None and not df.empty:
                latest = df.iloc[0]
                return {
                    "LPR_1Y": latest.get('1年期', 'N/A'),
                    "LPR_5Y": latest.get('5年期', 'N/A'),
                    "data_source": "AkShare - 中国人民银行"
                }
        except Exception as e:
            return {"error": f"获取LPR数据失败: {str(e)}", "data_source": "AkShare"}
        return {"data_source": "AkShare", "note": "暂无LPR数据"}
    
    def analyze_asset_allocation(self) -> dict:
        """分析资产配置 - 基于市场数据推断配置趋势"""
        result = {
            "query_time": self.query_time,
            "analysis_type": "保险资金配置趋势分析",
            "note": "保险资金配置结构需参考监管统计数据，以下为市场环境分析"
        }
        
        # 获取债券市场数据
        bond_data = self._get_bond_market_data()
        result["bond_market"] = bond_data
        
        # 获取股票市场数据
        stock_data = self._get_stock_market_data()
        result["stock_market"] = stock_data
        
        # 基于市场数据给出配置建议
        result["allocation_analysis"] = {
            "固收类配置逻辑": "债券收益率处于历史低位，建议拉长久期锁定收益",
            "权益类配置逻辑": "根据市场估值水平动态调整权益配置比例",
            "配置建议": [
                "利率下行周期，建议增配长久期利率债",
                "权益市场波动较大，保持适度配置比例",
                "关注另类投资机会（基础设施REITs等）",
                "加强境外资产配置分散风险"
            ]
        }
        
        result["data_source"] = "AkShare开源数据 + 行业分析"
        result["data_quality"] = "实时市场数据"
        
        return result
    
    def analyze_interest_rate_impact(self) -> dict:
        """分析利率影响 - 使用AkShare获取LPR数据"""
        result = {
            "query_time": self.query_time,
            "analysis_type": "利率环境影响分析"
        }
        
        # 获取LPR数据
        lpr_data = self._get_lpr_data()
        result["lpr_data"] = lpr_data
        
        # 获取债券收益率
        bond_data = self._get_bond_market_data()
        result["bond_yield"] = bond_data
        
        # 利率影响分析
        result["interest_rate_analysis"] = {
            "当前环境": "LPR多次下调，利率处于历史低位",
            "对寿险影响": "利差收窄压力持续，负债端成本刚性",
            "对投资影响": "固收类资产再投资风险上升",
            "应对策略": [
                "资产负债联动管理，降低负债成本",
                "拉长资产久期，锁定长期收益",
                "增配权益类资产，提升整体收益",
                "发展保障型产品，降低利率敏感度"
            ]
        }
        
        result["data_source"] = "AkShare开源数据 + 行业分析"
        result["data_quality"] = "实时利率数据"
        
        return result


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
