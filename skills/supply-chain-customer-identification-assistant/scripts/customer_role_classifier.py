#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""根据企业与交易特征对供应链客户角色进行初步分类。"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict, List


def classify_role(item: Dict[str, Any]) -> Dict[str, Any]:
    role_hints = " ".join(
        str(item.get(k, "")) for k in ["主营业务", "合作说明", "客户描述", "关键词"]
    )
    text = role_hints.lower()

    role = "待识别"
    if any(x in text for x in ["供应", "原料", "零部件", "采购"]):
        role = "上游供应商"
    elif any(x in text for x in ["经销", "分销", "渠道", "销售"]):
        role = "下游销售客户"
    elif any(x in text for x in ["物流", "运输", "仓储", "配送"]):
        role = "物流/仓储服务方"
    elif any(x in text for x in ["安装", "维保", "服务", "外包"]):
        role = "配套服务方"

    cooperation_years = float(item.get("合作年限", 0) or 0)
    tx_count = int(item.get("交易笔数", 0) or 0)

    stability = "一般"
    if cooperation_years >= 3 and tx_count >= 12:
        stability = "较稳定"
    elif cooperation_years < 1 or tx_count < 3:
        stability = "较弱"

    return {
        "客户名称": item.get("客户名称", ""),
        "客户角色": role,
        "合作稳定性": stability,
        "证据摘要": item.get("合作说明", ""),
    }


def main() -> None:
    data = json.load(sys.stdin)
    items: List[Dict[str, Any]] = data if isinstance(data, list) else data.get("items", [])
    result = [classify_role(x) for x in items]
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
