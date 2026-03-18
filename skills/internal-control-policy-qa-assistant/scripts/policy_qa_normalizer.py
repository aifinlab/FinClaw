from __future__ import annotations

import json
import re
import sys
from typing import Any, Dict, List

QUESTION_TYPES = {
    "审批": ["谁审批", "谁来批", "审批", "复核", "授权"],
    "材料": ["材料", "资料", "附件", "证明", "留存"],
    "能否办理": ["能不能", "是否可以", "可否", "能否", "是否允许"],
    "职责": ["谁负责", "职责", "岗位", "分工"],
    "时效": ["多久", "时效", "几天", "期限"],
    "例外": ["例外", "特殊情况", "豁免", "特殊处理"],
}


def detect_question_type(text: str) -> List[str]:
    found: List[str] = []
    for qtype, keywords in QUESTION_TYPES.items():
        if any(k in text for k in keywords):
            found.append(qtype)
    return found or ["一般制度问答"]


def extract_policy_names(text: str) -> List[str]:
    pattern = r"《[^》]{2,60}》"
    return re.findall(pattern, text)


def normalize(payload: Dict[str, Any]) -> Dict[str, Any]:
    question = str(payload.get("question", "")).strip()
    scenario = str(payload.get("scenario", "")).strip()
    policy_text = str(payload.get("policy_text", "")).strip()

    merged = "\n".join([question, scenario, policy_text])

    return {
        "question": question,
        "scenario": scenario,
        "detected_question_types": detect_question_type(merged),
        "mentioned_policies": extract_policy_names(merged),
        "has_policy_text": bool(policy_text),
        "needs_version_check": True,
        "needs_escalation_check": any(word in merged for word in ["冲突", "例外", "处罚", "投诉", "监管"]),
    }


def main() -> None:
    payload = json.load(sys.stdin)
    result = normalize(payload)
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
