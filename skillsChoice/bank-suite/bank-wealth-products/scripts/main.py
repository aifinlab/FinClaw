#!/usr/bin/env python3
"""银行理财产品分析器 - 使用AkShare开源数据接口

功能：分析银行理财产品市场、收益率走势
数据源：AkShare开源金融数据接口
说明：详细理财产品数据需参考中国理财网
"""

import akshare as ak
import json
from datetime import datetime
import argparse


class BankWealthProducts:
    """银行理财产品分析器 - 基于市场利率分析"""
    
    def __init__(self):
        self.query_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _get_lpr_data(self) -> dict:
        """获取LPR数据 - 使用AkShare"""
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
    
    def _get_bond_yield(self) -> dict:
        """获取债券收益率 - 使用AkShare"""
        try:
            df = ak.bond_zh_yield()
            if df is not None and not df.empty:
                latest = df.iloc[-1]
                return {
                    "国债收益率_10Y": latest.get('中债国债到期收益率:10年', 'N/A'),
                    "国开债收益率_10Y": latest.get('中债国开债到期收益率:10年', 'N/A'),
                    "data_source": "AkShare - 中债登"
                }
        except Exception as e:
            return {"error": f"获取债券收益率失败: {str(e)}", "data_source": "AkShare"}
        return {"data_source": "AkShare", "note": "暂无债券收益率数据"}
    
    def get_products(self, bank_name: str = None, risk_level: str = None) -> dict:
        """获取理财产品概况 - 基于市场利率环境分析"""
        result = {
            "query_time": self.query_time,
            "analysis_type": "银行理财产品市场分析",
            "note": "详细产品数据需参考中国理财网"
        }
        
        if bank_name:
            result["filter"] = {"bank_name": bank_name}
        if risk_level:
            result["filter"] = {"risk_level": risk_level}
        
        # 获取LPR数据
        lpr_data = self._get_lpr_data()
        result["interest_rate_environment"] = lpr_data
        
        # 获取债券收益率
        bond_yield = self._get_bond_yield()
        result["bond_market"] = bond_yield
        
        result["market_analysis"] = {
            "产品类型分布": {
                "现金管理类": "流动性高，收益相对稳定",
                "固定收益类": "主要投资债券，收益受利率影响",
                "混合类": "股债混合，收益波动适中",
                "权益类": "主要投资股票，收益波动较大"
            },
            "风险等级说明": {
                "R1(低风险)": "保本型或低风险固收产品",
                "R2(中低风险)": "主要投资债券，风险可控",
                "R3(中等风险)": "可投资非标、混合类产品",
                "R4(中高风险)": "可投资权益类产品",
                "R5(高风险)": "主要投资权益或衍生品"
            },
            "数据来源说明": "详细产品数据参考中国理财网、银行业理财登记托管中心"
        }
        
        result["data_source"] = "AkShare开源数据 + 行业分析"
        result["data_quality"] = "实时利率数据 + 定性分析"
        
        return result
    
    def analyze_yields(self) -> dict:
        """分析理财产品收益率 - 基于市场利率"""
        result = {
            "query_time": self.query_time,
            "analysis_type": "理财产品收益率分析"
        }
        
        # 获取LPR数据
        lpr_data = self._get_lpr_data()
        result["interest_rate_environment"] = lpr_data
        
        # 获取债券收益率
        bond_yield = self._get_bond_yield()
        result["bond_market"] = bond_yield
        
        result["yield_analysis"] = {
            "收益率趋势": "市场利率下行，理财收益率承压",
            "产品类型收益率参考": {
                "现金管理类产品": "七日年化约2.0%-2.5%（参考）",
                "固收类产品": "业绩基准约2.5%-3.5%（参考）",
                "混合类产品": "业绩基准约3.0%-4.5%（参考）",
                "权益类产品": "收益波动较大，长期预期5%-8%（参考）"
            },
            "影响收益率的因素": [
                "市场利率水平（LPR、债券收益率）",
                "产品投资范围和风险等级",
                "产品期限长短",
                "管理人投资能力"
            ],
            "投资建议": [
                "关注产品风险等级与自身风险承受能力匹配",
                "选择正规渠道购买理财产品",
                "关注产品投资范围和业绩基准",
                "了解产品流动性安排"
            ],
            "数据来源说明": "收益率参考范围基于历史数据，实际收益以产品披露为准"
        }
        
        result["data_source"] = "AkShare开源数据 + 行业分析"
        result["data_quality"] = "实时利率数据 + 定性分析"
        
        return result


def main():
    parser = argparse.ArgumentParser(description="银行理财产品分析器")
    parser.add_argument("--bank", help="银行名称")
    parser.add_argument("--risk", help="风险等级(R1/R2/R3/R4)")
    parser.add_argument("--yields", action="store_true", help="分析收益率")
    
    args = parser.parse_args()
    analyzer = BankWealthProducts()
    
    if args.yields:
        result = analyzer.analyze_yields()
    else:
        result = analyzer.get_products(args.bank, args.risk)
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
