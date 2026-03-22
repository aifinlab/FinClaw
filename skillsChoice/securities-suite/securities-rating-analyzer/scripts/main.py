#!/usr/bin/env python3
"""券商评级分析器"""

import json
from datetime import datetime
import argparse


class SecuritiesRatingAnalyzer:
    """券商评级分析器"""
    
    def get_latest_ratings(self) -> dict:
        """获取最新券商评级"""
        # 基于最新年度证监会分类评价结果的头部券商数据
        ratings = {
            "AA级": ["中信证券", "华泰证券", "海通证券", "国泰君安", "招商证券", 
                     "广发证券", "中金公司", "中信建投", "东方证券", "兴业证券"],
            "A级": ["光大证券", "国信证券", "申万宏源", "中国银河", "方正证券",
                    "浙商证券", "东吴证券", "财通证券", "国金证券", "华安证券"],
            "BBB级": ["长城证券", "国联证券", "南京证券", "红塔证券", "中银证券"]
        }
        
        return {
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "year": "2024",
            "ratings": ratings,
            "total_count": sum(len(v) for v in ratings.values()),
            "data_source": "证监会证券公司分类评价结果",
            "note": "完整评级名单以证监会发布为准"
        }
    
    def get_rating_by_securities(self, name: str) -> dict:
        """查询单家券商评级"""
        ratings_data = self.get_latest_ratings()
        
        for level, securities_list in ratings_data["ratings"].items():
            if name in securities_list:
                return {
                    "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "securities_name": name,
                    "rating": level,
                    "year": "2024",
                    "privileges": self._get_privileges(level)
                }
        
        return {
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "securities_name": name,
            "rating": "未查询到",
            "note": "可能为更低评级或未在头部名单"
        }
    
    def _get_privileges(self, level: str) -> list:
        """获取对应级别的业务资格"""
        privileges_map = {
            "AA级": ["所有创新业务", "场外期权一级交易商", "跨境业务", "衍生品全牌照"],
            "A级": ["大部分创新业务", "场外期权二级交易商", "跨境业务", "衍生品业务"],
            "BBB级": ["常规业务", "部分创新业务"],
            "BB级": ["基础业务", "有限创新业务"],
            "B级": ["基础业务"]
        }
        return privileges_map.get(level, ["基础业务"])


def main():
    parser = argparse.ArgumentParser(description="券商评级分析器")
    parser.add_argument("--all", action="store_true", help="全部评级")
    parser.add_argument("--securities", help="查询特定券商")
    
    args = parser.parse_args()
    analyzer = SecuritiesRatingAnalyzer()
    
    if args.securities:
        result = analyzer.get_rating_by_securities(args.securities)
    else:
        result = analyzer.get_latest_ratings()
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
