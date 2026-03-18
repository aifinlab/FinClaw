#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
沉默客户唤醒分析器

功能：
1. 沉默客户识别
2. 沉默原因分析
3. 唤醒成功率统计
4. 唤醒策略推荐

使用示例：
    from awakening_analyzer import AwakeningAnalyzer
    
    analyzer = AwakeningAnalyzer()
    
    customers = [
        {"name": "张三", "last_interaction": "2023-10-01", "assets": 500000, "status": "持仓中"},
        {"name": "李四", "last_interaction": "2023-06-01", "assets": 200000, "status": "已清仓"},
        # ... 更多客户
    ]
    
    silent_customers = analyzer.identify_silent_customers(customers)
    print(analyzer.generate_awakening_plan(silent_customers))
"""

from typing import List, Dict
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class SilentCustomer:
    """沉默客户"""
    name: str
    last_interaction: str
    silent_days: int
    silent_level: str  # 轻度/中度/重度/流失
    assets: float
    status: str
    awakening_strategy: str
    priority: str


class AwakeningAnalyzer:
    """沉默客户唤醒分析器"""
    
    # 沉默程度定义
    SILENT_LEVELS = {
        "轻度": {"min_days": 30, "max_days": 90, "priority": "P2"},
        "中度": {"min_days": 91, "max_days": 180, "priority": "P1"},
        "重度": {"min_days": 181, "max_days": 365, "priority": "P0"},
        "流失": {"min_days": 366, "max_days": float('inf'), "priority": "P1"},
    }
    
    # 唤醒策略
    AWAKENING_STRATEGIES = {
        "轻度": "微信关怀 + 市场解读",
        "中度": "电话 + 微信，真诚道歉",
        "重度": "专人跟进，了解原因",
        "流失": "挽回话术，接受结果",
    }
    
    # 沉默原因
    SILENT_REASONS = [
        "服务不到位",
        "业绩不佳",
        "需求变化",
        "竞争流失",
        "个人原因",
    ]
    
    def __init__(self):
        pass
    
    def calculate_silent_days(self, last_interaction: str) -> int:
        """计算沉默天数"""
        try:
            last_date = datetime.strptime(last_interaction, "%Y-%m-%d")
            return (datetime.now() - last_date).days
        except:
            return 999
    
    def determine_silent_level(self, silent_days: int) -> str:
        """确定沉默程度"""
        for level, range_info in self.SILENT_LEVELS.items():
            if range_info["min_days"] <= silent_days <= range_info["max_days"]:
                return level
        return "流失"
    
    def identify_silent_customers(self, customers: List[Dict], min_silent_days: int = 30) -> List[Dict]:
        """
        识别沉默客户
        
        Args:
            customers: 客户列表
            min_silent_days: 最小沉默天数
        
        Returns:
            沉默客户列表
        """
        silent_customers = []
        
        for customer in customers:
            silent_days = self.calculate_silent_days(customer.get("last_interaction", ""))
            
            if silent_days >= min_silent_days:
                silent_level = self.determine_silent_level(silent_days)
                
                result = {
                    **customer,
                    "silent_days": silent_days,
                    "silent_level": silent_level,
                    "priority": self.SILENT_LEVELS[silent_level]["priority"],
                    "awakening_strategy": self.AWAKENING_STRATEGIES[silent_level],
                }
                silent_customers.append(result)
        
        # 按优先级和资产排序
        priority_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
        silent_customers.sort(key=lambda x: (priority_order.get(x["priority"], 3), -x.get("assets", 0)))
        
        return silent_customers
    
    def analyze_silent_reasons(self, customers: List[Dict]) -> Dict:
        """
        分析沉默原因
        
        Args:
            customers: 沉默客户列表
        
        Returns:
            原因分析结果
        """
        reason_counts = {reason: 0 for reason in self.SILENT_REASONS}
        
        for customer in customers:
            # 简化：根据状态推测原因
            status = customer.get("status", "")
            assets = customer.get("assets", 0)
            silent_level = customer.get("silent_level", "")
            
            if status == "已清仓":
                reason_counts["业绩不佳"] += 1
            elif assets == 0:
                reason_counts["竞争流失"] += 1
            elif silent_level == "流失":
                reason_counts["需求变化"] += 1
            else:
                reason_counts["服务不到位"] += 1
        
        total = len(customers) if customers else 1
        
        return {
            "reasons": [
                {"reason": reason, "count": count, "pct": count / total * 100}
                for reason, count in sorted(reason_counts.items(), key=lambda x: x[1], reverse=True)
            ],
            "top_reason": max(reason_counts, key=reason_counts.get) if reason_counts else "未知",
        }
    
    def generate_awakening_plan(self, customers: List[Dict]) -> str:
        """
        生成唤醒计划
        
        Args:
            customers: 沉默客户列表
        
        Returns:
            格式化计划文本
        """
        lines = []
        lines.append("=" * 80)
        lines.append("沉默客户唤醒计划")
        lines.append(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append("=" * 80)
        lines.append("")
        
        # 汇总统计
        total = len(customers)
        level_counts = {}
        priority_counts = {}
        total_assets = 0
        
        for customer in customers:
            level = customer.get("silent_level", "未知")
            priority = customer.get("priority", "P3")
            
            level_counts[level] = level_counts.get(level, 0) + 1
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
            total_assets += customer.get("assets", 0)
        
        lines.append("【汇总统计】")
        lines.append(f"  沉默客户总数：{total}")
        lines.append(f"  涉及资产：{total_assets / 10000:.0f} 万")
        lines.append("")
        
        lines.append("  按沉默程度:")
        for level in ["轻度", "中度", "重度", "流失"]:
            count = level_counts.get(level, 0)
            lines.append(f"    {level}: {count} 人")
        lines.append("")
        
        lines.append("  按优先级:")
        for priority in ["P0", "P1", "P2", "P3"]:
            count = priority_counts.get(priority, 0)
            lines.append(f"    {priority}: {count} 人")
        lines.append("")
        
        # 唤醒策略
        lines.append("【唤醒策略】")
        for level, strategy in self.AWAKENING_STRATEGIES.items():
            count = level_counts.get(level, 0)
            if count > 0:
                lines.append(f"  {level} ({count}人): {strategy}")
        lines.append("")
        
        # 重点客户清单
        lines.append("【重点唤醒客户清单】")
        lines.append("")
        lines.append(f"{'优先级':<6} {'客户':<10} {'沉默天数':<10} {'沉默程度':<8} {'资产 (万)':<10} {'唤醒策略':<25}")
        lines.append("-" * 80)
        
        for customer in customers[:20]:  # 显示前 20 个
            lines.append(
                f"{customer['priority']:<6} {customer['name']:<10} "
                f"{customer['silent_days']:<10} {customer['silent_level']:<8} "
                f"{customer.get('assets', 0) / 10000:<10.0f} {customer['awakening_strategy']:<25}"
            )
        
        lines.append("")
        
        # 执行计划
        lines.append("【执行计划】")
        lines.append("  第 1 周：完成 P0 级客户触达")
        lines.append("  第 2 周：完成 P1 级客户触达")
        lines.append("  第 3-4 周：完成 P2 级客户触达")
        lines.append("  持续：P3 级客户定期维护")
        lines.append("")
        
        # 目标
        lines.append("【唤醒目标】")
        lines.append("  唤醒率：20-30%")
        lines.append("  转化率：10-15%")
        lines.append(f"  目标唤醒客户数：{int(total * 0.25)} 人")
        lines.append(f"  目标转化资产：{total_assets / 10000 * 0.1:.0f} 万")
        lines.append("")
        
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def generate_awakening_script(self, silent_level: str) -> str:
        """
        生成唤醒话术
        
        Args:
            silent_level: 沉默程度
        
        Returns:
            唤醒话术
        """
        scripts = {
            "轻度": """
