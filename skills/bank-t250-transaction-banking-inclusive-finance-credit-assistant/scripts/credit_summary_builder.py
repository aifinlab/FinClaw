#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
普惠授信摘要结构化生成脚本

用法:
  python credit_summary_builder.py --input assets/credit_input.json --format markdown --output outputs/credit_summary.md
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import argparse
import json


@dataclass
class ClientProfile:
    name: str = ""
    credit_code: str = ""
    legal_rep: str = ""
    controller: str = ""
    industry: str = ""
    main_business: str = ""


@dataclass
class FinancingRequest:
    amount: str = ""
    term: str = ""
    purpose: str = ""
    repayment_source: str = ""
    product_preferences: List[str] = field(default_factory=list)


@dataclass
class MaterialItem:
    name: str
    status: str
    owner: str = ""
    note: str = ""
    priority: str = "中"


@dataclass
class SummaryPayload:
    client_profile: ClientProfile = field(default_factory=ClientProfile)
    business_flow: Dict[str, Any] = field(default_factory=dict)
    financing_request: FinancingRequest = field(default_factory=FinancingRequest)
    materials: List[MaterialItem] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    follow_up: List[str] = field(default_factory=list)
    output_type: str = "summary"
    confirmed: List[str] = field(default_factory=list)
    to_verify: List[str] = field(default_factory=list)


DEFAULT_REQUIRED_MATERIALS = [
    "税票",
    "近12个月流水",
    "订单合同",
    "票据/保理材料",
    "物流或验收证明",
    "上游/下游客户清单",
    "主营业务说明",
]


def parse_payload(raw: Dict[str, Any]) -> SummaryPayload:
    client_raw = raw.get("client_profile", {})
    financing_raw = raw.get("financing_request", {})
    materials_raw = raw.get("materials", [])

    materials: List[MaterialItem] = []
    for item in materials_raw:
        if isinstance(item, dict):
            materials.append(
                MaterialItem(
                    name=str(item.get("name", "")),
                    status=str(item.get("status", "")),
                    owner=str(item.get("owner", "")),
                    note=str(item.get("note", "")),
                    priority=str(item.get("priority", "中")),
                )
            )
        else:
            materials.append(MaterialItem(name=str(item), status="待核验"))

    return SummaryPayload(
        client_profile=ClientProfile(
            name=str(client_raw.get("name", "")),
            credit_code=str(client_raw.get("credit_code", "")),
            legal_rep=str(client_raw.get("legal_rep", "")),
            controller=str(client_raw.get("controller", "")),
            industry=str(client_raw.get("industry", "")),
            main_business=str(client_raw.get("main_business", "")),
        ),
        business_flow=raw.get("business_flow", {}),
        financing_request=FinancingRequest(
            amount=str(financing_raw.get("amount", "")),
            term=str(financing_raw.get("term", "")),
            purpose=str(financing_raw.get("purpose", "")),
            repayment_source=str(financing_raw.get("repayment_source", "")),
            product_preferences=list(financing_raw.get("product_preferences", []) or []),
        ),
        materials=materials,
        risks=list(raw.get("risks", []) or []),
        follow_up=list(raw.get("follow_up", []) or []),
        output_type=str(raw.get("output_type", "summary")),
        confirmed=list(raw.get("confirmed", []) or []),
        to_verify=list(raw.get("to_verify", []) or []),
    )


def detect_missing_materials(materials: List[MaterialItem]) -> List[MaterialItem]:
    existing_names = {item.name for item in materials if item.name}
    missing = []
    for required in DEFAULT_REQUIRED_MATERIALS:
        if required not in existing_names:
            missing.append(
                MaterialItem(name=required, status="缺失", owner="", note="需补充", priority="高")
            )
    return missing


def summarize_materials(materials: List[MaterialItem]) -> Dict[str, List[MaterialItem]]:
    summary = {"已提供": [], "待核验": [], "缺失": []}
    for item in materials:
        status = item.status or "待核验"
        if "缺" in status:
            summary["缺失"].append(item)
        elif "已" in status or "齐" in status:
            summary["已提供"].append(item)
        else:
            summary["待核验"].append(item)
    return summary


