#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""对不同材料抽取出的关键字段进行一致性检查。"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List

KEY_FIELDS = [
    "企业名称",
    "统一社会信用代码",
    "法定代表人",
    "注册资本",
    "注册地址",
    "成立日期",
    "授信金额",
    "授信用途",
    "保证人名称",
    "抵押物权属人",
]


def check_consistency(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    field_values: Dict[str, List[Dict[str, str]]] = defaultdict(list)

    for record in records:
        source = str(record.get("材料名称", "未命名材料"))
        for field in KEY_FIELDS:
            value = str(record.get(field, "")).strip()
            if value:
                field_values[field].append({"材料名称": source, "字段值": value})

    result = {"一致字段": [], "不一致字段": [], "待核验字段": []}

    for field in KEY_FIELDS:
        values = field_values.get(field, [])
        unique_values = sorted({item["字段值"] for item in values if item["字段值"]})
        if not values:
            result["待核验字段"].append({"字段": field, "说明": "未提取到有效值"})
        elif len(unique_values) == 1:
            result["一致字段"].append({"字段": field, "字段值": unique_values[0], "来源": values})
        else:
            result["不一致字段"].append({"字段": field, "候选值": unique_values, "来源": values})

    return result



def main() -> None:
    if len(sys.argv) < 3:
        print("用法: python document_consistency_checker.py 输入.json 输出.json")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    records = json.loads(input_path.read_text(encoding="utf-8"))
    if not isinstance(records, list):
        raise ValueError("输入文件必须是列表 JSON")

    result = check_consistency(records)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"已输出一致性检查结果: {output_path}")


if __name__ == "__main__":
    main()
