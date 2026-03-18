#!/usr/bin/env python3
"""将寿险投保问卷整理为标准化分析报告。"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


RISK_TOPICS = {
    "健康风险": ["高血压", "糖尿病", "住院", "手术", "长期服药", "服药", "心脑血管", "病史"],
    "职业风险": ["高空", "施工", "外勤", "驾驶", "出差", "危险", "暴露"],
    "保额风险": ["保额", "高额", "累计保额", "重复投保"],
    "行为风险": ["拒保", "延期", "加费", "除外", "保单", "投保", "投保目的"],
    "生活习惯风险": ["吸烟", "饮酒", "BMI", "体重"],
}

SUMMARY_FLAGS = [
    "高血压", "长期服药", "吸烟", "饮酒", "外勤", "驾驶", "出差", "保额", "保单", "延期"
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成寿险问卷分析报告")
    parser.add_argument("--input", required=True, help="输入文件路径，支持 txt、md、json")
    parser.add_argument("--format", choices=["auto", "text", "json"], default="auto")
    return parser.parse_args()


def load_input(path: Path, input_format: str) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8")
    fmt = input_format
    if fmt == "auto":
        fmt = "json" if path.suffix.lower() == ".json" else "text"
    if fmt == "json":
        data = json.loads(raw)
        data["_raw_text"] = build_text_from_json(data)
        return data
    return {"questionnaire_text": raw, "_raw_text": raw}


def build_text_from_json(data: dict[str, Any]) -> str:
    parts: list[str] = []
    for key in ["insurance_type", "product_name", "questionnaire_type", "source_type", "questionnaire_text"]:
        value = data.get(key)
        if value:
            parts.append(str(value))
    notes = data.get("notes")
    if isinstance(notes, list):
        parts.extend(str(item) for item in notes if item)
    insured = data.get("insured", {})
    if isinstance(insured, dict):
        parts.extend(str(v) for v in insured.values() if v not in (None, ""))
    return "\n".join(parts)


def extract_basic_info(data: dict[str, Any]) -> dict[str, str]:
    insured = data.get("insured", {}) if isinstance(data.get("insured"), dict) else {}
    insured_parts = []
    for key, label in [("name", "姓名"), ("age", "年龄"), ("gender", "性别"), ("occupation", "职业")]:
        value = insured.get(key)
        if value not in (None, ""):
            insured_parts.append(f"{label}：{value}")
    return {
        "insurance_type": str(data.get("insurance_type") or "未提供"),
        "product_name": str(data.get("product_name") or "未提供"),
        "insured_info": "；".join(insured_parts) if insured_parts else "材料中未明确",
        "questionnaire_type": str(data.get("questionnaire_type") or "未提供"),
        "source_type": str(data.get("source_type") or "未明确"),
    }


def collect_topic_risks(text: str) -> list[str]:
    findings = []
    for topic, keywords in RISK_TOPICS.items():
        hits = [keyword for keyword in keywords if keyword in text]
        if hits:
            findings.append(f"{topic}：识别到 {('、'.join(hits))} 相关线索，需结合时间、程度、频率或匹配情况进一步判断。")
    return findings


def extract_health_points(text: str) -> list[str]:
    points = []
    mapping = [
        ("病史", "问卷涉及既往病史线索，需核实疾病名称、诊断时间及当前状态。"),
        ("住院", "问卷涉及住院或手术线索，需核实原因、诊断和恢复情况。"),
        ("服药", "问卷涉及长期服药或慢病管理线索，需核实药物名称、时长和控制情况。"),
        ("吸烟", "问卷涉及吸烟线索，需核实年限、频率和数量。"),
        ("饮酒", "问卷涉及饮酒线索，需核实频率和饮酒量。"),
        ("体重", "问卷涉及体重或 BMI 线索，需核实体重情况及是否存在异常。"),
    ]
    for keyword, message in mapping:
        if keyword in text:
            points.append(message)
    return list(dict.fromkeys(points))


def build_matching_section(text: str) -> list[str]:
    lines = []
    if "保额" in text and "收入" in text:
        lines.append("问卷同时存在保额与收入线索，但两者是否匹配仍需结合具体金额进一步核实。")
    elif "保额" in text:
        lines.append("已披露投保金额或保额线索，但收入信息不足，当前无法直接判断保障匹配性。")
    else:
        lines.append("材料中未见明确保额信息，无法判断保障配置水平。")

    if any(word in text for word in ["家庭责任", "家属", "子女", "房贷"]):
        lines.append("问卷存在家庭责任相关线索，可作为保障需求背景参考，但仍需结合具体负担情况判断。")
    else:
        lines.append("材料中未见明确家庭责任说明，保障需求合理性判断依据有限。")

    if any(word in text for word in ["多份", "保单", "重复投保", "累计保额"]):
        lines.append("存在既往保单或重复投保线索，建议补充累计保额和既往投保分布后再判断高额配置风险。")
    else:
        lines.append("材料中未见明确既有保单分布信息，无法完整评估高额保障配置问题。")
    return lines


def build_summary(text: str, topic_risks: list[str]) -> list[str]:
    summary = []
    if topic_risks:
        summary.append("已识别出需重点关注的健康、职业或投保合理性风险，建议结合补问或补件进一步判断。")
    else:
        summary.append("当前未见明确高关注寿险风险事实，但仍需结合材料完整度审视。")
    if any(word in text for word in ["高血压", "服药", "吸烟", "饮酒", "外勤", "驾驶", "出差"]):
        summary.append("问卷中存在健康、生活习惯或职业暴露线索，建议重点核实持续时间、频率和当前状态。")
    if any(word in text for word in ["保额", "保单", "延期", "拒保", "收入"]):
        summary.append("问卷中存在高额投保、既往投保或收入匹配性线索，建议进一步核实保障合理性。")
    return summary[:3]


def build_followups(text: str) -> list[str]:
    questions = []
    if any(word in text for word in ["高血压", "糖尿病", "住院", "手术", "服药", "病史"]):
        questions.append("请补充既往病史或长期治疗情况，包括诊断名称、发现时间、治疗经过、当前控制状态及最近一次复查结果。")
    if any(word in text for word in ["吸烟", "饮酒", "体重", "BMI"]):
        questions.append("请补充吸烟饮酒习惯或体重情况，包括持续年限、频率、数量及当前状态。")
    if any(word in text for word in ["外勤", "驾驶", "出差", "危险", "高空", "施工"]):
        questions.append("请补充当前职业职责、外勤或出差频率、驾驶情况以及是否涉及危险作业或特殊暴露。")
    if any(word in text for word in ["保额", "高额", "保单", "重复投保", "投保", "延期", "拒保", "收入"]):
        questions.append("请补充本次保额、既往保单、累计保额、收入水平、投保目的及是否存在拒保、延期、加费或除外记录。")
    if not questions:
        questions.append("当前材料未见明确补问方向，建议核对原件后再做人工审查。")
    return questions


def build_next_steps(text: str, topic_risks: list[str]) -> list[str]:
    steps = []
    if topic_risks or any(word in text for word in SUMMARY_FLAGS):
        steps.append("建议补充说明关键健康风险、职业风险、投保行为和收入匹配情况后再做进一步判断。")
    if any(word in text for word in ["高血压", "长期服药", "吸烟", "饮酒", "保额", "保单", "延期", "拒保", "收入"]):
        steps.append("建议补充收入说明、既往保单信息、职业说明或复查资料摘要等相关材料。")
        steps.append("建议重点人工审核，并进一步核实收入、保额配置、职业分级或健康风险。")
    if not steps:
        steps.append("当前可进入下一环节核保审查。")
    steps.append("本结果仅用于寿险问卷分析与补问准备，不替代正式核保决定。")
    return steps


def render_report(data: dict[str, Any]) -> str:
    text = data.get("_raw_text", "")
    basic = extract_basic_info(data)
    topic_risks = collect_topic_risks(text)
    health_points = extract_health_points(text)
    summary = build_summary(text, topic_risks)
    followups = build_followups(text)
    next_steps = build_next_steps(text, topic_risks)
    matching = build_matching_section(text)

    abnormal_items = topic_risks or ["当前未识别到明确健康高风险、职业高风险或投保行为异常线索，或材料不足以确认。"]

    focus_lines = []
    if any(word in text for word in SUMMARY_FLAGS):
        focus_lines.append("问卷存在健康异常、生活习惯风险、职业暴露或高额投保等高关注线索，需进一步核实频率、程度和匹配关系。")
    if "未说明" in text or "不明确" in text or "较高" in text:
        focus_lines.append("部分健康、职业或投保信息表述不完整，当前不足以支持完整寿险核保判断。")
    if not focus_lines:
        focus_lines.append("当前未见明确高关注寿险风险信号，但仍需结合原件和材料完整度复核。")

    lines = [
        "# 寿险问卷分析结果",
        "",
        "一、问卷基本信息",
        f"- 险种/产品：{basic['insurance_type']} / {basic['product_name']}",
        f"- 被保人基本信息：{basic['insured_info']}",
        f"- 问卷类型：{basic['questionnaire_type']}",
        f"- 材料来源或文本类型：{basic['source_type']}",
        "",
        "二、寿险核保结论摘要",
    ]
    lines.extend(f"- {item}" for item in summary)
    lines.extend([
        "",
        "三、健康与生活习惯要点提取",
    ])
    lines.extend(f"- {item}" for item in (health_points or ["当前可确认的健康与生活习惯要点有限，建议核对原始问卷。"]))
    lines.extend([
        "",
        "四、职业风险与投保行为识别",
    ])
    lines.extend(f"- {item}" for item in abnormal_items)
    lines.extend([
        "",
        "五、收入与保障匹配情况梳理",
    ])
    lines.extend(f"- {item}" for item in matching)
    lines.extend([
        "",
        "六、高风险信号与核保关注点",
    ])
    lines.extend(f"- {item}" for item in focus_lines)
    lines.extend([
        "",
        "七、建议补充核实的问题",
    ])
    lines.extend(f"- {item}" for item in followups)
    lines.extend([
        "",
        "八、后续处理建议",
    ])
    lines.extend(f"- {item}" for item in next_steps)
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    path = Path(args.input)
    if not path.exists():
        print(f"输入文件不存在：{path}", file=sys.stderr)
        return 1
    data = load_input(path, args.format)
    print(render_report(data))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
