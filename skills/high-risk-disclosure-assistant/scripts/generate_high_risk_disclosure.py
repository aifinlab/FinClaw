#!/usr/bin/env python3
"""将核保相关风险资料整理为高风险告知结果。"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

RISK_TOPICS = {
    "健康风险事项": ["病史", "住院", "手术", "复查", "随访", "结节", "肿瘤", "慢病", "长期用药", "异常"],
    "职业风险事项": ["职业", "施工", "高空", "驾驶", "运输", "差旅", "危险", "现场"],
    "生活习惯风险事项": ["吸烟", "饮酒", "戒烟", "戒酒", "生活习惯"],
    "投保行为或财务合理性风险事项": ["高额", "保单", "收入", "资金来源", "投保目的", "集中投保"],
    "免责或责任边界相关风险事项": ["免责", "责任", "边界", "条款", "不能确定", "需核实"],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成高风险告知整理结果")
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
    for key in ["product_name", "scenario", "risk_source", "source_type", "context_text"]:
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
        "product_name": str(data.get("product_name") or "未明确"),
        "scenario": str(data.get("scenario") or "未明确"),
        "risk_source": str(data.get("risk_source") or "未明确"),
        "source_type": str(data.get("source_type") or "未明确"),
    }


def collect_topic_risks(text: str) -> dict[str, list[str]]:
    findings: dict[str, list[str]] = {}
    for topic, keywords in RISK_TOPICS.items():
        hits = [keyword for keyword in keywords if keyword in text]
        if hits:
            findings[topic] = list(dict.fromkeys(hits))
    return findings


def build_summary(text: str, findings: dict[str, list[str]]) -> list[str]:
    summary = []
    if findings:
        summary.append("已识别出需要重点提示的高风险事项，建议按优先级整理后用于业务沟通和内部留痕。")
    else:
        summary.append("当前未见可直接提炼的明确高风险事项，但仍需结合资料完整度进一步复核。")
    if any(word in text for word in ["需核实", "边界", "条款", "不能确定", "冲突", "不一致"]):
        summary.append("资料中存在边界不清或需谨慎表述的问题，沟通时应明确保留核查边界。")
    if any(word in text for word in ["补充", "补件", "复查", "收入说明", "职业说明"]):
        summary.append("当前资料仍存在补充确认空间，建议先完成关键补问或补件后再形成完整沟通口径。")
    return summary[:3]


def build_risk_items(findings: dict[str, list[str]], text: str) -> list[str]:
    lines = []
    topic_order = [
        "健康风险事项",
        "职业风险事项",
        "生活习惯风险事项",
        "投保行为或财务合理性风险事项",
        "免责或责任边界相关风险事项",
    ]
    for topic in topic_order:
        hits = findings.get(topic)
        if hits:
            lines.append(f"{topic}：识别到 {'、'.join(hits)} 相关线索，建议纳入重点告知范围。")
    if not lines:
        lines.append("当前资料中未能确认明确高风险事项，或现有信息不足以支持完整告知整理。")
    return lines


def build_priority_lines(text: str, findings: dict[str, list[str]]) -> list[str]:
    lines = []
    if findings.get("健康风险事项") or findings.get("职业风险事项"):
        lines.append("必须优先明确说明的事项：健康高风险或职业高风险线索，以及其对后续核保审查的重要性。")
    if any(word in text for word in ["补充", "复查", "收入说明", "职业说明", "需核实"]):
        lines.append("需要补充确认后再沟通的事项：资料未闭环、关键背景缺失或需内部先核查的问题。")
    if any(word in text for word in ["免责", "责任", "条款", "边界", "不能确定"]):
        lines.append("边界不清但建议提醒的事项：可能涉及责任或条款边界的问题，沟通时需保留边界，避免确定性表述。")
    return lines or ["当前优先级判断依据有限，建议先补充主要风险来源和业务场景。"]


def build_communication_points(text: str, findings: dict[str, list[str]]) -> list[str]:
    lines = []
    if findings:
        lines.append("业务人员需重点说明：当前资料中已识别出需要重点关注的风险事项，后续判断仍以正式核保审核为准。")
    if findings.get("健康风险事项"):
        lines.append("需要向客户确认的问题：相关病史、复查、治疗或异常检查是否已有最新结果，是否还有未补充资料。")
    if findings.get("职业风险事项"):
        lines.append("需要向客户确认的问题：申报职业是否与实际岗位、作业场景和差旅情况一致，是否存在兼职或额外暴露。")
    if findings.get("投保行为或财务合理性风险事项"):
        lines.append("容易遗漏或误解的部分：高额投保、既有保单、收入或资金来源问题不能仅凭单一材料直接定性。")
    lines.append("需保留边界的部分：不得将风险提示直接表述为最终承保结论、免责结论或条款解释。")
    return lines


def build_compliance_lines(text: str, findings: dict[str, list[str]]) -> list[str]:
    lines = []
    if findings.get("健康风险事项"):
        lines.append("存在高风险健康问题线索，后续可能影响核保判断，建议先完成资料核查。")
    if findings.get("职业风险事项"):
        lines.append("存在危险职业或高暴露作业线索，需结合职业分类规则和岗位说明进一步核实。")
    if findings.get("投保行为或财务合理性风险事项"):
        lines.append("存在异常投保行为或财务合理性线索，需进一步核实，不宜直接对客户作确定性判断。")
    if findings.get("免责或责任边界相关风险事项") or any(word in text for word in ["免责", "责任", "条款", "边界"]):
        lines.append("相关内容不得替代正式核保结论或条款解释，沟通时应明确保留审查边界。")
    if not lines:
        lines.append("当前未见必须单列的合规边界事项，但仍应避免绝对化沟通表述。")
    return lines


def build_followups(text: str, findings: dict[str, list[str]]) -> list[str]:
    questions = []
    if findings.get("健康风险事项"):
        questions.append("请补充相关体检、门诊、住院、复查或病史资料，以支持高风险健康事项的进一步核查。")
    if findings.get("职业风险事项"):
        questions.append("请补充职业说明、岗位职责证明、差旅说明或其他职业资料。")
    if findings.get("投保行为或财务合理性风险事项"):
        questions.append("请补充收入说明、保费安排说明、既有保单情况或资金来源说明。")
    questions.append("请核实当前业务沟通场景、险种背景和主要风险来源，确保后续告知对象和口径一致。")
    return questions or ["当前未见明确补查方向，建议先核对原件和关键背景信息。"]


def build_next_steps(text: str, findings: dict[str, list[str]]) -> list[str]:
    steps = []
    steps.append("建议补充说明主要高风险事项、资料来源和沟通场景后再形成稳定告知口径。")
    if findings or any(word in text for word in ["补件", "复查", "收入说明", "职业说明", "需核实"]):
        steps.append("建议补件并完成关键核查后再对外沟通。")
        steps.append("建议重点人工审核，必要时内部先完成核查后再开展风险告知。")
    else:
        steps.append("当前可进入下一环节业务沟通或核保审查，但仍应保留合规边界提示。")
    steps.append("本结果仅用于高风险告知整理与内部协同，不替代正式核保结论或条款解释。")
    return steps


def render_report(data: dict[str, Any]) -> str:
    text = data.get("_raw_text", "")
    basic = extract_basic_info(data)
    findings = collect_topic_risks(text)
    summary = build_summary(text, findings)
    risk_items = build_risk_items(findings, text)
    priority_lines = build_priority_lines(text, findings)
    communication_points = build_communication_points(text, findings)
    compliance_lines = build_compliance_lines(text, findings)
    followups = build_followups(text, findings)
    next_steps = build_next_steps(text, findings)

    lines = [
        "# 高风险告知整理结果",
        "",
        "一、告知背景信息",
        f"- 产品/险种：{basic['product_name']}",
        f"- 告知对象或场景：{basic['scenario']}",
        f"- 风险资料来源：{basic['risk_source']}",
        f"- 材料来源或文本类型：{basic['source_type']}",
        "",
        "二、高风险告知结论摘要",
    ]
    lines.extend(f"- {item}" for item in summary)
    lines.extend(["", "三、重点高风险事项提取"])
    lines.extend(f"- {item}" for item in risk_items)
    lines.extend(["", "四、风险等级与沟通优先级梳理"])
    lines.extend(f"- {item}" for item in priority_lines)
    lines.extend(["", "五、业务沟通要点"])
    lines.extend(f"- {item}" for item in communication_points)
    lines.extend(["", "六、核保关注点与合规提示"])
    lines.extend(f"- {item}" for item in compliance_lines)
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
