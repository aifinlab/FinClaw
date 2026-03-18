#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""跨表勾稽校验示例脚本。
输入：JSON，格式：
{
  "left": [{"key": "贷款余额", "value": 100}],
  "right": [{"key": "贷款余额", "value": 95}]
}
"""

from __future__ import annotations
import json
import sys
from typing import Dict, List, Any


def to_map(items: List[Dict[str, Any]]) -> Dict[str, float]:
    out: Dict[str, float] = {}
    for item in items:
        key = str(item.get("key", "")).strip()
        try:
            val = float(item.get("value", 0))
        except Exception:
            val = 0.0
        if key:
            out[key] = val
    return out


def main() -> None:
    payload = json.load(sys.stdin)
    left = to_map(payload.get("left", []))
    right = to_map(payload.get("right", []))

    issues = []
    for key in sorted(set(left) | set(right)):
        lv = left.get(key)
        rv = right.get(key)
        if lv is None or rv is None:
            issues.append({
                "issue_id": f"R-{key}",
                "issue_type": "跨表缺项",
                "field": key,
                "severity": "P1",
                "evidence": f"指标 {key} 仅在一侧表中存在",
                "status": "已确认",
            })
            continue
        if abs(lv - rv) > 0.0001:
            issues.append({
                "issue_id": f"R-{key}",
                "issue_type": "跨表不一致",
                "field": key,
                "severity": "P1",
                "evidence": f"左表={lv}, 右表={rv}, 差异={lv-rv}",
                "status": "已确认",
            })

    json.dump(issues, sys.stdout, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