【轻度沉默唤醒话术】

"XX 总，好久没联系了，最近还好吗？
整理客户资料时看到您，想着给您发个消息。
最近市场有些变化，您这边投资还顺利吗？
有任何需要帮忙的随时联系我。"
""",
            "中度": """
【中度沉默唤醒话术】

"XX 总，好久没联系了。
反思了一下，之前确实跟您联系太少了，不好意思。
不知道您这边最近怎么样？投资还顺利吗？
有什么需要我帮忙的，随时联系我。"
""",
            "重度": """
【重度沉默唤醒话术】

"XX 总，我是 XX，好久没联系了。
今天给您打电话，主要是想问候一下，顺便听听您对我们这边有什么建议。
不管您还在不在我们这边做，都感谢您一直以来的支持。"
""",
            "流失": """
【流失客户挽回话术】

"XX 总，我是 XX。知道您现在已经不在我们这边做了。
今天联系您，主要是想听听您的建议，我们这边有哪些做得不好的地方。
您的反馈对我们很重要，不管您回不回来，都感谢。"
""",
        }
        
        return scripts.get(silent_level, "暂无话术")


# 快速测试
if __name__ == "__main__":
    analyzer = AwakeningAnalyzer()
    
    # 模拟数据
    customers = [
        {"name": "张三", "last_interaction": "2024-01-01", "assets": 500000, "status": "持仓中"},
        {"name": "李四", "last_interaction": "2023-10-01", "assets": 200000, "status": "已清仓"},
        {"name": "王五", "last_interaction": "2023-06-01", "assets": 1000000, "status": "持仓中"},
        {"name": "赵六", "last_interaction": "2023-01-01", "assets": 50000, "status": "已清仓"},
        {"name": "钱七", "last_interaction": "2024-02-01", "assets": 300000, "status": "持仓中"},
    ]
    
    silent_customers = analyzer.identify_silent_customers(customers)
    print(analyzer.generate_awakening_plan(silent_customers))
    print("\n")
    print("示例话术:")
    print(analyzer.generate_awakening_script("中度"))
