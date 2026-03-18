#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
债券尽调财务指标计算脚本
用于计算发行人的关键财务指标和偿债能力指标
"""

import json
from datetime import datetime

def calculate_liquidity_ratios(current_assets: float, current_liabilities: float, 
                                inventory: float = 0, cash: float = 0) -> dict:
    """
    计算短期偿债能力指标
    
    Args:
        current_assets: 流动资产
        current_liabilities: 流动负债
        inventory: 存货
        cash: 货币资金
    
    Returns:
        指标字典
    """
    results = {
        "current_ratio": round(current_assets / current_liabilities, 2) if current_liabilities else 0,
        "quick_ratio": round((current_assets - inventory) / current_liabilities, 2) if current_liabilities else 0,
        "cash_ratio": round(cash / current_liabilities, 2) if current_liabilities else 0
    }
    return results

def calculate_leverage_ratios(total_assets: float, total_liabilities: float,
                               equity: float, interest_expense: float,
                               ebitda: float) -> dict:
    """
    计算长期偿债能力指标
    
    Args:
        total_assets: 总资产
        total_liabilities: 总负债
        equity: 所有者权益
        interest_expense: 利息费用
        ebitda: 息税折旧摊销前利润
    
    Returns:
        指标字典
    """
    results = {
        "asset_liability_ratio": round(total_liabilities / total_assets * 100, 2) if total_assets else 0,
        "equity_ratio": round(equity / total_assets * 100, 2) if total_assets else 0,
        "interest_coverage": round(ebitda / interest_expense, 2) if interest_expense else 0,
        "debt_to_ebitda": round(total_liabilities / ebitda, 2) if ebitda else 0
    }
    return results

def evaluate_credit_risk(ratios: dict) -> dict:
    """
    评估信用风险等级
    
    Args:
        ratios: 财务指标字典
    
    Returns:
        风险评估结果
    """
    risk_score = 0
    risk_factors = []
    
    # 资产负债率评估
    alr = ratios.get("asset_liability_ratio", 0)
    if alr > 70:
        risk_score += 3
        risk_factors.append("资产负债率超过 70%")
    elif alr > 60:
        risk_score += 2
        risk_factors.append("资产负债率较高")
    
    # 流动比率评估
    cr = ratios.get("current_ratio", 0)
    if cr < 1:
        risk_score += 3
        risk_factors.append("流动比率低于 1，短期偿债压力大")
    elif cr < 1.5:
        risk_score += 2
        risk_factors.append("流动比率偏低")
    
    # 利息保障倍数评估
    ic = ratios.get("interest_coverage", 0)
    if ic < 2:
        risk_score += 3
        risk_factors.append("利息保障倍数低于 2")
    elif ic < 3:
        risk_score += 2
        risk_factors.append("利息保障倍数偏低")
    
    # 风险等级判定
    if risk_score >= 8:
        risk_level = "高风险"
    elif risk_score >= 5:
        risk_level = "中风险"
    else:
        risk_level = "低风险"
    
    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "risk_factors": risk_factors
    }

def generate_report(financial_data: dict) -> dict:
    """
    生成财务分析报告
    
    Args:
        financial_data: 财务数据字典
    
    Returns:
        分析报告
    """
    # 计算短期偿债能力
    liquidity = calculate_liquidity_ratios(
        financial_data.get("current_assets", 0),
        financial_data.get("current_liabilities", 0),
        financial_data.get("inventory", 0),
        financial_data.get("cash", 0)
    )
    
    # 计算长期偿债能力
    leverage = calculate_leverage_ratios(
        financial_data.get("total_assets", 0),
        financial_data.get("total_liabilities", 0),
        financial_data.get("equity", 0),
        financial_data.get("interest_expense", 0),
        financial_data.get("ebitda", 0)
    )
    
    # 合并指标
    all_ratios = {**liquidity, **leverage}
    
    # 风险评估
    risk_eval = evaluate_credit_risk(all_ratios)
    
    report = {
        "report_date": datetime.now().strftime("%Y-%m-%d"),
        "liquidity_ratios": liquidity,
        "leverage_ratios": leverage,
        "risk_evaluation": risk_eval,
        "recommendation": "建议关注" if risk_eval["risk_score"] >= 5 else "风险可控"
    }
    
    return report

if __name__ == "__main__":
    # 示例数据
    sample_data = {
        "current_assets": 100000,
        "current_liabilities": 80000,
        "inventory": 30000,
        "cash": 20000,
        "total_assets": 200000,
        "total_liabilities": 150000,
        "equity": 50000,
        "interest_expense": 5000,
        "ebitda": 20000
    }
    
    report = generate_report(sample_data)
    print(json.dumps(report, ensure_ascii=False, indent=2))
