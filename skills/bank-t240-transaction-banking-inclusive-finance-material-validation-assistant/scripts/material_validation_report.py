#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
普惠材料核验报告生成脚本

用法:
  python material_validation_report.py --input assets/materials.json --format markdown --output outputs/material_validation.md
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
import argparse
import json


@dataclass
class MaterialItem:
    name: str
    status: str
    source: str = ""
    note: str = ""
    severity: str = "一般"
    action: str = "待核验"


@dataclass
class ValidationPayload:
    client_profile: Dict[str, Any] = field(default_factory=dict)
    materials: List[MaterialItem] = field(default_factory=list)
    required_fields: List[str] = field(default_factory=list)
    cross_checks: List[str] = field(default_factory=list)
    period: str = ""
    confirmed: List[str] = field(default_factory=list)
    to_verify: List[str] = field(default_factory=list)


DEFAULT_REQUIRED_FIELDS = [
    "主体名称",
    "统一社会信用代码",
    "近12个月流水",
    "税票或发票",
    "合同或订单",
    "物流或验收证明",
]


def parse_payload(raw: Dict[str, Any]) -> ValidationPayload:
    materials_raw = raw.get("materials", [])
    materials: List[MaterialItem] = []
    for item in materials_raw:
        if isinstance(item, dict):
            materials.append(
                MaterialItem(
                    name=str(item.get("name", "")),
                    status=str(item.get("status", "待核验")),
                    source=str(item.get("source", "")),
                    note=str(item.get("note", "")),
                    severity=str(item.get("severity", "一般")),
                    action=str(item.get("action", "待核验")),
                )
            )
        else:
            materials.append(MaterialItem(name=str(item), status="待核验"))

    return ValidationPayload(
        client_profile=dict(raw.get("client_profile", {}) or {}),
        materials=materials,
        required_fields=list(raw.get("required_fields", []) or []),
        cross_checks=list(raw.get("cross_checks", []) or []),
        period=str(raw.get("period", "")),
        confirmed=list(raw.get("confirmed", []) or []),
        to_verify=list(raw.get("to_verify", []) or []),
    )


def build_missing_fields(payload: ValidationPayload) -> List[str]:
    required = payload.required_fields or DEFAULT_REQUIRED_FIELDS
    present = {item.name for item in payload.materials if item.name}
    return [field for field in required if field not in present]


def summarize_materials(payload: ValidationPayload) -> Dict[str, List[MaterialItem]]:
    summary = {"已提供": [], "待核验": [], "异常": []}
    for item in payload.materials:
        status = item.status or "待核验"
        if "异常" in status or "缺" in status:
            summary["异常"].append(item)
        elif "已" in status or "齐" in status:
            summary["已提供"].append(item)
        else:
            summary["待核验"].append(item)
    return summary


def build_markdown(payload: ValidationPayload) -> str:
    summary = summarize_materials(payload)
    missing_fields = build_missing_fields(payload)

    lines: List[str] = []
    lines.append("# 普惠材料核验报告")
    lines.append("")
    lines.append("## 基本信息概览")
    lines.append(f"- 核验期间: {payload.period or '待补充'}")
    for key, value in payload.client_profile.items():
        lines.append(f"- {key}: {value}")
    lines.append("")

    lines.append("## 核验结论")
    if summary["异常"]:
        lines.append("- 结论等级: 重点关注")
        lines.append(f"- 异常项数量: {len(summary['异常'])}")
    else:
        lines.append("- 结论等级: 正常")
        lines.append("- 异常项数量: 0")
    lines.append("")

    lines.append("## 异常项清单")
    if not summary["异常"]:
        lines.append("- 暂无")
    else:
        for item in summary["异常"]:
            lines.append(
                f"- {item.name}: {item.status} | 严重度: {item.severity} | 建议动作: {item.action}"
            )
    lines.append("")

    lines.append("## 待核验与补件清单")
    if missing_fields:
        for field in missing_fields:
            lines.append(f"- {field}: 缺失，需补充")
    else:
        lines.append("- 必备字段已覆盖")
    lines.append("")

    lines.append("## 待核验信息")
    if payload.to_verify:
        for item in payload.to_verify:
            lines.append(f"- {item}")
    else:
        lines.append("- 暂无")
    lines.append("")

    lines.append("## 已确认信息")
    if payload.confirmed:
        for item in payload.confirmed:
            lines.append(f"- {item}")
    else:
        lines.append("- 待补充")
    lines.append("")

    lines.append("## 跨材料一致性关注点")
    if payload.cross_checks:
        for rule in payload.cross_checks:
            lines.append(f"- {rule}")
    else:
        lines.append("- 暂无")
    lines.append("")
    lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    return "\n".join(lines)


def build_json(payload: ValidationPayload) -> Dict[str, Any]:
    return {
        "client_profile": payload.client_profile,
        "period": payload.period,
        "summary": {
            "materials": {
                key: [item.__dict__ for item in value]
                for key, value in summarize_materials(payload).items()
            },
            "missing_fields": build_missing_fields(payload),
        },
        "confirmed": payload.confirmed,
        "to_verify": payload.to_verify,
        "cross_checks": payload.cross_checks,
        "generated_at": datetime.now().isoformat(timespec="minutes"),
    }


def read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_output(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, content: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(content, file, ensure_ascii=False, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(description="普惠材料核验报告生成脚本")
    parser.add_argument("--input", required=True, help="输入 JSON 文件路径")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--output", required=True, help="输出文件路径")
    args = parser.parse_args()

    payload = parse_payload(read_json(Path(args.input)))
    if args.format == "json":
        write_json(Path(args.output), build_json(payload))
    else:
        write_output(Path(args.output), build_markdown(payload))


if __name__ == "__main__":
    main()
