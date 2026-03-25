#!/usr/bin/env python3
"""银行业宏观分析器 - 使用AkShare开源数据接口

功能：获取银行业货币政策、利率走势、市场流动性
数据源：AkShare开源金融数据接口
说明：银行业总资产/存贷款等宏观数据需参考央行统计公报
"""

import akshare as ak
import json
from datetime import datetime
import argparse


class BankIndustryAnalyzer:
    """银行业宏观分析器 - 基于利率和货币政策数据"""
    
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
    
    def _get_shibor(self) -> dict:
        """获取Shibor数据 - 使用AkShare"""
        try:
            df = ak.macro_china_shibor_all()
            if df is not None and not df.empty:
                latest = df.iloc[-1]
                return {
                    "隔夜": latest.get('隔夜', 'N/A'),
                    "1周": latest.get('1周', 'N/A'),
                    "1个月": latest.get('1个月', 'N/A'),
                    "3个月": latest.get('3个月', 'N/A'),
                    "data_source": "AkShare - Shibor"
                }
        except Exception as e:
            return {"error": f"获取Shibor失败: {str(e)}", "data_source": "AkShare"}
        return {"data_source": "AkShare", "note": "暂无Shibor数据"}
    
    def _get_interbank_rate(self) -> dict:
        """获取银行间利率 - 使用AkShare"""
        try:
            df = ak.macro_china_interbank_rate()
            if df is not None and not df.empty:
                latest = df.iloc[-1]
                return {
                    "隔夜利率": latest.get('隔夜', 'N/A'),
                    "7天利率": latest.get('7天', 'N/A'),
                    "1个月利率": latest.get('1个月', 'N/A'),
                    "data_source": "AkShare - 银行间同业拆借"
                }
        except Exception as e:
            return {"error": f"获取银行间利率失败: {str(e)}", "data_source": "AkShare"}
        return {"data_source": "AkShare", "note": "暂无银行间利率数据"}
    
    def get_industry_overview(self) -> dict:
        """获取银行业概览 - 基于利率和货币政策"""
        result = {
            "query_time": self.query_time,
            "analysis_type": "银行业宏观环境分析",
            "note": "银行业总资产/存贷款等详细数据需参考央行金融统计公报"
        }
        
        # 获取LPR数据
        lpr_data = self._get_lpr_data()
        result["monetary_policy"] = {
            "lpr": lpr_data,
            "policy_direction": "货币政策保持适度宽松，支持实体经济发展"
        }
        
        # 获取Shibor数据
        shibor_data = self._get_shibor()
        result["interbank_market"] = shibor_data
        
        result["industry_highlights"] = {
            "关注要点": [
                "银行业总资产增速",
                "不良贷款率变化",
                "净息差走势",
                "资本充足率水平"
            ],
            "数据来源说明": "详细经营数据参考中国人民银行金融统计数据、国家金融监督管理总局公告"
        }
        
        result["data_source"] = "AkShare开源数据 + 行业分析"
        result["data_quality"] = "实时利率数据 + 定性分析"
        
        return result
    
    def get_asset_quality(self) -> dict:
        """获取银行业资产质量分析 - 基于监管要求"""
        result = {
            "query_time": self.query_time,
            "analysis_type": "银行业资产质量分析",
            "note": "详细资产质量数据需参考金融监管总局公告"
        }
        
        result["regulatory_standards"] = {
            "不良贷款率": {
                "监管红线": "≤5%",
                "当前水平": "约1.5-1.6%（行业平均）",
                "说明": "行业整体不良率处于较低水平"
            },
            "拨备覆盖率": {
                "监管要求": "≥150%",
                "当前水平": "约200%+（行业平均）",
                "说明": "风险抵补能力充足"
            },
            "资本充足率": {
                "监管要求": "≥10.5%",
                "当前水平": "约15%（行业平均）",
                "说明": "资本水平充足"
            }
        }
        
        result["data_source"] = "国家金融监督管理总局（监管标准）+ 行业分析"
        result["data_quality"] = "监管规定 + 定性分析"
        
        return result
    
    def get_monetary_policy(self, year: int = None) -> dict:
        """获取货币政策数据 - 使用AkShare"""
        if year is None:
            year = datetime.now().year
        
        result = {
            "query_time": self.query_time,
            "data_type": "货币政策",
            "year": year
        }
        
        # 获取LPR数据
        lpr_data = self._get_lpr_data()
        result["lpr"] = lpr_data
        
        # 获取Shibor数据
        shibor_data = self._get_shibor()
        result["shibor"] = shibor_data
        
        # 获取银行间利率
        interbank_data = self._get_interbank_rate()
        result["interbank_rate"] = interbank_data
        
        result["policy_analysis"] = {
            "政策方向": "稳健的货币政策灵活适度、精准有效",
            "主要工具": [
                "LPR改革引导贷款利率下行",
                "降准释放长期流动性",
                "结构性货币政策工具精准滴灌"
            ],
            "关注要点": [
                "LPR报价变化",
                "公开市场操作",
                "存款准备金率调整",
                "再贷款再贴现政策"
            ]
        }
        
        result["data_source"] = "AkShare开源数据 + 行业分析"
        result["data_quality"] = "实时利率数据 + 定性分析"
        
        return result
    
    def get_deposit_loan_growth(self) -> dict:
        """获取存贷款增长分析"""
        result = {
            "query_time": self.query_time,
            "analysis_type": "存贷款增长分析",
            "note": "详细存贷款数据需参考央行金融统计数据"
        }
        
        # 获取LPR数据作为利率环境参考
        lpr_data = self._get_lpr_data()
        result["interest_rate_environment"] = lpr_data
        
        result["growth_analysis"] = {
            "关注指标": [
                "人民币各项存款余额增速",
                "人民币各项贷款余额增速",
                "社融存量增速",
                "M2增速"
            ],
            "分析维度": [
                "企业中长期贷款增长",
                "居民住房贷款变化",
                "普惠小微贷款增速",
                "绿色贷款增长"
            ],
            "数据来源说明": "数据参考中国人民银行金融统计数据"
        }
        
        result["data_source"] = "AkShare开源数据 + 行业分析"
        result["data_quality"] = "实时利率数据 + 定性分析"
        
        return result


def main():
    parser = argparse.ArgumentParser(description="银行业宏观分析器")
    parser.add_argument("--action", choices=["overview", "asset-quality", "monetary-policy", "deposit-loan"],
                       default="overview", help="执行的操作")
    parser.add_argument("--year", type=int, help="查询年份")
    
    args = parser.parse_args()
    analyzer = BankIndustryAnalyzer()
    
    if args.action == "overview":
        result = analyzer.get_industry_overview()
    elif args.action == "asset-quality":
        result = analyzer.get_asset_quality()
    elif args.action == "monetary-policy":
        result = analyzer.get_monetary_policy(args.year)
    elif args.action == "deposit-loan":
        result = analyzer.get_deposit_loan_growth()
    else:
        result = {"error": "未知的操作类型"}
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
