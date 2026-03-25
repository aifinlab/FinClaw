#!/usr/bin/env python3
"""银行信贷分析器 - 使用AkShare开源数据接口

功能：分析信贷市场趋势、贷款结构、利率走势
数据源：AkShare开源金融数据接口
说明：宏观信贷数据需参考央行金融统计数据
"""

import akshare as ak
import json
from datetime import datetime
import argparse


class BankCreditAnalyzer:
    """银行信贷分析器 - 基于LPR和市场数据分析"""
    
    def __init__(self):
        self.query_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
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
    
    def _get_interbank_rate(self) -> dict:
        """获取银行间利率数据 - 使用AkShare"""
        try:
            df = ak.macro_china_interbank_rate()
            if df is not None and not df.empty:
                latest = df.iloc[-1]
                return {
                    "隔夜利率": latest.get('隔夜', 'N/A'),
                    "7天利率": latest.get('7天', 'N/A'),
                    "data_source": "AkShare - 银行间同业拆借"
                }
        except Exception as e:
            return {"error": f"获取银行间利率失败: {str(e)}", "data_source": "AkShare"}
        return {"data_source": "AkShare", "note": "暂无银行间利率数据"}
    
    def get_credit_overview(self) -> dict:
        """获取信贷概览 - 基于利率数据和市场分析"""
        result = {
            "query_time": self.query_time,
            "analysis_type": "信贷市场利率分析",
            "note": "详细信贷规模数据需参考央行金融统计数据"
        }
        
        # 获取LPR数据
        lpr_data = self._get_lpr_data()
        result["lpr_data"] = lpr_data
        
        # 获取银行间利率
        interbank_data = self._get_interbank_rate()
        result["interbank_rate"] = interbank_data
        
        result["credit_analysis"] = {
            "利率环境": "LPR处于历史低位，信贷成本较低",
            "政策导向": [
                "引导贷款利率下行",
                "加大对实体经济支持力度",
                "优化信贷结构",
                "支持重点领域和薄弱环节"
            ],
            "关注指标": [
                "月度新增人民币贷款",
                "社会融资规模",
                "M2增速",
                "信贷结构变化"
            ],
            "数据来源说明": "信贷规模数据参考中国人民银行金融统计数据"
        }
        
        result["data_source"] = "AkShare开源数据 + 行业分析"
        result["data_quality"] = "实时利率数据 + 定性分析"
        
        return result
    
    def analyze_loan_structure(self) -> dict:
        """分析贷款结构 - 基于利率数据推断"""
        result = {
            "query_time": self.query_time,
            "analysis_type": "贷款结构分析",
            "note": "详细贷款结构数据需参考央行统计数据"
        }
        
        # 获取LPR数据
        lpr_data = self._get_lpr_data()
        result["lpr_data"] = lpr_data
        
        result["structure_analysis"] = {
            "企业贷款": {
                "description": "中长期贷款 vs 短期贷款",
                "trend": "制造业中长期贷款保持较快增长"
            },
            "居民贷款": {
                "description": "住房贷款 vs 消费贷款",
                "trend": "房贷利率下调，刺激住房需求"
            },
            "票据融资": {
                "description": "短期流动性调节工具",
                "trend": "反映银行信贷投放节奏"
            },
            "关注要点": [
                "企业中长期贷款增速",
                "居民住房贷款变化",
                "普惠小微贷款增长",
                "绿色贷款增速"
            ],
            "数据来源说明": "贷款结构数据参考中国人民银行金融机构贷款投向统计报告"
        }
        
        result["data_source"] = "AkShare开源数据 + 行业分析"
        result["data_quality"] = "实时利率数据 + 定性分析"
        
        return result


def main():
    parser = argparse.ArgumentParser(description="银行信贷分析器")
    parser.add_argument("--overview", action="store_true", help="信贷概览")
    parser.add_argument("--structure", action="store_true", help="贷款结构")
    
    args = parser.parse_args()
    analyzer = BankCreditAnalyzer()
    
    if args.structure:
        result = analyzer.analyze_loan_structure()
    else:
        result = analyzer.get_credit_overview()
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
