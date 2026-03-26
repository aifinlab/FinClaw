#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
两融风险计算脚本
用于计算客户维保比例、杠杆倍数等风险指标
"""

from datetime import datetime
import json

def calculate_maintenance_ratio(total_assets: float, total_liabilities: float) -> float:
    """
    计算维保比例

    Args:
        total_assets: 总资产
        total_liabilities: 总负债

    Returns:
        维保比例 (%)
    """
    if total_liabilities == 0:
        return 0
    return round((total_assets / total_liabilities) * 100, 2)

def calculate_leverage_ratio(total_assets: float, equity: float) -> float:
    """
    计算杠杆倍数

    Args:
        total_assets: 总资产
        equity: 自有资金/净资产

    Returns:
        杠杆倍数
    """
    if equity == 0:
        return 0
    return round(total_assets / equity, 2)

def calculate_concentration_ratio(position_value: float, total_assets: float) -> float:
    """
    计算持仓集中度

    Args:
        position_value: 单一证券持仓市值
        total_assets: 总资产

    Returns:
        集中度 (%)
    """
    if total_assets == 0:
        return 0
    return round((position_value / total_assets) * 100, 2)

def evaluate_risk_level(maintenance_ratio: float, leverage_ratio: float,
                        concentration_ratio: float) -> dict:
    """
    评估风险等级

    Args:
        maintenance_ratio: 维保比例
        leverage_ratio: 杠杆倍数
        concentration_ratio: 持仓集中度

    Returns:
        风险评估结果
    """
    risk_score = 0
    risk_factors = []

    # 维保比例评估
    if maintenance_ratio < 120:
        risk_score += 4
        risk_factors.append("维保比例低于平仓线")
    elif maintenance_ratio < 130:
        risk_score += 3
        risk_factors.append("维保比例低于警戒线")
    elif maintenance_ratio < 140:
        risk_score += 2
        risk_factors.append("维保比例低于预警线")
    elif maintenance_ratio < 150:
        risk_score += 1
        risk_factors.append("维保比例偏低")

    # 杠杆倍数评估
    if leverage_ratio > 5:
        risk_score += 3
        risk_factors.append("杠杆倍数过高")
    elif leverage_ratio > 4:
        risk_score += 2
        risk_factors.append("杠杆倍数偏高")
    elif leverage_ratio > 3:
        risk_score += 1
        risk_factors.append("杠杆倍数较高")

    # 集中度评估
    if concentration_ratio > 50:
        risk_score += 3
        risk_factors.append("持仓集中度过高")
    elif concentration_ratio > 40:
        risk_score += 2
        risk_factors.append("持仓集中度偏高")
    elif concentration_ratio > 30:
        risk_score += 1
        risk_factors.append("持仓集中度较高")

    # 风险等级判定
    if risk_score >= 8:
        risk_level = "红色预警"
    elif risk_score >= 5:
        risk_level = "橙色预警"
    elif risk_score >= 3:
        risk_level = "黄色预警"
    else:
        risk_level = "正常"

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "risk_factors": risk_factors,
        "action_required": get_action_required(risk_level)
    }

def get_action_required(risk_level: str) -> str:
    """获取应对措施"""
    actions = {
        "红色预警": "立即追保或减仓，准备平仓",
        "橙色预警": "要求追保，限制新开仓",
        "黄色预警": "发送风险提示，加强监控",
        "正常": "常规监控"
    }
    return actions.get(risk_level, "未知")

def generate_risk_report(client_data: dict) -> dict:
    """
    生成风险报告

    Args:
        client_data: 客户数据字典

    Returns:
        风险报告
    """
    # 计算指标
    maintenance_ratio = calculate_maintenance_ratio(
        client_data.get("total_assets", 0),
        client_data.get("total_liabilities", 0)
    )

    leverage_ratio = calculate_leverage_ratio(
        client_data.get("total_assets", 0),
        client_data.get("equity", 0)
    )

    max_position_ratio = calculate_concentration_ratio(
        client_data.get("max_position_value", 0),
        client_data.get("total_assets", 0)
    )

    # 风险评估
    risk_eval = evaluate_risk_level(maintenance_ratio, leverage_ratio, max_position_ratio)

    # 生成报告
    report = {
        "report_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "client_id": client_data.get("client_id", ""),
        "indicators": {
            "maintenance_ratio": maintenance_ratio,
            "leverage_ratio": leverage_ratio,
            "max_position_ratio": max_position_ratio
        },
        "thresholds": {
            "maintenance_warning": 140,
            "maintenance_alert": 130,
            "maintenance_liquidation": 120
        },
        "risk_evaluation": risk_eval,
        "recommendation": risk_eval["action_required"]
    }

    return report

if __name__ == "__main__":
    # 示例数据
    sample_client = {
        "client_id": "C001",
        "total_assets": 1500000,
        "total_liabilities": 1000000,
        "equity": 500000,
        "max_position_value": 600000
    }

    report = generate_risk_report(sample_client)
    print(json.dumps(report, ensure_ascii=False, indent=2))
