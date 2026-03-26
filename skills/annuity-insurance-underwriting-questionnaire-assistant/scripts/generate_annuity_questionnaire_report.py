#!/usr/bin/env python3
"""将年金险投保问卷整理为标准化分析报告。"""

from __future__ import annotations

from pathlib import Path
from typing import Any
import argparse
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




RISK_TOPICS = {
    "健康风险": ["病史", "住院", "手术", "长期用药", "复查", "吸烟", "饮酒", "结节"],
    "缴费能力风险": ["保费", "趸交", "期交", "缴费", "收入", "支付能力"],
    "资金来源风险": ["资金来源", "资产", "家庭资产", "代缴"],
    "投保行为风险": ["保单", "投保目的", "集中投保", "重复投保", "代理投保"],
}

SUMMARY_FLAGS = [
    "结节", "复查", "保费", "趸交", "收入", "资金来源", "保单", "投保目的"
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成年金险问卷分析报告")
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
            findings.append(f"{topic}：识别到 {('、'.join(hits))} 相关线索，需结合时间、金额、来源或当前状态进一步判断。")
    return findings


def extract_health_points(text: str) -> list[str]:
    points = []
    mapping = [
        ("病史", "问卷涉及既往病史线索，需核实疾病名称、诊断时间及当前状态。"),
        ("住院", "问卷涉及住院或手术线索，需核实原因、诊断和恢复情况。"),
        ("长期用药", "问卷涉及长期用药或慢病管理线索，需核实药物名称、时长和控制情况。"),
        ("复查", "问卷涉及持续复查线索，需核实最新结果和当前状态。"),
        ("吸烟", "问卷涉及吸烟线索，需核实年限、频率和数量。"),
        ("饮酒", "问卷涉及饮酒线索，需核实频率和饮酒量。"),
        ("职业", "问卷涉及职业暴露线索，需结合工作环境判断基础风险。"),
    ]
    for keyword, message in mapping:
        if keyword in text:
            points.append(message)
    return list(dict.fromkeys(points))


def build_configuration_section(text: str) -> list[str]:
    lines = []
    if any(word in text for word in ["保单", "长期储蓄", "年金险", "寿险"]):
        lines.append("材料存在既有保单或长期储蓄类配置线索，但累计配置和结构是否合理仍需进一步核实。")
    else:
        lines.append("材料中未见明确既有保单信息，无法完整评估现有保障与储蓄配置。")

    if any(word in text for word in ["重复投保", "集中投保", "多份"]):
        lines.append("存在重复配置或集中投保线索，需补充累计缴费压力和配置目的。")
    else:
        lines.append("当前未见明确重复配置线索，但配置结构仍需结合既有保单情况判断。")

    if any(word in text for word in ["资产配置", "养老", "教育金", "财富传承"]):
        lines.append("已披露部分投保目的，但仍需结合缴费能力和长期规划判断是否合理。")
    else:
        lines.append("投保目的说明不足，配置合理性判断依据有限。")
    return lines


def build_summary(text: str, topic_risks: list[str]) -> list[str]:
    summary = []
    if topic_risks:
        summary.append("已识别出需重点关注的健康、缴费能力或投保合理性风险，建议结合补问或补件进一步判断。")
    else:
        summary.append("当前未见明确高关注年金险风险事实，但仍需结合材料完整度审视。")
    if any(word in text for word in ["保费", "趸交", "收入", "资金来源", "保单", "投保目的"]):
        summary.append("问卷中存在高额保费、资金来源或配置合理性线索，建议重点核实支付能力和资金来源。")
    if any(word in text for word in ["病史", "复查", "结节", "长期用药"]):
        summary.append("问卷中存在健康异常或持续管理线索，建议结合健康风险与财务安排一并复核。")
    return summary[:3]


def build_followups(text: str) -> list[str]:
    questions = []
    if any(word in text for word in ["病史", "住院", "手术", "长期用药", "复查", "结节"]):
        questions.append("请补充既往病史或长期治疗情况，包括诊断名称、发现时间、治疗经过、当前控制状态及最近一次复查结果。")
    if any(word in text for word in ["保费", "趸交", "期交", "缴费", "收入", "支付能力"]):
        questions.append("请补充本次保费安排、缴费年限、收入水平、可持续缴费能力及是否存在其他长期缴费负担。")
    if any(word in text for word in ["资金来源", "资产", "家庭资产", "代缴"]):
        questions.append("请补充资金来源、出资主体、是否为本人资金以及相关资产或现金流支持情况。")
    if any(word in text for word in ["保单", "长期储蓄", "重复投保", "投保目的", "资产配置"]):
        questions.append("请补充既有保单类型、累计缴费情况、本次投保目的、配置规划以及是否存在短期集中投保安排。")
    if not questions:
        questions.append("当前材料未见明确补问方向，建议核对原件后再做人工审查。")
    return questions


def build_next_steps(text: str, topic_risks: list[str]) -> list[str]:
    steps = []
    if topic_risks or any(word in text for word in SUMMARY_FLAGS):
        steps.append("建议补充说明关键健康风险、缴费能力、资金来源和投保配置情况后再做进一步判断。")
    if any(word in text for word in ["保费", "趸交", "收入", "资金来源", "保单", "投保目的", "复查", "结节"]):
        steps.append("建议补充收入或资产说明、资金来源说明、既有保单信息或健康复查资料摘要等相关材料。")
        steps.append("建议重点人工审核，并进一步核实收入、资产、资金来源、保费安排或健康风险。")
    if not steps:
        steps.append("当前可进入下一环节核保审查。")
    steps.append("本结果仅用于年金险问卷分析与补问准备，不替代正式核保决定。")
    return steps


def render_report(data: dict[str, Any]) -> str:
    text = data.get("_raw_text", "")
    basic = extract_basic_info(data)
    topic_risks = collect_topic_risks(text)
    health_points = extract_health_points(text)
    summary = build_summary(text, topic_risks)
    followups = build_followups(text)
    next_steps = build_next_steps(text, topic_risks)
    configuration = build_configuration_section(text)

    abnormal_items = topic_risks or ["当前未识别到明确健康高风险、缴费能力风险或投保行为异常线索，或材料不足以确认。"]

    focus_lines = []
    if any(word in text for word in SUMMARY_FLAGS):
        focus_lines.append("问卷存在健康异常、高额保费、资金来源或配置合理性等高关注线索，需进一步核实金额、来源和长期承担能力。")
    if "未说明" in text or "不明确" in text or "较高" in text:
        focus_lines.append("部分健康、保费或投保信息表述不完整，当前不足以支持完整年金险核保判断。")
    if not focus_lines:
        focus_lines.append("当前未见明确高关注年金险风险信号，但仍需结合原件和材料完整度复核。")

    lines = [
        "# 年金险问卷分析结果",
        "",
        "一、问卷基本信息",
        f"- 险种/产品：{basic['insurance_type']} / {basic['product_name']}",
        f"- 被保人基本信息：{basic['insured_info']}",
        f"- 问卷类型：{basic['questionnaire_type']}",
        f"- 材料来源或文本类型：{basic['source_type']}",
        "",
        "二、年金险核保结论摘要",
    ]
    lines.extend(f"- {item}" for item in summary)
    lines.extend([
        "",
        "三、健康与基本风险要点提取",
    ])
    lines.extend(f"- {item}" for item in (health_points or ["当前可确认的健康与基本风险要点有限，建议核对原始问卷。"]))
    lines.extend([
        "",
        "四、缴费能力与投保行为识别",
    ])
    lines.extend(f"- {item}" for item in abnormal_items)
    lines.extend([
        "",
        "五、既有保障与配置情况梳理",
    ])
    lines.extend(f"- {item}" for item in configuration)
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
