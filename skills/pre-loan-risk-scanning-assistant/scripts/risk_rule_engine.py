"""贷前风险规则引擎。

基于各维度风险信号数量和关键红旗，输出初步风险等级、红旗列表和建议动作。
"""

from __future__ import annotations

from typing import Dict, List


HIGH_PRIORITY_KEYWORDS = ["当前逾期", "被执行", "伪造", "高优先级", "回流", "多头借贷"]


def flatten_signals(signals: Dict[str, List[str]]) -> List[str]:
    items: List[str] = []
    for arr in signals.values():
        items.extend(arr)
    return items


def extract_red_flags(items: List[str]) -> List[str]:
    red_flags = []
    for item in items:
        if any(keyword in item for keyword in HIGH_PRIORITY_KEYWORDS):
            red_flags.append(item)
    return red_flags


def score_risk_level(signals: Dict[str, List[str]]) -> Dict[str, object]:
    items = flatten_signals(signals)
    red_flags = extract_red_flags(items)
    total = len(items)

    if total == 0:
        level = "低风险"
        action = "当前未发现明显红旗，可进入下一阶段，但仍需按标准流程继续核验。"
    elif len(red_flags) >= 2 or total >= 8:
        level = "高风险"
        action = "存在较明确红旗，建议升级审查、补强核验，必要时谨慎推进。"
    elif len(red_flags) == 1 or total >= 4:
        level = "中风险"
        action = "存在一定风险点，建议补件、访谈或走访后再判断是否进入下一阶段。"
    else:
        level = "低风险"
        action = "存在少量一般风险点，建议常规补充核验。"

    return {
        "preliminary_risk_level": level,
        "red_flags": red_flags,
        "recommended_action": action,
        "signal_count": total,
    }


if __name__ == "__main__":
    demo = {
        "credit": ["近期征信查询次数偏多，存在多头申请或资金紧张可能。", "存在多头借贷迹象，需核验总负债与偿债能力。"],
        "judicial_compliance": ["存在被执行记录，需重点关注司法与履约风险。"],
        "finance": ["经营现金流持续偏弱，需关注还款来源质量。"],
    }
    print(score_risk_level(demo))
