from __future__ import annotations

from typing import Any, Dict, List
import json
import sys

POSITIVE = ["可以", "应当", "允许", "须", "必须"]
NEGATIVE = ["不得", "禁止", "不可", "不应", "严禁"]


def sentence_signal(text: str) -> str:
    pos = sum(1 for w in POSITIVE if w in text)
    neg = sum(1 for w in NEGATIVE if w in text)
    if neg > pos:
        return "限制/禁止"
    if pos > neg:
        return "允许/要求"
    return "中性/不明确"


def check_conflicts(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    results = []
    signals = set()
    for item in items:
        content = str(item.get("content", ""))
        sig = sentence_signal(content)
        signals.add(sig)
        results.append({
            "source": item.get("source", "未命名来源"),
            "signal": sig,
            "content": content,
        })
    has_conflict = "允许/要求" in signals and "限制/禁止" in signals
    return {
        "has_conflict": has_conflict,
        "results": results,
        "recommendation": "建议升级确认" if has_conflict else "可继续结合场景解释",
    }


def main() -> None:
    payload = json.load(sys.stdin)
    items = payload.get("items", [])
    result = check_conflicts(items)
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
