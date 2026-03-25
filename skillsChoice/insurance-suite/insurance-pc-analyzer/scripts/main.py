#!/usr/bin/env python3
"""财产险业务分析器 - 使用AkShare开源数据接口

功能：分析财险公司市场表现、车险与非车险趋势
数据源：AkShare实时行情 + 行业分析
说明：详细保费数据需参考各公司定期报告
"""

import akshare as ak
import json
from datetime import datetime
import argparse


class InsurancePCAnalyzer:
    """财产险业务分析器 - 基于上市财险公司数据"""
    
    # 主要财险公司代码（通常财险业务包含在综合险企中）
    COMPANY_CODES = {
        "中国人保": "601319",
        "中国平安": "601318",
        "中国太保": "601601"
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
                "change_pct": float(stock_row['涨跌幅'].values[0]) if '涨跌幅' in stock_row.columns else None,
                "pb": float(stock_row['市净率'].values[0]) if '市净率' in stock_row.columns else None,
                "pe": float(stock_row['市盈率-动态'].values[0]) if '市盈率-动态' in stock_row.columns else None,
                "total_mv": float(stock_row['总市值'].values[0]) if '总市值' in stock_row.columns else None
            }
        except Exception:
            return None
    
    def analyze_pc_market(self) -> dict:
        """分析财险市场 - 基于上市险企数据"""
        result = {
            "query_time": self.query_time,
            "analysis_type": "财产险公司市场表现",
            "note": "详细保费数据需查阅各公司定期报告"
        }
        
        companies = []
        for name, code in self.COMPANY_CODES.items():
            stock_data = self._get_stock_data(code)
            if stock_data:
                companies.append({
                    "company": name,
                    "code": code,
                    "price": stock_data.get("price"),
                    "change_pct": f"{stock_data.get('change_pct')}%" if stock_data.get('change_pct') else None,
                    "pb": stock_data.get("pb"),
                    "pe": stock_data.get("pe"),
                    "market_cap_yi": round(stock_data.get("total_mv") / 1e8, 2) if stock_data.get("total_mv") else None
                })
        
        companies.sort(key=lambda x: x.get("market_cap_yi") or 0, reverse=True)
        result["companies"] = companies
        
        result["market_analysis"] = {
            "行业趋势": [
                "车险综改深化，行业竞争加剧",
                "非车险业务快速增长",
                "头部公司集中度持续提升",
                "综合成本率承压"
            ],
            "关注要点": [
                "各公司保费收入增速",
                "综合成本率变化",
                "车险与非车险占比",
                "投资收益贡献"
            ],
            "数据来源说明": "详细经营数据需查阅各公司月度保费公告及年报"
        }
        
        result["data_source"] = "AkShare实时行情 + 行业分析"
        result["data_quality"] = "实时市场数据 + 定性分析"
        
        return result
    
    def analyze_auto_insurance(self) -> dict:
        """分析车险业务 - 基于行业趋势分析"""
        result = {
            "query_time": self.query_time,
            "analysis_type": "车险业务分析",
            "note": "车险详细数据需参考各公司公告及行业统计"
        }
        
        # 获取相关公司行情
        companies = []
        for name, code in self.COMPANY_CODES.items():
            stock_data = self._get_stock_data(code)
            if stock_data:
                companies.append({
                    "company": name,
                    "code": code,
                    "price": stock_data.get("price"),
                    "change_pct": stock_data.get("change_pct")
                })
        
        result["companies"] = companies
        
        result["auto_insurance_analysis"] = {
            "改革影响": "车险综改后车均保费下降，承保利润承压",
            "竞争格局": "头部公司优势明显，市场集中度提升",
            "发展趋势": [
                "UBB车险（基于使用行为）探索",
                "新能源车险快速增长",
                "车险+服务生态构建",
                "渠道线上化转型"
            ],
            "关注指标": [
                "车均保费变化",
                "综合成本率",
                "续保率",
                "赔付率"
            ],
            "数据来源说明": "车险经营数据参考各公司公告及中国保险行业协会统计"
        }
        
        result["data_source"] = "AkShare实时行情 + 行业分析"
        result["data_quality"] = "实时市场数据 + 定性分析"
        
        return result


def main():
    parser = argparse.ArgumentParser(description="财产险业务分析器")
    parser.add_argument("--market", action="store_true", help="财险市场分析")
    parser.add_argument("--auto", action="store_true", help="车险分析")
    
    args = parser.parse_args()
    analyzer = InsurancePCAnalyzer()
    
    if args.auto:
        result = analyzer.analyze_auto_insurance()
    else:
        result = analyzer.analyze_pc_market()
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
