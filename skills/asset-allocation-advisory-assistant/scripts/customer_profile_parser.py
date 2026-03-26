"""客户画像标准化脚本（示例）"""
from __future__ import annotations
from typing import Any, Dict, List
import json

RISK_MAP = {
    "保守型": 1,
    "稳健型": 2,
    "平衡型": 3,
    "成长型": 4,
    "进取型": 5,
}

def normalize_customer_profile(payload: Dict[str, Any]) -> Dict[str, Any]:
    """将客户输入信息整理为标准结构。"""
    profile = {
        "客户姓名": payload.get("客户姓名", ""),
        "客户类型": payload.get("客户类型", "零售客户"),
        "年龄": payload.get("年龄"),
        "风险等级": payload.get("风险等级", "未知"),
        "风险等级数值": RISK_MAP.get(payload.get("风险等级", ""), 0),
        "投资期限": payload.get("投资期限", "未提供"),
        "流动性需求": payload.get("流动性需求", "未提供"),
        "收益目标": payload.get("收益目标", "未提供"),
        "总资产规模": payload.get("总资产规模"),
        "现有持仓": payload.get("现有持仓", []),
        "特殊约束": payload.get("特殊约束", []),
    }
    profile["信息完整度"] = _calc_completeness(profile)
    return profile

def _calc_completeness(profile: Dict[str, Any]) -> float:
    required_keys = ["风险等级", "投资期限", "流动性需求", "收益目标", "现有持仓"]
    score = 0
    for key in required_keys:
        value = profile.get(key)
        if value not in (None, "", [], "未知", "未提供"):
            score += 1
    return round(score / len(required_keys), 2)

if __name__ == "__main__":
    sample = {
        "客户姓名": "张某",
        "客户类型": "财富客户",
        "年龄": 42,
        "风险等级": "平衡型",
        "投资期限": "3年以上",
        "流动性需求": "中等",
        "收益目标": "稳健增值",
        "总资产规模": 5000000,
        "现有持仓": [
            {"资产类型": "存款", "占比": 0.45},
            {"资产类型": "固收理财", "占比": 0.35},
            {"资产类型": "权益基金", "占比": 0.20},
        ],
        "特殊约束": ["未来1年需预留子女教育资金"],
    }
    print(json.dumps(normalize_customer_profile(sample), ensure_ascii=False, indent=2))
