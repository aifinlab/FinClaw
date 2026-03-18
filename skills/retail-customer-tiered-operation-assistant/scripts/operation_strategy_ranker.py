#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from typing import Dict, List

STRATEGIES = {
    "重点维护层": {
        "经营目标": "维护关系与提升综合贡献",
        "推荐动作": ["客户经理重点回访", "财富配置沟通", "高价值活动邀约"],
        "推荐渠道": ["客户经理电话", "线下网点", "企业微信"]
    },
    "潜力提升层": {
        "经营目标": "提升资产留存和产品渗透",
        "推荐动作": ["首购产品引导", "工资代发深耕", "主结算关系提升"],
        "推荐渠道": ["客户经理电话", "APP 消息", "短信"]
    },
    "经营转化层": {
        "经营目标": "提升活跃与轻转化",
        "推荐动作": ["活动触达", "权益提醒", "轻量产品推荐"],
        "推荐渠道": ["APP 消息", "短信", "电话外呼"]
    },
    "唤醒激活层": {
        "经营目标": "恢复触达和唤醒使用",
        "推荐动作": ["沉默唤醒活动", "功能提醒", "低门槛权益触达"],
        "推荐渠道": ["短信", "APP 消息"]
    },
    "流失挽留层": {
        "经营目标": "识别流失原因并实施挽留",
        "推荐动作": ["专项回访", "资产流失排查", "服务补救与关怀"],
        "推荐渠道": ["客户经理电话", "人工回访"]
    }
}


def rank_operations(tiered_customers: List[Dict]) -> List[Dict]:
    results = []
    for idx, item in enumerate(tiered_customers, start=1):
        tier = item.get("层级", "经营转化层")
        plan = STRATEGIES.get(tier, STRATEGIES["经营转化层"])
        results.append({
            "优先级": idx,
            "客户标识": item.get("客户标识"),
            "层级": tier,
            "经营目标": plan["经营目标"],
            "推荐动作": plan["推荐动作"],
            "推荐渠道": plan["推荐渠道"],
            "总分": item.get("总分")
        })
    return results


if __name__ == "__main__":
    import sys
    data = json.load(sys.stdin)
    print(json.dumps(rank_operations(data), ensure_ascii=False, indent=2))
