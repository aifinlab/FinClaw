#!/usr/bin/env python3
"""将吸烟饮酒相关资料整理为标准化风险识别结果。"""

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
    "吸烟风险": ["吸烟", "长期吸烟", "戒烟", "复吸", "20年", "每天", "包", "支"],
    "饮酒风险": ["饮酒", "每周", "每日", "应酬", "大量", "戒酒", "复饮"],
    "一致性风险": ["体检", "病史", "不一致", "冲突", "称已戒烟", "备注"],
    "相关健康风险": ["肝功能", "高血压", "肺", "呼吸", "脂肪肝", "心血管", "睡眠"],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成吸烟饮酒风险识别报告")
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
    for key in ["smoking_status", "alcohol_status", "duration_info", "source_type", "context_text"]:
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
        "smoking_status": str(data.get("smoking_status") or "未明确"),
        "alcohol_status": str(data.get("alcohol_status") or "未明确"),
        "duration_info": str(data.get("duration_info") or "未明确"),
        "source_type": str(data.get("source_type") or "未明确"),
    }


def collect_topic_risks(text: str) -> list[str]:
    findings = []
    for topic, keywords in RISK_TOPICS.items():
        hits = [keyword for keyword in keywords if keyword in text]
        if hits:
            findings.append(f"{topic}：识别到 {('、'.join(hits))} 相关线索，需结合频率、剂量、持续时间和真实性进一步判断。")
    return findings


def extract_behavior_points(text: str) -> list[str]:
    points = []
    if "吸烟" in text:
        points.append("资料存在吸烟行为线索，需核实当前是否持续吸烟、日均数量和持续年限。")
    if "饮酒" in text:
        points.append("资料存在饮酒行为线索，需核实频率、单次量、年限及是否属于长期高频饮酒。")
    if any(word in text for word in ["戒烟", "戒酒", "复吸", "复饮"]):
        points.append("资料存在戒断或复吸复饮线索，提示当前状态与历史暴露均需进一步核实。")
    if any(word in text for word in ["偶尔", "应酬", "不多", "较多"]):
        points.append("资料存在表述模糊的生活习惯描述，需进一步量化频率和强度。")
    return points or ["当前可确认的吸烟饮酒行为信息有限，建议补充生活习惯描述。"]


def build_pattern_lines(text: str) -> list[str]:
    lines = []
    if any(word in text for word in ["长期吸烟", "20年", "每天", "包", "支"]):
        lines.append("资料存在长期或高强度吸烟线索，需重点关注暴露年限和当前状态。")
    if any(word in text for word in ["每周", "每日", "大量", "应酬"]):
        lines.append("资料存在高频或长期饮酒线索，需进一步核实饮酒量和持续时间。")
    if any(word in text for word in ["戒烟", "戒酒", "3个月", "短期"]):
        lines.append("资料存在近期戒断线索，需关注是否已稳定戒断以及是否存在复吸复饮风险。")
    if any(word in text for word in ["体检", "病史", "不一致", "冲突", "备注"]):
        lines.append("资料存在前后记录交叉线索，需核验吸烟饮酒信息是否一致。")
    return lines or ["当前未见明确高风险模式或一致性问题描述，或材料不足以判断。"]


def build_health_risk_lines(text: str) -> list[str]:
    lines = []
    if any(word in text for word in ["肺", "呼吸", "咳嗽"]):
        lines.append("资料存在肺部或呼吸系统相关线索，需关注与吸烟暴露的关联。")
    if any(word in text for word in ["高血压", "心血管"]):
        lines.append("资料存在心血管相关线索，需关注吸烟或饮酒对心血管风险的叠加影响。")
    if any(word in text for word in ["肝功能", "脂肪肝", "转氨酶"]):
        lines.append("资料存在肝功能或代谢相关线索，需关注长期饮酒可能带来的健康风险。")
    if any(word in text for word in ["睡眠", "消化", "胃"]):
        lines.append("资料存在睡眠或消化系统相关线索，建议结合生活方式因素进一步核实。")
    return lines or ["当前未见明确相关健康风险线索，或材料不足以确认。"]


def build_summary(text: str, topic_risks: list[str]) -> list[str]:
    summary = []
    if topic_risks:
        summary.append("已识别出需重点关注的生活习惯风险模式或一致性问题，建议结合补问或补件进一步判断。")
    else:
        summary.append("当前未见明确高关注吸烟饮酒风险事实，但仍需结合材料完整度审视。")
    if any(word in text for word in ["长期吸烟", "20年", "每周", "大量", "应酬"]):
        summary.append("资料中存在长期或高频吸烟饮酒线索，建议重点核实暴露强度、持续时间和当前状态。")
    if any(word in text for word in ["戒烟", "戒酒", "不一致", "肝功能", "高血压"]):
        summary.append("资料中存在近期戒断、信息不一致或伴随健康异常线索，建议补充相关说明和体检依据。")
    return summary[:3]


