"""资产配置建议引擎（示例）"""
from __future__ import annotations
import json
from typing import Dict, Any, List

BASE_PLANS = {
    "保守型": {"现金": (20, 35), "固收": (45, 65), "权益": (5, 15), "多资产": (0, 10)},
    "稳健型": {"现金": (10, 25), "固收": (40, 60), "权益": (10, 25), "多资产": (5, 15)},
    "平衡型": {"现金": (5, 15), "固收": (30, 50), "权益": (20, 40), "多资产": (10, 20)},
    "成长型": {"现金": (5, 10), "固收": (20, 35), "权益": (35, 55), "多资产": (10, 20)},
    "进取型": {"现金": (0, 10), "固收": (10, 25), "权益": (45, 70), "多资产": (10, 20)},
}

def generate_plan(profile: Dict[str, Any], market_data_ready: bool = False, industry_data_ready: bool = False) -> Dict[str, Any]:
    risk = profile.get("风险等级", "未知")
    complete = profile.get("信息完整度", 0)
    can_high_confidence = market_data_ready and industry_data_ready and complete >= 0.8 and risk in BASE_PLANS

    if risk not in BASE_PLANS:
        return {
            "结论级别": "降级输出",
            "原因": ["客户风险等级未知或无法识别"],
            "建议": "先补充风险测评结果，再生成正式资产配置建议。"
        }

    plan = BASE_PLANS[risk].copy()
    reasons: List[str] = []

    if not can_high_confidence:
        reasons.append("行业数据或市场数据不足，采用保守区间建议。")

    if "高" in str(profile.get("流动性需求", "")):
        c_low, c_high = plan["现金"]
        plan["现金"] = (c_low + 5, c_high + 10)
        reasons.append("客户流动性需求较高，适度提升现金及高流动性资产占比。")

    if "1年" in str(profile.get("投资期限", "")) or "短期" in str(profile.get("投资期限", "")):
        e_low, e_high = plan["权益"]
        plan["权益"] = (max(0, e_low - 10), max(0, e_high - 10))
        reasons.append("客户投资期限偏短，下调权益类配置区间。")

    return {
        "结论级别": "正式建议" if can_high_confidence else "框架建议",
        "配置区间": plan,
        "使用行业数据": industry_data_ready,
        "使用市场数据": market_data_ready,
        "说明": reasons or ["配置区间与客户画像基本匹配。"]
    }

if __name__ == "__main__":
    sample_profile = {
        "风险等级": "平衡型",
        "信息完整度": 0.9,
        "流动性需求": "中等",
        "投资期限": "3年以上"
    }
    result = generate_plan(sample_profile, market_data_ready=True, industry_data_ready=True)
    print(json.dumps(result, ensure_ascii=False, indent=2))
