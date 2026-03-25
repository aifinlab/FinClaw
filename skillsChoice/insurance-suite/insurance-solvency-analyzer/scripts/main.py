#!/usr/bin/env python3
"""保险偿付能力分析器 - 使用AkShare开源数据接口

功能：分析保险公司偿付能力、监管要求、合规状态
数据源：AkShare实时行情 + 监管规则说明
说明：偿付能力详细数据需从保险公司定期报告获取
"""

import akshare as ak
import json
from datetime import datetime
import argparse


class InsuranceSolvencyAnalyzer:
    """保险偿付能力分析器 - 监管规则 + 实时行情"""
    
    # 主要保险公司代码映射（仅用于获取实时行情）
    COMPANY_CODES = {
        "中国平安": "601318",
        "中国人寿": "601628",
        "中国太保": "601601",
        "新华保险": "601336",
        "中国人保": "601319"
    }
    
    def __init__(self):
        self.query_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _get_stock_data(self, code: str) -> dict:
        """获取股票实时数据 - 使用AkShare"""
        try:
            df = ak.stock_zh_a_spot_em()
            stock_row = df[df['代码'] == code]
            
            if stock_row.empty:
                return None
            
            return {
                "price": float(stock_row['最新价'].values[0]) if '最新价' in stock_row.columns else None,
                "pb": float(stock_row['市净率'].values[0]) if '市净率' in stock_row.columns else None,
                "total_mv": float(stock_row['总市值'].values[0]) if '总市值' in stock_row.columns else None
            }
        except Exception:
            return None
    
    def analyze_solvency(self, company: str = None) -> dict:
        """分析偿付能力 - 基于实时行情 + 监管规则说明"""
        result = {
            "query_time": self.query_time,
            "note": "偿付能力详细数据需查阅各公司偿付能力报告",
            "regulatory_standards": {
                "核心偿付能力充足率": "≥50%",
                "综合偿付能力充足率": "≥100%",
                "风险综合评级": "A或B级为达标"
            }
        }
        
        if company:
            code = self.COMPANY_CODES.get(company)
            if not code:
                return {
                    "error": f"未找到保险公司: {company}",
                    "available_companies": list(self.COMPANY_CODES.keys())
                }
            
            stock_data = self._get_stock_data(code)
            
            result["company"] = company
            result["stock_code"] = code
            
            if stock_data:
                result["market_data"] = {
                    "股价": stock_data.get("price"),
                    "市净率_PB": stock_data.get("pb"),
                    "总市值_亿元": round(stock_data.get("total_mv") / 1e8, 2) if stock_data.get("total_mv") else None
                }
                
                # PB估值与偿付能力关联分析
                pb = stock_data.get("pb")
                if pb:
                    if pb < 0.8:
                        result["solvency_assessment"] = "估值较低，关注偿付能力变化"
                    elif pb < 1.0:
                        result["solvency_assessment"] = "估值偏低，偿付能力或承压"
                    else:
                        result["solvency_assessment"] = "估值合理"
            
            result["data_source"] = "AkShare实时行情 + 监管规则"
            result["data_quality"] = "实时市场数据 + 定性分析"
            
        else:
            # 获取所有上市险企数据
            companies = []
            for name, code in self.COMPANY_CODES.items():
                stock_data = self._get_stock_data(code)
                if stock_data:
                    companies.append({
                        "company": name,
                        "code": code,
                        "pb": stock_data.get("pb"),
                        "market_cap_yi": round(stock_data.get("total_mv") / 1e8, 2) if stock_data.get("total_mv") else None
                    })
            
            companies.sort(key=lambda x: x.get("market_cap_yi") or 0, reverse=True)
            result["listed_companies"] = companies
            
            # 计算平均PB
            valid_pb = [c["pb"] for c in companies if c.get("pb")]
            if valid_pb:
                result["industry_avg_pb"] = round(sum(valid_pb) / len(valid_pb), 2)
            
            result["data_source"] = "AkShare实时行情"
            result["data_quality"] = "实时市场数据"
        
        return result
    
    def get_regulatory_requirements(self) -> dict:
        """获取监管要求 - 监管规定（合理硬编码）"""
        return {
            "query_time": self.query_time,
            "regulatory_requirements": {
                "核心偿付能力充足率": {
                    "requirement": "≥50%",
                    "description": "核心资本/最低资本",
                    "source": "《保险公司偿付能力管理规定》"
                },
                "综合偿付能力充足率": {
                    "requirement": "≥100%",
                    "description": "实际资本/最低资本",
                    "source": "《保险公司偿付能力管理规定》"
                },
                "风险综合评级": {
                    "requirement": "A或B级",
                    "description": "C/D级为不达标，将受监管限制",
                    "source": "《保险公司偿付能力管理规定》"
                }
            },
            "regulatory_actions": {
                "充足I类公司": {
                    "criteria": "核心≥50%，综合≥100%",
                    "treatment": "正常监管"
                },
                "充足II类公司": {
                    "criteria": "核心≥60%，综合≥150%",
                    "treatment": "鼓励发展"
                },
                "重点关注公司": {
                    "criteria": "不达标",
                    "treatment": "限制业务发展，要求限期整改"
                }
            },
            "data_source": "《保险公司偿付能力管理规定》（监管法规）",
            "data_quality": "监管规定文本"
        }


def main():
    parser = argparse.ArgumentParser(description="保险偿付能力分析器")
    parser.add_argument("--company", help="保险公司名称")
    parser.add_argument("--requirements", action="store_true", help="监管要求")
    
    args = parser.parse_args()
    analyzer = InsuranceSolvencyAnalyzer()
    
    if args.requirements:
        result = analyzer.get_regulatory_requirements()
    else:
        result = analyzer.analyze_solvency(args.company)
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
