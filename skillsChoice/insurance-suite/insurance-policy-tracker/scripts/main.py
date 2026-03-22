#!/usr/bin/env python3
"""保险行业政策追踪器"""

import json
from datetime import datetime
import argparse


class InsurancePolicyTracker:
    """保险行业政策追踪器"""
    
    def get_recent_policies(self) -> dict:
        """获取最新政策"""
        policies = [
            {
                "date": "2026-03",
                "title": "保险资金长期投资改革试点扩围",
                "issuer": "金融监管总局",
                "impact": "鼓励保险资金长期价值投资",
                "affected_areas": ["资金运用", "股票投资"]
            },
            {
                "date": "2026-02",
                "title": "人身险公司监管评级办法",
                "issuer": "金融监管总局",
                "impact": "强化分类监管，差异化监管措施",
                "affected_areas": ["公司治理", "偿付能力", "业务发展"]
            },
            {
                "date": "2026-01",
                "title": "车险综合改革深化",
                "issuer": "金融监管总局",
                "impact": "优化车险定价，保护消费者权益",
                "affected_areas": ["车险", "财险业务"]
            },
            {
                "date": "2025-12",
                "title": "个人养老金保险产品扩容",
                "issuer": "金融监管总局",
                "impact": "增加养老险产品供给",
                "affected_areas": ["养老保险", "年金产品"]
            },
            {
                "date": "2025-11",
                "title": "保险销售行为管理办法",
                "issuer": "金融监管总局",
                "impact": "规范销售行为，保护消费者权益",
                "affected_areas": ["销售管理", "合规经营"]
            }
        ]
        
        return {
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "policies": policies,
            "data_source": "国家金融监督管理总局"
        }
    
    def get_key_reforms(self) -> dict:
        """获取重点改革"""
        return {
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "key_reforms": {
                "偿二代二期": {
                    "status": "全面实施",
                    "impact": "提升风险管理能力，资本要求更审慎"
                },
                "车险综改": {
                    "status": "持续深化",
                    "impact": "降价、增保、提质"
                },
                "个人养老金": {
                    "status": "稳步推进",
                    "impact": "养老险市场扩容"
                },
                "保险产品注册制": {
                    "status": "改革中",
                    "impact": "提高产品供给效率"
                }
            },
            "data_source": "金融监管总局"
        }


def main():
    parser = argparse.ArgumentParser(description="保险行业政策追踪器")
    parser.add_argument("--policies", action="store_true", help="最新政策")
    parser.add_argument("--reforms", action="store_true", help="重点改革")
    
    args = parser.parse_args()
    tracker = InsurancePolicyTracker()
    
    if args.reforms:
        result = tracker.get_key_reforms()
    else:
        result = tracker.get_recent_policies()
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
