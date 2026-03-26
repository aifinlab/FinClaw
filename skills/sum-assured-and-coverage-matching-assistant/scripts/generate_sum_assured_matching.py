  # !/usr/bin/env python3
"""将投保方案整理为保额责任匹配分析结果。"""

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
    "家庭责任与保障目标": ["子女", "赡养", "房贷", "家庭责任", "教育", "养老", "家庭主要收入"],
    "收入与缴费能力": ["收入", "年收入", "负债", "房贷", "车贷", "缴费", "保费", "资金来源"],
    "健康职业生活习惯风险": ["病史", "体检", "脂肪肝", "慢病", "职业", "高危", "吸烟", "饮酒"],
    "既有保障结构": ["已有", "保单", "团体医疗", "重疾险", "寿险", "意外险", "年金险"],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成保额责任匹配分析结果")
    parser.add_argument("--input", required=True, help="输入文件路径，支持 txt、md、json")
    parser.add_argument("--format", choices=["auto", "text", "json"], default="auto")
    return parser.parse_args()


def load_input(path: Path, input_format: str) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8-sig")
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
    for key in ["product_name", "insured_info", "coverage_info", "payment_plan", "source_type", "context_text"]:
        value = data.get(key)
        if value not in (None, ""):
            parts.append(str(value))
    notes = data.get("notes")
    if isinstance(notes, list):
        parts.extend(str(item) for item in notes if item)
    return "\n".join(parts)


def extract_basic_info(data: dict[str, Any]) -> dict[str, str]:
    return {
        "product_name": str(data.get("product_name") or "未明确"),
        "insured_info": str(data.get("insured_info") or "未明确"),
        "coverage_info": str(data.get("coverage_info") or "未明确"),
        "payment_plan": str(data.get("payment_plan") or "未明确"),
        "source_type": str(data.get("source_type") or "未明确"),
    }


def collect_topic_hits(text: str) -> dict[str, list[str]]:
    findings: dict[str, list[str]] = {}
    for topic, keywords in RISK_TOPICS.items():
        hits = [keyword for keyword in keywords if keyword in text]
        if hits:
            findings[topic] = list(dict.fromkeys(hits))
    return findings


def build_summary(text: str, findings: dict[str, list[str]]) -> list[str]:
    summary = []
    if any(word in text for word in ["房贷", "子女", "家庭主要收入"]) and any(word in text for word in ["寿险", "80万", "保额"]):
        summary.append("当前方案与客户家庭责任之间存在需要重点审视的保额匹配问题，建议结合收入、负债和既有保障进一步核查。")
    elif findings:
        summary.append("已识别出需要重点关注的保额或责任匹配问题，建议结合补问或补件进一步判断。")
    else:
        summary.append("当前未见明确配置失衡信号，但仍需结合资料完整度复核。")
    if any(word in text for word in ["已有", "保单", "团体医疗", "重疾险"]):
        summary.append("现有资料显示既有保障对当前方案存在影响，需进一步判断是否存在缺口、重叠或结构失衡。")
    if any(word in text for word in ["收入", "缴费", "房贷", "负债"]):
        summary.append("当前方案的保额与缴费安排仍需结合收入和负债情况综合判断，建议进一步确认财务适配性。")
    return summary[:3]


def build_need_points(findings: dict[str, list[str]]) -> list[str]:
    lines = []
    if findings.get("家庭责任与保障目标"):
        lines.append("家庭责任与保障目标：资料显示存在家庭责任、教育支出、房贷或收入替代需求，需重点关注核心保障是否覆盖。")
    if findings.get("收入与缴费能力"):
        lines.append("收入与缴费能力：资料中存在收入、负债或缴费能力相关线索，需结合长期支付能力判断方案适配性。")
    if findings.get("健康职业生活习惯风险"):
        lines.append("健康、职业或生活习惯风险：现有风险线索可能影响责任配置的优先级和保障侧重点。")
    if not lines:
        lines.append("当前可确认的客户需求与风险特征信息有限，需补充家庭责任、收入和保障目标说明。")
    return lines


def build_matching_lines(text: str) -> list[str]:
    lines = []
    if any(word in text for word in ["房贷", "子女", "家庭主要收入"]) and "寿险" in text:
        lines.append("保额问题：寿险责任与家庭责任存在直接关联，当前保额是否足以覆盖收入替代和负债风险仍需进一步核实。")
    if any(word in text for word in ["重疾险", "重大疾病", "脂肪肝", "病史", "体检"]):
        lines.append("责任问题：当前重大疾病责任需结合健康风险和既有重疾保障判断是否存在明显缺口或覆盖不足。")
    if any(word in text for word in ["团体医疗", "医疗", "附加住院医疗"]):
        lines.append("责任问题：医疗责任已存在既有配置或附加责任线索，需判断是否为补充覆盖还是责任重复。")
    if not lines:
        lines.append("当前未见可直接确认的保额或责任错配问题，或现有信息不足以支持完整判断。")
    return lines


