#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
可转债估值计算器

功能：
1. 转股价值/溢价率计算
2. 纯债价值/溢价率计算
3. 双低策略筛选
4. 强赎条件判断
5. 下修分析

使用示例：
    from convertible_bond_valuation import CBValuation
    
    cb = CBValuation(
        cb_price=115.0,        # 可转债价格
        par_value=100,         # 面值
        conversion_price=10.5, # 转股价
        stock_price=11.2,      # 正股价
        bond_yield=0.03,       # 债券到期收益率
        years_to_maturity=3,   # 剩余年限
    )
    
    print(cb.calculate_conversion_value())
    print(cb.calculate_pure_bond_value())
    print(cb.get_valuation_summary())
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class ConvertibleBond:
    """可转债基本信息"""
    name: str
    code: str
    cb_price: float       # 可转债价格
    par_value: float      # 面值（通常 100）
    conversion_price: float  # 转股价
    stock_price: float    # 正股价
    stock_name: str       # 正股名称
    years_to_maturity: float  # 剩余年限
    coupon_rate: float    = 0.01  # 票面利率
    credit_rating: str    = "AA"  # 信用评级


class CBValuation:
    """可转债估值计算器"""
    
    # 强赎条件（典型）
    REDEMPTION_CONDITION = {
        "days": 30,           # 30 个交易日中
        "threshold_days": 15,  # 至少 15 天
        "price_ratio": 1.30,   # 股价≥转股价×130%
    }
    
    # 下修条件（典型）
    DOWNWARD_REVISION_CONDITION = {
        "days": 30,
        "threshold_days": 15,
        "price_ratio": 0.85,   # 股价≤转股价×85%
    }
    
    def __init__(
        self,
        cb_price: float,
        par_value: float,
        conversion_price: float,
        stock_price: float,
        years_to_maturity: float,
        coupon_rate: float = 0.01,
        credit_rating: str = "AA",
        name: str = None,
        code: str = None,
        stock_name: str = None,
    ):
        """
        初始化估值器
        
        Args:
            cb_price: 可转债价格
            par_value: 面值
            conversion_price: 转股价
            stock_price: 正股价
            years_to_maturity: 剩余年限
            coupon_rate: 票面利率
            credit_rating: 信用评级
        """
        self.cb_price = cb_price
        self.par_value = par_value
        self.conversion_price = conversion_price
        self.stock_price = stock_price
        self.years_to_maturity = years_to_maturity
        self.coupon_rate = coupon_rate
        self.credit_rating = credit_rating
        self.name = name
        self.code = code
        self.stock_name = stock_name
    
    def calculate_conversion_value(self) -> Dict:
        """
        计算转股价值
        
        Returns:
            转股价值相关指标
        """
        # 转股价值 = 100 / 转股价 × 正股价
        conversion_value = self.par_value / self.conversion_price * self.stock_price
        
        # 转股溢价率 = (转债价格 - 转股价值) / 转股价值
        conversion_premium = (self.cb_price - conversion_value) / conversion_value if conversion_value > 0 else 0
        
        # 平价溢价率（同上）
        parity_premium = conversion_premium
        
        # 判断股性强弱
        if conversion_premium < 0.10:
            equity_nature = "强股性"
        elif conversion_premium < 0.30:
            equity_nature = "平衡型"
        else:
            equity_nature = "强债性"
        
        return {
            "conversion_value": round(conversion_value, 2),
            "conversion_premium": f"{conversion_premium * 100:.2f}%",
            "conversion_premium_raw": conversion_premium,
            "parity_premium": f"{parity_premium * 100:.2f}%",
            "equity_nature": equity_nature,
            "cb_price": self.cb_price,
            "stock_price": self.stock_price,
            "conversion_price": self.conversion_price,
        }
    
    def calculate_pure_bond_value(self) -> Dict:
        """
        计算纯债价值（简化版：现金流折现）
        
        Returns:
            纯债价值相关指标
        """
        # 根据信用评级设定折现率
        yield_by_rating = {
            "AAA": 0.025,
            "AA+": 0.030,
            "AA": 0.035,
            "AA-": 0.045,
            "A+": 0.060,
        }
        discount_rate = yield_by_rating.get(self.credit_rating, 0.04)
        
        # 简化计算：假设每年付息，到期还本
        annual_coupon = self.par_value * self.coupon_rate
        pure_bond_value = 0
        
        # 利息现值
        for year in range(1, int(self.years_to_maturity) + 1):
            pure_bond_value += annual_coupon / (1 + discount_rate) ** year
        
        # 本金现值
        pure_bond_value += self.par_value / (1 + discount_rate) ** self.years_to_maturity
        
        # 纯债溢价率
        bond_premium = (self.cb_price - pure_bond_value) / pure_bond_value if pure_bond_value > 0 else 0
        
        # 到期收益率（简化）
        ytm = (self.par_value - self.cb_price) / self.cb_price / self.years_to_maturity + self.coupon_rate
        
        # 判断债底保护
        if bond_premium < 0.10:
            bond_protection = "强保护"
        elif bond_premium < 0.30:
            bond_protection = "中等保护"
        else:
            bond_protection = "弱保护"
        
        return {
            "pure_bond_value": round(pure_bond_value, 2),
            "bond_premium": f"{bond_premium * 100:.2f}%",
            "bond_premium_raw": bond_premium,
            "ytm_estimate": f"{ytm * 100:.2f}%",
            "bond_protection": bond_protection,
            "credit_rating": self.credit_rating,
            "years_to_maturity": self.years_to_maturity,
        }
    
    def get_valuation_summary(self) -> Dict:
        """
        获取估值综合评估
        
        Returns:
            估值总结
        """
        conversion = self.calculate_conversion_value()
        bond = self.calculate_pure_bond_value()
        
        # 双低值 = 价格 + 转股溢价率×100
        dual_low_value = self.cb_price + conversion["conversion_premium_raw"] * 100
        
        # 价格区间判断
        if self.cb_price < 90:
            price_zone = "深度破发"
            strategy = "防守型，关注债底保护"
        elif self.cb_price < 110:
            price_zone = "低估区间"
            strategy = "双低策略好选择"
        elif self.cb_price < 130:
            price_zone = "合理区间"
            strategy = "关注正股走势"
        elif self.cb_price < 150:
            price_zone = "高估区间"
            strategy = "注意强赎风险"
        else:
            price_zone = "高风险区间"
            strategy = "谨慎，警惕强赎"
        
        # 综合评级
        score = 0
        if conversion["conversion_premium_raw"] < 0.10:
            score += 3
        elif conversion["conversion_premium_raw"] < 0.30:
            score += 2
        elif conversion["conversion_premium_raw"] < 0.50:
            score += 1
        
        if bond["bond_premium_raw"] < 0.20:
            score += 3
        elif bond["bond_premium_raw"] < 0.40:
            score += 2
        elif bond["bond_premium_raw"] < 0.60:
            score += 1
        
        if self.cb_price < 110:
            score += 3
        elif self.cb_price < 130:
            score += 2
        elif self.cb_price < 150:
            score += 1
        
        if score >= 7:
            rating = "★★★★★"
        elif score >= 5:
            rating = "★★★★"
        elif score >= 3:
            rating = "★★★"
        else:
            rating = "★★"
        
        return {
            "name": self.name,
            "code": self.code,
            "cb_price": self.cb_price,
            "stock_name": self.stock_name,
            "stock_price": self.stock_price,
            "conversion_value": conversion["conversion_value"],
            "conversion_premium": conversion["conversion_premium"],
            "pure_bond_value": bond["pure_bond_value"],
            "bond_premium": bond["bond_premium"],
            "dual_low_value": round(dual_low_value, 2),
            "price_zone": price_zone,
            "strategy": strategy,
            "equity_nature": conversion["equity_nature"],
            "bond_protection": bond["bond_protection"],
            "rating": rating,
            "score": score,
        }
    
    def check_redemption_condition(
        self,
        recent_stock_prices: List[float],
        days_count: int = 30,
    ) -> Dict:
        """
        检查强赎条件
        
        Args:
            recent_stock_prices: 最近 N 天正股价
            days_count: 统计天数
        
        Returns:
            强赎条件检查结果
        """
        threshold_price = self.conversion_price * self.REDEMPTION_CONDITION["price_ratio"]
        threshold_days = self.REDEMPTION_CONDITION["threshold_days"]
        
        # 统计达到条件的天数
        qualified_days = sum(
            1 for price in recent_stock_prices[-days_count:]
            if price >= threshold_price
        )
        
        is_triggered = qualified_days >= threshold_days
        remaining_days = threshold_days - qualified_days
        
        return {
            "threshold_price": round(threshold_price, 2),
            "qualified_days": qualified_days,
            "threshold_days": threshold_days,
            "is_triggered": is_triggered,
            "remaining_days": max(0, remaining_days),
            "risk_level": "高" if is_triggered else ("中" if qualified_days > threshold_days / 2 else "低"),
            "warning": (
                f"⚠️ 已触发强赎条件！请尽快转股或卖出"
                if is_triggered else
                f"⚠️ 接近强赎条件，还需{remaining_days}天" if qualified_days > threshold_days / 2 else
                "✅ 强赎风险较低"
            ),
        }
    
    def check_downward_revision_condition(
        self,
        recent_stock_prices: List[float],
        days_count: int = 30,
    ) -> Dict:
        """
        检查下修条件
        
        Args:
            recent_stock_prices: 最近 N 天正股价
            days_count: 统计天数
        
        Returns:
            下修条件检查结果
        """
        threshold_price = self.conversion_price * self.DOWNWARD_REVISION_CONDITION["price_ratio"]
        threshold_days = self.DOWNWARD_REVISION_CONDITION["threshold_days"]
        
        # 统计达到条件的天数
        qualified_days = sum(
            1 for price in recent_stock_prices[-days_count:]
            if price <= threshold_price
        )
        
        is_triggered = qualified_days >= threshold_days
        
        # 下修可能性评估
        if is_triggered:
            probability = "高"
        elif qualified_days > threshold_days / 2:
            probability = "中"
        else:
            probability = "低"
        
        return {
            "threshold_price": round(threshold_price, 2),
            "qualified_days": qualified_days,
            "threshold_days": threshold_days,
            "is_triggered": is_triggered,
            "probability": probability,
            "suggestion": (
                "公司可能公告下修转股价，可关注"
                if probability == "高" else
                "下修可能性存在，持续关注" if probability == "中" else
                "下修条件未触发"
            ),
        }
    
    def screen_dual_low(
        candidates: List["CBValuation"],
        max_price: float = 110,
        max_premium: float = 0.20,
    ) -> List[Dict]:
        """
        双低策略筛选
        
        Args:
            candidates: 可转债候选列表
            max_price: 最高价格
            max_premium: 最高转股溢价率
        
        Returns:
            筛选结果
        """
        results = []
        
        for cb in candidates:
            summary = cb.get_valuation_summary()
            
            if cb.cb_price <= max_price and summary["conversion_premium_raw"] <= max_premium:
                results.append({
                    "name": cb.name,
                    "code": cb.code,
                    "cb_price": cb.cb_price,
                    "conversion_premium": summary["conversion_premium"],
                    "dual_low_value": summary["dual_low_value"],
                    "rating": summary["rating"],
                    "stock_name": cb.stock_name,
                })
        
        # 按双低值排序
        results.sort(key=lambda x: x["dual_low_value"])
        
        return results
    
    def generate_report(self) -> str:
        """
        生成估值报告
        
        Returns:
            格式化报告文本
        """
        summary = self.get_valuation_summary()
        
        lines = []
        lines.append("=" * 60)
        lines.append("可转债估值报告")
        lines.append("=" * 60)
        lines.append("")
        
        lines.append(f"名称：{summary['name']} ({summary['code']})")
        lines.append(f"正股：{summary['stock_name']} ({summary['stock_price']} 元)")
        lines.append("")
        
        lines.append("【价格信息】")
        lines.append(f"转债价格：{summary['cb_price']} 元")
        lines.append(f"价格区间：{summary['price_zone']}")
        lines.append(f"策略建议：{summary['strategy']}")
        lines.append("")
        
        lines.append("【转股价值】")
        conv = self.calculate_conversion_value()
        lines.append(f"转股价值：{conv['conversion_value']} 元")
        lines.append(f"转股溢价率：{conv['conversion_premium']}")
        lines.append(f"股性：{conv['equity_nature']}")
        lines.append("")
        
        lines.append("【纯债价值】")
        bond = self.calculate_pure_bond_value()
        lines.append(f"纯债价值：{bond['pure_bond_value']} 元")
        lines.append(f"纯债溢价率：{bond['bond_premium']}")
        lines.append(f"债底保护：{bond['bond_protection']}")
        lines.append(f"到期收益率：{bond['ytm_estimate']}")
        lines.append("")
        
        lines.append("【综合评估】")
        lines.append(f"双低值：{summary['dual_low_value']}")
        lines.append(f"评级：{summary['rating']}")
        lines.append("")
        
        lines.append("=" * 60)
        
        return "\n".join(lines)


# 快速测试
if __name__ == "__main__":
    cb = CBValuation(
        name="XX 转债",
        code="123456",
        cb_price=115.0,
        par_value=100,
        conversion_price=10.5,
        stock_price=11.2,
        years_to_maturity=3,
        coupon_rate=0.01,
        credit_rating="AA",
        stock_name="XX 股份",
    )
    
    print(cb.generate_report())
