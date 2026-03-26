#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""对供应链交易资料进行轻量规则核验。"""

from __future__ import annotations

from typing import Any, Dict, List
import json
import sys


REQUIRED_DOCS = ["合同", "订单", "发票", "物流", "回款"]


def check_item(item: Dict[str, Any]) -> Dict[str, Any]:
    docs = item.get("资料", {}) or {}
    present = {k: bool(docs.get(k)) for k in REQUIRED_DOCS}
    score = sum(1 for v in present.values() if v)

    if score >= 4:
        closure = "闭环较完整"
    elif score >= 3:
        closure = "闭环基本成立"
    elif score >= 2:
        closure = "闭环证据不足"
    else:
        closure = "闭环存在明显缺口"

    risks: List[str] = []
    if not present["物流"] and present["发票"]:
        risks.append("有票缺物流")
    if not present["回款"] and present["合同"]:
        risks.append("缺少结算证明")
    if item.get("金额波动异常"):
        risks.append("金额异常跳变")
    if item.get("疑似关联交易"):
        risks.append("疑似关联交易")

    return {
        "客户名称": item.get("客户名称", ""),
        "交易闭环状态": closure,
        "资料完备度得分": score,
        "缺失资料": [k for k, v in present.items() if not v],
        "风险标签": risks,
    }


def main() -> None:
    data = json.load(sys.stdin)
    items: List[Dict[str, Any]] = data if isinstance(data, list) else data.get("items", [])
    result = [check_item(x) for x in items]
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
