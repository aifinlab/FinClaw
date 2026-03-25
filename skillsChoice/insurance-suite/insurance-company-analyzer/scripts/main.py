#!/usr/bin/env python3
"""保险公司分析器 - 使用AkShare开源数据接口

功能：分析保险公司财务指标、估值水平、市场表现
数据源：AkShare开源金融数据接口
"""

import akshare as ak
import json
from datetime import datetime
import argparse


class InsuranceCompanyAnalyzer:
    """保险公司分析器 - 使用AkShare获取实时行情和财务数据"""
    
    # 上市保险公司代码映射
    COMPANY_CODES = {
        "中国平安": "601318",
        "中国人寿": "601628",
        "中国太保": "601601",
        "新华保险": "601336",
        "中国人保": "601319"
    }
    
    # 公司类型信息（用于展示）
    COMPANY_TYPES = {
        "中国平安": "综合保险",
        "中国人寿": "寿险",
        "中国太保": "综合保险",
        "新华保险": "寿险",
        "中国人保": "财险"
    }
    
    def __init__(self):
        self.query_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _get_realtime_data(self, code: str) -> dict:
        """获取实时行情 - 使用AkShare"""
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
                "total_mv": float(stock_row['总市值'].values[0]) if '总市值' in stock_row.columns else None,
                "volume": int(stock_row['成交量'].values[0]) if '成交量' in stock_row.columns else None
            }
        except Exception:
            return None
    
    def _get_financial_data(self, code: str) -> dict:
        """获取财务指标 - 使用AkShare"""
        try:
            df_fin = ak.stock_financial_analysis_indicator(symbol=code)
            if df_fin is not None and not df_fin.empty:
                latest = df_fin.iloc[0]
                return {
                    "roe": latest.get('净资产收益率', 'N/A'),
                    "roa": latest.get('总资产报酬率', 'N/A'),
                    "eps": latest.get('每股收益', 'N/A'),
                    "bvps": latest.get('每股净资产', 'N/A'),
                    "report_date": latest.get('报告期', 'N/A')
                }
        except Exception:
            pass
        return {}
    
    def analyze_company(self, company_name: str) -> dict:
        """分析保险公司 - 使用AkShare实时数据"""
        if company_name not in self.COMPANY_CODES:
            return {
                "error": f"不支持的保险公司: {company_name}",
                "supported_companies": list(self.COMPANY_CODES.keys())
            }
        
        code = self.COMPANY_CODES[company_name]
        company_type = self.COMPANY_TYPES.get(company_name, "未知")
        
        result = {
            "query_time": self.query_time,
            "company_name": company_name,
            "stock_code": code,
            "company_type": company_type
        }
        
        # 获取实时行情
        realtime_data = self._get_realtime_data(code)
        if realtime_data:
            result["realtime"] = {
                "price": realtime_data.get("price"),
                "change_pct": f"{realtime_data.get('change_pct')}%" if realtime_data.get('change_pct') else None,
                "pb": realtime_data.get("pb"),
                "pe": realtime_data.get("pe"),
                "market_cap_yi": round(realtime_data.get("total_mv") / 1e8, 2) if realtime_data.get("total_mv") else None,
                "volume": realtime_data.get("volume")
            }
            
            # 估值评估
            pb = realtime_data.get("pb")
            if pb:
                if pb < 0.8:
                    result["valuation_assessment"] = "估值偏低，关注基本面改善"
                elif pb < 1.0:
                    result["valuation_assessment"] = "估值较低，具备配置价值"
                elif pb > 1.5:
                    result["valuation_assessment"] = "估值合理偏贵"
                else:
                    result["valuation_assessment"] = "估值合理"
        else:
            result["realtime_error"] = "无法获取实时行情数据"
        
        # 获取财务指标
        fin_data = self._get_financial_data(code)
        if fin_data:
            result["financial_indicators"] = fin_data
        
        result["data_source"] = "AkShare - 东方财富"
        result["data_quality"] = "实时行情 + 财务指标"
        
        return result
    
    def compare_companies(self) -> dict:
        """对比上市保险公司 - 使用AkShare实时数据"""
        comparison = []
        
        for name, code in self.COMPANY_CODES.items():
            company_type = self.COMPANY_TYPES.get(name, "未知")
            realtime_data = self._get_realtime_data(code)
            
            comp_data = {
                "company": name,
                "code": code,
                "type": company_type
            }
            
            if realtime_data:
                comp_data.update({
                    "price": realtime_data.get("price"),
                    "change_pct": f"{realtime_data.get('change_pct')}%" if realtime_data.get('change_pct') else None,
                    "pb": realtime_data.get("pb"),
                    "pe": realtime_data.get("pe"),
                    "market_cap_yi": round(realtime_data.get("total_mv") / 1e8, 2) if realtime_data.get("total_mv") else None
                })
            
            comparison.append(comp_data)
        
        # 按市值排序
        comparison.sort(key=lambda x: x.get("market_cap_yi") or 0, reverse=True)
        
        # 计算平均估值
        valid_pb = [c["pb"] for c in comparison if c.get("pb")]
        avg_pb = round(sum(valid_pb) / len(valid_pb), 2) if valid_pb else None
        
        return {
            "query_time": self.query_time,
            "comparison": comparison,
            "total_companies": len(comparison),
            "industry_avg_pb": avg_pb,
            "data_source": "AkShare - 东方财富",
            "data_quality": "实时行情数据"
        }


def main():
    parser = argparse.ArgumentParser(description="保险公司分析器")
    parser.add_argument("--company", help="保险公司名称")
    parser.add_argument("--compare", action="store_true", help="对比所有公司")
    
    args = parser.parse_args()
    analyzer = InsuranceCompanyAnalyzer()
    
    if args.compare:
        result = analyzer.compare_companies()
    elif args.company:
        result = analyzer.analyze_company(args.company)
    else:
        result = {
            "supported_companies": list(analyzer.COMPANY_CODES.keys()),
            "usage": "--company 中国平安 或 --compare"
        }
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
