#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量风险筛查工具

功能：
1. 批量客户风险筛查
2. 风险等级评估
3. 优先级排序
4. 生成风险提示清单

使用示例：
    from risk_batch_checker import RiskBatchChecker
    
    checker = RiskBatchChecker()
    
    customers = [
        {
            "name": "张三",
            "total_assets": 500000,
            "equity_ratio": 0.85,
            "risk_level": "稳健型",
            "single_product_max": 0.45,
            "margin_ratio": None,
        },
        {
            "name": "李四",
            "total_assets": 2000000,
            "equity_ratio": 0.60,
            "risk_level": "平衡型",
            "single_product_max": 0.25,
            "margin_ratio": 1.45,  # 维保比例 145%
        },
    ]
    
    results = checker.batch_check(customers)
    print(checker.generate_warning_list(results))
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class RiskResult:
    """风险筛查结果"""
    customer_name: str
    total_assets: float
    risk_score: int  # 风险评分 0-100
    risk_level: str  # 低/中/高/危急
    issues: List[str]
    priority: str  # P0/P1/P2/P3
    suggested_action: str


class RiskBatchChecker:
    """批量风险筛查工具"""
    
    # 风险权重配置
    RISK_WEIGHTS = {
        "risk_mismatch": 25,      # 风险不匹配
        "concentration": 20,      # 集中度过高
        "margin_warning": 30,     # 两融预警
        "liquidity": 15,          # 流动性不足
        "loss": 10,               # 大幅亏损
    }
    
    # 风险等级阈值
    RISK_SCORE_LEVELS = {
        "危急": 70,
        "高": 50,
        "中": 30,
        "低": 0,
    }
    
    # 优先级阈值
    PRIORITY_LEVELS = {
        "P0": 70,  # 立即处理
        "P1": 50,  # 3 日内
        "P2": 30,  # 1 周内
        "P3": 0,   # 常规监控
    }
    
    def __init__(self):
        pass
    
    def calculate_risk_score(self, customer: Dict) -> int:
        """
        计算客户风险评分（0-100）
        
        Args:
            customer: 客户信息字典
        
        Returns:
            风险评分
        """
        score = 0
        issues = []
        
        # 1. 风险不匹配检查
        equity_ratio = customer.get("equity_ratio", 0)
        risk_level = customer.get("risk_level", "稳健型")
        
        risk_limits = {
            "保守型": 0.20,
            "稳健型": 0.40,
            "平衡型": 0.60,
            "成长型": 0.80,
            "进取型": 1.00,
        }
        
        limit = risk_limits.get(risk_level, 0.60)
        if equity_ratio > limit:
            excess = (equity_ratio - limit) / limit * 100
            score += min(self.RISK_WEIGHTS["risk_mismatch"], int(25 + excess / 10))
            issues.append(f"风险不匹配：股票类占比{equity_ratio * 100:.0f}%，超出{risk_level}建议范围")
        
        # 2. 集中度检查
        single_max = customer.get("single_product_max", 0)
        if single_max > 0.50:
            score += self.RISK_WEIGHTS["concentration"]
            issues.append(f"集中度过高：单一产品占比{single_max * 100:.0f}%")
        elif single_max > 0.30:
            score += self.RISK_WEIGHTS["concentration"] // 2
            issues.append(f"集中度偏高：单一产品占比{single_max * 100:.0f}%")
        
        # 3. 两融预警检查
        margin_ratio = customer.get("margin_ratio")
        if margin_ratio:
            if margin_ratio < 1.30:
                score += self.RISK_WEIGHTS["margin_warning"]
                issues.append(f"两融平仓风险：维保比例{margin_ratio * 100:.0f}%")
            elif margin_ratio < 1.50:
                score += self.RISK_WEIGHTS["margin_warning"] // 2
                issues.append(f"两融预警：维保比例{margin_ratio * 100:.0f}%")
        
        # 4. 流动性检查
        liquid_ratio = customer.get("liquid_ratio", 0.10)
        if liquid_ratio < 0.05:
            score += self.RISK_WEIGHTS["liquidity"]
            issues.append(f"流动性不足：高流动性资产仅{liquid_ratio * 100:.1f}%")
        
        # 5. 大幅亏损检查
        total_pnl = customer.get("total_pnl", 0)
        if total_pnl < -0.30:
            score += self.RISK_WEIGHTS["loss"]
            issues.append(f"大幅亏损：浮亏{total_pnl * 100:.1f}%")
        elif total_pnl < -0.20:
            score += self.RISK_WEIGHTS["loss"] // 2
            issues.append(f"较大亏损：浮亏{total_pnl * 100:.1f}%")
        
        # 保存 issues 到 customer（供后续使用）
        customer["_issues"] = issues
        
        return min(100, score)
    
    def get_risk_level(self, score: int) -> str:
        """根据评分获取风险等级"""
        for level, threshold in self.RISK_SCORE_LEVELS.items():
            if score >= threshold:
                return level
        return "低"
    
    def get_priority(self, score: int) -> str:
        """根据评分获取优先级"""
        for priority, threshold in self.PRIORITY_LEVELS.items():
            if score >= threshold:
                return priority
        return "P3"
    
    def get_suggested_action(self, risk_level: str, issues: List[str]) -> str:
        """根据风险等级和问题生成建议行动"""
        if risk_level == "危急":
            return "立即电话联系，必要时上门拜访"
        elif risk_level == "高":
            return "3 日内电话沟通，发送风险提示函"
        elif risk_level == "中":
            return "1 周内微信/电话沟通"
        else:
            return "常规监控，定期回访"
    
    def batch_check(self, customers: List[Dict]) -> List[RiskResult]:
        """
        批量风险筛查
        
        Args:
            customers: 客户列表
        
        Returns:
            风险结果列表
        """
        results = []
        
        for customer in customers:
            score = self.calculate_risk_score(customer)
            risk_level = self.get_risk_level(score)
            priority = self.get_priority(score)
            issues = customer.get("_issues", [])
            
            result = RiskResult(
                customer_name=customer.get("name", "未知"),
                total_assets=customer.get("total_assets", 0),
                risk_score=score,
                risk_level=risk_level,
                issues=issues,
                priority=priority,
                suggested_action=self.get_suggested_action(risk_level, issues),
            )
            results.append(result)
        
        # 按风险评分降序排序
        results.sort(key=lambda x: x.risk_score, reverse=True)
        
        return results
    
    def generate_warning_list(self, results: List[RiskResult]) -> str:
        """
        生成风险提示清单
        
        Args:
            results: 风险筛查结果
        
        Returns:
            格式化清单文本
        """
        lines = []
        lines.append("=" * 80)
        lines.append("批量风险提示清单")
        lines.append(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append("=" * 80)
        lines.append("")
        
        # 按优先级分组
        priority_groups = {"P0": [], "P1": [], "P2": [], "P3": []}
        for r in results:
            priority_groups[r.priority].append(r)
        
        # P0 - 危急
        if priority_groups["P0"]:
            lines.append("🔴 P0 - 危急（需立即处理）")
            lines.append("-" * 60)
            for r in priority_groups["P0"]:
                lines.append(f"客户：{r.customer_name} | 资产：{r.total_assets:,.0f} 元 | 评分：{r.risk_score}")
                for issue in r.issues:
                    lines.append(f"  ⚠️ {issue}")
                lines.append(f"  📞 行动：{r.suggested_action}")
                lines.append("")
        
        # P1 - 高
        if priority_groups["P1"]:
            lines.append("🟠 P1 - 高（3 日内处理）")
            lines.append("-" * 60)
            for r in priority_groups["P1"]:
                lines.append(f"客户：{r.customer_name} | 资产：{r.total_assets:,.0f} 元 | 评分：{r.risk_score}")
                for issue in r.issues:
                    lines.append(f"  ⚠️ {issue}")
                lines.append(f"  📞 行动：{r.suggested_action}")
                lines.append("")
        
        # P2 - 中
        if priority_groups["P2"]:
            lines.append("🟡 P2 - 中（1 周内处理）")
            lines.append("-" * 60)
            for r in priority_groups["P2"]:
                lines.append(f"客户：{r.customer_name} | 资产：{r.total_assets:,.0f} 元")
                for issue in r.issues:
                    lines.append(f"  ⚠️ {issue}")
                lines.append("")
        
        # P3 - 低
        if priority_groups["P3"]:
            lines.append("🟢 P3 - 低（常规监控）")
            lines.append("-" * 60)
            for r in priority_groups["P3"]:
                lines.append(f"客户：{r.customer_name} | 资产：{r.total_assets:,.0f} 元")
            lines.append("")
        
        # 汇总统计
        lines.append("=" * 80)
        lines.append("汇总统计")
        lines.append(f"  总客户数：{len(results)}")
        lines.append(f"  P0 危急：{len(priority_groups['P0'])} 人")
        lines.append(f"  P1 高：{len(priority_groups['P1'])} 人")
        lines.append(f"  P2 中：{len(priority_groups['P2'])} 人")
        lines.append(f"  P3 低：{len(priority_groups['P3'])} 人")
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def generate_wechat_template(self, result: RiskResult) -> str:
        """
        生成微信风险提示模板
        
        Args:
            result: 单个客户风险结果
        
        Returns:
            微信消息模板
        """
        emoji = {"P0": "🔴", "P1": "🟠", "P2": "🟡", "P3": "🟢"}
        
        lines = []
        lines.append(f"{emoji.get(result.priority, '⚪')}【风险提示】")
        lines.append("")
        lines.append(f"{result.customer_name} 总，提示您关注：")
        lines.append("")
        
        for issue in result.issues[:3]:
            lines.append(f"⚠️ {issue}")
        
        lines.append("")
        lines.append(f"💡 建议：{result.suggested_action}")
        lines.append("")
        lines.append("详情可电话沟通：[联系方式]")
        
        return "\n".join(lines)
    
    def export_to_csv(self, results: List[RiskResult], filepath: str) -> None:
        """
        导出为 CSV 文件
        
        Args:
            results: 风险结果列表
            filepath: 输出文件路径
        """
        import csv
        
        with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow([
                "优先级", "客户姓名", "总资产", "风险评分", "风险等级",
                "问题列表", "建议行动",
            ])
            
            for r in results:
                writer.writerow([
                    r.priority,
                    r.customer_name,
                    r.total_assets,
                    r.risk_score,
                    r.risk_level,
                    "；".join(r.issues),
                    r.suggested_action,
                ])


# 快速测试
if __name__ == "__main__":
    checker = RiskBatchChecker()
    
    customers = [
        {
            "name": "张三",
            "total_assets": 500000,
            "equity_ratio": 0.85,
            "risk_level": "稳健型",
            "single_product_max": 0.45,
            "margin_ratio": None,
            "liquid_ratio": 0.08,
            "total_pnl": -0.15,
        },
        {
            "name": "李四",
            "total_assets": 2000000,
            "equity_ratio": 0.60,
            "risk_level": "平衡型",
            "single_product_max": 0.25,
            "margin_ratio": 1.45,
            "liquid_ratio": 0.15,
            "total_pnl": 0.05,
        },
        {
            "name": "王五",
            "total_assets": 300000,
            "equity_ratio": 0.95,
            "risk_level": "保守型",
            "single_product_max": 0.60,
            "margin_ratio": 1.25,
            "liquid_ratio": 0.02,
            "total_pnl": -0.35,
        },
        {
            "name": "赵六",
            "total_assets": 1000000,
            "equity_ratio": 0.50,
            "risk_level": "平衡型",
            "single_product_max": 0.20,
            "margin_ratio": None,
            "liquid_ratio": 0.12,
            "total_pnl": 0.08,
        },
    ]
    
    results = checker.batch_check(customers)
    print(checker.generate_warning_list(results))
