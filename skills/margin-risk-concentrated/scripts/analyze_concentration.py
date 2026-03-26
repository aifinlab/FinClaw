#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
持仓集中度分析脚本
用于分析客户持仓集中度风险
"""

from datetime import datetime
import json

def calculate_hhi_index(positions: list) -> float:
    """
    计算赫芬达尔指数 (HHI)
    HHI = Σ(市场份额)^2

    Args:
        positions: 持仓列表 [{'name': '股票 A', 'value': 100000}, ...]

    Returns:
        HHI 指数 (0-10000)
    """
    total_value = sum(p['value'] for p in positions)
    if total_value == 0:
        return 0

    hhi = sum((p['value'] / total_value) ** 2 for p in positions)
    return round(hhi * 10000, 2)

def analyze_top_holdings(positions: list, top_n: int = 5) -> dict:
    """
    分析前 N 大持仓

    Args:
        positions: 持仓列表
        top_n: 前 N 大

    Returns:
        分析结果
    """
    # 按市值排序
    sorted_positions = sorted(positions, key=lambda x: x['value'], reverse=True)
    total_value = sum(p['value'] for p in positions)

    top_holdings = []
    cumulative_ratio = 0

    for i, pos in enumerate(sorted_positions[:top_n]):
        ratio = round((pos['value'] / total_value) * 100, 2) if total_value else 0
        cumulative_ratio += ratio
        top_holdings.append({
            "rank": i + 1,
            "name": pos['name'],
            "value": pos['value'],
            "ratio": ratio,
            "cumulative_ratio": round(cumulative_ratio, 2)
        })

    return {
        "top_holdings": top_holdings,
        "top_n_ratio": cumulative_ratio,
        "total_positions": len(positions)
    }

def analyze_industry_concentration(positions: list) -> dict:
    """
    分析行业集中度

    Args:
        positions: 持仓列表 [{'name': '股票 A', 'value': 100000, 'industry': '金融'}, ...]

    Returns:
        行业集中度分析
    """
    industry_values = {}

    for pos in positions:
        industry = pos.get('industry', '其他')
        industry_values[industry] = industry_values.get(industry, 0) + pos['value']

    total_value = sum(industry_values.values())

    industry_ratios = []
    for industry, value in sorted(industry_values.items(), key=lambda x: x[1], reverse=True):
        ratio = round((value / total_value) * 100, 2) if total_value else 0
        industry_ratios.append({
            "industry": industry,
            "value": value,
            "ratio": ratio
        })

    return {
        "industry_distribution": industry_ratios,
        "top_industry": industry_ratios[0] if industry_ratios else None,
        "industry_count": len(industry_ratios)
    }

def evaluate_concentration_risk(top_ratio: float, hhi: float,
                                 industry_count: int) -> dict:
    """
    评估集中度风险

    Args:
        top_ratio: 前三持仓占比
        hhi: HHI 指数
        industry_count: 行业数量

    Returns:
        风险评估
    """
    risk_score = 0
    risk_factors = []

    # 前三持仓占比评估
    if top_ratio > 70:
        risk_score += 3
        risk_factors.append("前三持仓占比超过 70%")
    elif top_ratio > 60:
        risk_score += 2
        risk_factors.append("前三持仓占比偏高")
    elif top_ratio > 50:
        risk_score += 1
        risk_factors.append("前三持仓占比较高")

    # HHI 指数评估
    if hhi > 2500:
        risk_score += 3
        risk_factors.append("HHI 指数显示高度集中")
    elif hhi > 1500:
        risk_score += 2
        risk_factors.append("HHI 指数显示中度集中")
    elif hhi > 1000:
        risk_score += 1
        risk_factors.append("HHI 指数显示低度集中")

    # 行业分散度评估
    if industry_count < 2:
        risk_score += 2
        risk_factors.append("行业过于集中")
    elif industry_count < 3:
        risk_score += 1
        risk_factors.append("行业分散度不足")

    # 风险等级
    if risk_score >= 6:
        risk_level = "高风险"
    elif risk_score >= 4:
        risk_level = "中风险"
    else:
        risk_level = "低风险"

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "risk_factors": risk_factors,
        "recommendation": get_recommendation(risk_level)
    }

def get_recommendation(risk_level: str) -> str:
    """获取建议"""
    recommendations = {
        "高风险": "建议立即分散持仓，降低集中度",
        "中风险": "建议适当分散持仓，关注集中度变化",
        "低风险": "持仓分散度良好，继续保持"
    }
    return recommendations.get(risk_level, "")

def generate_concentration_report(positions: list) -> dict:
    """
    生成集中度分析报告

    Args:
        positions: 持仓列表

    Returns:
        分析报告
    """
    # 前 N 大持仓分析
    top_analysis = analyze_top_holdings(positions, 5)

    # 行业集中度分析
    industry_analysis = analyze_industry_concentration(positions)

    # HHI 指数
    hhi = calculate_hhi_index(positions)

    # 风险评估
    risk_eval = evaluate_concentration_risk(
        top_analysis['top_n_ratio'],
        hhi,
        industry_analysis['industry_count']
    )

    report = {
        "report_date": datetime.now().strftime("%Y-%m-%d"),
        "portfolio_summary": {
            "total_value": sum(p['value'] for p in positions),
            "position_count": len(positions),
            "hhi_index": hhi
        },
        "top_holdings_analysis": top_analysis,
        "industry_analysis": industry_analysis,
        "risk_evaluation": risk_eval
    }

    return report

if __name__ == "__main__":
    # 示例数据
    sample_positions = [
        {"name": "股票 A", "value": 300000, "industry": "金融"},
        {"name": "股票 B", "value": 250000, "industry": "金融"},
        {"name": "股票 C", "value": 200000, "industry": "科技"},
        {"name": "股票 D", "value": 150000, "industry": "消费"},
        {"name": "股票 E", "value": 100000, "industry": "医药"}
    ]

    report = generate_concentration_report(sample_positions)
    print(json.dumps(report, ensure_ascii=False, indent=2))
