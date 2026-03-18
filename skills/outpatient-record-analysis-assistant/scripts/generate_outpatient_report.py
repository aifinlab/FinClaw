#!/usr/bin/env python3
"""将门诊资料整理为标准化解析结果。"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


RISK_TOPICS = {
    "明确诊断": ["诊断", "糖代谢异常", "高血压", "糖尿病", "结节"],
    "持续症状": ["反复", "持续", "加重", "乏力", "口渴", "症状"],
    "复诊频繁": ["复诊", "两次", "多次", "随访"],
    "治疗持续中": ["药物治疗", "口服药物", "治疗", "观察", "继续随访"],
    "待排查问题": ["建议进一步检查", "待查", "未明确", "考虑"],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成门诊记录解析报告")
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
    return {"record_text": raw, "_raw_text": raw}


def build_text_from_json(data: dict[str, Any]) -> str:
    parts: list[str] = []
    for key in ["visit_date", "department", "institution", "source_type", "record_text"]:
        value = data.get(key)
        if value:
            parts.append(str(value))
    notes = data.get("notes")
    if isinstance(notes, list):
        parts.extend(str(item) for item in notes if item)
    patient = data.get("patient", {})
    if isinstance(patient, dict):
        parts.extend(str(v) for v in patient.values() if v not in (None, ""))
    return "\n".join(parts)


def extract_basic_info(data: dict[str, Any]) -> dict[str, str]:
    patient = data.get("patient", {}) if isinstance(data.get("patient"), dict) else {}
    patient_parts = []
    for key, label in [("name", "姓名"), ("age", "年龄"), ("gender", "性别")]:
        value = patient.get(key)
        if value not in (None, ""):
            patient_parts.append(f"{label}：{value}")
    return {
        "patient_info": "；".join(patient_parts) if patient_parts else "材料中未明确",
        "visit_date": str(data.get("visit_date") or "未提供"),
        "institution": str(data.get("institution") or "未提供"),
        "department": str(data.get("department") or "未明确"),
        "source_type": str(data.get("source_type") or "未明确"),
    }


def collect_topic_risks(text: str) -> list[str]:
    findings = []
    for topic, keywords in RISK_TOPICS.items():
        hits = [keyword for keyword in keywords if keyword in text]
        if hits:
            findings.append(f"{topic}：识别到 {('、'.join(hits))} 相关线索，需结合病程、检查结果和后续处置进一步判断。")
    return findings


def extract_key_points(text: str) -> list[str]:
    points = []
    mapping = [
        ("主诉", "资料包含主诉线索，需结合症状持续时间和变化判断病情活动性。"),
        ("现病史", "资料包含现病史线索，需关注起病经过和病程演变。"),
        ("考虑", "资料存在临床判断或待排查问题，提示诊断可能尚未完全明确。"),
        ("建议", "资料包含检查或复诊建议，需关注是否已完成后续检查。"),
    ]
    for keyword, message in mapping:
        if keyword in text:
            points.append(message)
    if any(word in text for word in ["乏力", "口渴", "血糖升高"]):
        points.append("资料明确存在症状与代谢异常线索，需结合复诊情况和检查结果综合判断。")
    return list(dict.fromkeys(points))


def build_activity_lines(text: str) -> list[str]:
    lines = []
    if any(word in text for word in ["复诊", "两次", "多次"]):
        lines.append("资料显示存在多次复诊线索，提示问题可能并非一次性、短暂性事件。")
    if any(word in text for word in ["持续", "反复", "近三个月", "近两个月"]):
        lines.append("症状或问题持续存在一段时间，提示病情可能仍处于活动期或观察期。")
    if any(word in text for word in ["随访", "慢病", "长期"]):
        lines.append("资料显示存在随访或持续管理线索，需关注是否形成长期门诊管理。")
    return lines or ["当前可确认的复诊频次与活动性信息有限，建议结合完整门诊记录再核对。"]


def build_treatment_lines(text: str) -> list[str]:
    lines = []
    if any(word in text for word in ["药物治疗", "口服药物", "处方"]):
        lines.append("资料显示已给予药物治疗，提示当前问题可能仍在处置过程中。")
    if any(word in text for word in ["建议进一步检查", "检查", "糖化血红蛋白"]):
        lines.append("资料存在检查建议，需核实相关检查是否已完成及结果如何。")
    if any(word in text for word in ["复诊", "随访", "观察"]):
        lines.append("资料存在复诊、随访或观察安排，提示当前问题尚未完全闭环。")
    return lines or ["当前未见明确治疗或随访安排描述，或材料不足以确认。"]


def build_summary(text: str, topic_risks: list[str]) -> list[str]:
    summary = []
    if topic_risks:
        summary.append("已识别出需重点关注的诊断、复诊或治疗连续性风险，建议结合补问或补件进一步判断。")
    else:
        summary.append("当前未见明确高关注门诊风险事实，但仍需结合材料完整度审视。")
    if any(word in text for word in ["复诊", "两次", "多次", "随访", "观察"]):
        summary.append("资料中存在反复就诊或持续管理线索，建议重点核实病情是否仍处于活动期。")
    if any(word in text for word in ["考虑", "建议进一步检查", "未明确", "血糖升高"]):
        summary.append("资料中存在待排查问题或检查未闭环线索，建议补充后续检查结果和诊断判断。")
    return summary[:3]


def build_followups(text: str) -> list[str]:
    questions = []
    if any(word in text for word in ["主诉", "乏力", "口渴", "症状", "持续", "反复"]):
        questions.append("请补充症状持续时间、变化过程、目前是否仍存在以及是否影响日常生活或工作。")
    if any(word in text for word in ["诊断", "考虑", "血糖升高", "糖代谢异常", "待查"]):
        questions.append("请补充门诊初步诊断是否已进一步明确，以及相关检查或复查结果。")
    if any(word in text for word in ["复诊", "两次", "多次", "随访"]):
        questions.append("请补充近阶段复诊次数、复诊间隔、就诊科室及每次就诊结论。")
    if any(word in text for word in ["药物治疗", "口服药物", "治疗", "观察", "建议进一步检查"]):
        questions.append("请补充当前是否仍在用药、观察或随访中，以及医生建议的检查是否已完成。")
    if not questions:
        questions.append("当前材料未见明确补查方向，建议核对原件后再做人工审查。")
    return questions


def build_next_steps(text: str, topic_risks: list[str]) -> list[str]:
    steps = []
    if topic_risks or any(word in text for word in ["复诊", "治疗", "随访", "考虑", "检查"]):
        steps.append("建议补充说明关键症状、诊断判断、复诊频次和当前治疗状态后再做进一步判断。")
    if any(word in text for word in ["复诊", "两次", "多次", "药物治疗", "建议进一步检查", "随访"]):
        steps.append("建议补充复诊记录、专项检查结果、处方记录或健康说明等相关材料。")
        steps.append("建议重点人工审核，并结合问卷、病史、专项检查或住院资料进一步判断。")
    if not steps:
        steps.append("当前可进入下一环节核保审查。")
    steps.append("本结果仅用于门诊记录解析与补查准备，不替代正式核保决定。")
    return steps


def render_report(data: dict[str, Any]) -> str:
    text = data.get("_raw_text", "")
    basic = extract_basic_info(data)
    topic_risks = collect_topic_risks(text)
    key_points = extract_key_points(text)
    activity_lines = build_activity_lines(text)
    treatment_lines = build_treatment_lines(text)
    summary = build_summary(text, topic_risks)
    followups = build_followups(text)
    next_steps = build_next_steps(text, topic_risks)

    focus_lines = []
    if any(word in text for word in ["复诊", "随访", "观察", "药物治疗", "建议进一步检查"]):
        focus_lines.append("资料存在复诊、持续治疗或检查未闭环线索，需进一步核实病情是否仍处于活动期。")
    if any(word in text for word in ["考虑", "未明确", "待查", "血糖升高"]):
        focus_lines.append("诊断判断或代谢异常线索尚未完全明确，建议结合后续检查和复诊结果综合判断。")
    if not focus_lines:
        focus_lines.append("当前未见明确高关注门诊风险信号，但仍需结合原件和材料完整度复核。")

    lines = [
        "# 门诊记录解析结果",
        "",
        "一、门诊基本信息",
        f"- 患者基本信息：{basic['patient_info']}",
        f"- 就诊时间：{basic['visit_date']}",
        f"- 医疗机构：{basic['institution']}",
        f"- 就诊科室：{basic['department']}",
        f"- 材料来源或文本类型：{basic['source_type']}",
        "",
        "二、门诊记录解析结论摘要",
    ]
    lines.extend(f"- {item}" for item in summary)
    lines.extend([
        "",
        "三、主诉与诊断要点提取",
    ])
    lines.extend(f"- {item}" for item in (key_points or ["当前可确认的主诉与诊断要点有限，建议核对完整门诊记录。"]))
    lines.extend(f"- {item}" for item in topic_risks[:2])
    lines.extend([
        "",
        "四、就诊频次与病情活动性梳理",
    ])
    lines.extend(f"- {item}" for item in activity_lines)
    lines.extend([
        "",
        "五、治疗措施与随访安排提取",
    ])
    lines.extend(f"- {item}" for item in treatment_lines)
    lines.extend([
        "",
        "六、核保关注点与风险提示",
    ])
    lines.extend(f"- {item}" for item in focus_lines)
    lines.extend([
        "",
        "七、建议补充核实的问题或资料",
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