def build_markdown(payload: SummaryPayload) -> str:
    materials = payload.materials + detect_missing_materials(payload.materials)
    material_summary = summarize_materials(materials)

    lines = []
    lines.append(f"# 普惠授信摘要 ({payload.output_type})")
    lines.append("")
    lines.append("## 客户主体信息")
    lines.append(f"- 客户名称: {payload.client_profile.name}")
    lines.append(f"- 统一社会信用代码: {payload.client_profile.credit_code}")
    lines.append(f"- 法人代表: {payload.client_profile.legal_rep}")
    lines.append(f"- 实控人: {payload.client_profile.controller}")
    lines.append(f"- 行业: {payload.client_profile.industry}")
    lines.append(f"- 主营业务: {payload.client_profile.main_business}")
    lines.append("")

    lines.append("## 交易链路与资金流")
    if payload.business_flow:
        for key, value in payload.business_flow.items():
            lines.append(f"- {key}: {value}")
    else:
        lines.append("- 待补充交易链路/资金流信息")
    lines.append("")

    lines.append("## 融资诉求")
    lines.append(f"- 金额: {payload.financing_request.amount}")
    lines.append(f"- 期限: {payload.financing_request.term}")
    lines.append(f"- 用途: {payload.financing_request.purpose}")
    lines.append(f"- 还款来源: {payload.financing_request.repayment_source}")
    if payload.financing_request.product_preferences:
        lines.append("- 产品偏好: " + " / ".join(payload.financing_request.product_preferences))
    lines.append("")

    lines.append("## 已确认信息")
    if payload.confirmed:
        for item in payload.confirmed:
            lines.append(f"- {item}")
    else:
        lines.append("- 待补充已确认信息")
    lines.append("")

    lines.append("## 待核验信息")
    if payload.to_verify:
        for item in payload.to_verify:
            lines.append(f"- {item}")
    else:
        lines.append("- 暂无")
    lines.append("")

    lines.append("## 材料核验与补件清单")
    for label in ["已提供", "待核验", "缺失"]:
        lines.append(f"### {label}")
        items = material_summary.get(label, [])
        if not items:
            lines.append("- 暂无")
        else:
            for item in items:
                note = f"（{item.priority}优先级" + (f"，责任人: {item.owner}" if item.owner else "") + ")"
                if item.note:
                    note = note + f" {item.note}"
                lines.append(f"- {item.name}: {item.status} {note}")
    lines.append("")

    lines.append("## 风险提示")
    if payload.risks:
        for risk in payload.risks:
            lines.append(f"- {risk}")
    else:
        lines.append("- 暂无明确风险提示")
    lines.append("")

    lines.append("## 后续动作")
    if payload.follow_up:
        for action in payload.follow_up:
            lines.append(f"- {action}")
    else:
        lines.append("- 待补充后续动作")
    lines.append("")
    lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    return "\n".join(lines)


def build_json(payload: SummaryPayload) -> Dict[str, Any]:
    materials = payload.materials + detect_missing_materials(payload.materials)
    material_summary = summarize_materials(materials)

    return {
        "output_type": payload.output_type,
        "client_profile": payload.client_profile.__dict__,
        "business_flow": payload.business_flow,
        "financing_request": payload.financing_request.__dict__,
        "confirmed": payload.confirmed,
        "to_verify": payload.to_verify,
        "materials": {
            key: [item.__dict__ for item in value] for key, value in material_summary.items()
        },
        "risks": payload.risks,
        "follow_up": payload.follow_up,
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
    parser = argparse.ArgumentParser(description="普惠授信摘要结构化生成脚本")
    parser.add_argument("--input", required=True, help="输入 JSON 文件路径")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--output", required=True, help="输出文件路径")

    args = parser.parse_args()
    input_path = Path(args.input)
    payload = parse_payload(read_json(input_path))

    if args.format == "json":
        output = build_json(payload)
        write_json(Path(args.output), output)
    else:
        output = build_markdown(payload)
        write_output(Path(args.output), output)


if __name__ == "__main__":
    main()
