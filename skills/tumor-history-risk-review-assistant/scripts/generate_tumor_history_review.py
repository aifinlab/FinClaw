#!/usr/bin/env python3
"""将肿瘤病史资料整理为标准化风险审查结果。"""

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
    "明确肿瘤诊断": ["恶性肿瘤", "原位癌", "癌", "结节", "占位", "交界性", "良性"],
    "病理高风险": ["病理", "浸润", "淋巴结", "转移", "分期", "分级"],
    "治疗信息": ["手术", "放疗", "化疗", "靶向", "免疫治疗", "内分泌治疗", "消融"],
    "复发/转移线索": ["复发", "转移", "残留", "异常复查", "未见明确复发"],
    "随访异常": ["随访", "复查", "继续治疗", "观察", "定期复查"],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成肿瘤病史风险审查报告")
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
    for key in ["history_period", "lesion_type", "source_type", "record_text"]:
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
        "lesion_type": str(data.get("lesion_type") or "材料中未明确"),
        "history_period": str(data.get("history_period") or "材料中未明确"),
        "source_type": str(data.get("source_type") or "未明确"),
    }


def collect_topic_risks(text: str) -> list[str]:
    findings = []
    for topic, keywords in RISK_TOPICS.items():
        hits = [keyword for keyword in keywords if keyword in text]
        if hits:
            findings.append(f"{topic}：识别到 {('、'.join(hits))} 相关线索，需结合诊断依据、治疗阶段和随访结果进一步判断。")
    return findings


def extract_diagnosis_points(text: str) -> list[str]:
    points = []
    if any(word in text for word in ["恶性肿瘤", "原位癌", "良性", "交界性", "占位", "结节"]):
        points.append("资料存在明确或疑似肿瘤性质线索，需核实良恶性、病变部位和确诊依据。")
    if "病理" in text:
        points.append("资料包含病理依据线索，需重点关注组织学类型、浸润情况和边界信息。")
    if any(word in text for word in ["分期", "分级", "淋巴结", "转移"]):
        points.append("资料存在分期分级或转移相关线索，提示需重点关注病理风险层次。")
    return points or ["当前可确认的肿瘤诊断信息有限，建议补充病理或影像依据。"]


def build_treatment_lines(text: str) -> list[str]:
    lines = []
    if any(word in text for word in ["手术", "切除"]):
        lines.append("资料显示已实施手术治疗，需核实手术范围、切缘情况和术后结论。")
    if any(word in text for word in ["化疗", "放疗", "靶向", "免疫治疗", "内分泌治疗"]):
        lines.append("资料显示存在术后或系统性治疗线索，提示需关注治疗阶段、是否完成及耐受情况。")
    if any(word in text for word in ["继续治疗", "仍在治疗", "观察"]):
        lines.append("资料提示当前可能仍在治疗或观察阶段，说明病情尚未完全脱离管理期。")
    return lines or ["当前未见明确治疗过程描述，或材料不足以确认。"]


def build_followup_lines(text: str) -> list[str]:
    lines = []
    if any(word in text for word in ["随访", "复查", "定期复查"]):
        lines.append("资料显示仍在随访管理中，需关注复查频率和最近一次复查结论。")
    if any(word in text for word in ["复发", "转移", "残留", "异常复查"]):
        lines.append("资料存在复发、转移或残留病灶相关线索，提示肿瘤稳定性风险较高。")
    if "未见明确复发" in text:
        lines.append("资料提示近期复查暂未见明确复发，但稳定性仍需结合随访时长和后续结果综合判断。")
    return lines or ["当前未见明确随访或复发风险描述，或材料不足以确认。"]


def build_summary(text: str, topic_risks: list[str]) -> list[str]:
    summary = []
    if topic_risks:
        summary.append("已识别出需重点关注的肿瘤性质、治疗或随访风险，建议结合补问或补件进一步判断。")
    else:
        summary.append("当前未见明确高关注肿瘤风险事实，但仍需结合材料完整度审视。")
    if any(word in text for word in ["恶性肿瘤", "病理", "浸润", "淋巴结", "转移"]):
        summary.append("资料中存在病理高风险或恶性病变线索，建议重点核实病理性质、分期分级和转移情况。")
    if any(word in text for word in ["随访", "复查", "继续治疗", "未见明确复发"]):
        summary.append("资料中存在持续随访或治疗后观察线索，建议结合最近一次复查结果评估稳定性。")
    return summary[:3]


