#!/usr/bin/env python3
"""将心血管病史资料整理为标准化风险审查结果。"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


RISK_TOPICS = {
    "明确心血管诊断": ["高血压", "冠心病", "心绞痛", "心肌梗死", "心律失常", "心衰", "脑卒中", "TIA", "血管狭窄"],
    "重大事件史": ["急性", "梗死", "卒中", "晕厥", "胸痛", "胸闷", "脑血管"],
    "治疗干预": ["支架", "搭桥", "消融", "起搏器", "溶栓", "抗凝", "降压", "降脂"],
    "控制波动": ["控制一般", "控制不佳", "反复", "偶有", "随访", "长期服用"],
    "并发症线索": ["心衰", "肾功能", "后遗症", "再狭窄", "反复住院"],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成心血管病史风险审查报告")
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
    for key in ["history_period", "disease_type", "source_type", "record_text"]:
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
        "disease_type": str(data.get("disease_type") or "材料中未明确"),
        "history_period": str(data.get("history_period") or "材料中未明确"),
        "source_type": str(data.get("source_type") or "未明确"),
    }


def collect_topic_risks(text: str) -> list[str]:
    findings = []
    for topic, keywords in RISK_TOPICS.items():
        hits = [keyword for keyword in keywords if keyword in text]
        if hits:
            findings.append(f"{topic}：识别到 {('、'.join(hits))} 相关线索，需结合病程、干预结果和复查稳定性进一步判断。")
    return findings


def extract_diagnosis_points(text: str) -> list[str]:
    points = []
    if any(word in text for word in ["高血压", "冠心病", "心绞痛", "心肌梗死", "心律失常", "脑卒中"]):
        points.append("资料存在明确或疑似心血管诊断线索，需核实诊断名称、确诊时间及当前状态。")
    if any(word in text for word in ["急性", "胸痛", "胸闷", "晕厥", "卒中"]):
        points.append("资料存在急性事件或症状发作线索，需重点关注首次发作、再发情况和严重程度。")
    return points or ["当前可确认的心血管诊断信息有限，建议补充门诊、住院或检查依据。"]


def build_treatment_lines(text: str) -> list[str]:
    lines = []
    if any(word in text for word in ["支架", "搭桥", "消融", "起搏器"]):
        lines.append("资料显示存在介入或手术治疗线索，需核实实施时间、治疗结果和术后稳定性。")
    if any(word in text for word in ["抗凝", "降压", "降脂", "长期服用", "药物"]):
        lines.append("资料显示存在长期药物治疗或慢病管理线索，提示需关注依从性和控制效果。")
    if any(word in text for word in ["随访", "复查", "控制一般", "控制不佳"]):
        lines.append("资料提示当前仍在随访或控制观察中，稳定性判断需结合最近复查结果。")
    return lines or ["当前未见明确治疗或长期管理描述，或材料不足以确认。"]


def build_complication_lines(text: str) -> list[str]:
    lines = []
    if any(word in text for word in ["再狭窄", "再梗", "反复住院", "后遗症", "肾功能", "心衰"]):
        lines.append("资料存在并发症或长期器官风险线索，提示心血管病史复杂度较高。")
    if any(word in text for word in ["反复", "偶有", "胸闷", "控制一般", "控制不佳"]):
        lines.append("资料提示症状或控制状态可能存在波动，需关注是否仍处于活动或不稳定阶段。")
    return lines or ["当前未见明确并发症或复发风险描述，或材料不足以确认。"]


def build_summary(text: str, topic_risks: list[str]) -> list[str]:
    summary = []
    if topic_risks:
        summary.append("已识别出需重点关注的诊断、治疗或控制风险，建议结合补问或补件进一步判断。")
    else:
        summary.append("当前未见明确高关注心血管风险事实，但仍需结合材料完整度审视。")
    if any(word in text for word in ["梗死", "卒中", "支架", "搭桥", "心衰"]):
        summary.append("资料中存在重大心脑血管事件或介入治疗线索，建议重点核实术后稳定性和长期风险。")
    if any(word in text for word in ["随访", "控制一般", "控制不佳", "偶有", "再狭窄"]):
        summary.append("资料中存在控制波动、持续随访或复发风险线索，建议结合最近复查结果评估稳定性。")
    return summary[:3]


def build_followups(text: str) -> list[str]:
    questions = []
    if any(word in text for word in ["高血压", "冠心病", "心绞痛", "心肌梗死", "脑卒中", "TIA"]):
        questions.append("请补充主要心血管诊断名称、首次发病时间、发作经过及目前是否仍存在相关症状。")
    if any(word in text for word in ["支架", "搭桥", "消融", "起搏器", "造影"]):
        questions.append("请补充介入或手术治疗的时间、方式、术后结论、最近一次复查结果及是否存在再狭窄或其他术后异常。")
    if any(word in text for word in ["长期服用", "抗凝", "降压", "降脂", "控制一般", "控制不佳"]):
        questions.append("请补充当前用药方案、用药依从性、血压或症状控制情况及最近一次随访结论。")
    if any(word in text for word in ["胸闷", "反复", "再狭窄", "后遗症", "肾功能", "反复住院"]):
        questions.append("请补充是否存在再次发作、并发症、后遗症、器官损害或近期住院治疗情况。")
    if not questions:
        questions.append("当前材料未见明确补查方向，建议核对原件后再做人工审查。")
    return questions


def build_next_steps(text: str, topic_risks: list[str]) -> list[str]:
    steps = []
    if topic_risks or any(word in text for word in ["支架", "梗死", "卒中", "控制一般", "随访", "长期服用"]):
        steps.append("建议补充说明关键心血管诊断、重大事件经过、当前控制状态和随访结果后再做进一步判断。")
    if any(word in text for word in ["支架", "搭桥", "心肌梗死", "脑卒中", "再狭窄", "控制不佳", "心衰"]):
        steps.append("建议补充门诊记录、随访记录、复查报告、住院资料、介入记录或健康说明等相关材料。")
        steps.append("建议重点人工审核，并结合体检、门诊、住院、影像或专项检查进一步判断。")
    if not steps:
        steps.append("当前可进入下一环节核保审查。")
    steps.append("本结果仅用于心血管病史风险审查与补查准备，不替代正式核保决定。")
    return steps


def render_report(data: dict[str, Any]) -> str:
    text = data.get("_raw_text", "")
    basic = extract_basic_info(data)
    topic_risks = collect_topic_risks(text)
    diagnosis_points = extract_diagnosis_points(text)
    treatment_lines = build_treatment_lines(text)
    complication_lines = build_complication_lines(text)
    summary = build_summary(text, topic_risks)
    followups = build_followups(text)
    next_steps = build_next_steps(text, topic_risks)

    focus_lines = []
    if any(word in text for word in ["梗死", "卒中", "支架", "搭桥", "心衰"]):
        focus_lines.append("资料存在重大既往事件或介入治疗线索，需重点核实当前稳定性、术后恢复和长期风险。")
    if any(word in text for word in ["控制一般", "控制不佳", "反复", "再狭窄", "随访"]):
        focus_lines.append("资料存在控制波动、持续随访或复发风险线索，提示当前核保判断仍需结合最新复查依据。")
    if not focus_lines:
        focus_lines.append("当前未见明确高关注心血管风险信号，但仍需结合原件和材料完整度复核。")

    lines = [
        "# 心血管病史风险审查结果",
        "",
        "一、病史基本信息",
        f"- 被保人基本信息：{basic['patient_info']}",
        f"- 涉及心血管疾病类型：{basic['disease_type']}",
        f"- 病史时间范围：{basic['history_period']}",
        f"- 材料来源或文本类型：{basic['source_type']}",
        "",
        "二、心血管病史风险审查结论摘要",
    ]
    lines.extend(f"- {item}" for item in summary)
    lines.extend([
        "",
        "三、心血管诊断与发病经过要点提取",
    ])
    lines.extend(f"- {item}" for item in diagnosis_points)
    lines.extend(f"- {item}" for item in topic_risks[:2])
    lines.extend([
        "",
        "四、治疗干预与管理情况梳理",
    ])
    lines.extend(f"- {item}" for item in (topic_risks or ["当前未识别到明确治疗干预或管理线索，或材料不足以确认。"]))
    lines.extend(f"- {item}" for item in treatment_lines)
    lines.extend([
        "",
        "五、并发症与复发风险线索识别",
    ])
    lines.extend(f"- {item}" for item in complication_lines)
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
