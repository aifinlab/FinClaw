#!/usr/bin/env python3
"""保险行业对比分析器"""

import json
from datetime import datetime
import argparse


class InsuranceSectorComparison:
    """保险行业对比分析器"""
    
    def compare_global_markets(self) -> dict:
        """对比全球保险市场"""
        return {
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "global_comparison": {
                "全球市场规模": {
                    "total_premium": "约7万亿美元",
                    "life_share": "52%",
                    "non_life_share": "48%"
                },
                "主要市场": {
                    "美国": {
                        "premium": "约1.4万亿美元",
                        "global_share": "20%",
                        "penetration": "7.5%"
                    },
                    "中国": {
                        "premium": "约0.8万亿美元",
                        "global_share": "11%",
                        "penetration": "4.5%"
                    },
                    "日本": {
                        "premium": "约0.4万亿美元",
                        "global_share": "6%",
                        "penetration": "8.5%"
                    },
                    "英国": {
                        "premium": "约0.3万亿美元",
                        "global_share": "4%",
                        "penetration": "10%"
                    }
                }
            },
            "china_position": {
                "global_rank": "全球第2大保险市场",
                "growth_potential": "保险深度/密度仍有提升空间",
                "key_opportunities": ["养老保险", "健康保险", "农业保险"]
            },
            "data_source": "瑞士再保险研究所、行业报告"
        }
    
    def compare_penetration(self) -> dict:
        """对比保险深度和密度"""
        return {
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "penetration_comparison": {
                "保险深度(保费/GDP)": {
                    "全球平均": "6.8%",
                    "发达市场平均": "8.5%",
                    "新兴市场平均": "3.5%",
                    "中国": "4.5%",
                    "中国台湾": "18%",
                    "中国香港": "18%",
                    "日本": "8.5%",
                    "美国": "7.5%"
                },
                "保险密度(人均保费)": {
                    "全球平均": "约800美元",
                    "发达市场平均": "约3500美元",
                    "新兴市场平均": "约150美元",
                    "中国": "约550美元",
                    "中国香港": "约8000美元",
                    "日本": "约3500美元",
                    "美国": "约4500美元"
                }
            },
            "analysis": "中国保险深度和密度均低于发达市场，发展潜力大",
            "data_source": "瑞士再保险研究所"
        }


def main():
    parser = argparse.ArgumentParser(description="保险行业对比分析器")
    parser.add_argument("--global", action="store_true", help="全球市场对比")
    parser.add_argument("--penetration", action="store_true", help="保险深度/密度对比")
    
    args = parser.parse_args()
    comparator = InsuranceSectorComparison()
    
    if args.penetration:
        result = comparator.compare_penetration()
    else:
        result = comparator.compare_global_markets()
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
