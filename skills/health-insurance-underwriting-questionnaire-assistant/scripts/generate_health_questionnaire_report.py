#!/usr/bin/env python3
"""将健康险投保问卷整理为标准化分析报告。"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


SYSTEM_KEYWORDS = {
    "心血管系统": ["高血压", "冠心病", "心律失常", "心电图", "心脏"],
    "呼吸系统": ["肺结节", "哮喘", "肺部", "胸部", "呼吸"],
    "消化系统": ["肝炎", "肝功能", "脂肪肝", "胆囊", "胃", "肠"],
    "肾脏与泌尿系统": ["蛋白尿", "血尿", "肾功能", "肾炎", "肾结石"],
    "内分泌系统": ["糖尿病", "血糖", "甲状腺", "甲功", "高尿酸"],
    "肿瘤与占位性病变": ["肿瘤", "癌", "结节", "肿块", "包块", "占位"],
    "神经精神系统": ["脑梗", "脑出血", "癫痫", "抑郁", "焦虑", "精神"],
}

VISIT_KEYWORDS = {
    "门诊情况": ["门诊", "复诊", "就诊"],
    "住院情况": ["住院", "出院"],
    "手术情况": ["手术", "切除", "术后"],
    "检查异常": ["体检", "彩超", "CT", "MRI", "影像", "化验", "指标", "异常"],
    "随访复查": ["复查", "随访", "监测"],
}

MEDICATION_KEYWORDS = ["服药", "用药", "降压药", "降糖药", "长期服用", "长期用药"]
HIGH_RISK_KEYWORDS = ["肿瘤", "癌", "住院", "手术", "长期服药", "长期用药", "复查", "异常", "结节", "包块", "占位"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成健康险问卷分析报告")
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


def collect_system_risks(text: str) -> list[str]:
    findings = []
    for system, keywords in SYSTEM_KEYWORDS.items():
        hits = [keyword for keyword in keywords if keyword in text]
        if hits:
            findings.append(f"{system}：识别到 {('、'.join(hits))} 相关线索，需结合诊断、时间和当前状态进一步判断。")
    return findings


def collect_health_points(text: str) -> list[str]:
    points = []
    keywords = ["病史", "住院", "手术", "体检", "异常", "结节", "服药", "复查", "随访", "门诊"]
    for keyword in keywords:
        if keyword in text:
            if keyword == "病史":
                points.append("问卷存在既往病史相关描述，建议结合具体诊断名称理解。")
            elif keyword == "异常":
                points.append("问卷出现检查或健康异常线索，但需核实具体项目和结果。")
            else:
                points.append(f"问卷涉及“{keyword}”相关信息，需结合时间、原因和当前状态判断。")
    return list(dict.fromkeys(points))


def collect_visits(text: str) -> dict[str, str]:
    result = {}
    for title, keywords in VISIT_KEYWORDS.items():
        hits = [keyword for keyword in keywords if keyword in text]
        result[title] = f"识别到 {('、'.join(hits))} 相关线索，需结合具体时间、原因和结论核实。" if hits else "未见明确相关信息，或当前材料不足以确认。"
    return result


def collect_medication(text: str) -> list[str]:
    hits = [keyword for keyword in MEDICATION_KEYWORDS if keyword in text]
    if not hits:
        return []
    return [f"识别到 {('、'.join(hits))} 相关线索，需核实药物名称、用药时长、频率及控制情况。"]


def build_summary(text: str, system_risks: list[str], medication: list[str]) -> list[str]:
    summary = []
    if system_risks:
        summary.append("已识别出需要重点关注的健康异常或检查异常，建议结合补问或补件进一步判断。")
    else:
        summary.append("当前未见明确重大健康异常线索，但仍需结合材料完整度审视。")
    if medication or any(word in text for word in ["复查", "随访", "住院", "手术", "结节", "异常"]):
        summary.append("问卷中存在持续管理、复查或异常线索，建议重点核实当前状态。")
    if any(word in text for word in HIGH_RISK_KEYWORDS):
        summary.append("存在可能影响健康险核保判断的高风险健康信号，建议补问或重点人工审核。")
    return summary[:3]


def build_followups(text: str) -> list[str]:
    questions = []
    if any(word in text for word in ["结节", "肿块", "包块", "占位"]):
        questions.append("请补充异常结节或占位的发现时间、部位、检查结论、分级情况及最近一次复查结果。")
    if any(word in text for word in ["高血压", "糖尿病", "长期服药", "长期用药", "降压药", "降糖药"]):
        questions.append("请补充慢病或长期用药的确诊时间、药物名称、用药时长、控制情况及最近一次复查结果。")
    if any(word in text for word in ["住院", "手术"]):
        questions.append("请补充住院或手术的时间、原因、诊断名称、治疗经过及当前恢复情况。")
    if any(word in text for word in ["体检", "异常", "彩超", "CT", "MRI", "化验", "指标"]):
        questions.append("请补充异常检查项目名称、检查时间、异常程度、医生建议及后续复查情况。")
    if any(word in text for word in ["门诊", "复查", "随访", "监测"]):
        questions.append("请说明是否仍在门诊随访或长期监测，并补充最近一次随访时间及结论。")
    if not questions:
        questions.append("当前材料未见明确补问方向，建议核对原件后再做人工审查。")
    return questions


def build_next_steps(text: str, system_risks: list[str], medication: list[str]) -> list[str]:
    steps = []
    if system_risks or medication or any(word in text for word in ["复查", "异常", "住院", "手术"]):
        steps.append("建议补充说明关键病史、检查异常或治疗经过后再做进一步判断。")
    if any(word in text for word in ["结节", "住院", "手术", "长期服药", "长期用药", "肿瘤", "癌", "占位"]):
        steps.append("建议补充近期复查、出院小结、影像或化验结论等相关材料。")
        steps.append("建议重点人工审核，并结合其他医疗资料进一步判断。")
    if not steps:
        steps.append("当前可进入下一环节核保审查。")
    steps.append("本结果仅用于健康险问卷分析与补问准备，不替代正式核保决定。")
    return steps


def render_report(data: dict[str, Any]) -> str:
    text = data.get("_raw_text", "")
    basic = extract_basic_info(data)
    health_points = collect_health_points(text)
    system_risks = collect_system_risks(text)
    visits = collect_visits(text)
    medication = collect_medication(text)
    summary = build_summary(text, system_risks, medication)
    followups = build_followups(text)
    next_steps = build_next_steps(text, system_risks, medication)

    abnormal_items = system_risks + medication
    if not abnormal_items:
        abnormal_items = ["当前未识别到明确异常病史或高风险健康线索，或材料不足以确认。"]

    focus_lines = []
    if any(word in text for word in HIGH_RISK_KEYWORDS):
        focus_lines.append("问卷存在结节、异常检查、住院手术或长期管理等健康信号，需进一步核实具体诊断、时间和当前状态。")
    if "未说明" in text or "不明确" in text or "待查" in text:
        focus_lines.append("部分健康信息表述不完整，当前不足以支持完整健康险核保判断。")
    if not focus_lines:
        focus_lines.append("当前未见明确高风险健康信号，但仍需结合原件和材料完整度复核。")

    lines = [
        "# 健康险问卷分析结果",
        "",
        "一、问卷基本信息",
        f"- 险种/产品：{basic['insurance_type']} / {basic['product_name']}",
        f"- 被保人基本信息：{basic['insured_info']}",
        f"- 问卷类型：{basic['questionnaire_type']}",
        f"- 材料来源或文本类型：{basic['source_type']}",
        "",
        "二、健康险核保结论摘要",
    ]
    lines.extend(f"- {item}" for item in summary)
    lines.extend([
        "",
        "三、健康告知要点提取",
    ])
    lines.extend(f"- {item}" for item in (health_points or ["当前可确认的健康告知要点有限，建议核对原始问卷。"]))
    lines.extend([
        "",
        "四、异常病史与健康风险识别",
    ])
    lines.extend(f"- {item}" for item in abnormal_items)
    lines.extend([
        "",
        "五、就医与检查情况梳理",
        f"- 门诊情况：{visits['门诊情况']}",
        f"- 住院情况：{visits['住院情况']}",
        f"- 手术情况：{visits['手术情况']}",
        f"- 体检或专项检查异常：{visits['检查异常']}",
        f"- 随访复查或长期监测情况：{visits['随访复查']}",
        "",
        "六、高风险健康信号与核保关注点",
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
