#!/usr/bin/env python3
"""将常规体检报告整理为标准化解析结果。"""

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
    "明确异常": ["升高", "降低", "异常", "偏高", "偏低"],
    "边界异常": ["轻度", "接近", "临界", "边界"],
    "代谢风险": ["BMI", "血压", "血糖", "血脂", "甘油三酯", "胆固醇"],
    "肝功能风险": ["ALT", "AST", "转氨酶", "脂肪肝", "胆红素"],
    "肾功能风险": ["肌酐", "尿蛋白", "尿潜血", "尿酸"],
    "心血管风险": ["心电图", "血压", "心率"],
    "呼吸系统风险": ["胸片", "肺", "呼吸"],
}

KEY_SECTION_MAP = {
    "血压与 BMI": ["血压", "BMI"],
    "血糖与血脂": ["血糖", "血脂", "甘油三酯", "胆固醇"],
    "肝肾功能": ["ALT", "AST", "转氨酶", "肝", "肾", "肌酐", "尿酸"],
    "血常规与尿常规": ["血常规", "尿常规", "尿蛋白", "尿潜血"],
    "心电图、胸片、彩超等影像或功能检查": ["心电图", "胸片", "彩超", "超声", "影像"],
}

SUMMARY_FLAGS = ["偏高", "异常", "升高", "脂肪肝", "复查", "建议"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成常规体检解析报告")
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
    return {"report_text": raw, "_raw_text": raw}


def build_text_from_json(data: dict[str, Any]) -> str:
    parts: list[str] = []
    for key in ["exam_date", "institution", "source_type", "exam_scope", "report_text"]:
        value = data.get(key)
        if value:
            parts.append(str(value))
    notes = data.get("notes")
    if isinstance(notes, list):
        parts.extend(str(item) for item in notes if item)
    person = data.get("person", {})
    if isinstance(person, dict):
        parts.extend(str(v) for v in person.values() if v not in (None, ""))
    return "\n".join(parts)


def extract_basic_info(data: dict[str, Any]) -> dict[str, str]:
    person = data.get("person", {}) if isinstance(data.get("person"), dict) else {}
    person_parts = []
    for key, label in [("name", "姓名"), ("age", "年龄"), ("gender", "性别")]:
        value = person.get(key)
        if value not in (None, ""):
            person_parts.append(f"{label}：{value}")
    return {
        "person_info": "；".join(person_parts) if person_parts else "材料中未明确",
        "exam_date": str(data.get("exam_date") or "未提供"),
        "institution": str(data.get("institution") or "未提供"),
        "source_type": str(data.get("source_type") or "未明确"),
        "exam_scope": str(data.get("exam_scope") or "材料中未明确"),
    }


def collect_topic_risks(text: str) -> list[str]:
    findings = []
    for topic, keywords in RISK_TOPICS.items():
        hits = [keyword for keyword in keywords if keyword in text]
        if hits:
            findings.append(f"{topic}：识别到 {('、'.join(hits))} 相关线索，需结合具体指标、结论和持续性进一步判断。")
    return findings


def extract_abnormal_points(text: str) -> list[str]:
    points = []
    mapping = [
        ("偏高", "报告存在偏高类异常指标，需核实具体项目及偏离程度。"),
        ("偏低", "报告存在偏低类异常指标，需核实具体项目及偏离程度。"),
        ("异常", "报告存在明确异常提示，需核实是否已有复查或进一步检查。"),
        ("建议", "报告包含医生建议或健康管理提示，需关注是否要求复查或随访。"),
        ("复查", "报告提及复查建议，提示当前异常可能需要持续关注。"),
    ]
    for keyword, message in mapping:
        if keyword in text:
            points.append(message)
    return list(dict.fromkeys(points))


def build_section_summary(text: str) -> dict[str, str]:
    result = {}
    for title, keywords in KEY_SECTION_MAP.items():
        hits = [keyword for keyword in keywords if keyword in text]
        result[title] = f"识别到 {('、'.join(hits))} 相关线索，需结合具体数值、参考范围和结论核实。" if hits else "未见明确相关内容，或当前材料不足以确认。"
    return result


def build_summary(text: str, topic_risks: list[str]) -> list[str]:
    summary = []
    if topic_risks:
        summary.append("已识别出需重点关注的异常指标、异常结论或系统性风险，建议结合补问或补件进一步判断。")
    else:
        summary.append("当前未见明确高关注异常，但仍需结合材料完整度审视。")
    if any(word in text for word in ["脂肪肝", "甘油三酯", "血压", "血糖", "血脂", "ALT", "肌酐"]):
        summary.append("问卷中存在代谢或器官功能相关异常线索，建议重点核实是否存在持续异常或复查结果。")
    if any(word in text for word in ["建议", "复查", "异常", "偏高", "升高"]):
        summary.append("报告存在异常提示或复查建议，建议进一步补充相关复查资料或健康说明。")
    return summary[:3]


def build_followups(text: str) -> list[str]:
    questions = []
    if any(word in text for word in ["血压", "BMI", "血糖", "血脂", "甘油三酯", "胆固醇"]):
        questions.append("请补充相关代谢指标是否已复查、最近一次复查时间及复查结果，是否已有慢病诊断或健康管理建议。")
    if any(word in text for word in ["ALT", "AST", "转氨酶", "脂肪肝", "肝", "肾", "肌酐", "尿酸"]):
        questions.append("请补充肝肾功能或相关超声异常是否已复查、是否有专科诊断及最近一次检查结论。")
    if any(word in text for word in ["心电图", "胸片", "彩超", "超声", "影像"]):
        questions.append("请补充影像或功能检查异常的具体结论、医生建议及是否已进一步检查。")
    if any(word in text for word in ["建议", "复查", "异常"]):
        questions.append("请补充报告中建议复查项目是否已完成复查，以及目前是否仍需持续观察或治疗。")
    if not questions:
        questions.append("当前材料未见明确补查方向，建议核对原件后再做人工审查。")
    return questions


def build_next_steps(text: str, topic_risks: list[str]) -> list[str]:
    steps = []
    if topic_risks or any(word in text for word in SUMMARY_FLAGS):
        steps.append("建议补充说明关键异常指标、复查情况和当前健康状态后再做进一步判断。")
    if any(word in text for word in ["脂肪肝", "ALT", "异常", "偏高", "复查", "建议", "心电图", "彩超"]):
        steps.append("建议补充复查报告、门诊记录、专项检查结果或健康说明等相关材料。")
        steps.append("建议重点人工审核，并结合问卷、病史或专项检查进一步判断。")
    if not steps:
        steps.append("当前可进入下一环节核保审查。")
    steps.append("本结果仅用于常规体检解析与补查准备，不替代正式核保决定。")
    return steps


def render_report(data: dict[str, Any]) -> str:
    text = data.get("_raw_text", "")
    basic = extract_basic_info(data)
    topic_risks = collect_topic_risks(text)
    abnormal_points = extract_abnormal_points(text)
    summary = build_summary(text, topic_risks)
    followups = build_followups(text)
    next_steps = build_next_steps(text, topic_risks)
    sections = build_section_summary(text)

    focus_lines = []
    if any(word in text for word in SUMMARY_FLAGS):
        focus_lines.append("报告存在异常指标、复查建议或持续关注线索，需进一步核实异常是否持续存在及是否已有专科处理。")
    if any(word in text for word in ["BMI", "血压", "血糖", "血脂", "甘油三酯", "脂肪肝"]):
        focus_lines.append("多项代谢相关指标或结论可能共同提示代谢风险，建议结合病史和复查结果进一步评估。")
    if not focus_lines:
        focus_lines.append("当前未见明确高关注体检异常信号，但仍需结合原件和材料完整度复核。")

    lines = [
        "# 常规体检解析结果",
        "",
        "一、体检基本信息",
        f"- 体检人基本信息：{basic['person_info']}",
        f"- 体检日期：{basic['exam_date']}",
        f"- 体检机构：{basic['institution']}",
        f"- 材料来源或文本类型：{basic['source_type']}",
        f"- 主要检查项目范围：{basic['exam_scope']}",
        "",
        "二、体检解析结论摘要",
    ]
    lines.extend(f"- {item}" for item in summary)
    lines.extend([
        "",
        "三、异常指标与异常结论提取",
    ])
    lines.extend(f"- {item}" for item in (abnormal_points or ["当前未识别到明确异常指标或异常结论描述，或材料不足以确认。"]))
    lines.extend(f"- {item}" for item in topic_risks[:3])
    lines.extend([
        "",
        "四、边界异常与系统性风险识别",
    ])
    lines.extend(f"- {item}" for item in (topic_risks or ["当前未识别到明确边界异常或系统性风险组合，或材料不足以确认。"]))
    lines.extend([
        "",
        "五、重点检查项目梳理",
        f"- 血压与 BMI：{sections['血压与 BMI']}",
        f"- 血糖与血脂：{sections['血糖与血脂']}",
        f"- 肝肾功能：{sections['肝肾功能']}",
        f"- 血常规与尿常规：{sections['血常规与尿常规']}",
        f"- 心电图、胸片、彩超等影像或功能检查：{sections['心电图、胸片、彩超等影像或功能检查']}",
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



def main():


        raise SystemExit(main())


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n操作被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)