#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
客户流失预测器

功能：
1. 流失风险评分
2. 流失原因分析
3. 挽留方案推荐
4. 挽留成功率预测

使用示例：
    from churn_predictor import ChurnPredictor
    
    predictor = ChurnPredictor()
    
    customers = [
        {"name": "张三", "assets_change": -0.6, "interaction_days": 90, "complaints": 2, "pnl": -0.2},
        {"name": "李四", "assets_change": -0.3, "interaction_days": 45, "complaints": 0, "pnl": 0.05},
        # ... 更多客户
    ]
    
    results = predictor.predict_churn(customers)
    print(predictor.generate_churn_warning_report(results))
"""

from typing import List, Dict
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ChurnRisk:
    """流失风险"""
    name: str
    risk_score: int
    risk_level: str  # 高危/高/中/低
    risk_factors: List[str]
    retention_strategy: str
    retention_probability: float


class ChurnPredictor:
    """客户流失预测器"""
    
    # 风险因素权重
    RISK_FACTORS = {
        "assets_decline": {"weight": 30, "name": "资产大幅转出"},
        "no_interaction": {"weight": 25, "name": "长期不互动"},
        "complaints": {"weight": 20, "name": "投诉频繁"},
        "poor_performance": {"weight": 15, "name": "业绩不佳"},
        "competitor_inquiry": {"weight": 10, "name": "对比竞品"},
    }
    
    # 风险等级阈值
    RISK_LEVELS = {
        "高危": 70,
        "高": 50,
        "中": 30,
        "低": 0,
    }
    
    # 挽留策略
    RETENTION_STRATEGIES = {
        "高危": "高层介入，专属方案，紧急挽留",
        "高": "专人跟进，了解原因，定制挽留",
        "中": "主动沟通，服务改进，定期回访",
        "低": "常规维护，保持联系",
    }
    
    def __init__(self):
        pass
    
    def calculate_risk_score(self, customer: Dict) -> int:
        """
        计算流失风险评分（0-100）
        
        Args:
            customer: 客户信息
        
        Returns:
            风险评分
        """
        score = 0
        
        # 1. 资产变化（-1 到 1，负值表示转出）
        assets_change = customer.get("assets_change", 0)
        if assets_change < -0.5:
            score += 30
        elif assets_change < -0.3:
            score += 20
        elif assets_change < -0.1:
            score += 10
        
        # 2. 未互动天数
        interaction_days = customer.get("interaction_days", 0)
        if interaction_days > 180:
            score += 25
        elif interaction_days > 90:
            score += 15
        elif interaction_days > 30:
            score += 5
        
        # 3. 投诉次数
        complaints = customer.get("complaints", 0)
        if complaints >= 3:
            score += 20
        elif complaints >= 1:
            score += 10
        
        # 4. 持仓收益
        pnl = customer.get("pnl", 0)
        if pnl < -0.3:
            score += 15
        elif pnl < -0.1:
            score += 5
        
        # 5. 竞品对比
        if customer.get("competitor_inquiry", False):
            score += 10
        
        return min(100, score)
    
    def determine_risk_level(self, score: int) -> str:
        """根据评分确定风险等级"""
        for level, threshold in self.RISK_LEVELS.items():
            if score >= threshold:
                return level
        return "低"
    
    def identify_risk_factors(self, customer: Dict) -> List[str]:
        """识别风险因素"""
        factors = []
        
        if customer.get("assets_change", 0) < -0.3:
            factors.append("资产大幅转出")
        
        if customer.get("interaction_days", 0) > 90:
            factors.append("长期不互动")
        
        if customer.get("complaints", 0) >= 1:
            factors.append("有投诉记录")
        
        if customer.get("pnl", 0) < -0.1:
            factors.append("持仓亏损")
        
        if customer.get("competitor_inquiry", False):
            factors.append("对比竞品")
        
        return factors
    
    def calculate_retention_probability(self, risk_level: str, customer: Dict) -> float:
        """
        计算挽留成功概率
        
        Args:
            risk_level: 风险等级
            customer: 客户信息
        
        Returns:
            挽留成功概率（0-1）
        """
        base_prob = {
            "高危": 0.3,
            "高": 0.5,
            "中": 0.7,
            "低": 0.9,
        }
        
        prob = base_prob.get(risk_level, 0.5)
        
        # 根据客户价值调整
        assets = customer.get("assets", 0)
        if assets > 5000000:
            prob += 0.1  # 高价值客户更值得挽留
        elif assets < 100000:
            prob -= 0.1
        
        return min(1.0, max(0.0, prob))
    
    def predict_churn(self, customers: List[Dict]) -> List[Dict]:
        """
        批量预测流失风险
        
        Args:
            customers: 客户列表
        
        Returns:
            预测结果列表
        """
        results = []
        
        for customer in customers:
            risk_score = self.calculate_risk_score(customer)
            risk_level = self.determine_risk_level(risk_score)
            risk_factors = self.identify_risk_factors(customer)
            retention_prob = self.calculate_retention_probability(risk_level, customer)
            
            result = {
                **customer,
                "risk_score": risk_score,
                "risk_level": risk_level,
                "risk_factors": risk_factors,
                "retention_strategy": self.RETENTION_STRATEGIES[risk_level],
                "retention_probability": retention_prob,
            }
            results.append(result)
        
        # 按风险评分降序排序
        results.sort(key=lambda x: x["risk_score"], reverse=True)
        
        return results
    
    def generate_churn_warning_report(self, customers: List[Dict]) -> str:
        """
        生成流失预警报告
        
        Args:
            customers: 预测结果列表
        
        Returns:
            格式化报告文本
        """
        lines = []
        lines.append("=" * 80)
        lines.append("客户流失预警报告")
        lines.append(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append("=" * 80)
        lines.append("")
        
        # 汇总统计
        total = len(customers)
        level_counts = {"高危": 0, "高": 0, "中": 0, "低": 0}
        total_assets = 0
        
        for customer in customers:
            level = customer.get("risk_level", "低")
            level_counts[level] = level_counts.get(level, 0) + 1
            total_assets += customer.get("assets", 0)
        
        lines.append("【汇总统计】")
        lines.append(f"  评估客户数：{total}")
        lines.append(f"  涉及资产：{total_assets / 10000:.0f} 万")
        lines.append("")
        
        lines.append("  风险分布:")
        for level in ["高危", "高", "中", "低"]:
            count = level_counts.get(level, 0)
            pct = count / total * 100 if total > 0 else 0
            lines.append(f"    {level}: {count} 人 ({pct:.1f}%)")
        lines.append("")
        
        # 高危客户清单
        high_risk = [c for c in customers if c.get("risk_level") in ["高危", "高"]]
        
        if high_risk:
            lines.append("【高危客户清单】")
            lines.append("")
            lines.append(f"{'客户':<10} {'风险评分':<10} {'风险等级':<8} {'风险因素':<30} {'挽留概率':<10}")
            lines.append("-" * 80)
            
            for customer in high_risk[:15]:  # 显示前 15 个
                factors = ", ".join(customer.get("risk_factors", [])[:3])
                lines.append(
                    f"{customer['name']:<10} {customer['risk_score']:<10} "
                    f"{customer['risk_level']:<8} {factors:<30} "
                    f"{customer.get('retention_probability', 0) * 100:<10.0f}%"
                )
            
            lines.append("")
            
            # 挽留建议
            lines.append("【挽留建议】")
            for level in ["高危", "高"]:
                level_customers = [c for c in high_risk if c.get("risk_level") == level]
                if level_customers:
                    lines.append(f"  {level} ({len(level_customers)}人):")
                    lines.append(f"    策略：{self.RETENTION_STRATEGIES[level]}")
                    lines.append(f"    平均挽留概率：{sum(c.get('retention_probability', 0) for c in level_customers) / len(level_customers) * 100:.0f}%")
            lines.append("")
        
        # 行动建议
        lines.append("【行动建议】")
        lines.append("  1. 立即联系高危客户，了解流失原因")
        lines.append("  2. 针对高价值客户制定专属挽留方案")
        lines.append("  3. 分析共性原因，改进服务")
        lines.append("  4. 建立流失预警机制，提前干预")
        lines.append("")
        
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def generate_retention_plan(self, customer: Dict) -> str:
        """
        生成单个客户挽留方案
        
        Args:
            customer: 客户信息
        
        Returns:
            挽留方案文本
        """
        lines = []
        lines.append("=" * 60)
        lines.append(f"客户挽留方案 - {customer['name']}")
        lines.append("=" * 60)
        lines.append("")
        
        lines.append(f"风险等级：{customer.get('risk_level', 'N/A')}")
        lines.append(f"风险评分：{customer.get('risk_score', 0)}")
        lines.append(f"挽留概率：{customer.get('retention_probability', 0) * 100:.0f}%")
        lines.append("")
        
        lines.append("风险因素:")
        for factor in customer.get("risk_factors", []):
            lines.append(f"  - {factor}")
        lines.append("")
        
        lines.append("挽留策略:")
        lines.append(f"  {customer.get('retention_strategy', 'N/A')}")
        lines.append("")
        
        lines.append("具体行动:")
        lines.append("  Day 1: 电话联系，了解原因")
        lines.append("  Day 3: 根据原因制定方案")
        lines.append("  Day 7: 跟进方案执行")
        lines.append("  Day 14: 确认挽留结果")
        lines.append("")
        
        lines.append("=" * 60)
        
        return "\n".join(lines)


# 快速测试
if __name__ == "__main__":
    predictor = ChurnPredictor()
    
    customers = [
        {"name": "张三", "assets": 5000000, "assets_change": -0.6, "interaction_days": 90, "complaints": 2, "pnl": -0.2},
        {"name": "李四", "assets": 2000000, "assets_change": -0.3, "interaction_days": 45, "complaints": 0, "pnl": 0.05},
        {"name": "王五", "assets": 10000000, "assets_change": -0.8, "interaction_days": 180, "complaints": 3, "pnl": -0.4},
        {"name": "赵六", "assets": 500000, "assets_change": -0.1, "interaction_days": 30, "complaints": 0, "pnl": -0.05},
    ]
    
    results = predictor.predict_churn(customers)
    print(predictor.generate_churn_warning_report(results))