def build_followups(text: str) -> list[str]:
    questions = []
    if any(word in text for word in ["病理", "浸润", "淋巴结", "分期", "分级", "转移"]):
        questions.append("请补充完整病理报告内容，包括组织学类型、分期分级、浸润情况、淋巴结情况及是否存在转移依据。")
    if any(word in text for word in ["手术", "化疗", "放疗", "靶向", "免疫治疗", "内分泌治疗"]):
        questions.append("请补充手术及后续治疗的时间、治疗方案、治疗完成情况及目前是否仍在治疗中。")
    if any(word in text for word in ["随访", "复查", "复发", "转移", "残留", "未见明确复发"]):
        questions.append("请补充最近一次随访或复查时间、复查项目、复查结论及当前是否存在复发、转移或残留病灶。")
    if any(word in text for word in ["结节", "占位", "待查", "良恶性未明"]):
        questions.append("请补充病变性质是否已进一步明确，以及是否已完成病理、影像或专科评估。")
    if not questions:
        questions.append("当前材料未见明确补查方向，建议核对原件后再做人工审查。")
    return questions


def build_next_steps(text: str, topic_risks: list[str]) -> list[str]:
    steps = []
    if topic_risks or any(word in text for word in ["病理", "治疗", "随访", "复查", "转移", "复发"]):
        steps.append("建议补充说明关键病理性质、治疗阶段、随访结果和当前稳定性后再做进一步判断。")
    if any(word in text for word in ["恶性肿瘤", "病理", "浸润", "淋巴结", "转移", "复发", "继续治疗"]):
        steps.append("建议补充病理报告、影像资料、手术记录、门诊随访记录或复查结果等相关材料。")
        steps.append("建议重点人工审核，并结合病理、影像、住院、门诊或随访资料进一步判断。")
    if not steps:
        steps.append("当前可进入下一环节核保审查。")
    steps.append("本结果仅用于肿瘤病史风险审查与补查准备，不替代正式核保决定。")
    return steps


def render_report(data: dict[str, Any]) -> str:
    text = data.get("_raw_text", "")
    basic = extract_basic_info(data)
    topic_risks = collect_topic_risks(text)
    diagnosis_points = extract_diagnosis_points(text)
    treatment_lines = build_treatment_lines(text)
    followup_lines = build_followup_lines(text)
    summary = build_summary(text, topic_risks)
    followups = build_followups(text)
    next_steps = build_next_steps(text, topic_risks)

    focus_lines = []
    if any(word in text for word in ["恶性肿瘤", "浸润", "淋巴结", "转移", "复发"]):
        focus_lines.append("资料存在恶性病变、病理高风险或复发转移线索，需重点核实当前病情稳定性和后续治疗计划。")
    if any(word in text for word in ["继续治疗", "随访", "复查", "未见明确复发"]):
        focus_lines.append("资料存在治疗后持续随访或治疗未完全结束线索，说明风险评估仍需结合最新复查结果。")
    if not focus_lines:
        focus_lines.append("当前未见明确高关注肿瘤风险信号，但仍需结合原件和材料完整度复核。")

    lines = [
        "# 肿瘤病史风险审查结果",
        "",
        "一、病史基本信息",
        f"- 被保人基本信息：{basic['patient_info']}",
        f"- 涉及病变类型：{basic['lesion_type']}",
        f"- 病史时间范围：{basic['history_period']}",
        f"- 材料来源或文本类型：{basic['source_type']}",
        "",
        "二、肿瘤病史风险审查结论摘要",
    ]
    lines.extend(f"- {item}" for item in summary)
    lines.extend([
        "",
        "三、肿瘤类型与诊断要点提取",
    ])
    lines.extend(f"- {item}" for item in diagnosis_points)
    lines.extend(f"- {item}" for item in topic_risks[:2])
    lines.extend([
        "",
        "四、病理结果与治疗经过梳理",
    ])
    lines.extend(f"- {item}" for item in (topic_risks or ["当前未识别到明确病理或治疗线索，或材料不足以确认。"]))
    lines.extend(f"- {item}" for item in treatment_lines)
    lines.extend([
        "",
        "五、随访情况与复发风险线索识别",
    ])
    lines.extend(f"- {item}" for item in followup_lines)
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
