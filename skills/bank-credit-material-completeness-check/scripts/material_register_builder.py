#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""根据输入材料列表构建标准化材料台账。"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import json
import sys

DEFAULT_CATEGORY_RULES = {
    "营业执照": "主体资格类",
    "公司章程": "主体资格类",
    "董事会决议": "公司治理与授权类",
    "股东会决议": "公司治理与授权类",
    "授权委托书": "公司治理与授权类",
    "财务报表": "经营与财务类",
    "审计报告": "经营与财务类",
    "纳税": "经营与财务类",
    "流水": "经营与财务类",
    "授信用途": "融资与用途类",
    "融资申请书": "融资与用途类",
    "保证": "担保与押品类",
    "抵押": "担保与押品类",
    "评估报告": "担保与押品类",
    "保险单": "担保与押品类",
    "征信授权": "征信与合规授权类",
    "调查报告": "行内审批流转类",
    "评级": "行内审批流转类",
}


def infer_category(name: str) -> str:
    for keyword, category in DEFAULT_CATEGORY_RULES.items():
        if keyword in name:
            return category
    return "待分类"



def validate_input(items: List[Dict[str, Any]]) -> None:
    """验证输入参数"""
    if not isinstance(items, list):
        raise ValueError("输入必须是列表类型")


def build_register(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    validate_input(items)
    rows: List[Dict[str, Any]] = []
    for idx, item in enumerate(items, start=1):
        name = str(item.get("材料名称", "")).strip()
        row = {
            "序号": idx,
            "材料名称": name,
            "材料类别": item.get("材料类别") or infer_category(name),
            "是否已提供": item.get("是否已提供", "是"),
            "材料日期": item.get("材料日期", ""),
            "是否签章": item.get("是否签章", "待核验"),
            "是否清晰完整": item.get("是否清晰完整", "待核验"),
            "是否在有效期内": item.get("是否在有效期内", "待核验"),
            "是否一致": item.get("是否一致", "待核验"),
            "是否需补件": item.get("是否需补件", "待判断"),
            "备注": item.get("备注", ""),
        }
        rows.append(row)
    return rows



def main() -> None:
    if len(sys.argv) < 3:
        print("用法: python material_register_builder.py 输入.json 输出.json")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    data = json.loads(input_path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("输入文件必须是列表 JSON")

    register = build_register(data)
    output_path.write_text(json.dumps(register, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"已输出材料台账: {output_path}")


if __name__ == "__main__":
    main()
