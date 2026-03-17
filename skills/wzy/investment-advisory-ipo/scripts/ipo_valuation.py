#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
IPO 新股估值分析器

功能：
1. 发行估值与同行对比
2. PEG/PS 等估值指标计算
3. 可比公司分析
4. 申购建议生成
5. 破发风险评估

使用示例：
    from ipo_valuation import IPOValuation
    
    ipo = IPOValuation(
        company_name="XX 科技",
        industry="半导体",
        issue_pe=35.0,      # 发行 PE
        industry_pe=40.0,   # 行业 PE
        growth_rate=0.30,   # 净利润增速
        issue_price=25.0,   # 发行价
        eps=0.71,          # 每股收益
    )
    
    print(ipo.calculate_valuation())
    print(ipo.get_subscription_suggestion())
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ComparableCompany:
    """可比公司信息"""
    name: str
    code: str
    pe: float
    pb: float
    ps: float = None
    peg: float = None
    growth_rate: float = None
    market_cap: float = None  # 亿


class IPOValuation:
    """IPO 新股估值分析器"""
    
    # 各板块典型 PE 区间（参考）
    TYPICAL_PE_RANGES = {
        "主板": (15, 25),
        "科创板": (30, 60),
        "创业板": (25, 50),
        "北交所": (15, 30),
    }
    
    # 行业 PE 参考（简化）
    INDUSTRY_PE_REFERENCES = {
        "银行": 6,
        "房地产": 8,
        "建筑": 10,
        "制造业": 20,
        "消费": 25,
        "医药": 35,
        "半导体": 45,
        "新能源": 35,
        "互联网": 30,
        "软件": 40,
    }
    
    def __init__(
        self,
        company_name: str,
        industry: str,
        issue_pe: float,
        issue_price: float,
        eps: float,
        industry_pe: float = None,
        growth_rate: float = None,
        board: str = "主板",
        net_profit: float = None,  # 亿
        revenue: float = None,     # 亿
    ):
        """
        初始化 IPO 估值器
        
        Args:
            company_name: 公司名称
            industry: 所属行业
            issue_pe: 发行 PE
            issue_price: 发行价
            eps: 每股收益
            industry_pe: 行业 PE（可选）
            growth_rate: 净利润增速（可选）
            board: 上市板块
            net_profit: 净利润（可选）
            revenue: 营收（可选）
        """
        self.company_name = company_name
        self.industry = industry
        self.issue_pe = issue_pe
        self.issue_price = issue_price
        self.eps = eps
        self.industry_pe = industry_pe
        self.growth_rate = growth_rate
        self.board = board
        self.net_profit = net_profit
        self.revenue = revenue
        self.comparable_companies: List[ComparableCompany] = []
    
    def add_comparable_company(self, company: ComparableCompany) -> None:
        """添加可比公司"""
        self.comparable_companies.append(company)
    
    def set_comparable_companies(self, companies: List[Dict]) -> None:
        """批量设置可比公司"""
        for c in companies:
            self.comparable_companies.append(ComparableCompany(**c))
    
    def calculate_valuation(self) -> Dict:
        """
        计算估值指标
        
        Returns:
            估值分析结果
        """
        result = {
            "company_name": self.company_name,
            "industry": self.industry,
            "board": self.board,
            "issue_price": self.issue_price,
            "issue_pe": self.issue_pe,
            "eps": self.eps,
        }
        
        # 1. 与行业 PE 对比
        if self.industry_pe:
            result["industry_pe"] = self.industry_pe
            result["pe_vs_industry"] = f"{(self.issue_pe / self.industry_pe - 1) * 100:+.1f}%"
            result["is_cheaper_than_industry"] = self.issue_pe < self.industry_pe
        else:
            # 使用行业参考
            ref_pe = self.INDUSTRY_PE_REFERENCES.get(self.industry, 25)
            result["industry_pe_ref"] = ref_pe
            result["pe_vs_industry_ref"] = f"{(self.issue_pe / ref_pe - 1) * 100:+.1f}%"
        
        # 2. PEG 计算
        if self.growth_rate and self.growth_rate > 0:
            peg = self.issue_pe / (self.growth_rate * 100)
            result["peg"] = round(peg, 2)
            result["peg_interpretation"] = self._peg_interpretation(peg)
        
        # 3. 板块 PE 区间对比
        if self.board in self.TYPICAL_PE_RANGES:
            min_pe, max_pe = self.TYPICAL_PE_RANGES[self.board]
            result["board_pe_range"] = f"{min_pe}-{max_pe}"
            if self.issue_pe < min_pe:
                result["vs_board"] = "偏低"
            elif self.issue_pe > max_pe:
                result["vs_board"] = "偏高"
            else:
                result["vs_board"] = "合理"
        
        # 4. 与可比公司对比
        if self.comparable_companies:
            avg_pe = sum(c.pe for c in self.comparable_companies) / len(self.comparable_companies)
            result["comparable_avg_pe"] = round(avg_pe, 1)
            result["pe_vs_comparable"] = f"{(self.issue_pe / avg_pe - 1) * 100:+.1f}%"
            result["is_cheaper_than_comparable"] = self.issue_pe < avg_pe
            
            # 可比公司详情
            result["comparable_details"] = [
                {"name": c.name, "pe": c.pe, "pb": c.pb}
                for c in self.comparable_companies
            ]
        
        return result
    
    def _peg_interpretation(self, peg: float) -> str:
        """PEG 解释"""
        if peg < 0.5:
            return "低估（增速远高于 PE）"
        elif peg < 1:
            return "合理偏低（增速高于 PE）"
        elif peg < 1.5:
            return "合理"
        elif peg < 2:
            return "偏高（增速低于 PE）"
        else:
            return "高估（增速远低于 PE）"
    
    def assess_break_risk(self) -> Dict:
        """
        评估破发风险
        
        Returns:
            破发风险评估
        """
        risk_score = 0
        risk_factors = []
        
        # 1. 发行 PE 过高
        if self.industry_pe:
            if self.issue_pe > self.industry_pe * 1.5:
                risk_score += 30
                risk_factors.append("发行 PE 显著高于行业平均")
            elif self.issue_pe > self.industry_pe * 1.2:
                risk_score += 15
                risk_factors.append("发行 PE 高于行业平均")
        
        # 2. PEG 过高
        if self.growth_rate and self.growth_rate > 0:
            peg = self.issue_pe / (self.growth_rate * 100)
            if peg > 2:
                risk_score += 20
                risk_factors.append("PEG 过高，估值与增速不匹配")
            elif peg > 1.5:
                risk_score += 10
                risk_factors.append("PEG 偏高")
        
        # 3. 板块因素
        if self.board == "科创板":
            risk_score += 10
            risk_factors.append("科创板波动较大")
        elif self.board == "创业板":
            risk_score += 5
            risk_factors.append("创业板波动较大")
        
        # 4. 市场环境（简化，实际需要根据市场情况调整）
        # 这里假设市场情绪中性
        risk_score += 10
        risk_factors.append("当前市场情绪中性")
        
        # 5. 可比公司对比
        if self.comparable_companies:
            avg_pe = sum(c.pe for c in self.comparable_companies) / len(self.comparable_companies)
            if self.issue_pe > avg_pe * 1.3:
                risk_score += 20
                risk_factors.append("发行估值显著高于可比公司")
            elif self.issue_pe > avg_pe * 1.1:
                risk_score += 10
                risk_factors.append("发行估值高于可比公司")
        
        # 风险等级
        if risk_score >= 60:
            risk_level = "高"
            break_probability = ">40%"
        elif risk_score >= 40:
            risk_level = "中高"
            break_probability = "25-40%"
        elif risk_score >= 20:
            risk_level = "中"
            break_probability = "15-25%"
        else:
            risk_level = "低"
            break_probability = "<15%"
        
        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "break_probability": break_probability,
            "risk_factors": risk_factors,
            "suggestion": self._break_risk_suggestion(risk_level),
        }
    
    def _break_risk_suggestion(self, risk_level: str) -> str:
        """根据风险等级给出建议"""
        suggestions = {
            "高": "破发风险较高，建议谨慎申购或放弃",
            "中高": "存在一定破发风险，建议谨慎申购",
            "中": "破发风险中等，可适度申购",
            "低": "破发风险较低，建议申购",
        }
        return suggestions.get(risk_level, "综合评估后决策")
    
    def get_subscription_suggestion(self) -> Dict:
        """
        获取申购建议
        
        Returns:
            申购建议
        """
        valuation = self.calculate_valuation()
        break_risk = self.assess_break_risk()
        
        # 综合评分
        score = 100 - break_risk["risk_score"]
        
        # 建议等级
        if score >= 70:
            suggestion_level = "建议申购"
            confidence = "高"
        elif score >= 50:
            suggestion_level = "谨慎申购"
            confidence = "中"
        elif score >= 30:
            suggestion_level = "谨慎参与"
            confidence = "低"
        else:
            suggestion_level = "建议放弃"
            confidence = "很低"
        
        # 理由
        reasons = []
        if valuation.get("is_cheaper_than_industry", True):
            reasons.append("发行估值低于行业平均")
        if valuation.get("peg", 1) < 1.5:
            reasons.append("PEG 合理")
        if valuation.get("vs_board") in ["偏低", "合理"]:
            reasons.append(f"发行 PE 在{self.board}合理区间")
        if break_risk["risk_level"] in ["低", "中"]:
            reasons.append("破发风险可控")
        
        negative_reasons = break_risk["risk_factors"]
        
        return {
            "company_name": self.company_name,
            "suggestion_level": suggestion_level,
            "confidence": confidence,
            "score": score,
            "positive_reasons": reasons,
            "negative_reasons": negative_reasons,
            "break_risk": break_risk,
            "valuation_summary": valuation,
        }
    
    def calculate_listing_return_estimate(self) -> Dict:
        """
        估算上市首日收益（简化模型）
        
        Returns:
            收益估算
        """
        # 基于行业平均和可比公司的简单估算
        if self.industry_pe:
            # 假设上市首日 PE 向行业平均回归
            expected_pe = (self.issue_pe + self.industry_pe) / 2
            expected_price = expected_pe * self.eps
            expected_return = (expected_price - self.issue_price) / self.issue_price
        elif self.comparable_companies:
            avg_pe = sum(c.pe for c in self.comparable_companies) / len(self.comparable_companies)
            expected_pe = (self.issue_pe + avg_pe) / 2
            expected_price = expected_pe * self.eps
            expected_return = (expected_price - self.issue_price) / self.issue_price
        else:
            expected_return = None
            expected_price = None
        
        # 情景分析
        scenarios = {
            "乐观": {"pe_multiple": 1.3, "description": "市场情绪好，估值提升"},
            "中性": {"pe_multiple": 1.0, "description": "估值向行业平均回归"},
            "悲观": {"pe_multiple": 0.7, "description": "破发情景"},
        }
        
        scenario_results = {}
        for name, params in scenarios.items():
            if expected_pe:
                scenario_price = self.issue_pe * params["pe_multiple"] * self.eps
                scenario_return = (scenario_price - self.issue_price) / self.issue_price
                scenario_results[name] = {
                    "price": round(scenario_price, 2),
                    "return": f"{scenario_return * 100:+.1f}%",
                }
        
        return {
            "expected_price": round(expected_price, 2) if expected_price else None,
            "expected_return": f"{expected_return * 100:+.1f}%" if expected_return else "N/A",
            "scenarios": scenario_results,
            "note": "以上为简化估算，实际表现受市场情绪、资金面等多因素影响",
        }
    
    def generate_report(self) -> str:
        """
        生成 IPO 估值报告
        
        Returns:
            格式化报告文本
        """
        valuation = self.calculate_valuation()
        break_risk = self.assess_break_risk()
        suggestion = self.get_subscription_suggestion()
        return_estimate = self.calculate_listing_return_estimate()
        
        lines = []
        lines.append("=" * 70)
        lines.append("IPO 新股估值分析报告")
        lines.append("=" * 70)
        lines.append("")
        
        lines.append(f"公司名称：{self.company_name}")
        lines.append(f"所属行业：{self.industry}")
        lines.append(f"上市板块：{self.board}")
        lines.append(f"发行价格：{self.issue_price} 元")
        lines.append(f"每股收益：{self.eps} 元")
        lines.append("")
        
        lines.append("【估值分析】")
        lines.append(f"发行 PE：{self.issue_pe} 倍")
        if valuation.get("industry_pe"):
            lines.append(f"行业 PE：{valuation['industry_pe']} 倍")
            lines.append(f"vs 行业：{valuation['pe_vs_industry']}")
        if valuation.get("peg"):
            lines.append(f"PEG：{valuation['peg']}（{valuation['peg_interpretation']}）")
        if valuation.get("board_pe_range"):
            lines.append(f"{self.board}PE 区间：{valuation['board_pe_range']}")
            lines.append(f"vs 板块：{valuation['vs_board']}")
        if valuation.get("comparable_avg_pe"):
            lines.append(f"可比公司平均 PE：{valuation['comparable_avg_pe']} 倍")
            lines.append(f"vs 可比：{valuation['pe_vs_comparable']}")
        lines.append("")
        
        lines.append("【破发风险】")
        lines.append(f"风险等级：{break_risk['risk_level']}")
        lines.append(f"破发概率：{break_risk['break_probability']}")
        if break_risk["risk_factors"]:
            lines.append("风险因素:")
            for factor in break_risk["risk_factors"]:
                lines.append(f"  - {factor}")
        lines.append("")
        
        lines.append("【申购建议】")
        lines.append(f"建议等级：{suggestion['suggestion_level']}")
        lines.append(f"信心程度：{suggestion['confidence']}")
        lines.append(f"综合评分：{suggestion['score']} 分")
        if suggestion["positive_reasons"]:
            lines.append("正面因素:")
            for reason in suggestion["positive_reasons"]:
                lines.append(f"  ✓ {reason}")
        if suggestion["negative_reasons"]:
            lines.append("风险因素:")
            for reason in suggestion["negative_reasons"]:
                lines.append(f"  ⚠ {reason}")
        lines.append("")
        
        lines.append("【收益估算】")
        lines.append(f"预期价格：{return_estimate['expected_price']} 元")
        lines.append(f"预期收益：{return_estimate['expected_return']}")
        lines.append("情景分析:")
        for name, data in return_estimate["scenarios"].items():
            lines.append(f"  {name}: {data['price']} 元 ({data['return']})")
        lines.append(f"注：{return_estimate['note']}")
        lines.append("")
        
        lines.append("=" * 70)
        
        return "\n".join(lines)


# 快速测试
if __name__ == "__main__":
    ipo = IPOValuation(
        company_name="XX 科技",
        industry="半导体",
        issue_pe=35.0,
        issue_price=25.0,
        eps=0.71,
        industry_pe=40.0,
        growth_rate=0.30,
        board="科创板",
    )
    
    # 添加可比公司
    ipo.set_comparable_companies([
        {"name": "中芯国际", "code": "688981", "pe": 45, "pb": 2.5},
        {"name": "华虹半导体", "code": "688347", "pe": 38, "pb": 2.0},
        {"name": "韦尔股份", "code": "603501", "pe": 42, "pb": 3.5},
    ])
    
    print(ipo.generate_report())
