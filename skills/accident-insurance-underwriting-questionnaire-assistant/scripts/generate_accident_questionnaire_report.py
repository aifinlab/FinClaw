#!/usr/bin/env python3
"""将意外险投保问卷整理为标准化分析报告。"""

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
    "职业风险": ["施工", "高空", "井下", "海上", "危化", "电力", "设备", "机械", "外勤"],
    "活动风险": ["潜水", "攀岩", "跳伞", "赛车", "滑雪", "登山", "越野", "探险", "竞技"],
    "出行风险": ["驾驶", "长途", "出差", "海外", "摩托", "货运", "客运"],
    "免责边界风险": ["酒后驾驶", "无证", "非法作业", "涉爆", "涉毒", "涉危"],
}

TRAVEL_SECTIONS = {
    "驾驶频率或交通工具使用情况": ["驾驶", "自驾", "摩托", "车辆", "交通工具"],
    "长途运输或频繁出差情况": ["长途", "运输", "出差", "外勤"],
    "海外或特殊地区出行情况": ["海外", "境外", "特殊地区"],
    "与意外暴露相关的其他出行情形": ["海上", "井下", "高空", "特殊交通工具"],
}

HIGH_RISK_WORDS = [
    "施工", "高空", "井下", "海上", "危化", "设备", "机械", "攀岩", "滑雪", "驾驶", "长途", "无证"
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成意外险问卷分析报告")
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
            findings.append(f"{topic}：识别到 {('、'.join(hits))} 相关线索，需结合频率、环境、作业方式和当前状态进一步判断。")
    return findings


def extract_key_points(text: str) -> list[str]:
    points = []
    mapping = [
        ("施工", "问卷涉及施工或现场作业线索，需核实岗位职责和是否直接参与危险作业。"),
        ("高空", "问卷涉及高空或登高线索，需核实作业高度、频率和安全防护情况。"),
        ("外勤", "问卷涉及外勤或出差线索，需核实频率、地点和出行方式。"),
        ("驾驶", "问卷涉及驾驶线索，需核实驾驶频率、车型和是否营运。"),
        ("攀岩", "问卷涉及危险活动线索，需核实参与频率、性质和安全环境。"),
        ("滑雪", "问卷涉及危险活动线索，需核实参与频率、性质和安全环境。"),
        ("设备", "问卷涉及设备或机械环境线索，需核实是否直接操作和危险暴露程度。"),
    ]
    for keyword, message in mapping:
        if keyword in text:
            points.append(message)
    return list(dict.fromkeys(points))


def collect_travel_info(text: str) -> dict[str, str]:
    result = {}
    for title, keywords in TRAVEL_SECTIONS.items():
        hits = [keyword for keyword in keywords if keyword in text]
        result[title] = f"识别到 {('、'.join(hits))} 相关线索，需结合频率、用途和暴露程度核实。" if hits else "未见明确相关信息，或当前材料不足以确认。"
    return result


def build_summary(text: str, topic_risks: list[str]) -> list[str]:
    summary = []
    if topic_risks:
        summary.append("已识别出需重点关注的职业、活动或出行暴露风险，建议结合补问或补件进一步判断。")
    else:
        summary.append("当前未见明确高风险职业或活动事实，但仍需结合材料完整度审视。")
    if any(word in text for word in ["施工", "高空", "外勤", "驾驶", "长途", "攀岩", "滑雪"]):
        summary.append("问卷中存在职业环境、危险活动或出行暴露线索，建议重点核实频率、环境和作业方式。")
    if any(word in text for word in HIGH_RISK_WORDS):
        summary.append("存在可能显著影响意外险核保判断的高风险信号，建议补问、补件或重点人工审核。")
    return summary[:3]


def build_followups(text: str) -> list[str]:
    questions = []
    if any(word in text for word in ["施工", "高空", "井下", "海上", "设备", "机械"]):
        questions.append("请补充当前岗位职责、是否直接参与危险作业、作业环境、作业频率以及是否接触高空、机械、危化品或其他危险源。")
    if any(word in text for word in ["驾驶", "长途", "货运", "客运", "摩托"]):
        questions.append("请补充驾驶或出行情况，包括驾驶频率、车型、是否营运、是否长途以及是否存在高频骑行或特殊交通工具使用。")
    if any(word in text for word in ["攀岩", "滑雪", "潜水", "跳伞", "赛车", "登山", "探险", "竞技"]):
        questions.append("请补充危险活动或兴趣爱好的参与频率、活动性质、是否竞技或商业性质、活动地点及安全防护情况。")
    if any(word in text for word in ["无证", "酒后驾驶", "非法作业", "涉危"]):
        questions.append("请补充相关作业或驾驶是否具备合法资质、是否存在违规操作或特殊危险环境暴露。")
    if not questions:
        questions.append("当前材料未见明确补问方向，建议核对原件后再做人工审查。")
    return questions


def build_next_steps(text: str, topic_risks: list[str]) -> list[str]:
    steps = []
    if topic_risks or any(word in text for word in ["施工", "高空", "驾驶", "活动", "外勤", "设备"]):
        steps.append("建议补充说明关键职业职责、活动频率、出行方式和作业环境后再做进一步判断。")
    if any(word in text for word in ["高空", "井下", "海上", "危化", "攀岩", "滑雪", "驾驶", "长途", "无证"]):
        steps.append("建议补充职业说明、活动说明或资质说明等相关材料。")
        steps.append("建议重点人工审核，并进一步核实职业分级、活动频率或作业环境。")
    if not steps:
        steps.append("当前可进入下一环节核保审查。")
    steps.append("本结果仅用于意外险问卷分析与补问准备，不替代正式核保决定。")
    return steps


def render_report(data: dict[str, Any]) -> str:
    text = data.get("_raw_text", "")
    basic = extract_basic_info(data)
    topic_risks = collect_topic_risks(text)
    key_points = extract_key_points(text)
    travel_info = collect_travel_info(text)
    summary = build_summary(text, topic_risks)
    followups = build_followups(text)
    next_steps = build_next_steps(text, topic_risks)

    abnormal_items = topic_risks or ["当前未识别到明确高危职业、危险活动或特殊意外暴露线索，或材料不足以确认。"]

    focus_lines = []
    if any(word in text for word in HIGH_RISK_WORDS):
        focus_lines.append("问卷存在高危作业环境、危险活动、驾驶或特殊暴露等高关注线索，需进一步核实频率、作业方式和风险边界。")
    if "未说明" in text or "不明确" in text or "偶尔" in text:
        focus_lines.append("部分职业或活动信息表述不完整，当前不足以支持完整意外险核保判断。")
    if not focus_lines:
        focus_lines.append("当前未见明确高关注意外风险信号，但仍需结合原件和材料完整度复核。")

    lines = [
        "# 意外险问卷分析结果",
        "",
        "一、问卷基本信息",
        f"- 险种/产品：{basic['insurance_type']} / {basic['product_name']}",
        f"- 被保人基本信息：{basic['insured_info']}",
        f"- 问卷类型：{basic['questionnaire_type']}",
        f"- 材料来源或文本类型：{basic['source_type']}",
        "",
        "二、意外险核保结论摘要",
    ]
    lines.extend(f"- {item}" for item in summary)
    lines.extend([
        "",
        "三、职业与工作信息要点提取",
    ])
    lines.extend(f"- {item}" for item in (key_points or ["当前可确认的职业与工作信息要点有限，建议核对原始问卷。"]))
    lines.extend([
        "",
        "四、职业风险与活动风险识别",
    ])
    lines.extend(f"- {item}" for item in abnormal_items)
    lines.extend([
        "",
        "五、出行与交通风险梳理",
        f"- 驾驶频率或交通工具使用情况：{travel_info['驾驶频率或交通工具使用情况']}",
        f"- 长途运输或频繁出差情况：{travel_info['长途运输或频繁出差情况']}",
        f"- 海外或特殊地区出行情况：{travel_info['海外或特殊地区出行情况']}",
        f"- 与意外暴露相关的其他出行情形：{travel_info['与意外暴露相关的其他出行情形']}",
        "",
        "六、高风险意外信号与核保关注点",
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
