#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
开户转化追踪器

功能：
1. 转化漏斗分析
2. 转化率计算
3. 障碍分析
4. 转化周期统计

使用示例：
    from conversion_tracker import ConversionTracker

    tracker = ConversionTracker()

    # 添加客户转化数据
    tracker.add_customer("张三", "潜在", "2024-01-01")
    tracker.update_stage("张三", "意向", "2024-01-03")
    tracker.update_stage("张三", "开户", "2024-01-05")
    tracker.update_stage("张三", "入金", "2024-01-07")

    # 添加更多客户...

    print(tracker.generate_funnel_report())
    print(tracker.calculate_conversion_metrics())
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional


@dataclass
class CustomerJourney:
    """客户转化旅程"""
    name: str
    stages: List[tuple] = field(default_factory=list)  # [(stage, date), ...]
    current_stage: str = "潜在"
    converted: bool = False
    conversion_days: int = 0


class ConversionTracker:
    """开户转化追踪器"""

    # 转化阶段定义
    STAGES = ["潜在", "意向", "开户", "入金", "活跃"]

    # 各阶段典型转化率（行业参考）
    BENCHMARK_RATES = {
        "潜在→意向": 0.50,
        "意向→开户": 0.60,
        "开户→入金": 0.60,
        "入金→活跃": 0.50,
        "整体转化": 0.10,
    }

    def __init__(self):
        self.customers: Dict[str, CustomerJourney] = {}

    def add_customer(self, name: str, stage: str = "潜在", date: str = None) -> None:
        """
        添加客户

        Args:
            name: 客户姓名
            stage: 初始阶段
            date: 日期（YYYY-MM-DD）
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        self.customers[name] = CustomerJourney(
            name=name,
            stages=[(stage, date)],
            current_stage=stage,
        )

    def update_stage(self, name: str, new_stage: str, date: str = None) -> bool:
        """
        更新客户阶段

        Args:
            name: 客户姓名
            new_stage: 新阶段
            date: 日期

        Returns:
            是否更新成功
        """
        if name not in self.customers:
            return False

        if new_stage not in self.STAGES:
            return False

        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        customer = self.customers[name]
        customer.stages.append((new_stage, date))
        customer.current_stage = new_stage

        # 检查是否完成转化（到达"活跃"阶段）
        if new_stage == "活跃":
            customer.converted = True
            # 计算转化周期
            start_date = datetime.strptime(customer.stages[0][1], "%Y-%m-%d")
            end_date = datetime.strptime(date, "%Y-%m-%d")
            customer.conversion_days = (end_date - start_date).days

        return True

    def get_stage_counts(self) -> Dict[str, int]:
        """获取各阶段客户数量"""
        counts = {stage: 0 for stage in self.STAGES}

        for customer in self.customers.values():
            stage = customer.current_stage
            if stage in counts:
                counts[stage] += 1

        return counts

    def calculate_conversion_rates(self) -> Dict[str, float]:
        """计算各阶段转化率"""
        counts = self.get_stage_counts()
        rates = {}

        # 潜在→意向
        if counts["潜在"] > 0:
            rates["潜在→意向"] = counts["意向"] / counts["潜在"]

        # 意向→开户
        if counts["意向"] > 0:
            rates["意向→开户"] = counts["开户"] / counts["意向"]

        # 开户→入金
        if counts["开户"] > 0:
            rates["开户→入金"] = counts["入金"] / counts["开户"]

        # 入金→活跃
        if counts["入金"] > 0:
            rates["入金→活跃"] = counts["活跃"] / counts["入金"]

        # 整体转化
        if counts["潜在"] > 0:
            rates["整体转化"] = counts["活跃"] / counts["潜在"]

        return rates

    def calculate_average_conversion_days(self) -> float:
        """计算平均转化周期"""
        converted_customers = [c for c in self.customers.values() if c.converted]

        if not converted_customers:
            return 0

        total_days = sum(c.conversion_days for c in converted_customers)
        return total_days / len(converted_customers)

    def identify_bottlenecks(self) -> List[Dict]:
        """识别转化瓶颈"""
        rates = self.calculate_conversion_rates()
        bottlenecks = []

        for stage_transition, rate in rates.items():
            benchmark = self.BENCHMARK_RATES.get(stage_transition, 0.5)
            if rate < benchmark * 0.7:  # 低于基准的 70% 视为瓶颈
                bottlenecks.append({
                    "transition": stage_transition,
                    "rate": rate,
                    "benchmark": benchmark,
                    "gap": benchmark - rate,
                    "severity": "高" if rate < benchmark * 0.5 else "中",
                })

        # 按差距排序
        bottlenecks.sort(key=lambda x: x["gap"], reverse=True)

        return bottlenecks

    def generate_funnel_report(self) -> str:
        """
        生成转化漏斗报告

        Returns:
            格式化报告文本
        """
        lines = []
        lines.append("=" * 60)
        lines.append("开户转化漏斗报告")
        lines.append(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append("=" * 60)
        lines.append("")

        counts = self.get_stage_counts()
        rates = self.calculate_conversion_rates()
        total = len(self.customers)

        # 漏斗展示
        lines.append("【转化漏斗】")
        lines.append("")

        max_count = max(counts.values()) if counts.values() else 1

        for i, stage in enumerate(self.STAGES):
            count = counts[stage]
            pct = count / total * 100 if total > 0 else 0
            bar_length = int(count / max_count * 40) if max_count > 0 else 0
            bar = "█" * bar_length

            lines.append(f"{stage:<6} {bar:<40} {count:>4} ({pct:>5.1f}%)")

            # 显示转化率
            if i > 0:
                prev_stage = self.STAGES[i - 1]
                transition = f"{prev_stage}→{stage}"
                rate = rates.get(transition, 0)
                benchmark = self.BENCHMARK_RATES.get(transition, 0)
                status = "✅" if rate >= benchmark else "⚠️"
                lines.append(f"       {status} 转化率：{rate * 100:.1f}% (基准：{benchmark * 100:.0f}%)")

        lines.append("")

        # 转化指标
        lines.append("【转化指标】")
        lines.append(f"  总客户数：{total}")
        lines.append(f"  已转化客户：{sum(1 for c in self.customers.values() if c.converted)}")
        lines.append(f"  整体转化率：{rates.get('整体转化', 0) * 100:.1f}%")
        lines.append(f"  平均转化周期：{self.calculate_average_conversion_days():.1f} 天")
        lines.append("")

        # 瓶颈分析
        bottlenecks = self.identify_bottlenecks()
        if bottlenecks:
            lines.append("【瓶颈分析】")
            for bn in bottlenecks:
                lines.append(f"  ⚠️ {bn['transition']}: {bn['rate'] * 100:.1f}% (基准：{bn['benchmark'] * 100:.0f}%), 严重性：{bn['severity']}")
            lines.append("")

        lines.append("=" * 60)

        return "\n".join(lines)

    def calculate_conversion_metrics(self) -> Dict:
        """
        计算转化指标

        Returns:
            指标字典
        """
        counts = self.get_stage_counts()
        rates = self.calculate_conversion_rates()

        return {
            "total_customers": len(self.customers),
            "converted_customers": sum(1 for c in self.customers.values() if c.converted),
            "conversion_rate": rates.get("整体转化", 0),
            "average_conversion_days": self.calculate_average_conversion_days(),
            "stage_counts": counts,
            "stage_rates": rates,
            "bottlenecks": self.identify_bottlenecks(),
        }


# 快速测试
if __name__ == "__main__":
    tracker = ConversionTracker()

    # 模拟数据
    import random

    for i in range(50):
        name = f"客户{i + 1}"
        tracker.add_customer(name, "潜在", "2024-01-01")

        # 模拟转化过程
        if random.random() < 0.5:
            tracker.update_stage(name, "意向", "2024-01-03")
            if random.random() < 0.6:
                tracker.update_stage(name, "开户", "2024-01-05")
                if random.random() < 0.6:
                    tracker.update_stage(name, "入金", "2024-01-07")
                    if random.random() < 0.5:
                        tracker.update_stage(name, "活跃", "2024-01-10")

    print(tracker.generate_funnel_report())
