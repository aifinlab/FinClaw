#!/usr/bin/env python3
"""将住院资料整理为标准化解析结果。"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


RISK_TOPICS = {
    "明确诊断": ["诊断", "胆囊结石", "胆囊炎", "肿瘤", "梗死", "出血"],
    "治疗信息": ["手术", "介入", "治疗", "抗感染", "药物", "重症"],
    "严重性线索": ["并发症", "发热", "危重", "器官损害", "异常", "加重"],
    "恢复风险": ["恢复一般", "带药", "复查", "随访", "继续治疗", "未愈"],
}

TIMELINE_MARKERS = ["入院", "住院期间", "术后", "出院"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成住院资料解析报告")
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
    for key in ["admission_date", "discharge_date", "department", "institution", "source_type", "record_text"]:
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
        "hospitalization_time": build_hospitalization_time(data),
        "institution": str(data.get("institution") or "未提供"),
        "department": str(data.get("department") or "未明确"),
        "source_type": str(data.get("source_type") or "未明确"),
    }


def build_hospitalization_time(data: dict[str, Any]) -> str:
    admission = data.get("admission_date")
    discharge = data.get("discharge_date")
    if admission and discharge:
        return f"{admission} 至 {discharge}"
    if admission:
        return f"入院时间：{admission}，出院时间未提供"
    return "材料中未明确"


def collect_topic_risks(text: str) -> list[str]:
    findings = []
    for topic, keywords in RISK_TOPICS.items():
        hits = [keyword for keyword in keywords if keyword in text]
        if hits:
            findings.append(f"{topic}：识别到 {('、'.join(hits))} 相关线索，需结合诊断、治疗结论和转归进一步判断。")
    return findings


def extract_diagnosis_points(text: str) -> list[str]:
    points = []
    mapping = [
        ("入院诊断", "资料包含入院诊断线索，需核实诊断名称和入院原因。"),
        ("出院诊断", "资料包含出院诊断线索，需核实主要诊断、伴随疾病及转归。"),
        ("疼痛", "资料披露主要症状线索，提示需关注入院原因和严重程度。"),
        ("并发症", "资料存在并发症线索，需重点核实对病情和恢复的影响。"),
    ]
    for keyword, message in mapping:
        if keyword in text:
            points.append(message)
    if "胆囊结石" in text or "胆囊炎" in text:
        points.append("资料明确涉及胆囊结石或胆囊炎相关诊断，需结合手术和术后恢复情况综合判断。")
    return list(dict.fromkeys(points))


def build_timeline(text: str) -> list[str]:
    timeline = []
    if "入院" in text:
        timeline.append("入院阶段：资料显示存在明确入院原因或入院诊断线索。")
    if "住院期间" in text:
        timeline.append("住院阶段：住院期间完成检查并实施相应治疗。")
    if "术后" in text:
        timeline.append("术后阶段：术后恢复情况和病情变化需重点关注。")
    if "出院" in text:
        timeline.append("出院阶段：资料显示存在出院诊断、出院带药或复查建议线索。")
    return timeline or ["当前可确认的诊疗时间线有限，建议结合完整病历再核对。"]


def build_recovery_lines(text: str) -> list[str]:
    lines = []
    if any(word in text for word in ["恢复一般", "未愈", "待观察"]):
        lines.append("资料提示出院时恢复并非完全恢复，需进一步核实当前状态和后续治疗安排。")
    if any(word in text for word in ["带药", "继续治疗", "复查", "随访"]):
        lines.append("资料显示出院后仍需带药、复查或继续随访，提示当前转归尚需持续观察。")
    if "好转" in text:
        lines.append("资料提示住院后病情较入院时已有改善，但是否完全恢复仍需结合复查结果判断。")
    return lines or ["当前未见明确恢复状态描述，或材料不足以确认。"]


def build_summary(text: str, topic_risks: list[str]) -> list[str]:
    summary = []
    if topic_risks:
        summary.append("已识别出需重点关注的诊断、治疗或恢复风险，建议结合补问或补件进一步判断。")
    else:
        summary.append("当前未见明确高关注住院风险事实，但仍需结合材料完整度审视。")
    if any(word in text for word in ["手术", "介入", "并发症", "发热"]):
        summary.append("资料中存在手术治疗或病情变化线索，建议重点核实并发症、术后异常及恢复情况。")
    if any(word in text for word in ["带药", "复查", "随访", "恢复一般", "未愈"]):
        summary.append("出院后仍有带药、复查或恢复未明线索，建议补充后续随访资料。")
    return summary[:3]


def build_followups(text: str) -> list[str]:
    questions = []
    if any(word in text for word in ["诊断", "胆囊结石", "胆囊炎", "肿瘤", "梗死"]):
        questions.append("请补充完整入院诊断、出院诊断、伴随疾病及是否存在并发症或术前术后诊断差异。")
    if any(word in text for word in ["手术", "介入", "术后"]):
        questions.append("请补充手术或介入治疗名称、实施时间、术后结论、是否存在并发症及当前恢复状态。")
    if any(word in text for word in ["带药", "复查", "随访", "继续治疗", "恢复一般"]):
        questions.append("请补充出院后是否仍在带药、门诊随访或继续治疗，以及最近一次复查时间和结果。")
    if any(word in text for word in ["病理", "检查", "彩超", "影像"]):
        questions.append("请补充关键检查、病理或影像结果，以支持主要诊断和严重性判断。")
    if not questions:
        questions.append("当前材料未见明确补查方向，建议核对原件后再做人工审查。")
    return questions


def build_next_steps(text: str, topic_risks: list[str]) -> list[str]:
    steps = []
    if topic_risks or any(word in text for word in ["手术", "并发症", "复查", "带药", "恢复一般"]):
        steps.append("建议补充说明关键诊断、治疗经过、并发症情况和当前恢复状态后再做进一步判断。")
    if any(word in text for word in ["手术", "并发症", "带药", "复查", "随访", "病理"]):
        steps.append("建议补充完整出院记录、手术记录、病理资料、复查报告或门诊随访记录等相关材料。")
        steps.append("建议重点人工审核，并结合问卷、病史、门诊随访或专项检查进一步判断。")
    if not steps:
        steps.append("当前可进入下一环节核保审查。")
    steps.append("本结果仅用于住院资料解析与补查准备，不替代正式核保决定。")
    return steps


def render_report(data: dict[str, Any]) -> str:
    text = data.get("_raw_text", "")
    basic = extract_basic_info(data)
    topic_risks = collect_topic_risks(text)
    diagnosis_points = extract_diagnosis_points(text)
    timeline = build_timeline(text)
    recovery_lines = build_recovery_lines(text)
    summary = build_summary(text, topic_risks)
    followups = build_followups(text)
    next_steps = build_next_steps(text, topic_risks)

    focus_lines = []
    if any(word in text for word in ["手术", "并发症", "发热", "带药", "复查", "恢复一般"]):
        focus_lines.append("资料存在手术、病情变化、带药出院或复查安排等高关注线索，需进一步核实转归和持续治疗风险。")
    if any(word in text for word in ["诊断", "出院诊断", "术后", "随访"]):
        focus_lines.append("主要诊断、治疗方式与出院后管理共同构成核保关注点，建议结合后续随访资料综合判断。")
    if not focus_lines:
        focus_lines.append("当前未见明确高关注住院风险信号，但仍需结合原件和材料完整度复核。")

    lines = [
        "# 住院资料解析结果",
        "",
        "一、住院基本信息",
        f"- 患者基本信息：{basic['patient_info']}",
        f"- 住院时间：{basic['hospitalization_time']}",
        f"- 医疗机构：{basic['institution']}",
        f"- 入院科室：{basic['department']}",
        f"- 材料来源或文本类型：{basic['source_type']}",
        "",
        "二、住院资料解析结论摘要",
    ]
    lines.extend(f"- {item}" for item in summary)
    lines.extend([
        "",
        "三、主要诊断与住院原因提取",
    ])
    lines.extend(f"- {item}" for item in (diagnosis_points or ["当前可确认的主要诊断和住院原因信息有限，建议核对完整病历。"]))
    lines.extend(f"- {item}" for item in topic_risks[:2])
    lines.extend([
        "",
        "四、住院经过与诊疗时间线梳理",
    ])
    lines.extend(f"- {item}" for item in timeline)
    lines.extend([
        "",
        "五、治疗措施与严重性线索识别",
    ])
    lines.extend(f"- {item}" for item in (topic_risks or ["当前未识别到明确治疗措施或严重性线索，或材料不足以确认。"]))
    lines.extend([
        "",
        "六、恢复情况与核保关注点",
    ])
    lines.extend(f"- {item}" for item in recovery_lines)
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
