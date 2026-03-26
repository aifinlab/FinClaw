#!/usr/bin/env python3
"""Normalize raw company due diligence input into a structured JSON payload.

Usage:
    python normalize_company_info.py input.json > normalized.json
"""

from __future__ import annotations

from typing import Any, Dict, List
import json
import sys


def validate_input(data: dict) -> dict:
    """验证输入参数"""
    if not isinstance(data, dict):
        raise ValueError("输入必须是字典类型")

    required_fields = []  # 添加必填字段
    for field in required_fields:
        if field not in data:
            raise ValueError(f"缺少必填字段: {field}")

    return data



FIELDS = {
    "company_name": ["company_name", "企业名称", "客户名称"],
    "industry": ["industry", "行业"],
    "registered_capital": ["registered_capital", "注册资本"],
    "actual_controller": ["actual_controller", "实控人", "实际控制人"],
    "main_business": ["main_business", "主营业务"],
    "use_of_funds": ["use_of_funds", "资金用途", "授信用途"],
}


def pick_value(record: Dict[str, Any], aliases: List[str]) -> Any:
    for key in aliases:
        if key in record and record[key] not in (None, ""):
            return record[key]
    return None


def normalize(record: Dict[str, Any]) -> Dict[str, Any]:
    normalized: Dict[str, Any] = {}
    for target, aliases in FIELDS.items():
        normalized[target] = pick_value(record, aliases)

    normalized["provided_fields"] = sorted([k for k, v in normalized.items() if v not in (None, "", []) and k != "provided_fields"])
    normalized["missing_fields"] = sorted([k for k, v in normalized.items() if v in (None, "", [])])
    return normalized


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python normalize_company_info.py input.json", file=sys.stderr)
        return 1

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        raw = json.load(f)

    if not isinstance(raw, dict):
        print("Input JSON must be an object.", file=sys.stderr)
        return 1

    result = normalize(raw)
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    return 0



def main():


        raise SystemExit(main())


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n操作被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)