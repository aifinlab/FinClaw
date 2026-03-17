#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
零售客户持仓分析器

功能：
1. 集中度风险分析
2. 风险匹配度评估
3. 产品重叠度检测
4. 流动性分析
5. 简洁版诊断报告生成

使用示例：
    from portfolio_analyzer import PortfolioAnalyzer
    
    analyzer = PortfolioAnalyzer(
        holdings=[
            {"name": "易方达沪深 300ETF", "type": "指数基金", "amount": 100000, "pct": 0.25},
            {"name": "易方达中证 500ETF", "type": "指数基金", "amount": 80000, "pct": 0.20},
            {"name": "招商中证白酒", "type": "行业基金", "amount": 120000, "pct": 0.30},
            {"name": "工银瑞信金融地产", "type": "行业基金", "amount": 60000, "pct": 0.15},
            {"name": "余额宝", "type": "货币基金", "amount": 40000, "pct": 0.10},
        ],
        customer_risk_level="稳健型",
        total_assets=400000,
    )
    
    print(analyzer.analyze_concentration())
    print(analyzer.check_risk_match())
    print(analyzer.generate_report())
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class Holding:
    """持仓信息"""
    name: str
    type: str  # 产品类型
    amount: float  # 金额
    pct: float  # 占比
    pnl: float = 0.0  # 盈亏比例
    sector: str = None  # 所属行业/主题


