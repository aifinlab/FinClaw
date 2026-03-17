#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
两融保证金计算器

功能：
1. 计算维保比例
2. 压力测试（市场下跌对维保比例的影响）
3. 追保金额计算
4. 可用保证金计算

使用示例：
    from margin_calculator import MarginCalculator
    
    calc = MarginCalculator(
        total_assets=2000000,  # 总资产 200 万
        total_liabilities=800000,  # 总负债 80 万
        positions=[  # 持仓明细
            {"name": "贵州茅台", "market_value": 1000000, "discount_rate": 0.70},
            {"name": "中国平安", "market_value": 500000, "discount_rate": 0.70},
            {"name": "国债", "market_value": 500000, "discount_rate": 0.95},
        ]
    )
    
    print(f"维保比例：{calc.get_maintenance_ratio():.2f}%")
    print(calc.stress_test())
    print(calc.calculate_margin_call(target_ratio=1.50))
"""

from typing import List, Dict
from dataclasses import dataclass


@dataclass
class Position:
    """持仓信息"""
    name: str
    market_value: float
    discount_rate: float
    is_st: bool = False


class MarginCalculator:
    """两融保证金计算器"""
    
    # 标准折算率
    STANDARD_DISCOUNT_RATES = {
        "国债": 0.95,
        "金融债": 0.85,
        "AAA 信用债": 0.85,
        "沪深 300 成分股": 0.70,
        "其他 A 股": 0.65,
        "基金": 0.85,
        "ST 股": 0.00,
    }
    
    # 预警线和平仓线
    WARNING_RATIO = 1.50  # 150%
    LIQUIDATION_RATIO = 1.30  # 130%
    
    def __init__(
        self,
        total_assets: float,
        total_liabilities: float,
        positions: List[Dict] = None,
        financing_amount: float = 0,
        securities_selling_amount: float = 0,
    ):
        """
        初始化计算器
        
        Args:
            total_assets: 总资产（市值 + 现金）
            total_liabilities: 总负债（融资 + 融券）
            positions: 持仓明细列表
            financing_amount: 融资负债金额
            securities_selling_amount: 融券负债金额
        """
        self.total_assets = total_assets
        self.total_liabilities = total_liabilities
        self.positions = positions or []
        self.financing_amount = financing_amount
        self.securities_selling_amount = securities_selling_amount
    
    def get_maintenance_ratio(self) -> float:
        """
        计算维保比例
        
        Returns:
            维保比例（小数形式，如 1.85 表示 185%）
        """
        if self.total_liabilities == 0:
            return float('inf')
        return self.total_assets / self.total_liabilities
    
    def get_maintenance_ratio_percent(self) -> str:
        """获取维保比例百分比字符串"""
        ratio = self.get_maintenance_ratio()
        if ratio == float('inf'):
            return "无负债"
        return f"{ratio * 100:.2f}%"
    
    def get_status(self) -> str:
        """
        获取当前状态
        
        Returns:
            状态描述
        """
        ratio = self.get_maintenance_ratio()
        if ratio == float('inf'):
            return "安全（无负债）"
        elif ratio > 3.0:
            return "安全"
        elif ratio > 2.0:
            return "较安全"
        elif ratio > self.WARNING_RATIO:
            return "预警"
        elif ratio > self.LIQUIDATION_RATIO:
            return "高危"
        else:
            return "平仓风险"
    
    def calculate_available_margin(self) -> float:
        """
        计算可用保证金
        
        Returns:
            可用保证金金额
        """
        if not self.positions:
            return 0
        
        total_discount_value = sum(
            pos["market_value"] * pos.get("discount_rate", 0.65)
            for pos in self.positions
        )
        
        # 可用保证金 = ∑(证券市值×折算率) - 融券市值
        available = total_discount_value - self.securities_selling_amount
        return max(0, available)
    
    def stress_test(
        self,
        decline_scenarios: List[float] = None,
    ) -> List[Dict]:
        """
        压力测试：计算市场下跌对维保比例的影响
        
        Args:
            decline_scenarios: 下跌幅度列表，如 [0.05, 0.10, 0.15, 0.20]
        
        Returns:
            压力测试结果列表
        """
        if decline_scenarios is None:
            decline_scenarios = [0.05, 0.10, 0.15, 0.20, 0.30]
        
        results = []
        for decline in decline_scenarios:
            # 假设资产全部是股票，下跌幅度直接影响总资产
            new_assets = self.total_assets * (1 - decline)
            # 负债不变
            new_liabilities = self.total_liabilities
            # 计算新维保比例
            new_ratio = new_assets / new_liabilities if new_liabilities > 0 else float('inf')
            
            # 判断状态
            if new_ratio == float('inf'):
                status = "无负债"
            elif new_ratio > 3.0:
                status = "安全"
            elif new_ratio > 2.0:
                status = "较安全"
            elif new_ratio > self.WARNING_RATIO:
                status = "预警"
            elif new_ratio > self.LIQUIDATION_RATIO:
                status = "高危"
            else:
                status = "平仓风险"
            
            results.append({
                "decline": f"-{decline * 100:.0f}%",
                "new_assets": round(new_assets, 2),
                "new_liabilities": round(new_liabilities, 2),
                "maintenance_ratio": f"{new_ratio * 100:.2f}%" if new_ratio != float('inf') else "无负债",
                "status": status,
            })
        
        return results
    
    def calculate_margin_call(self, target_ratio: float = None) -> Dict:
        """
        计算追保金额
        
        Args:
            target_ratio: 目标维保比例，默认 1.60（160%）
        
        Returns:
            追保方案字典
        """
        if target_ratio is None:
            target_ratio = 1.60
        
        current_ratio = self.get_maintenance_ratio()
        
        # 如果已经达到目标，不需要追保
        if current_ratio >= target_ratio:
            return {
                "need_margin_call": False,
                "current_ratio": f"{current_ratio * 100:.2f}%",
                "target_ratio": f"{target_ratio * 100:.2f}%",
                "cash_to_add": 0,
                "assets_to_sell": 0,
                "message": "当前维保比例已达到目标，无需追保",
            }
        
        # 方案 1：追加现金
        # (总资产 + X) / 总负债 = 目标比例
        # X = 目标比例 × 总负债 - 总资产
        cash_to_add = target_ratio * self.total_liabilities - self.total_assets
        
        # 方案 2：卖出资产还券/还款
        # (总资产 - X) / (总负债 - X) = 目标比例
        # X = (目标比例 × 总负债 - 总资产) / (目标比例 - 1)
        if target_ratio != 1:
            assets_to_sell = (target_ratio * self.total_liabilities - self.total_assets) / (target_ratio - 1)
        else:
            assets_to_sell = cash_to_add
        
        # 方案 3：组合方案（各承担 50%）
        cash_half = cash_to_add / 2
        assets_half = assets_to_sell / 2
        
        return {
            "need_margin_call": True,
            "current_ratio": f"{current_ratio * 100:.2f}%",
            "target_ratio": f"{target_ratio * 100:.2f}%",
            "warning_ratio": f"{self.WARNING_RATIO * 100:.0f}%",
            "liquidation_ratio": f"{self.LIQUIDATION_RATIO * 100:.0f}%",
            "solutions": {
                "cash_only": {
                    "type": "追加现金",
                    "amount": round(max(0, cash_to_add), 2),
                    "description": f"追加 {round(max(0, cash_to_add), 2)} 元现金",
                },
                "sell_only": {
                    "type": "卖出资产",
                    "amount": round(max(0, assets_to_sell), 2),
                    "description": f"卖出 {round(max(0, assets_to_sell), 2)} 元资产并还款",
                },
                "combination": {
                    "type": "组合方案",
                    "cash": round(max(0, cash_half), 2),
                    "assets": round(max(0, assets_half), 2),
                    "description": f"追加 {round(max(0, cash_half), 2)} 元现金 + 卖出 {round(max(0, assets_half), 2)} 元资产",
                },
            },
        }
    
    def calculate_max_financing(self) -> Dict:
        """
        计算最大可融资额度
        
        Returns:
            最大融资额度信息
        """
        if not self.positions:
            return {"max_additional": 0, "message": "无持仓，无法计算"}
        
        # 计算总折算价值
        total_discount_value = sum(
            pos["market_value"] * pos.get("discount_rate", 0.65)
            for pos in self.positions
        )
        
        # 最大负债 = 总折算价值 / 维保比例要求（按 150% 计算）
        max_liabilities = total_discount_value / self.WARNING_RATIO
        
        # 还可增加负债 = 最大负债 - 当前负债
        max_additional = max(0, max_liabilities - self.total_liabilities)
        
        return {
            "total_discount_value": round(total_discount_value, 2),
            "max_liabilities": round(max_liabilities, 2),
            "current_liabilities": round(self.total_liabilities, 2),
            "max_additional": round(max_additional, 2),
            "message": f"基于当前持仓，最多还可融资 {round(max_additional, 2)} 元",
        }
    
    def get_concentration_analysis(self) -> Dict:
        """
        分析持仓集中度
        
        Returns:
            集中度分析结果
        """
        if not self.positions:
            return {"message": "无持仓数据"}
        
        total_value = sum(pos["market_value"] for pos in self.positions)
        if total_value == 0:
            return {"message": "持仓总市值为 0"}
        
        # 计算单一证券占比
        concentrations = []
        for pos in self.positions:
            ratio = pos["market_value"] / total_value
            concentrations.append({
                "name": pos["name"],
                "market_value": pos["market_value"],
                "ratio": f"{ratio * 100:.2f}%",
                "warning": ratio > 0.70,  # 超过 70% 预警
            })
        
        # 排序
        concentrations.sort(key=lambda x: x["market_value"], reverse=True)
        
        # 前三大占比
        top3_ratio = sum(
            pos["market_value"] / total_value
            for pos in concentrations[:3]
        )
        
        return {
            "total_value": total_value,
            "positions_count": len(self.positions),
            "top_concentration": concentrations[0] if concentrations else None,
            "top3_ratio": f"{top3_ratio * 100:.2f}%",
            "details": concentrations,
            "warnings": [
                f"{pos['name']} 占比 {pos['ratio']}，超过 70% 预警线"
                for pos in concentrations if pos["warning"]
            ],
        }
    
    def generate_report(self) -> str:
        """
        生成完整诊断报告
        
        Returns:
            格式化的报告文本
        """
        lines = []
        lines.append("=" * 60)
        lines.append("两融持仓诊断报告")
        lines.append("=" * 60)
        lines.append("")
        
        # 账户概览
        lines.append("【账户概览】")
        lines.append(f"总资产：{self.total_assets:,.2f} 元")
        lines.append(f"总负债：{self.total_liabilities:,.2f} 元")
        lines.append(f"融资负债：{self.financing_amount:,.2f} 元")
        lines.append(f"融券负债：{self.securities_selling_amount:,.2f} 元")
        lines.append(f"可用保证金：{self.calculate_available_margin():,.2f} 元")
        lines.append("")
        
        # 维保比例
        lines.append("【维保比例】")
        lines.append(f"当前比例：{self.get_maintenance_ratio_percent()}")
        lines.append(f"状态：{self.get_status()}")
        lines.append(f"预警线：{self.WARNING_RATIO * 100:.0f}%")
        lines.append(f"平仓线：{self.LIQUIDATION_RATIO * 100:.0f}%")
        lines.append("")
        
        # 压力测试
        lines.append("【压力测试】")
        for result in self.stress_test():
            lines.append(
                f"市场下跌 {result['decline']:>6}: "
                f"维保比例 {result['maintenance_ratio']:>8}, "
                f"状态：{result['status']}"
            )
        lines.append("")
        
        # 追保方案
        if self.get_maintenance_ratio() < self.WARNING_RATIO:
            lines.append("【追保方案】")
            margin_call = self.calculate_margin_call()
            for key, value in margin_call["solutions"].items():
                lines.append(f"  {value['description']}")
            lines.append("")
        
        # 集中度分析
        lines.append("【集中度分析】")
        concentration = self.get_concentration_analysis()
        if concentration.get("top_concentration"):
            lines.append(
                f"最大持仓：{concentration['top_concentration']['name']} "
                f"({concentration['top_concentration']['ratio']})"
            )
            lines.append(f"前三大占比：{concentration['top3_ratio']}")
            if concentration.get("warnings"):
                lines.append("⚠️ 预警:")
                for warning in concentration["warnings"]:
                    lines.append(f"  - {warning}")
        
        lines.append("")
        lines.append("=" * 60)
        
        return "\n".join(lines)


# 快速测试
if __name__ == "__main__":
    # 示例：维保比例 155% 的客户
    calc = MarginCalculator(
        total_assets=1550000,
        total_liabilities=1000000,
        financing_amount=1000000,
        positions=[
            {"name": "贵州茅台", "market_value": 800000, "discount_rate": 0.70},
            {"name": "宁德时代", "market_value": 500000, "discount_rate": 0.65},
            {"name": "现金", "market_value": 250000, "discount_rate": 1.0},
        ],
    )
    
    print(calc.generate_report())
