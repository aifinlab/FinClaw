#!/usr/bin/env python3
"""将投保问卷文本或 JSON 字段整理为标准化核保初审报告。"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


SECTION_TITLES = [
    "一、问卷基本信息",
    "二、初审结论摘要",
    "三、缺失项清单",
    "四、矛盾项清单",
    "五、高风险表述与风险提示",
    "六、建议补问问题",
    "七、后续处理建议",
]

HEALTH_KEYWORDS = [
    "肿瘤", "癌", "结节", "高血压", "糖尿病", "冠心病", "脑梗", "住院", "手术",
    "复查", "异常", "慢病", "服药", "哮喘", "抑郁", "焦虑", "肝炎", "肾"
]
OCCUPATION_KEYWORDS = [
    "高空", "井下", "危化", "爆破", "建筑", "施工", "船员", "消防", "警务",
    "电力", "机械", "矿", "驾驶", "自由职业", "个体经营"
]
HABIT_KEYWORDS = [
    "吸烟", "抽烟", "饮酒", "喝酒", "潜水", "跳伞", "攀岩", "赛车", "熬夜"
]
BEHAVIOR_KEYWORDS = [
    "拒保", "延期", "加费", "除外", "投保", "累计保额", "高额", "代填", "代答"
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成核保问卷初审报告")
    parser.add_argument("--input", required=True, help="输入文件路径，支持 txt、md、json")
    parser.add_argument(
        "--format",
        choices=["auto", "text", "json"],
        default="auto",
        help="输入格式，默认自动识别",
    )
    return parser.parse_args()


def load_input(path: Path, input_format: str) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8")
    fmt = input_format
    if fmt == "auto":
        fmt = "json" if path.suffix.lower() == ".json" else "text"

    if fmt == "json":
        data = json.loads(raw)
        text = build_text_from_json(data)
        data["_raw_text"] = text
        return data

    return {"questionnaire_text": raw, "_raw_text": raw}


def build_text_from_json(data: dict[str, Any]) -> str:
    fragments: list[str] = []
    for key in [
        "insurance_type",
        "product_name",
        "questionnaire_type",
        "source_type",
        "sum_assured",
        "filled_at",
    ]:
        value = data.get(key)
        if value:
            fragments.append(f"{key}:{value}")
    insured = data.get("insured", {})
    if isinstance(insured, dict):
        for key in ["name", "age", "gender", "occupation"]:
            value = insured.get(key)
            if value not in (None, ""):
                fragments.append(f"insured_{key}:{value}")
    q_text = data.get("questionnaire_text")
    if q_text:
        fragments.append(str(q_text))
    return "\n".join(fragments)


def extract_basic_info(data: dict[str, Any]) -> dict[str, str]:
    insured = data.get("insured", {}) if isinstance(data.get("insured"), dict) else {}
    return {
        "insurance_type": str(data.get("insurance_type") or "未提供"),
        "product_name": str(data.get("product_name") or "未提供"),
        "insured_info": format_insured_info(insured),
        "questionnaire_type": str(data.get("questionnaire_type") or "未提供"),
        "source_type": str(data.get("source_type") or "未明确"),
    }


def format_insured_info(insured: dict[str, Any]) -> str:
    if not insured:
        return "材料中未明确"
    parts = []
    mapping = {"name": "姓名", "age": "年龄", "gender": "性别", "occupation": "职业"}
    for key, label in mapping.items():
        value = insured.get(key)
        if value not in (None, ""):
            parts.append(f"{label}：{value}")
    return "；".join(parts) if parts else "材料中未明确"


def find_missing_items(data: dict[str, Any], text: str) -> list[str]:
    missing = []
    required_pairs = [
        ("insurance_type", "险种类型未提供，无法准确判断问卷审查口径。"),
        ("product_name", "产品名称未提供，无法核对产品对应健康告知背景。"),
        ("questionnaire_type", "问卷类型未提供，无法区分健康、职业或综合告知范围。"),
        ("source_type", "材料来源或文本类型未说明，无法判断识别边界。"),
    ]
    for field, message in required_pairs:
        if not data.get(field):
            missing.append(message)

    insured = data.get("insured", {}) if isinstance(data.get("insured"), dict) else {}
    if not insured.get("age"):
        missing.append("被保人年龄未提供，可能影响健康与投保行为初审判断。")
    if not insured.get("occupation"):
        missing.append("被保人职业未提供，无法判断职业风险等级。")

    fuzzy_patterns = [
        (r"偶尔", "存在“偶尔”等频率不清表述，需补充具体频率和数量。"),
        (r"有|异常|问题", "存在笼统描述但缺少明确诊断或结论，需补充具体情况。"),
    ]
    for pattern, message in fuzzy_patterns:
        if re.search(pattern, text) and message not in missing:
            missing.append(message)
    return missing


def find_contradictions(text: str) -> list[str]:
    contradictions = []
    rules = [
        ("无住院", "住院", "问卷中同时出现“无住院”与“住院”相关表述，需核对既往住院史。"),
        ("无手术", "手术", "问卷中同时出现“无手术”与“手术”相关表述，需核对既往手术史。"),
        ("无慢病", "服药", "问卷写明“无慢病”但又出现长期服药线索，前后可能不一致。"),
        ("无异常", "异常", "问卷既写“无异常”又出现异常检查或体检提示，需进一步核实。"),
    ]
    for left, right, message in rules:
        if left in text and right in text:
            contradictions.append(message)
    return contradictions


def collect_signals(text: str, keywords: list[str]) -> list[str]:
    hits = []
    for keyword in keywords:
        if keyword in text and keyword not in hits:
            hits.append(keyword)
    return hits


def generate_summary(missing: list[str], contradictions: list[str], risk_flags: dict[str, list[str]]) -> list[str]:
    summary = []
    if not missing and not contradictions and all(not v for v in risk_flags.values()):
        summary.append("当前材料未见明显缺失、矛盾或高风险信号，可进入下一环节审查。")
        return summary

    if missing:
        summary.append("当前材料存在影响初审判断的缺失项或模糊表述，需补充说明后再审。")
    if contradictions:
        summary.append("问卷内存在前后不一致信息，建议重点复核并核对原始问卷。")
    if any(risk_flags.values()):
        summary.append("已识别出需进一步核查的风险信号，建议结合补问结果进行人工复核。")
    return summary[:3]


def build_risk_lines(risk_flags: dict[str, list[str]]) -> dict[str, str]:
    labels = {
        "health": "未发现明确健康高风险表述，或当前材料不足以确认。",
        "occupation": "未发现明确职业高风险表述，或职业信息不足。",
        "habit": "未发现明确生活习惯高风险表述，或相关信息不足。",
        "behavior": "未发现明确投保行为高风险表述，或既往投保信息不足。",
    }
    if risk_flags["health"]:
        labels["health"] = f"识别到健康相关风险线索：{', '.join(risk_flags['health'])}。需进一步核查具体诊断、时间及当前状态。"
    if risk_flags["occupation"]:
        labels["occupation"] = f"识别到职业相关风险线索：{', '.join(risk_flags['occupation'])}。需补充岗位职责和作业环境。"
    if risk_flags["habit"]:
        labels["habit"] = f"识别到生活习惯相关风险线索：{', '.join(risk_flags['habit'])}。需补充频率、数量和持续年限。"
    if risk_flags["behavior"]:
        labels["behavior"] = f"识别到投保行为相关风险线索：{', '.join(risk_flags['behavior'])}。建议核查既往投保处理结果及当前累计保额。"
    return labels


def generate_followup_questions(risk_flags: dict[str, list[str]], missing: list[str]) -> list[str]:
    questions = []
    if risk_flags["health"] or any("诊断" in item or "异常" in item for item in missing):
        questions.append("请补充既往异常检查、住院或疾病情况的具体诊断名称、发现时间、治疗经过及最近一次复查结果。")
    if risk_flags["occupation"] or any("职业" in item for item in missing):
        questions.append("请说明当前职业的具体岗位、主要工作内容、是否涉及高空、井下、危化品、机械操作或夜间高风险作业。")
    if risk_flags["habit"] or any("频率不清" in item for item in missing):
        questions.append("请补充吸烟、饮酒或危险活动的频率、数量、持续年限及最近一次发生时间。")
    if risk_flags["behavior"] or "投保" in "".join(missing):
        questions.append("请补充既往投保公司、险种、处理结果，以及是否存在拒保、延期、加费或责任除外记录。")
    if not questions:
        questions.append("当前材料未见明确补问方向，如需流转作业，可结合原件再做人工抽查。")
    return questions


def generate_next_steps(missing: list[str], contradictions: list[str], risk_flags: dict[str, list[str]]) -> list[str]:
    steps = []
    if missing:
        steps.append("建议补充说明缺失项及模糊表述后再进行下一步审查。")
    if contradictions:
        steps.append("建议核对原始问卷或业务系统记录，确认前后冲突内容。")
    if any(risk_flags.values()):
        steps.append("建议就高风险信号补问或补件，并进入人工复核。")
    if not steps:
        steps.append("当前可进入下一环节审查。")
    steps.append("本结果仅用于首轮初审与风险分流，不替代正式核保决定。")
    return steps


def render_report(data: dict[str, Any]) -> str:
    text = data.get("_raw_text", "")
    basic_info = extract_basic_info(data)
    missing = find_missing_items(data, text)
    contradictions = find_contradictions(text)
    risk_flags = {
        "health": collect_signals(text, HEALTH_KEYWORDS),
        "occupation": collect_signals(text, OCCUPATION_KEYWORDS),
        "habit": collect_signals(text, HABIT_KEYWORDS),
        "behavior": collect_signals(text, BEHAVIOR_KEYWORDS),
    }
    summary = generate_summary(missing, contradictions, risk_flags)
    risk_lines = build_risk_lines(risk_flags)
    followups = generate_followup_questions(risk_flags, missing)
    next_steps = generate_next_steps(missing, contradictions, risk_flags)

    lines = [
        "# 核保问卷初审结果",
        "",
        SECTION_TITLES[0],
        f"- 险种/产品：{basic_info['insurance_type']} / {basic_info['product_name']}",
        f"- 被保人基本信息：{basic_info['insured_info']}",
        f"- 问卷类型：{basic_info['questionnaire_type']}",
        f"- 材料来源或文本类型：{basic_info['source_type']}",
        "",
        SECTION_TITLES[1],
    ]
    lines.extend(f"- {item}" for item in summary)
    lines.extend(["", SECTION_TITLES[2]])
    lines.extend(f"- {item}" for item in (missing or ["未识别到明显缺失项。"]))
    lines.extend(["", SECTION_TITLES[3]])
    lines.extend(f"- {item}" for item in (contradictions or ["未识别到明确矛盾项。"]))
    lines.extend(
        [
            "",
            SECTION_TITLES[4],
            f"- 健康风险：{risk_lines['health']}",
            f"- 职业风险：{risk_lines['occupation']}",
            f"- 生活习惯风险：{risk_lines['habit']}",
            f"- 投保行为风险：{risk_lines['behavior']}",
            "",
            SECTION_TITLES[5],
        ]
    )
    lines.extend(f"- {item}" for item in followups)
    lines.extend(["", SECTION_TITLES[6]])
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