def build_structure_lines(text: str) -> list[str]:
    lines = []
    if any(word in text for word in ["已有", "保单", "团体医疗", "重疾险"]):
        lines.append("已有保单对当前方案存在明显影响，需核实当前配置是在补保障缺口还是形成责任重叠。")
    if any(word in text for word in ["无单独寿险", "无寿险"]):
        lines.append("既有保障结构中寿险保障可能偏弱，当前方案需重点确认是否足以匹配家庭责任。")
    if any(word in text for word in ["团体医疗", "附加住院医疗"]):
        lines.append("医疗责任可能存在结构性叠加，需确认当前责任是否与既有医疗保障形成重复或互补。")
    return lines or ["当前无法完整确认既有保障结构，建议补充既有保单明细后再判断是否存在结构性错配。"]


def build_focus_lines(text: str) -> list[str]:
    lines = []
    if any(word in text for word in ["高额", "保额"]):
        lines.append("存在需要关注的保额匹配问题，需结合收入、家庭责任和既有保障进一步判断是否合理。")
    if any(word in text for word in ["收入", "房贷", "负债", "缴费"]):
        lines.append("存在缴费能力或财务适配性关注点，需进一步确认收入稳定性、负债压力和持续缴费能力。")
    if any(word in text for word in ["病史", "体检", "脂肪肝", "职业"]):
        lines.append("现有风险特征可能影响责任配置的适配性，需关注责任是否与主要风险方向匹配。")
    if any(word in text for word in ["已有", "保单", "团体医疗", "重疾险"]):
        lines.append("既有保障结构可能影响当前方案的必要性和配置平衡，需进一步核实是否存在责任重叠或缺口。")
    return lines or ["当前未见必须单列的高关注配置问题，但仍需结合原件和背景信息复核。"]


def build_followups(text: str) -> list[str]:
    questions = []
    questions.append("请补充客户当前收入水平、收入稳定性、主要负债情况及长期缴费承受能力说明。")
    questions.append("请补充客户家庭责任情况，包括配偶、子女、赡养责任和当前主要保障目标。")
    if any(word in text for word in ["已有", "保单", "团体医疗", "重疾险", "寿险"]):
        questions.append("请补充既有保单明细，包括险种、保额、责任范围和当前有效状态。")
    if any(word in text for word in ["病史", "体检", "脂肪肝", "职业"]):
        questions.append("请补充健康、职业或其他风险资料，以支持责任配置与风险特征的进一步匹配判断。")
    return questions


def build_next_steps(text: str) -> list[str]:
    steps = ["建议补充说明客户收入、家庭责任、既有保障和主要保障目标后再形成稳定匹配判断。"]
    if any(word in text for word in ["房贷", "收入", "已有", "保单", "病史", "职业"]):
        steps.append("建议补件并进一步确认收入、需求、责任选择或既有保障情况。")
        steps.append("建议重点人工审核，必要时内部先完成结构性核查后再开展业务沟通。")
    else:
        steps.append("当前可进入下一环节审查或沟通，但仍应保留对信息完整度的复核。")
    steps.append("本结果仅用于保额责任匹配分析与内部协同，不替代正式销售或核保结论。")
    return steps


def render_report(data: dict[str, Any]) -> str:
    text = data.get("_raw_text", "")
    basic = extract_basic_info(data)
    findings = collect_topic_hits(text)
    summary = build_summary(text, findings)
    need_points = build_need_points(findings)
    matching_lines = build_matching_lines(text)
    structure_lines = build_structure_lines(text)
    focus_lines = build_focus_lines(text)
    followups = build_followups(text)
    next_steps = build_next_steps(text)

    lines = [
        "  # 保额责任匹配分析结果",
        "",
        "一、方案基本信息",
        f"- 产品/险种：{basic['product_name']}",
        f"- 投保对象基本信息：{basic['insured_info']}",
        f"- 保额与主要责任：{basic['coverage_info']}",
        f"- 缴费方式或期限：{basic['payment_plan']}",
        f"- 材料来源或文本类型：{basic['source_type']}",
        "",
        "二、保额责任匹配结论摘要",
    ]
    lines.extend(f"- {item}" for item in summary)
    lines.extend(["", "三、客户需求与风险特征要点提取"])
    lines.extend(f"- {item}" for item in need_points)
    lines.extend(["", "四、保额匹配性与责任配置梳理"])
    lines.extend(f"- {item}" for item in matching_lines)
    lines.extend(["", "五、既有保障与结构性错配识别"])
    lines.extend(f"- {item}" for item in structure_lines)
    lines.extend(["", "六、核保关注点与风险提示"])
    lines.extend(f"- {item}" for item in focus_lines)
    lines.extend(["", "七、建议补充核实的问题或资料"])
    lines.extend(f"- {item}" for item in followups)
    lines.extend(["", "八、后续处理建议"])
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
