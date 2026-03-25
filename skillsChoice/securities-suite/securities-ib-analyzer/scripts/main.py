#!/usr/bin/env python3
"""券商投行业务分析器 - 使用AkShare开源数据接口

功能：分析券商投行业务、IPO承销、债券承销
数据源：AkShare开源金融数据接口
说明：详细承销数据需参考各券商年报
"""

import akshare as ak
import json
from datetime import datetime
import argparse


class SecuritiesIBAnalyzer:
    """券商投行业务分析器 - 使用AkShare获取上市券商行情"""
    
    # 主要上市券商代码映射
    SECURITIES_CODES = {
        "中信证券": "600030", "中信建投": "601066", "海通证券": "600837",
        "华泰证券": "601688", "国泰君安": "601211", "中金公司": "601995",
        "招商证券": "600999", "国信证券": "002736", "广发证券": "000776",
        "中国银河": "601881", "东方证券": "600958", "兴业证券": "601377"
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
                "total_mv": float(stock_row['总市值'].values[0]) if '总市值' in stock_row.columns else None
            }
        except Exception:
            return None
    
    def get_ipo_overview(self) -> dict:
        """获取IPO承销概览 - 基于上市券商行情"""
        result = {
            "query_time": self.query_time,
            "analysis_type": "IPO承销业务分析",
            "note": "详细IPO数据需查阅各券商年报"
        }
        
        # 获取主要券商行情
        securities = []
        for name, code in list(self.SECURITIES_CODES.items())[:8]:
            stock_data = self._get_realtime_data(code)
            if stock_data:
                securities.append({
                    "name": name,
                    "code": code,
                    "price": stock_data.get("price"),
                    "pb": stock_data.get("pb"),
                    "market_cap_yi": round(stock_data.get("total_mv") / 1e8, 2) if stock_data.get("total_mv") else None
                })
        
        # 按市值排序
        securities.sort(key=lambda x: x.get("market_cap_yi") or 0, reverse=True)
        result["securities_by_market_cap"] = securities
        
        result["ib_analysis"] = {
            "投行业务构成": [
                "IPO承销",
                "再融资承销",
                "并购重组",
                "债券承销"
            ],
            "行业趋势": [
                "注册制改革深化",
                "IPO审核趋严",
                "债券承销规模增长",
                "并购重组活跃度提升"
            ],
            "关注要点": [
                "IPO承销数量和规模",
                "债券承销排名",
                "并购重组项目",
                "投行收入占比"
            ],
            "数据来源说明": "详细数据参考各券商年报、中国证券业协会统计"
        }
        
        result["data_source"] = "AkShare开源数据 + 行业分析"
        result["data_quality"] = "实时行情 + 定性分析"
        
        return result
    
    def get_bond_underwriting(self) -> dict:
        """获取债券承销分析"""
        result = {
            "query_time": self.query_time,
            "analysis_type": "债券承销业务分析",
            "note": "详细债券承销数据需查阅各券商年报"
        }
        
        # 获取主要券商行情
        securities = []
        for name, code in list(self.SECURITIES_CODES.items())[:8]:
            stock_data = self._get_realtime_data(code)
            if stock_data:
                securities.append({
                    "name": name,
                    "code": code,
                    "price": stock_data.get("price"),
                    "pb": stock_data.get("pb")
                })
        
        result["securities"] = securities
        
        result["bond_analysis"] = {
            "债券承销类型": [
                "公司债",
                "企业债",
                "金融债",
                "ABS",
                "可转债"
            ],
            "行业特点": [
                "债券承销规模持续增长",
                "头部券商优势明显",
                "信用债风险需关注",
                "ABS业务快速发展"
            ],
            "关注要点": [
                "债券承销规模排名",
                "承销费率水平",
                "信用风险暴露",
                "细分品种优势"
            ],
            "数据来源说明": "详细数据参考各券商年报、Wind债券承销统计"
        }
        
        result["data_source"] = "AkShare开源数据 + 行业分析"
        result["data_quality"] = "实时行情 + 定性分析"
        
        return result


def main():
    parser = argparse.ArgumentParser(description="券商投行业务分析器")
    parser.add_argument("--ipo", action="store_true", help="IPO承销分析")
    parser.add_argument("--bond", action="store_true", help="债券承销分析")
    
    args = parser.parse_args()
    analyzer = SecuritiesIBAnalyzer()
    
    if args.bond:
        result = analyzer.get_bond_underwriting()
    else:
        result = analyzer.get_ipo_overview()
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
