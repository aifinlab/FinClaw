#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
客户分层分析器

功能：
1. 客户分层评定
2. 层级分布统计
3. 升级路径规划
4. 差异化服务清单生成

使用示例：
    from segmentation_analyzer import SegmentationAnalyzer
    
    analyzer = SegmentationAnalyzer()
    
    customers = [
        {"name": "张三", "assets": 15000000, "annual_contribution": 800000, "activity": "活跃"},
        {"name": "李四", "assets": 3000000, "annual_contribution": 150000, "activity": "普通"},
        # ... 更多客户
    ]
    
    results = analyzer.segment_customers(customers)
    print(analyzer.generate_distribution_report(results))
"""

from typing import List, Dict
from dataclasses import dataclass
from datetime import datetime


@dataclass
class CustomerSegment:
    """客户分层结果"""
    name: str
    assets: float
    annual_contribution: float
    activity: str
    segment: str  # A/B/C/D
    segment_name: str
    upgrade_path: str
    gap_to_next: float


class SegmentationAnalyzer:
    """客户分层分析器"""
    
    # 分层标准
    SEGMENTATION_CRITERIA = {
        "A": {  # 核心客户
            "min_assets": 10000000,  # 1000 万
            "min_contribution": 500000,  # 50 万
            "segment_name": "核心客户",
        },
        "B": {  # 重要客户
            "min_assets": 5000000,  # 500 万
            "min_contribution": 200000,  # 20 万
            "segment_name": "重要客户",
        },
        "C": {  # 潜力客户
            "min_assets": 1000000,  # 100 万
            "min_contribution": 50000,  # 5 万
            "segment_name": "潜力客户",
        },
        "D": {  # 基础客户
            "min_assets": 0,
            "min_contribution": 0,
            "segment_name": "基础客户",
        },
    }
    
    # 各层级服务标准
    SERVICE_STANDARDS = {
        "A": {
            "service_staff": "专属投顾 + 专家团队",
            "contact_frequency": "每周 1 次",
            "service_mode": "面谈为主，7×24 小时响应",
            "services": ["专属资产配置方案", "优先产品额度", "专属活动邀请", "非金融服务"],
        },
        "B": {
            "service_staff": "专属投顾",
            "contact_frequency": "每 2 周 1 次",
            "service_mode": "面谈 + 电话",
            "services": ["定期资产配置检视", "产品优先推荐", "活动优先参与"],
        },
        "C": {
            "service_staff": "投顾",
            "contact_frequency": "每月 1-2 次",
            "service_mode": "电话 + 微信",
            "services": ["标准化配置建议", "产品推荐", "定期市场解读"],
        },
        "D": {
            "service_staff": "投顾/智能服务",
            "contact_frequency": "每月 1 次",
            "service_mode": "微信 + 智能服务",
            "services": ["标准化服务", "市场资讯推送", "活动群发"],
        },
    }
    
    def __init__(self):
        pass
    
    def determine_segment(self, customer: Dict) -> str:
        """
        确定客户层级
        
        Args:
            customer: 客户信息
        
        Returns:
            层级（A/B/C/D）
        """
        assets = customer.get("assets", 0)
        contribution = customer.get("annual_contribution", 0)
        
        # 从高到低判断
        for segment in ["A", "B", "C", "D"]:
            criteria = self.SEGMENTATION_CRITERIA[segment]
            if assets >= criteria["min_assets"] and contribution >= criteria["min_contribution"]:
                return segment
        
        return "D"
    
    def calculate_upgrade_path(self, customer: Dict, current_segment: str) -> Dict:
        """
        计算升级路径
        
        Args:
            customer: 客户信息
            current_segment: 当前层级
        
        Returns:
            升级路径信息
        """
        segments = ["D", "C", "B", "A"]
        current_index = segments.index(current_segment)
        
        # 已经是最高级
        if current_index == 0:
            return {
                "next_segment": None,
                "segment_name": "已达最高级",
                "asset_gap": 0,
                "contribution_gap": 0,
                "upgrade_path": "保持当前层级，深化服务",
            }
        
        # 下一级目标
        next_segment = segments[current_index - 1]
        criteria = self.SEGMENTATION_CRITERIA[next_segment]
        
        asset_gap = criteria["min_assets"] - customer.get("assets", 0)
        contribution_gap = criteria["min_contribution"] - customer.get("annual_contribution", 0)
        
        return {
            "next_segment": next_segment,
            "segment_name": self.SEGMENTATION_CRITERIA[next_segment]["segment_name"],
            "asset_gap": max(0, asset_gap),
            "contribution_gap": max(0, contribution_gap),
            "upgrade_path": f"资产提升至{criteria['min_assets'] / 10000:.0f}万，年贡献提升至{criteria['min_contribution'] / 10000:.0f}万",
        }
    
    def segment_customers(self, customers: List[Dict]) -> List[Dict]:
        """
        批量分层客户
        
        Args:
            customers: 客户列表
        
        Returns:
            分层结果列表
        """
        results = []
        
        for customer in customers:
            segment = self.determine_segment(customer)
            upgrade_info = self.calculate_upgrade_path(customer, segment)
            
            result = {
                **customer,
                "segment": segment,
                "segment_name": self.SEGMENTATION_CRITERIA[segment]["segment_name"],
                "next_segment": upgrade_info["next_segment"],
                "next_segment_name": upgrade_info["segment_name"],
                "asset_gap": upgrade_info["asset_gap"],
                "contribution_gap": upgrade_info["contribution_gap"],
                "upgrade_path": upgrade_info["upgrade_path"],
            }
            results.append(result)
        
        return results
    
    def generate_distribution_report(self, customers: List[Dict]) -> str:
        """
        生成分层分布报告
        
        Args:
            customers: 分层后的客户列表
        
        Returns:
            格式化报告文本
        """
        lines = []
        lines.append("=" * 80)
        lines.append("客户分层分布报告")
        lines.append(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append("=" * 80)
        lines.append("")
        
        # 按层级统计
        segment_counts = {"A": 0, "B": 0, "C": 0, "D": 0}
        segment_assets = {"A": 0, "B": 0, "C": 0, "D": 0}
        segment_contributions = {"A": 0, "B": 0, "C": 0, "D": 0}
        
        for customer in customers:
            segment = customer.get("segment", "D")
            segment_counts[segment] += 1
            segment_assets[segment] += customer.get("assets", 0)
            segment_contributions[segment] += customer.get("annual_contribution", 0)
        
        total_customers = len(customers)
        total_assets = sum(segment_assets.values())
        total_contributions = sum(segment_contributions.values())
        
        # 分布表格
        lines.append("【分层分布】")
        lines.append("")
        lines.append(f"{'层级':<8} {'名称':<10} {'人数':<8} {'占比':<8} {'资产 (万)':<12} {'占比':<8} {'贡献 (万)':<12} {'占比':<8}")
        lines.append("-" * 80)
        
        for segment in ["A", "B", "C", "D"]:
            count = segment_counts[segment]
            assets = segment_assets[segment] / 10000
            contributions = segment_contributions[segment] / 10000
            
            count_pct = count / total_customers * 100 if total_customers > 0 else 0
            assets_pct = assets / (total_assets / 10000) * 100 if total_assets > 0 else 0
            contributions_pct = contributions / (total_contributions / 10000) * 100 if total_contributions > 0 else 0
            
            name = self.SEGMENTATION_CRITERIA[segment]["segment_name"]
            
            lines.append(
                f"{segment:<8} {name:<10} {count:<8} {count_pct:<7.1f}% "
                f"{assets:<12.0f} {assets_pct:<7.1f}% {contributions:<12.0f} {contributions_pct:<7.1f}%"
            )
        
        lines.append("")
        lines.append(f"总计：{total_customers} 人，资产 {total_assets / 10000:.0f} 万，年贡献 {total_contributions / 10000:.0f} 万")
        lines.append("")
        
        # 各层级服务标准
        lines.append("【各层级服务标准】")
        lines.append("")
        
        for segment in ["A", "B", "C", "D"]:
            standard = self.SERVICE_STANDARDS[segment]
            lines.append(f"{segment} 级 - {self.SEGMENTATION_CRITERIA[segment]['segment_name']}:")
            lines.append(f"  服务人员：{standard['service_staff']}")
            lines.append(f"  触达频率：{standard['contact_frequency']}")
            lines.append(f"  服务方式：{standard['service_mode']}")
            lines.append(f"  服务内容：{', '.join(standard['services'])}")
            lines.append("")
        
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def generate_upgrade_plan(self, customers: List[Dict], target_segment: str = None) -> str:
        """
        生成升级计划
        
        Args:
            customers: 分层后的客户列表
            target_segment: 目标层级（可选）
        
        Returns:
            格式化升级计划文本
        """
        lines = []
        lines.append("=" * 80)
        lines.append("客户层级升级计划")
        lines.append("=" * 80)
        lines.append("")
        
        # 筛选有升级空间的客户
        upgrade_candidates = []
        for customer in customers:
            if customer.get("next_segment"):
                if target_segment is None or customer.get("next_segment") == target_segment:
                    upgrade_candidates.append(customer)
        
        if not upgrade_candidates:
            lines.append("暂无符合升级条件的客户")
            lines.append("=" * 80)
            return "\n".join(lines)
        
        # 按资产差距排序
        upgrade_candidates.sort(key=lambda x: x.get("asset_gap", 0))
        
        lines.append(f"可升级客户数：{len(upgrade_candidates)}")
        lines.append("")
        
        lines.append(f"{'客户':<10} {'当前层级':<8} {'目标层级':<8} {'资产差距 (万)':<12} {'贡献差距 (万)':<12} {'升级路径':<30}")
        lines.append("-" * 80)
        
        for customer in upgrade_candidates[:20]:  # 显示前 20 个
            lines.append(
                f"{customer['name']:<10} {customer['segment_name']:<8} "
                f"{customer.get('next_segment_name', 'N/A'):<8} "
                f"{customer.get('asset_gap', 0) / 10000:<12.0f} "
                f"{customer.get('contribution_gap', 0) / 10000:<12.0f} "
                f"{customer.get('upgrade_path', 'N/A'):<30}"
            )
        
        lines.append("")
        lines.append("=" * 80)
        
        return "\n".join(lines)


# 快速测试
if __name__ == "__main__":
    analyzer = SegmentationAnalyzer()
    
    customers = [
        {"name": "张三", "assets": 15000000, "annual_contribution": 800000, "activity": "活跃"},
        {"name": "李四", "assets": 8000000, "annual_contribution": 400000, "activity": "活跃"},
        {"name": "王五", "assets": 3000000, "annual_contribution": 150000, "activity": "普通"},
        {"name": "赵六", "assets": 500000, "annual_contribution": 30000, "activity": "普通"},
        {"name": "钱七", "assets": 800000, "annual_contribution": 80000, "activity": "活跃"},
    ]
    
    results = analyzer.segment_customers(customers)
    print(analyzer.generate_distribution_report(results))
    print("\n")
    print(analyzer.generate_upgrade_plan(results))
