#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
营销机会评分器

功能：
1. 营销机会识别
2. 机会评分（0-100）
3. 优先级排序
4. 跟进建议生成

使用示例：
from dataclasses import dataclass

    scorer = OpportunityScorer()

    opportunities = [
        {
            "customer_name": "张三",
            "signal_type": "资金到期",
            "amount": 1000000,
            "urgency": "高",
            "trust_level": "高",
            "last_interaction_days": 3,
        },
        # ... 更多机会
    ]

    results = scorer.score_opportunities(opportunities)
    print(scorer.generate_ranking(results))
"""

from datetime import datetime
from opportunity_scorer import OpportunityScorer
from typing import List, Dict


@dataclass
class Opportunity:
    """营销机会"""
    customer_name: str
    signal_type: str
    amount: float
    urgency: str  # 高/中/低
    trust_level: str  # 高/中/低
    last_interaction_days: int
    score: int = 0
    priority: str = ""


class OpportunityScorer:
    """营销机会评分器"""

    # 信号类型权重
    SIGNAL_WEIGHTS = {
        "资金到期": 30,
        "主动咨询": 25,
        "痛点抱怨": 20,
        "生活事件": 15,
        "市场机会": 15,
        "服务节点": 10,
        "常规互动": 5,
    }

    # 紧迫性权重
    URGENCY_WEIGHTS = {
        "高": 1.0,
        "中": 0.6,
        "低": 0.3,
    }

    # 信任度权重
    TRUST_WEIGHTS = {
        "高": 1.0,
        "中": 0.7,
        "低": 0.4,
    }

    # 互动时效权重
    INTERACTION_WEIGHTS = {
        (0, 7): 1.0,  # 7 天内
        (8, 30): 0.8,  # 30 天内
        (31, 90): 0.5,  # 90 天内
        (91, 180): 0.3,  # 180 天内
        (181, float('inf')): 0.1,  # 180 天以上
    }

    def __init__(self):
        pass

    def calculate_score(self, opportunity: Dict) -> int:
        """
        计算机会评分（0-100）

        Args:
            opportunity: 机会信息

        Returns:
            机会评分
        """
        score = 0

        # 1. 信号类型基础分（0-30）
        signal_type = opportunity.get("signal_type", "常规互动")
        signal_score = self.SIGNAL_WEIGHTS.get(signal_type, 5)
        score += signal_score

        # 2. 资金规模分（0-20）
        amount = opportunity.get("amount", 0)
        if amount >= 5000000:
            amount_score = 20
        elif amount >= 1000000:
            amount_score = 15
        elif amount >= 500000:
            amount_score = 10
        elif amount >= 100000:
            amount_score = 5
        else:
            amount_score = 2
        score += amount_score

        # 3. 紧迫性系数
        urgency = opportunity.get("urgency", "中")
        urgency_multiplier = self.URGENCY_WEIGHTS.get(urgency, 0.6)

        # 4. 信任度系数
        trust_level = opportunity.get("trust_level", "中")
        trust_multiplier = self.TRUST_WEIGHTS.get(trust_level, 0.7)

        # 5. 互动时效系数
        last_days = opportunity.get("last_interaction_days", 999)
        interaction_multiplier = 0.1
        for (min_days, max_days), multiplier in self.INTERACTION_WEIGHTS.items():
            if min_days <= last_days <= max_days:
                interaction_multiplier = multiplier
                break

        # 计算最终分数
        base_score = score  # 0-50
        multiplier = (urgency_multiplier + trust_multiplier + interaction_multiplier) / 3

        final_score = int(base_score * 2 * multiplier)  # 0-100

        return min(100, max(0, final_score))

    def get_priority(self, score: int) -> str:
        """根据评分获取优先级"""
        if score >= 70:
            return "P0"
        elif score >= 50:
            return "P1"
        elif score >= 30:
            return "P2"
        else:
            return "P3"

    def get_followup_suggestion(self, score: int, signal_type: str) -> str:
        """根据评分和信号类型给出跟进建议"""
        if score >= 70:
            return "24 小时内电话跟进，重点沟通"
        elif score >= 50:
            return "3 日内微信/电话跟进"
        elif score >= 30:
            return "1 周内微信跟进，保持联系"
        else:
            return "定期维护，有合适机会再联系"

    def score_opportunities(self, opportunities: List[Dict]) -> List[Dict]:
        """
        批量评分机会

        Args:
            opportunities: 机会列表

        Returns:
            评分后的机会列表
        """
        results = []

        for opp in opportunities:
            score = self.calculate_score(opp)
            priority = self.get_priority(score)

            result = {
                **opp,
                "score": score,
                "priority": priority,
                "followup_suggestion": self.get_followup_suggestion(score, opp.get("signal_type", "")),
            }
            results.append(result)

        # 按评分降序排序
        results.sort(key=lambda x: x["score"], reverse=True)

        return results

    def generate_ranking(self, opportunities: List[Dict], top_n: int = 10) -> str:
        """
        生成机会排名列表

        Args:
            opportunities: 机会列表
            top_n: 显示前 N 名

        Returns:
            格式化排名文本
        """
        lines = []
        lines.append("=" * 90)
        lines.append("营销机会优先级排名")
        lines.append(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append("=" * 90)
        lines.append("")

        lines.append(f"{'排名':<4} {'客户':<10} {'信号类型':<12} {'金额 (万)':<10} {'紧迫性':<8} {'信任度':<8} {'评分':<6} {'优先级':<8}")
        lines.append("-" * 90)

        for i, opp in enumerate(opportunities[:top_n], 1):
            lines.append(
                f"{i:<4} {opp['customer_name']:<10} {opp['signal_type']:<12} "
                f"{opp.get('amount', 0) / 10000:<10.0f} {opp['urgency']:<8} "
                f"{opp['trust_level']:<8} {opp['score']:<6} {opp['priority']:<8}"
            )

        lines.append("")
        lines.append("=" * 90)

        # 汇总统计
        p0_count = sum(1 for o in opportunities if o.get("priority") == "P0")
        p1_count = sum(1 for o in opportunities if o.get("priority") == "P1")
        p2_count = sum(1 for o in opportunities if o.get("priority") == "P2")
        p3_count = sum(1 for o in opportunities if o.get("priority") == "P3")

        total_amount = sum(o.get("amount", 0) for o in opportunities)

        lines.append("汇总统计:")
        lines.append(f"  总机会数：{len(opportunities)}")
        lines.append(f"  P0 级：{p0_count} 人")
        lines.append(f"  P1 级：{p1_count} 人")
        lines.append(f"  P2 级：{p2_count} 人")
        lines.append(f"  P3 级：{p3_count} 人")
        lines.append(f"  潜在资金规模：{total_amount / 10000:.0f} 万")
        lines.append("=" * 90)

        return "\n".join(lines)

    def generate_action_plan(self, opportunities: List[Dict]) -> str:
        """
        生成行动计划

        Args:
            opportunities: 机会列表

        Returns:
            格式化行动计划文本
        """
        lines = []
        lines.append("=" * 80)
        lines.append("营销机会行动计划")
        lines.append("=" * 80)
        lines.append("")

        # 按优先级分组
        priority_groups = {"P0": [], "P1": [], "P2": [], "P3": []}
        for opp in opportunities:
            priority = opp.get("priority", "P3")
            priority_groups[priority].append(opp)

        for priority in ["P0", "P1", "P2", "P3"]:
            group = priority_groups[priority]
            if not group:
                continue

            lines.append(f"【{priority} 级 - {len(group)} 人】")
            lines.append("-" * 60)

            for opp in group:
                lines.append(f"客户：{opp['customer_name']}")
                lines.append(f"  信号：{opp['signal_type']}")
                lines.append(f"  金额：{opp.get('amount', 0) / 10000:.0f} 万")
                lines.append(f"  跟进建议：{opp.get('followup_suggestion', 'N/A')}")
                lines.append("")

        lines.append("=" * 80)

        return "\n".join(lines)


# 快速测试
if __name__ == "__main__":
    scorer = OpportunityScorer()

    opportunities = [
        {"customer_name": "张三", "signal_type": "资金到期", "amount": 1000000, "urgency": "高", "trust_level": "高", "last_interaction_days": 3},
        {"customer_name": "李四", "signal_type": "主动咨询", "amount": 500000, "urgency": "中", "trust_level": "高", "last_interaction_days": 7},
        {"customer_name": "王五", "signal_type": "痛点抱怨", "amount": 2000000, "urgency": "高", "trust_level": "中", "last_interaction_days": 15},
        {"customer_name": "赵六", "signal_type": "市场机会", "amount": 300000, "urgency": "低", "trust_level": "低", "last_interaction_days": 60},
        {"customer_name": "钱七", "signal_type": "服务节点", "amount": 5000000, "urgency": "中", "trust_level": "高", "last_interaction_days": 5},
    ]

    results = scorer.score_opportunities(opportunities)
    print(scorer.generate_ranking(results))
    print("\n")
    print(scorer.generate_action_plan(results))
