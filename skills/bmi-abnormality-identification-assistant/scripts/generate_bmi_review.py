#!/usr/bin/env python3
"""将 BMI 相关资料整理为标准化异常识别结果。"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成 BMI 异常识别报告")
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
    return {"context_text": raw, "_raw_text": raw}


def build_text_from_json(data: dict[str, Any]) -> str:
    parts: list[str] = []
    for key in ["height_cm", "weight_kg", "recorded_bmi", "measured_at", "source_type", "context_text"]:
        value = data.get(key)
        if value not in (None, ""):
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
        "height_cm": str(data.get("height_cm") or "未提供"),
        "weight_kg": str(data.get("weight_kg") or "未提供"),
        "recorded_bmi": str(data.get("recorded_bmi") or "未提供"),
        "measured_at": str(data.get("measured_at") or "未提供"),
        "source_type": str(data.get("source_type") or "未明确"),
    }


def calculate_bmi(height_cm: Any, weight_kg: Any) -> float | None:
    try:
        h = float(height_cm)
        w = float(weight_kg)
        if h <= 0 or w <= 0:
            return None
        meters = h / 100.0
        return w / (meters * meters)
    except (TypeError, ValueError):
        return None


def bmi_grade(bmi: float | None) -> str:
    if bmi is None:
        return "无法判断"
    if bmi < 18.5:
        return "偏瘦或低体重"
    if bmi < 24.0:
        return "正常范围"
    if bmi < 28.0:
        return "超重"
    if bmi < 32.0:
        return "肥胖"
    return "重度肥胖或明显肥胖"


def compare_bmi(recorded_bmi: Any, calculated_bmi: float | None) -> str:
    if calculated_bmi is None:
        return "当前无法完成 BMI 核验，需补充有效身高体重数据。"
    try:
        recorded = float(recorded_bmi)
        diff = abs(recorded - calculated_bmi)
        if diff > 0.5:
            return "记录 BMI 与按身高体重计算结果存在明显差异，建议复核录入数据。"
        return "记录 BMI 与计算结果基本一致。"
    except (TypeError, ValueError):
        return "资料中未提供可核验的 BMI 记录值，以下按身高体重计算结果判断。"


def build_weight_trend(text: str) -> list[str]:
    lines = []
    if any(word in text for word in ["增加", "增重", "上升", "变重"]):
        lines.append("资料存在体重上升线索，需核实变化时间、变化幅度及原因。")
    if any(word in text for word in ["下降", "减重", "消瘦", "变轻"]):
        lines.append("资料存在体重下降线索，需核实变化时间、变化幅度及原因。")
    if any(word in text for word in ["既往", "前次", "记录不一致", "不一致"]):
        lines.append("资料存在前后体征对比线索，建议核实既往记录与当前数据是否一致。")
    return lines or ["当前未见明确体重变化或一致性异常描述，或材料不足以判断趋势。"]


def build_risk_lines(text: str, bmi: float | None) -> list[str]:
    lines = []
    if bmi is not None and bmi >= 28:
        lines.append("BMI 已达到肥胖区间，需关注代谢、心血管和脂肪肝等相关风险线索。")
    if bmi is not None and bmi < 18.5:
        lines.append("BMI 偏低，需关注营养状态、不明原因体重下降或消耗性疾病风险。")
    if any(word in text for word in ["高血压", "糖尿病", "脂肪肝", "血脂", "血糖"]):
        lines.append("资料同时存在代谢或慢病相关线索，提示 BMI 异常可能伴随相关健康风险。")
    if any(word in text for word in ["睡眠", "呼吸", "关节"]):
        lines.append("资料存在睡眠、呼吸或关节负担线索，需结合 BMI 异常程度综合判断。")
    return lines or ["当前未见明确相关健康风险线索，或材料不足以确认。"]


def build_summary(text: str, bmi: float | None, grade: str) -> list[str]:
    summary = []
    if bmi is None:
        summary.append("当前资料不足以完成 BMI 准确计算，需补充有效身高体重数据。")
    else:
        summary.append(f"当前 BMI 计算结果约为 {bmi:.1f}，体重状态判断为“{grade}”。")
    if any(word in text for word in ["增加", "下降", "波动", "不一致"]):
        summary.append("资料中存在体重变化或一致性风险线索，建议核实测量时间、变化幅度和原因。")
    if any(word in text for word in ["高血压", "糖尿病", "脂肪肝", "血脂", "血糖"]) or (bmi is not None and (bmi >= 28 or bmi < 18.5)):
        summary.append("当前 BMI 异常或相关慢病线索可能影响核保判断，建议结合体检或病史资料进一步核实。")
    return summary[:3]


def build_followups(text: str, bmi: float | None) -> list[str]:
    questions = []
    questions.append("请确认当前身高、体重、测量时间及单位是否准确，并补充最近一次体征测量结果。")
    if any(word in text for word in ["增加", "下降", "波动", "变重", "减重"]):
        questions.append("请补充近期体重变化幅度、持续时间及变化原因，是否伴随饮食、运动或疾病因素。")
    if bmi is not None and bmi >= 28:
        questions.append("请补充是否存在高血压、糖脂代谢异常、脂肪肝、睡眠呼吸问题或相关慢病管理资料。")
    if bmi is not None and bmi < 18.5:
        questions.append("请补充是否存在营养不良、慢性消耗、近期疾病或其他导致体重下降的情况。")
    if any(word in text for word in ["高血压", "糖尿病", "脂肪肝", "血脂", "血糖"]):
        questions.append("请补充相关慢病资料、最近一次体检结果或门诊随访记录，以支持 BMI 相关风险判断。")
    return questions


def build_next_steps(text: str, bmi: float | None) -> list[str]:
    steps = []
    if bmi is None or any(word in text for word in ["增加", "下降", "波动", "不一致"]):
        steps.append("建议补充说明身高体重测量时间、体重变化情况及数据一致性后再做进一步判断。")
    if (bmi is not None and (bmi >= 28 or bmi < 18.5)) or any(word in text for word in ["高血压", "糖尿病", "脂肪肝", "血脂", "血糖"]):
        steps.append("建议补充体检报告、慢病资料、门诊记录或健康说明等相关材料。")
        steps.append("建议重点人工审核，并结合体检、病史、慢病资料或门诊记录进一步判断。")
    if not steps:
        steps.append("当前可进入下一环节核保审查。")
    steps.append("本结果仅用于 BMI 异常识别与补查准备，不替代正式核保决定。")
    return steps


def render_report(data: dict[str, Any]) -> str:
    text = data.get("_raw_text", "")
    basic = extract_basic_info(data)
    bmi = calculate_bmi(data.get("height_cm"), data.get("weight_kg"))
    grade = bmi_grade(bmi)
    validation = compare_bmi(data.get("recorded_bmi"), bmi)
    trend_lines = build_weight_trend(text)
    risk_lines = build_risk_lines(text, bmi)
    summary = build_summary(text, bmi, grade)
    followups = build_followups(text, bmi)
    next_steps = build_next_steps(text, bmi)

    focus_lines = []
    if bmi is not None and bmi >= 28:
        focus_lines.append("BMI 明显升高，提示需重点关注肥胖及相关代谢风险。")
    if bmi is not None and bmi < 18.5:
        focus_lines.append("BMI 明显偏低，提示需重点关注营养状态或体重下降原因。")
    if any(word in text for word in ["增加", "下降", "波动", "不一致"]):
        focus_lines.append("资料存在体重变化或前后不一致线索，建议进一步核实趋势及原因。")
    if any(word in text for word in ["高血压", "糖尿病", "脂肪肝", "血脂", "血糖"]):
        focus_lines.append("BMI 异常同时伴随慢病或代谢风险线索，可能提高核保关注度。")
    if not focus_lines:
        focus_lines.append("当前未见明确高关注 BMI 风险信号，但仍需结合原件和材料完整度复核。")

    bmi_text = f"{bmi:.1f}" if bmi is not None else "无法计算"
    lines = [
        "# BMI 异常识别结果",
        "",
        "一、基本体征信息",
        f"- 被保人基本信息：{basic['person_info']}",
        f"- 身高：{basic['height_cm']} cm",
        f"- 体重：{basic['weight_kg']} kg",
        f"- BMI（如可计算）：{bmi_text}",
        f"- 测量时间：{basic['measured_at']}",
        f"- 材料来源或文本类型：{basic['source_type']}",
        "",
        "二、BMI 异常识别结论摘要",
    ]
    lines.extend(f"- {item}" for item in summary)
    lines.extend([
        "",
        "三、BMI 计算与异常等级判断",
        f"- BMI 计算/核验结果：{validation}",
        f"- 体重状态判断：{grade}",
    ])
    if bmi is None:
        lines.append("- 信息完整度提示：当前缺少足够有效的体征数据，BMI 判断依据不足。")
    else:
        lines.append("- 信息完整度提示：已基于当前可确认的身高体重完成 BMI 判断，仍建议结合测量时间复核。")
    lines.extend([
        "",
        "四、体重变化与一致性梳理",
    ])
    lines.extend(f"- {item}" for item in trend_lines)
    lines.extend([
        "",
        "五、相关健康风险线索识别",
    ])
    lines.extend(f"- {item}" for item in risk_lines)
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
