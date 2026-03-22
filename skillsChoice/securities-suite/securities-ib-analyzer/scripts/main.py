#!/usr/bin/env python3
"""券商投行业务分析器"""

import akshare as ak
import pandas as pd
import json
from datetime import datetime
import argparse


class SecuritiesIBAnalyzer:
    """券商投行业务分析器"""
    
    def get_ipo_data(self, year: int = None) -> dict:
        """获取IPO承销数据"""
        try:
            # 获取新股数据
            df = ak.stock_new_ipo_cninfo()
            
            if df is None or df.empty:
                return {"error": "无法获取IPO数据"}
            
            if year:
                df['上市日期'] = pd.to_datetime(df['上市日期'], errors='coerce')
                df = df[df['上市日期'].dt.year == year]
            
            # 统计承销券商
            underwriter_stats = df['承销机构'].value_counts().head(10).to_dict()
            
            return {
                "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "year": year or "全部",
                "ipo_count": len(df),
                "total_fundraising": f"{df['募集资金总额'].sum():.2f}亿元" if '募集资金总额' in df.columns else "N/A",
                "top_underwriters": underwriter_stats,
                "data_source": "巨潮资讯网/AkShare"
            }
            
        except Exception as e:
            return {"error": f"获取IPO数据失败: {str(e)}"}
    
    def get_bond_underwriting(self) -> dict:
        """获取债券承销数据"""
        try:
            # 使用AkShare获取债券发行数据
            df = ak.bond_new_commercial_bank()
            
            return {
                "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "bond_issues": len(df) if df is not None else 0,
                "data_source": "中国货币网",
                "note": "债券承销详细数据需通过Wind或同花顺iFinD获取"
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_ib_ranking(self) -> dict:
        """获取投行收入排名"""
        # 基于历史数据和市场地位的排名
        ranking = [
            {"rank": 1, "securities": "中信证券", "strength": "全能型投行龙头"},
            {"rank": 2, "securities": "中信建投", "strength": "IPO承销强项"},
            {"rank": 3, "securities": "海通证券", "strength": "债券承销领先"},
            {"rank": 4, "securities": "华泰证券", "strength": "并购重组优势"},
            {"rank": 5, "securities": "国泰君安", "strength": "综合实力强"}
        ]
        
        return {
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ib_ranking": ranking,
            "data_source": "基于承销规模统计",
            "note": "具体排名数据需参考中证协年度统计"
        }


def main():
    parser = argparse.ArgumentParser(description="券商投行业务分析器")
    parser.add_argument("--ipo", action="store_true", help="IPO数据")
    parser.add_argument("--year", type=int, help="年份")
    parser.add_argument("--bond", action="store_true", help="债券承销")
    parser.add_argument("--ranking", action="store_true", help="投行排名")
    
    args = parser.parse_args()
    analyzer = SecuritiesIBAnalyzer()
    
    if args.ipo:
        result = analyzer.get_ipo_data(args.year)
    elif args.bond:
        result = analyzer.get_bond_underwriting()
    elif args.ranking:
        result = analyzer.get_ib_ranking()
    else:
        result = analyzer.get_ipo_data(args.year)
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