class PortfolioAnalyzer:
    """零售客户持仓分析器"""
    
    # 风险等级对应的建议股票类占比
    RISK_LEVEL_LIMITS = {
        "保守型": 0.20,
        "稳健型": 0.40,
        "平衡型": 0.60,
        "成长型": 0.80,
        "进取型": 1.00,
    }
    
    # 集中度预警线
    SINGLE_PRODUCT_WARNING = 0.30  # 单一产品>30%
    TOP3_WARNING = 0.60  # 前三大>60%
    SINGLE_SECTOR_WARNING = 0.40  # 单一行业>40%
    
    # 产品类型分类
    EQUITY_TYPES = ["股票基金", "混合基金", "指数基金", "行业基金", "股票"]
    BOND_TYPES = ["债券基金", "债券"]
    CASH_TYPES = ["货币基金", "现金", "银行理财"]
    
    def __init__(
        self,
        holdings: List[Dict],
        customer_risk_level: str = "稳健型",
        total_assets: float = None,
        customer_age: int = None,
        investment_horizon: str = "中期",
    ):
        """
        初始化分析器
        
        Args:
            holdings: 持仓列表
            customer_risk_level: 客户风险等级
            total_assets: 总资产（可选，会从 holdings 计算）
            customer_age: 客户年龄（可选）
            investment_horizon: 投资期限
        """
        self.holdings = holdings
        self.customer_risk_level = customer_risk_level
        self.customer_age = customer_age
        self.investment_horizon = investment_horizon
        
        # 计算总资产
        if total_assets:
            self.total_assets = total_assets
        else:
            self.total_assets = sum(h.get("amount", 0) for h in holdings)
        
        # 计算各持仓占比（如果未提供）
        for h in self.holdings:
            if "pct" not in h and self.total_assets > 0:
                h["pct"] = h.get("amount", 0) / self.total_assets
    
    def analyze_concentration(self) -> Dict:
        """
        分析集中度风险
        
        Returns:
            集中度分析结果
        """
        if not self.holdings:
            return {"message": "无持仓数据"}
        
        # 按金额排序
        sorted_holdings = sorted(
            self.holdings,
            key=lambda x: x.get("amount", 0),
            reverse=True,
        )
        
        # 单一产品集中度
        max_single = sorted_holdings[0]["pct"] if sorted_holdings else 0
        
        # 前三大集中度
        top3_pct = sum(h["pct"] for h in sorted_holdings[:3])
        
        # 行业集中度
        sector_holdings = defaultdict(float)
        for h in self.holdings:
            sector = h.get("sector", h.get("type", "未知"))
            sector_holdings[sector] += h["pct"]
        
        max_sector = max(sector_holdings.values()) if sector_holdings else 0
        max_sector_name = max(sector_holdings, key=sector_holdings.get) if sector_holdings else "N/A"
        
        # 生成预警
        warnings = []
        if max_single > self.SINGLE_PRODUCT_WARNING:
            warnings.append(f"⚠️ 单一产品集中：{sorted_holdings[0]['name']} 占比 {max_single * 100:.1f}%")
        if top3_pct > self.TOP3_WARNING:
            warnings.append(f"⚠️ 前三大集中：占比 {top3_pct * 100:.1f}%")
        if max_sector > self.SINGLE_SECTOR_WARNING:
            warnings.append(f"⚠️ 行业集中：{max_sector_name} 占比 {max_sector * 100:.1f}%")
        
        return {
            "max_single_product": {
                "name": sorted_holdings[0]["name"] if sorted_holdings else "N/A",
                "pct": f"{max_single * 100:.1f}%",
                "warning": max_single > self.SINGLE_PRODUCT_WARNING,
            },
            "top3_concentration": f"{top3_pct * 100:.1f}%",
            "top3_warning": top3_pct > self.TOP3_WARNING,
            "max_sector": {
                "name": max_sector_name,
                "pct": f"{max_sector * 100:.1f}%",
                "warning": max_sector > self.SINGLE_SECTOR_WARNING,
            },
            "sector_breakdown": dict(sector_holdings),
            "warnings": warnings,
            "risk_level": self._concentration_risk_level(max_single, top3_pct, max_sector),
        }
    
    def _concentration_risk_level(
        self,
        max_single: float,
        top3: float,
        max_sector: float,
    ) -> str:
        """评估集中度风险等级"""
        score = 0
        if max_single > 0.50:
            score += 3
        elif max_single > 0.30:
            score += 2
        elif max_single > 0.20:
            score += 1
        
        if top3 > 0.80:
            score += 3
        elif top3 > 0.60:
            score += 2
        elif top3 > 0.50:
            score += 1
        
        if max_sector > 0.60:
            score += 3
        elif max_sector > 0.40:
            score += 2
        elif max_sector > 0.30:
            score += 1
        
        if score >= 6:
            return "高"
        elif score >= 3:
            return "中"
        else:
            return "低"
    
    def check_risk_match(self) -> Dict:
        """
        检查风险匹配度
        
        Returns:
            风险匹配分析结果
        """
        # 计算股票类资产占比
        equity_pct = 0
        for h in self.holdings:
            product_type = h.get("type", "")
            if any(t in product_type for t in self.EQUITY_TYPES):
                equity_pct += h.get("pct", 0)
        
        # 获取风险等级限制
        limit = self.RISK_LEVEL_LIMITS.get(self.customer_risk_level, 0.60)
        
        # 判断是否匹配
        is_matched = equity_pct <= limit
        excess = equity_pct - limit
        
        # 建议
        if is_matched:
            suggestion = f"当前股票类占比 {equity_pct * 100:.1f}%，符合{self.customer_risk_level}客户建议范围（≤{limit * 100:.0f}%）"
        else:
            suggestion = f"当前股票类占比 {equity_pct * 100:.1f}%，超出{self.customer_risk_level}客户建议范围（≤{limit * 100:.0f}%）{excess * 100:.1f} 个百分点，建议降低股票类仓位"
        
        return {
            "customer_risk_level": self.customer_risk_level,
            "equity_ratio": f"{equity_pct * 100:.1f}%",
            "recommended_limit": f"{limit * 100:.0f}%",
            "is_matched": is_matched,
            "excess": f"{excess * 100:.1f}%" if excess > 0 else "0%",
            "suggestion": suggestion,
        }
    
    def check_overlap(self) -> Dict:
        """
        检查产品重叠度
        
        Returns:
            重叠度分析结果
        """
        if len(self.holdings) < 2:
            return {"message": "持仓产品数量不足，无法分析重叠"}
        
        # 按类型分组
        type_groups = defaultdict(list)
        for h in self.holdings:
            product_type = h.get("type", "未知")
            type_groups[product_type].append(h)
        
        # 找出可能重叠的产品
        overlaps = []
        
        # 同一类型内的产品可能重叠
        for product_type, products in type_groups.items():
            if len(products) >= 2 and product_type in ["指数基金", "行业基金", "股票基金"]:
                overlaps.append({
                    "type": product_type,
                    "products": [p["name"] for p in products],
                    "total_pct": sum(p["pct"] for p in products),
                    "suggestion": f"建议整合同类产品，保留 1-2 只即可",
                })
        
        # 检查名称相似的产品（可能跟踪同一指数）
        name_keywords = defaultdict(list)
        for h in self.holdings:
            name = h["name"]
            if "沪深 300" in name:
                name_keywords["沪深 300"].append(h)
            elif "中证 500" in name:
                name_keywords["中证 500"].append(h)
            elif "创业板" in name:
                name_keywords["创业板"].append(h)
            elif "白酒" in name:
                name_keywords["白酒"].append(h)
        
        for keyword, products in name_keywords.items():
            if len(products) >= 2:
                overlaps.append({
                    "type": f"跟踪同一指数/主题：{keyword}",
                    "products": [p["name"] for p in products],
                    "total_pct": sum(p["pct"] for p in products),
                    "suggestion": f"多只产品跟踪同一{keyword}，存在重复配置，建议整合",
                })
        
        return {
            "has_overlap": len(overlaps) > 0,
            "overlap_count": len(overlaps),
            "overlaps": overlaps,
            "suggestion": (
                "存在产品重叠，建议整合持仓，减少重复配置"
                if overlaps else "产品重叠度较低，配置合理"
            ),
        }
    
    def analyze_liquidity(self) -> Dict:
        """
        分析流动性
        
        Returns:
            流动性分析结果
        """
        liquid_assets = 0  # 高流动性资产
        locked_assets = 0  # 锁定/低流动性资产
        
        for h in self.holdings:
            product_type = h.get("type", "")
            amount = h.get("amount", 0)
            
            if any(t in product_type for t in self.CASH_TYPES):
                liquid_assets += amount
            elif "封闭" in product_type or "定开" in product_type:
                locked_assets += amount
        
        liquid_ratio = liquid_assets / self.total_assets if self.total_assets > 0 else 0
        locked_ratio = locked_assets / self.total_assets if self.total_assets > 0 else 0
        
        # 评估
        if liquid_ratio < 0.05:
            liquidity_status = "偏低（建议保留 5-10% 高流动性资产）"
        elif liquid_ratio > 0.30:
            liquidity_status = "偏高（现金类资产过多，可能影响收益）"
        else:
            liquidity_status = "合理"
        
        return {
            "liquid_assets": f"{liquid_assets:,.0f} 元",
            "liquid_ratio": f"{liquid_ratio * 100:.1f}%",
            "locked_assets": f"{locked_assets:,.0f} 元",
            "locked_ratio": f"{locked_ratio * 100:.1f}%",
            "status": liquidity_status,
            "suggestion": (
                "建议适当增加货币基金或现金类资产" if liquid_ratio < 0.05
                else "可考虑将部分现金配置到收益更高的资产" if liquid_ratio > 0.30
                else "流动性配置合理"
            ),
        }
    
    def analyze_pnl(self) -> Dict:
        """
        分析盈亏情况
        
        Returns:
            盈亏分析结果
        """
        if not self.holdings or not any("pnl" in h for h in self.holdings):
            return {"message": "无盈亏数据"}
        
        total_pnl = 0
        total_amount = 0
        profitable = []
        losing = []
        
        for h in self.holdings:
            pnl = h.get("pnl", 0)
            amount = h.get("amount", 0)
            total_pnl += pnl * amount
            total_amount += amount
            
            if pnl > 0:
                profitable.append({"name": h["name"], "pnl": pnl})
            elif pnl < 0:
                losing.append({"name": h["name"], "pnl": pnl})
        
        avg_pnl = total_pnl / total_amount if total_amount > 0 else 0
        
        # 排序
        profitable.sort(key=lambda x: x["pnl"], reverse=True)
        losing.sort(key=lambda x: x["pnl"])
        
        return {
            "total_pnl": f"{avg_pnl * 100:.2f}%",
            "total_pnl_amount": f"{total_pnl:,.0f} 元",
            "profitable_count": len(profitable),
            "losing_count": len(losing),
            "best_performer": profitable[0] if profitable else None,
            "worst_performer": losing[0] if losing else None,
            "profitable_holdings": profitable[:5],
            "losing_holdings": losing[:5],
        }
    
    def generate_report(self) -> str:
        """
        生成简洁版诊断报告（适合微信发送）
        
        Returns:
            格式化报告文本
        """
        lines = []
        lines.append("【持仓诊断简报】")
        lines.append("")
        
        # 持仓概览
        lines.append(f"📊 持仓概览")
        lines.append(f"   总资产：{self.total_assets:,.0f} 元")
        lines.append(f"   产品数：{len(self.holdings)} 只")
        lines.append(f"   风险等级：{self.customer_risk_level}")
        lines.append("")
        
        # 集中度
        concentration = self.analyze_concentration()
        lines.append(f"📌 集中度风险：{concentration.get('risk_level', 'N/A')}")
        if concentration.get("warnings"):
            for warning in concentration["warnings"][:2]:
                lines.append(f"   {warning}")
        else:
            lines.append("   集中度合理")
        lines.append("")
        
        # 风险匹配
        risk_match = self.check_risk_match()
        lines.append(f"⚖️ 风险匹配：{'✅ 匹配' if risk_match['is_matched'] else '⚠️ 超出'}")
        lines.append(f"   股票类占比：{risk_match['equity_ratio']}")
        lines.append("")
        
        # 产品重叠
        overlap = self.check_overlap()
        lines.append(f"🔄 产品重叠：{'⚠️ 存在' if overlap.get('has_overlap') else '✅ 合理'}")
        if overlap.get("overlaps"):
            for o in overlap["overlaps"][:2]:
                lines.append(f"   - {o['type']}")
        lines.append("")
        
        # 盈亏
        pnl = self.analyze_pnl()
        if "total_pnl" in pnl:
            lines.append(f"💰 整体盈亏：{pnl['total_pnl']}")
            lines.append("")
        
        # 建议
        lines.append("💡 核心建议：")
        suggestions = []
        
        if not risk_match["is_matched"]:
            suggestions.append("降低股票类仓位至建议范围")
        if overlap.get("has_overlap"):
            suggestions.append("整合同类产品，减少重复配置")
        if concentration.get("risk_level") == "高":
            suggestions.append("分散持仓，降低集中度")
        
        if suggestions:
            for i, s in enumerate(suggestions[:3], 1):
                lines.append(f"   {i}. {s}")
        else:
            lines.append("   当前配置合理，保持即可")
        
        lines.append("")
        lines.append("有需要随时联系我详细沟通。")
        
        return "\n".join(lines)
    
    def generate_detailed_report(self) -> str:
        """
        生成标准版诊断报告
        
        Returns:
            详细报告文本
        """
        lines = []
        lines.append("=" * 60)
        lines.append("持仓诊断报告")
        lines.append("=" * 60)
        lines.append("")
        
        # 一、持仓概览
        lines.append("一、持仓概览")
        lines.append(f"   总资产：{self.total_assets:,.0f} 元")
        lines.append(f"   产品数量：{len(self.holdings)} 只")
        lines.append(f"   客户风险等级：{self.customer_risk_level}")
        lines.append(f"   投资期限：{self.investment_horizon}")
        lines.append("")
        
        # 持仓明细
        lines.append("   持仓明细：")
        for i, h in enumerate(self.holdings, 1):
            pnl_str = f" ({h.get('pnl', 0) * 100:.1f}%)" if "pnl" in h else ""
            lines.append(f"   {i}. {h['name']}: {h.get('amount', 0):,.0f} 元 ({h.get('pct', 0) * 100:.1f}%){pnl_str}")
        lines.append("")
        
        # 二、集中度分析
        lines.append("二、集中度分析")
        concentration = self.analyze_concentration()
        lines.append(f"   风险等级：{concentration.get('risk_level', 'N/A')}")
        lines.append(f"   单一产品最大占比：{concentration['max_single_product']['pct']}")
        lines.append(f"   前三大集中度：{concentration['top3_concentration']}")
        lines.append(f"   最大行业：{concentration['max_sector']['name']} ({concentration['max_sector']['pct']})")
        if concentration.get("warnings"):
            lines.append("   ⚠️ 预警:")
            for w in concentration["warnings"]:
                lines.append(f"      {w}")
        lines.append("")
        
        # 三、风险匹配度
        lines.append("三、风险匹配度")
        risk_match = self.check_risk_match()
        lines.append(f"   股票类占比：{risk_match['equity_ratio']}")
        lines.append(f"   建议上限：{risk_match['recommended_limit']}")
        lines.append(f"   匹配状态：{'✅ 匹配' if risk_match['is_matched'] else '⚠️ 超出'}")
        lines.append(f"   建议：{risk_match['suggestion']}")
        lines.append("")
        
        # 四、产品重叠
        lines.append("四、产品重叠")
        overlap = self.check_overlap()
        if overlap.get("overlaps"):
            for o in overlap["overlaps"]:
                lines.append(f"   ⚠️ {o['type']}")
                lines.append(f"      产品：{', '.join(o['products'])}")
                lines.append(f"      合计占比：{o['total_pct'] * 100:.1f}%")
                lines.append(f"      建议：{o['suggestion']}")
        else:
            lines.append("   ✅ 产品重叠度较低")
        lines.append("")
        
        # 五、流动性分析
        lines.append("五、流动性分析")
        liquidity = self.analyze_liquidity()
        lines.append(f"   高流动性资产：{liquidity['liquid_assets']} ({liquidity['liquid_ratio']})")
        lines.append(f"   低流动性资产：{liquidity['locked_assets']} ({liquidity['locked_ratio']})")
        lines.append(f"   状态：{liquidity['status']}")
        lines.append(f"   建议：{liquidity['suggestion']}")
        lines.append("")
        
        # 六、调整建议
        lines.append("六、调整建议")
        lines.append("   优先级排序：")
        
        suggestions = []
        if not risk_match["is_matched"]:
            suggestions.append(("高", "降低股票类仓位", risk_match["suggestion"]))
        if overlap.get("has_overlap"):
            suggestions.append(("高", "整合重复产品", overlap["suggestion"]))
        if concentration.get("risk_level") == "高":
            suggestions.append(("中", "降低集中度", "分散配置到不同产品/行业"))
        if liquidity["status"] != "合理":
            suggestions.append(("中", "调整流动性", liquidity["suggestion"]))
        
        for i, (priority, action, detail) in enumerate(suggestions[:5], 1):
            lines.append(f"   {i}. [{priority}] {action}")
            lines.append(f"      {detail}")
        
        if not suggestions:
            lines.append("   当前配置合理，无需调整")
        
        lines.append("")
        lines.append("七、后续跟踪")
        lines.append("   建议 3 个月后复检持仓")
        lines.append("   关注市场波动对持仓的影响")
        lines.append("")
        lines.append("=" * 60)
        
        return "\n".join(lines)


# 快速测试
if __name__ == "__main__":
    analyzer = PortfolioAnalyzer(
        holdings=[
            {"name": "易方达沪深 300ETF", "type": "指数基金", "amount": 100000, "pct": 0.25, "pnl": 0.05},
            {"name": "易方达中证 500ETF", "type": "指数基金", "amount": 80000, "pct": 0.20, "pnl": -0.08},
            {"name": "招商中证白酒", "type": "行业基金", "amount": 120000, "pct": 0.30, "pnl": -0.15},
            {"name": "工银瑞信金融地产", "type": "行业基金", "amount": 60000, "pct": 0.15, "pnl": 0.02},
            {"name": "余额宝", "type": "货币基金", "amount": 40000, "pct": 0.10, "pnl": 0.02},
        ],
        customer_risk_level="稳健型",
        total_assets=400000,
    )
    
    print(analyzer.generate_report())
    print("\n" + "=" * 60 + "\n")
    print(analyzer.generate_detailed_report())