def build_followups(text: str) -> list[str]:
    questions = []
    if "吸烟" in text:
        questions.append("请补充当前是否仍吸烟、日均数量、持续年限、烟草类型以及戒烟时间或复吸情况。")
    if "饮酒" in text or any(word in text for word in ["每周", "应酬", "大量"]):
        questions.append("请补充饮酒频率、单次量、酒精类型、持续年限以及是否存在近期戒酒或复饮情况。")
    if any(word in text for word in ["体检", "病史", "不一致", "冲突", "备注", "称已戒烟"]):
        questions.append("请核实不同资料中的吸烟饮酒信息是否一致，并补充真实性说明或最新状态说明。")
    if any(word in text for word in ["肝功能", "高血压", "肺", "呼吸", "脂肪肝", "心血管"]):
        questions.append("请补充相关体检报告、门诊记录或慢病资料，以支持生活习惯与健康风险的关联判断。")
    return questions or ["当前材料未见明确补查方向，建议核对原件后再做人工审查。"]


def build_next_steps(text: str, topic_risks: list[str]) -> list[str]:
    steps = []
    if topic_risks or any(word in text for word in ["吸烟", "饮酒", "戒烟", "戒酒", "不一致"]):
        steps.append("建议补充说明吸烟饮酒频率、强度、持续年限、当前状态及资料一致性后再做进一步判断。")
    if any(word in text for word in ["长期吸烟", "每周", "大量", "戒烟", "戒酒", "肝功能", "高血压", "肺"]):
        steps.append("建议补充体检报告、门诊记录、健康说明或生活习惯补充材料等相关资料。")
        steps.append("建议重点人工审核，并结合体检、慢病资料、门诊记录或专项检查进一步判断。")
    if not steps:
        steps.append("当前可进入下一环节核保审查。")
    steps.append("本结果仅用于吸烟饮酒风险识别与补查准备，不替代正式核保决定。")
    return steps


def render_report(data: dict[str, Any]) -> str:
    text = data.get("_raw_text", "")
    basic = extract_basic_info(data)
    topic_risks = collect_topic_risks(text)
    behavior_points = extract_behavior_points(text)
    pattern_lines = build_pattern_lines(text)
    health_risk_lines = build_health_risk_lines(text)
    summary = build_summary(text, topic_risks)
    followups = build_followups(text)
    next_steps = build_nextSteps(text, topic_risks)

    focus_lines = []
    if any(word in text for word in ["长期吸烟", "20年", "每周", "应酬", "大量"]):
        focus_lines.append("资料存在长期或高强度生活习惯暴露线索，需重点核实暴露水平和持续时间。")
    if any(word in text for word in ["戒烟", "戒酒", "3个月", "不一致", "冲突"]):
        focus_lines.append("资料存在近期戒断或信息不一致线索，提示当前状态和真实性仍需进一步核实。")
    if any(word in text for word in ["肝功能", "高血压", "肺", "呼吸", "脂肪肝", "心血管"]):
        focus_lines.append("吸烟饮酒行为同时伴随相关健康异常线索，可能提高核保关注度。")
    if not focus_lines:
        focus_lines.append("当前未见明确高关注吸烟饮酒风险信号，但仍需结合原件和材料完整度复核。")

    lines = [
        "# 吸烟饮酒风险识别结果",
        "",
        "一、生活习惯基本信息",
        f"- 被保人基本信息：{basic['person_info']}",
        f"- 吸烟情况：{basic['smoking_status']}",
        f"- 饮酒情况：{basic['alcohol_status']}",
        f"- 起始时间/持续年限：{basic['duration_info']}",
        f"- 材料来源或文本类型：{basic['source_type']}",
        "",
        "二、吸烟饮酒风险识别结论摘要",
    ]
    lines.extend(f"- {item}" for item in summary)
    lines.extend([
        "",
        "三、吸烟行为与饮酒行为要点提取",
    ])
    lines.extend(f"- {item}" for item in behavior_points)
    lines.extend([
        "",
        "四、高风险模式与一致性问题识别",
    ])
    lines.extend(f"- {item}" for item in pattern_lines)
    lines.extend(f"- {item}" for item in topic_risks[:3])
    lines.extend([
        "",
        "五、关联健康风险线索梳理",
    ])
    lines.extend(f"- {item}" for item in health_risk_lines)
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


def build_nextSteps(text: str, topic_risks: list[str]) -> list[str]:
    return build_next_steps(text, topic_risks)


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
