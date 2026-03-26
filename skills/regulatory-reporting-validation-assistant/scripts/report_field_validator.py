#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""监管报送字段校验脚本。
输入：JSON 数组，每行表示一条记录。
输出：发现的字段问题列表。
"""

from __future__ import annotations
from typing import Any, Dict, List
import json
import sys

REQUIRED_FIELDS = ["report_name", "period", "field_name", "value"]


def validate_record(record: Dict[str, Any], idx: int) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []
    for f in REQUIRED_FIELDS:
        if f not in record or record.get(f) in (None, ""):
            issues.append({
                "issue_id": f"F-{idx}-{f}",
                "issue_type": "字段缺失",
                "field": f,
                "severity": "P1",
                "evidence": f"第 {idx} 条记录缺少字段 {f}",
                "status": "已确认",
            })

    value = record.get("value")
    if isinstance(value, str) and value.strip().upper() in {"N/A", "NULL", "-", "NONE"}:
        issues.append({
            "issue_id": f"F-{idx}-placeholder",
            "issue_type": "占位值异常",
            "field": record.get("field_name", "unknown"),
            "severity": "P2",
            "evidence": f"字段值使用占位值 {value}",
            "status": "已确认",
        })

    return issues


def main() -> None:
    data = json.load(sys.stdin)
    if not isinstance(data, list):
        raise SystemExit("输入必须是 JSON 数组")

    results: List[Dict[str, Any]] = []
    for idx, item in enumerate(data, start=1):
        if isinstance(item, dict):
            results.extend(validate_record(item, idx))

    json.dump(results, sys.stdout, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
