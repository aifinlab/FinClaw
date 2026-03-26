#!/usr/bin/env python3
"""将医疗险投保问卷整理为标准化分析报告。"""

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
    "既往症风险": ["既往", "病史", "结节", "慢病", "高血压", "糖尿病"],
    "当前治疗风险": ["服药", "治疗", "观察", "康复", "恢复中"],
    "住院/手术风险": ["住院", "出院", "手术", "术后"],
    "检查异常": ["异常", "彩超", "CT", "MRI", "影像", "化验", "指标"],
}

VISIT_KEYWORDS = {
    "门诊情况": ["门诊", "复诊", "就诊"],
    "住院情况": ["住院", "出院"],
    "手术情况": ["手术", "切除", "术后"],
    "出院恢复情况": ["恢复", "康复", "术后", "出院后"],
    "复查复诊安排": ["复查", "复诊", "随访"],
    "当前是否仍在治疗或观察中": ["服药", "治疗", "观察", "恢复中"],
}

HIGH_RISK_WORDS = [
    "住院", "手术", "术后", "复查", "复诊", "服药", "治疗", "观察", "异常", "恢复中"
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成医疗险问卷分析报告")
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
            findings.append(f"{topic}：识别到 {('、'.join(hits))} 相关线索，需结合时间、原因、结果和当前状态进一步判断。")
    return findings


def extract_key_points(text: str) -> list[str]:
    points = []
    mapping = [
        ("门诊", "问卷涉及门诊或复诊线索，需核实就诊频次、原因及最近一次结论。"),
        ("住院", "问卷涉及住院线索，需核实住院原因、诊断及出院结论。"),
        ("手术", "问卷涉及手术线索，需核实手术名称、时间及术后恢复情况。"),
        ("复查", "问卷涉及复查或随访线索，需核实复查安排和最新结果。"),
        ("服药", "问卷涉及当前服药或治疗线索，需核实药物名称、时长及控制情况。"),
        ("观察", "问卷显示当前仍在观察中，需核实是否已结案。"),
        ("异常", "问卷存在检查异常线索，需核实具体项目和结论。"),
    ]
    for keyword, message in mapping:
        if keyword in text:
            points.append(message)
    return list(dict.fromkeys(points))


def collect_visit_info(text: str) -> dict[str, str]:
    result = {}
    for title, keywords in VISIT_KEYWORDS.items():
        hits = [keyword for keyword in keywords if keyword in text]
        result[title] = f"识别到 {('、'.join(hits))} 相关线索，需结合具体时间、原因和结论核实。" if hits else "未见明确相关信息，或当前材料不足以确认。"
    return result


def build_summary(text: str, topic_risks: list[str]) -> list[str]:
    summary = []
    if topic_risks:
        summary.append("已识别出需重点关注的既往症、当前治疗或近期医疗异常，建议结合补问或补件进一步判断。")
    else:
        summary.append("当前未见明确高关注医疗风险事实，但仍需结合材料完整度审视。")
    if any(word in text for word in ["住院", "手术", "复查", "复诊", "服药", "观察", "恢复中"]):
        summary.append("问卷中存在近期就医、治疗或复查线索，建议重点核实是否仍处于未结案状态。")
    if any(word in text for word in HIGH_RISK_WORDS):
        summary.append("存在可能显著影响医疗险核保判断的高风险医疗信号，建议补问、补件或重点人工审核。")
    return summary[:3]


def build_followups(text: str) -> list[str]:
    questions = []
    if any(word in text for word in ["住院", "出院"]):
        questions.append("请补充住院时间、住院原因、明确诊断、治疗经过、出院结论及当前恢复情况。")
    if any(word in text for word in ["手术", "术后"]):
        questions.append("请补充手术名称、手术时间、术后结论、是否存在并发症及目前恢复状态。")
    if any(word in text for word in ["门诊", "复诊", "复查", "随访"]):
        questions.append("请补充最近一次门诊或复查时间、就诊科室、检查项目及最新结论。")
    if any(word in text for word in ["服药", "治疗", "观察", "恢复中"]):
        questions.append("请补充当前治疗或观察对应的疾病问题、药物名称、治疗时长、当前控制情况及是否仍需继续治疗。")
    if any(word in text for word in ["异常", "彩超", "CT", "MRI", "影像", "化验", "指标"]):
        questions.append("请补充异常检查项目名称、检查时间、异常程度、医生意见及是否已完成后续复查。")
    if not questions:
        questions.append("当前材料未见明确补问方向，建议核对原件后再做人工审查。")
    return questions


def build_next_steps(text: str, topic_risks: list[str]) -> list[str]:
    steps = []
    if topic_risks or any(word in text for word in ["复查", "异常", "住院", "手术", "治疗", "观察"]):
        steps.append("建议补充说明关键既往症、就医经过、检查异常或治疗状态后再做进一步判断。")
    if any(word in text for word in ["住院", "手术", "复查", "服药", "治疗", "异常", "恢复中"]):
        steps.append("建议补充门诊记录、出院小结、影像或检验结果、复查报告等相关材料。")
        steps.append("建议重点人工审核，并结合门诊、住院、影像、检验等资料进一步判断。")
    if not steps:
        steps.append("当前可进入下一环节核保审查。")
    steps.append("本结果仅用于医疗险问卷分析与补问准备，不替代正式核保决定。")
    return steps


def render_report(data: dict[str, Any]) -> str:
    text = data.get("_raw_text", "")
    basic = extract_basic_info(data)
    topic_risks = collect_topic_risks(text)
    key_points = extract_key_points(text)
    visits = collect_visit_info(text)
    summary = build_summary(text, topic_risks)
    followups = build_followups(text)
    next_steps = build_next_steps(text, topic_risks)

    abnormal_items = topic_risks or ["当前未识别到明确既往症、当前治疗风险或高风险就医线索，或材料不足以确认。"]

    focus_lines = []
    if any(word in text for word in HIGH_RISK_WORDS):
        focus_lines.append("问卷存在近期住院、手术、持续治疗、复查或检查异常等高关注线索，需进一步核实是否仍处于未结案或持续治疗状态。")
    if "未说明" in text or "不明确" in text or "待查" in text:
        focus_lines.append("部分医疗信息表述不完整，当前不足以支持完整医疗险核保判断。")
    if not focus_lines:
        focus_lines.append("当前未见明确高关注医疗信号，但仍需结合原件和材料完整度复核。")

    lines = [
        "# 医疗险问卷分析结果",
        "",
        "一、问卷基本信息",
        f"- 险种/产品：{basic['insurance_type']} / {basic['product_name']}",
        f"- 被保人基本信息：{basic['insured_info']}",
        f"- 问卷类型：{basic['questionnaire_type']}",
        f"- 材料来源或文本类型：{basic['source_type']}",
        "",
        "二、医疗险核保结论摘要",
    ]
    lines.extend(f"- {item}" for item in summary)
    lines.extend([
        "",
        "三、医疗相关健康告知要点提取",
    ])
    lines.extend(f"- {item}" for item in (key_points or ["当前可确认的医疗相关健康告知要点有限，建议核对原始问卷。"]))
    lines.extend([
        "",
        "四、既往症与当前治疗情况识别",
    ])
    lines.extend(f"- {item}" for item in abnormal_items)
    lines.extend([
        "",
        "五、就医与住院情况梳理",
        f"- 门诊情况：{visits['门诊情况']}",
        f"- 住院情况：{visits['住院情况']}",
        f"- 手术情况：{visits['手术情况']}",
        f"- 出院恢复情况：{visits['出院恢复情况']}",
        f"- 复查复诊安排：{visits['复查复诊安排']}",
        f"- 当前是否仍在治疗或观察中：{visits['当前是否仍在治疗或观察中']}",
        "",
        "六、高风险医疗信号与核保关注点",
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
