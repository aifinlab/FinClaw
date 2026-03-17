#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ETF 筛选器

功能：
1. 按规模筛选
2. 按费率筛选
3. 按跟踪误差筛选
4. 按流动性筛选
5. 综合评分

使用示例：
    from etf_screener import ETFScreener
    
    screener = ETFScreener()
    
    etfs = [
        {
            "name": "沪深 300ETF",
            "code": "510300",
            "index": "沪深 300",
            "aum": 500,  # 亿
            "expense_ratio": 0.005,
            "tracking_error": 0.01,
            "daily_volume": 5000,  # 万
        },
        # ... 更多 ETF
    ]
    
    results = screener.screen(etfs, min_aum=10, max_expense_ratio=0.01)
    print(screener.generate_ranking(results))
"""

from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class ETF:
    """ETF 基本信息"""
    name: str
    code: str
    index: str          # 跟踪指数
    aum: float          # 规模（亿）
    expense_ratio: float  # 费率
    tracking_error: float  # 跟踪误差（年化）
    daily_volume: float  # 日均成交（万）
    fund_company: str = None  # 基金公司


class ETFScreener:
    """ETF 筛选器"""
    
    # 筛选标准
    SCREENING_CRITERIA = {
        "wide_base": {  # 宽基
            "min_aum": 5,       # 亿
            "max_expense_ratio": 0.008,
            "max_tracking_error": 0.02,
            "min_daily_volume": 1000,  # 万
        },
        "sector": {  # 行业
            "min_aum": 2,
            "max_expense_ratio": 0.01,
            "max_tracking_error": 0.03,
            "min_daily_volume": 500,
        },
        "thematic": {  # 主题
            "min_aum": 1,
            "max_expense_ratio": 0.012,
            "max_tracking_error": 0.04,
            "min_daily_volume": 300,
        },
        "cross_border": {  # 跨境
            "min_aum": 2,
            "max_expense_ratio": 0.015,
            "max_tracking_error": 0.05,
            "min_daily_volume": 500,
        },
    }
    
    # 评分权重
    SCORE_WEIGHTS = {
        "aum": 0.30,
        "expense_ratio": 0.30,
        "tracking_error": 0.25,
        "liquidity": 0.15,
    }
    
    def __init__(self):
        pass
    
    def screen(
        self,
        etfs: List[Dict],
        etf_type: str = "wide_base",
        min_aum: float = None,
        max_expense_ratio: float = None,
        max_tracking_error: float = None,
        min_daily_volume: float = None,
    ) -> List[Dict]:
        """
        筛选 ETF
        
        Args:
            etfs: ETF 列表
            etf_type: ETF 类型（wide_base/sector/thematic/cross_border）
            min_aum: 最小规模
            max_expense_ratio: 最高费率
            max_tracking_error: 最大跟踪误差
            min_daily_volume: 最小日均成交
        
        Returns:
            筛选结果
        """
        # 获取筛选标准
        criteria = self.SCREENING_CRITERIA.get(etf_type, self.SCREENING_CRITERIA["wide_base"])
        
        # 用户自定义覆盖
        if min_aum is not None:
            criteria["min_aum"] = min_aum
        if max_expense_ratio is not None:
            criteria["max_expense_ratio"] = max_expense_ratio
        if max_tracking_error is not None:
            criteria["max_tracking_error"] = max_tracking_error
        if min_daily_volume is not None:
            criteria["min_daily_volume"] = min_daily_volume
        
        results = []
        
        for etf in etfs:
            # 检查是否满足所有条件
            if etf["aum"] < criteria["min_aum"]:
                continue
            if etf["expense_ratio"] > criteria["max_expense_ratio"]:
                continue
            if etf.get("tracking_error", 0) > criteria["max_tracking_error"]:
                continue
            if etf.get("daily_volume", 0) < criteria["min_daily_volume"]:
                continue
            
            # 计算综合评分
            score = self.calculate_score(etf, etf_type)
            
            results.append({
                **etf,
                "score": score,
                "criteria": etf_type,
            })
        
        # 按评分降序排序
        results.sort(key=lambda x: x["score"], reverse=True)
        
        return results
    
    def calculate_score(self, etf: Dict, etf_type: str = "wide_base") -> float:
        """
        计算 ETF 综合评分（0-100）
        
        Args:
            etf: ETF 信息
            etf_type: ETF 类型
        
        Returns:
            综合评分
        """
        score = 0
        
        # 1. 规模评分（0-100）
        criteria = self.SCREENING_CRITERIA.get(etf_type, self.SCREENING_CRITERIA["wide_base"])
        aum_score = min(100, (etf["aum"] / criteria["min_aum"]) * 50)
        
        # 2. 费率评分（0-100，越低越好）
        expense_score = max(0, 100 - (etf["expense_ratio"] / criteria["max_expense_ratio"]) * 100)
        
        # 3. 跟踪误差评分（0-100，越低越好）
        te = etf.get("tracking_error", criteria["max_tracking_error"])
        te_score = max(0, 100 - (te / criteria["max_tracking_error"]) * 100)
        
        # 4. 流动性评分（0-100）
        vol = etf.get("daily_volume", criteria["min_daily_volume"])
        vol_score = min(100, (vol / criteria["min_daily_volume"]) * 50)
        
        # 加权计算
        score = (
            aum_score * self.SCORE_WEIGHTS["aum"] +
            expense_score * self.SCORE_WEIGHTS["expense_ratio"] +
            te_score * self.SCORE_WEIGHTS["tracking_error"] +
            vol_score * self.SCORE_WEIGHTS["liquidity"]
        )
        
        return round(score, 1)
    
    def compare_etfs(self, etfs: List[Dict]) -> Dict:
        """
        对比多只 ETF
        
        Args:
            etfs: ETF 列表（2-5 只）
        
        Returns:
            对比结果
        """
        if len(etfs) < 2:
            return {"message": "至少需要 2 只 ETF 进行对比"}
        
        comparison = {
            "etfs": [],
            "best_aum": None,
            "lowest_expense": None,
            "lowest_te": None,
            "highest_liquidity": None,
            "highest_score": None,
        }
        
        for etf in etfs:
            score = self.calculate_score(etf)
            etf_with_score = {**etf, "score": score}
            comparison["etfs"].append(etf_with_score)
            
            # 找出各项最优
            if comparison["best_aum"] is None or etf["aum"] > comparison["best_aum"]["aum"]:
                comparison["best_aum"] = etf_with_score
            if comparison["lowest_expense"] is None or etf["expense_ratio"] < comparison["lowest_expense"]["expense_ratio"]:
                comparison["lowest_expense"] = etf_with_score
            if comparison["lowest_te"] is None or etf.get("tracking_error", 999) < comparison["lowest_te"].get("tracking_error", 999):
                comparison["lowest_te"] = etf_with_score
            if comparison["highest_liquidity"] is None or etf.get("daily_volume", 0) > comparison["highest_liquidity"].get("daily_volume", 0):
                comparison["highest_liquidity"] = etf_with_score
            if comparison["highest_score"] is None or score > comparison["highest_score"]["score"]:
                comparison["highest_score"] = etf_with_score
        
        return comparison
    
    def generate_ranking(self, etfs: List[Dict], top_n: int = 10) -> str:
        """
        生成 ETF 排名列表
        
        Args:
            etfs: ETF 列表
            top_n: 显示前 N 名
        
        Returns:
            格式化排名文本
        """
        lines = []
        lines.append("=" * 80)
        lines.append("ETF 综合评分排名")
        lines.append("=" * 80)
        lines.append("")
        
        lines.append(f"{'排名':<4} {'名称':<15} {'代码':<8} {'规模 (亿)':<10} {'费率':<8} {'跟踪误差':<10} {'成交 (万)':<10} {'评分':<6}")
        lines.append("-" * 80)
        
        for i, etf in enumerate(etfs[:top_n], 1):
            lines.append(
                f"{i:<4} {etf['name']:<15} {etf['code']:<8} "
                f"{etf['aum']:<10.1f} {etf['expense_ratio'] * 100:<7.2f}% "
                f"{etf.get('tracking_error', 0) * 100:<9.2f}% {etf.get('daily_volume', 0):<10.0f} "
                f"{etf['score']:<6.1f}"
            )
        
        lines.append("")
        lines.append("=" * 80)
        
        if etfs:
            best = etfs[0]
            lines.append(f"推荐：{best['name']} ({best['code']})")
            lines.append(f"理由：综合评分 {best['score']} 分，规模 {best['aum']} 亿，费率 {best['expense_ratio'] * 100:.2f}%")
        
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def generate_comparison_report(self, comparison: Dict) -> str:
        """
        生成 ETF 对比报告
        
        Args:
            comparison: 对比结果
        
        Returns:
            格式化报告文本
        """
        lines = []
        lines.append("=" * 80)
        lines.append("ETF 对比分析")
        lines.append("=" * 80)
        lines.append("")
        
        # 列出所有对比 ETF
        lines.append("【对比标的】")
        for i, etf in enumerate(comparison["etfs"], 1):
            lines.append(f"{i}. {etf['name']} ({etf['code']})")
            lines.append(f"   规模：{etf['aum']} 亿 | 费率：{etf['expense_ratio'] * 100:.2f}% | "
                        f"跟踪误差：{etf.get('tracking_error', 0) * 100:.2f}% | "
                        f"成交：{etf.get('daily_volume', 0):.0f} 万 | 评分：{etf['score']}")
        lines.append("")
        
        # 各项最优
        lines.append("【各项最优】")
        if comparison.get("best_aum"):
            lines.append(f"📊 规模最大：{comparison['best_aum']['name']} ({comparison['best_aum']['aum']} 亿)")
        if comparison.get("lowest_expense"):
            lines.append(f"💰 费率最低：{comparison['lowest_expense']['name']} ({comparison['lowest_expense']['expense_ratio'] * 100:.2f}%)")
        if comparison.get("lowest_te"):
            lines.append(f"📈 跟踪误差最小：{comparison['lowest_te']['name']} ({comparison['lowest_te'].get('tracking_error', 0) * 100:.2f}%)")
        if comparison.get("highest_liquidity"):
            lines.append(f"💧 流动性最好：{comparison['highest_liquidity']['name']} ({comparison['highest_liquidity'].get('daily_volume', 0):.0f} 万)")
        lines.append("")
        
        # 综合推荐
        if comparison.get("highest_score"):
            best = comparison["highest_score"]
            lines.append("【综合推荐】")
            lines.append(f"⭐ {best['name']} ({best['code']})")
            lines.append(f"   综合评分：{best['score']} 分")
            lines.append(f"   推荐理由：规模、费率、跟踪误差、流动性综合最优")
        
        lines.append("")
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def get_selection_guide(self, etf_type: str = "wide_base") -> str:
        """
        获取 ETF 选择指南
        
        Args:
            etf_type: ETF 类型
        
        Returns:
            选择指南文本
        """
        criteria = self.SCREENING_CRITERIA.get(etf_type, self.SCREENING_CRITERIA["wide_base"])
        
        type_names = {
            "wide_base": "宽基 ETF",
            "sector": "行业 ETF",
            "thematic": "主题 ETF",
            "cross_border": "跨境 ETF",
        }
        
        lines = []
        lines.append(f"【{type_names.get(etf_type, etf_type)} 选择标准】")
        lines.append("")
        lines.append(f"1. 规模：≥ {criteria['min_aum']} 亿（避免清盘风险）")
        lines.append(f"2. 费率：≤ {criteria['max_expense_ratio'] * 100:.2f}%（越低越好）")
        lines.append(f"3. 跟踪误差：≤ {criteria['max_tracking_error'] * 100:.2f}%（年化）")
        lines.append(f"4. 流动性：日均成交 ≥ {criteria['min_daily_volume']} 万")
        lines.append("")
        lines.append("选择建议：")
        lines.append("- 优先选择规模大、费率低的 ETF")
        lines.append("- 同一指数多只 ETF 时，选择综合评分最高的")
        lines.append("- 避免规模<1 亿的迷你 ETF")
        lines.append("- 跨境 ETF 注意溢价率风险")
        
        return "\n".join(lines)


# 快速测试
if __name__ == "__main__":
    screener = ETFScreener()
    
    etfs = [
        {"name": "沪深 300ETF", "code": "510300", "index": "沪深 300", "aum": 500, "expense_ratio": 0.005, "tracking_error": 0.01, "daily_volume": 5000},
        {"name": "沪深 300ETF 易方达", "code": "510310", "index": "沪深 300", "aum": 150, "expense_ratio": 0.006, "tracking_error": 0.012, "daily_volume": 2000},
        {"name": "沪深 300ETF 嘉实", "code": "510330", "index": "沪深 300", "aum": 80, "expense_ratio": 0.005, "tracking_error": 0.011, "daily_volume": 1500},
        {"name": "中证 500ETF", "code": "510500", "index": "中证 500", "aum": 300, "expense_ratio": 0.005, "tracking_error": 0.015, "daily_volume": 3000},
        {"name": "创业板 ETF", "code": "159915", "index": "创业板", "aum": 200, "expense_ratio": 0.006, "tracking_error": 0.018, "daily_volume": 2500},
    ]
    
    results = screener.screen(etfs, etf_type="wide_base")
    print(screener.generate_ranking(results))
    
    print("\n" + "=" * 80 + "\n")
    
    # 对比前 3 只
    comparison = screener.compare_etfs(results[:3])
    print(screener.generate_comparison_report(comparison))
