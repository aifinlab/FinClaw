from __future__ import annotations

from typing import Any, Dict


def calibrate_with_industry_data(signals: Dict[str, Any], industry_data: Dict[str, Any]) -> Dict[str, Any]:
    """根据行业数据调整需求洞察置信度。

    若行业数据缺失，则主动降低结论强度。
    """
    has_industry = bool(industry_data)
    result = dict(signals)

    base_confidence = "中"
    if signals.get("标签"):
        base_confidence = "中"
    if len(signals.get("标签", [])) >= 3:
        base_confidence = "较高"

    if not has_industry:
        result["结论强度"] = "中等或偏弱"
        result["说明"] = "缺少行业数据支持，结论主要基于客户内部行为信号，应作为初步经营准备参考。"
    else:
        result["结论强度"] = "中等或较强"
        result["说明"] = "已结合行业数据做初步校准，但仍需通过客户沟通进一步验证。"

    result["基础置信度"] = base_confidence
    return result


if __name__ == "__main__":
    demo = {"标签": ["存在资金承接机会", "可能存在跨境或外币配置需求"]}
    print(calibrate_with_industry_data(demo, {"同类客群偏好": ["美元资产"]}))
