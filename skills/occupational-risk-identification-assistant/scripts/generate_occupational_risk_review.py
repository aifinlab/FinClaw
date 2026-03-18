#!/usr/bin/env python3
"""将职业相关资料整理为标准化职业风险识别结果。"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

RISK_TOPICS = {
    "岗位风险": ["施工", "高空", "井下", "海上", "焊工", "电工", "吊装", "爆破", "设备操作", "特种设备", "体力劳动", "夜班", "轮班"],
    "环境风险": ["粉尘", "噪声", "高温", "高压", "化学品", "危化", "放射", "传染", "工地", "厂区", "仓库", "危险品"],
    "交通风险": ["驾驶", "自驾", "运输", "长途", "货运", "出差", "差旅", "营运", "叉车", "船", "飞行"],
    "一致性风险": ["不一致", "冲突", "备注", "补充说明", "管理人员", "项目管理", "兼职", "第二职业", "副业"],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成职业风险识别报告")
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
    for key in ["occupation_name", "job_title", "industry", "work_years", "duty_description", "environment_exposure", "traffic_travel", "second_job", "source_type", "context_text"]:
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
        "occupation_name": str(data.get("occupation_name") or "未明确"),
        "job_title": str(data.get("job_title") or "未明确"),
        "industry": str(data.get("industry") or "未明确"),
        "work_years": str(data.get("work_years") or "未明确"),
        "source_type": str(data.get("source_type") or "未明确"),
        "duty_description": str(data.get("duty_description") or ""),
    }


def collect_topic_risks(text: str) -> list[str]:
    findings = []
    for topic, keywords in RISK_TOPICS.items():
        hits = [keyword for keyword in keywords if keyword in text]
        if hits:
            findings.append(f"{topic}：识别到 {'、'.join(dict.fromkeys(hits))} 相关线索，需结合职责频率、作业场景和实际参与程度进一步判断。")
    return findings


def build_summary(text: str, topic_risks: list[str]) -> list[str]:
    summary = []
    if any(word in text for word in ["高空", "井下", "海上", "危化", "施工", "运输", "货运"]):
        summary.append("资料中存在明显高风险职业、危险作业或高暴露环境线索，建议重点人工审核。")
    elif topic_risks:
        summary.append("已识别出需重点关注的职业风险模式，建议结合补问或补件进一步判断。")
    else:
        summary.append("当前未见明确高关注职业风险事实，但仍需结合材料完整度进一步复核。")
    if any(word in text for word in ["不一致", "冲突", "兼职", "第二职业", "副业", "备注", "补充说明"]):
        summary.append("资料中存在职业信息不一致、兼职或描述不充分线索，需核实申报职业与实际作业是否一致。")
    if any(word in text for word in ["驾驶", "运输", "长途", "出差", "差旅"]):
        summary.append("资料中存在交通或差旅暴露线索，建议重点核实驾驶频率、出差范围和是否伴随现场作业。")
    return summary[:3]


def build_duty_points(data: dict[str, str], text: str) -> list[str]:
    points = []
    if data["duty_description"]:
        points.append(f"当前岗位职责：{data['duty_description']}")
    if any(word in text for word in ["体力劳动", "搬运", "设备操作", "机械", "叉车"]):
        points.append("资料存在体力劳动或设备操作线索，需核实是否属于长期或核心职责。")
    if any(word in text for word in ["户外", "现场", "施工", "巡查", "高空", "井下", "海上"]):
        points.append("资料存在现场、户外或危险作业场景线索，需关注实际进入现场的频率和参与深度。")
    if any(word in text for word in ["夜班", "轮班", "值守"]):
        points.append("资料存在轮班、夜班或值守线索，提示作业节律和工作场景需进一步核实。")
    if not points:
        points.append("当前可确认的岗位职责信息有限，建议补充实际工作内容、作业场景和是否涉及现场操作。")
    return points


def build_pattern_lines(text: str, topic_risks: list[str]) -> list[str]:
    lines = []
    if any(word in text for word in ["高空", "井下", "海上", "危化", "施工", "爆破", "焊工", "电工"]):
        lines.append("存在高危作业或高暴露职业线索，需重点核实是否为日常核心工作内容。")
    if any(word in text for word in ["粉尘", "噪声", "高温", "高压", "化学品", "放射", "传染"]):
        lines.append("存在环境暴露风险线索，需进一步补充暴露类型、频率和防护情况。")
    if any(word in text for word in ["驾驶", "运输", "长途", "货运", "出差", "差旅", "营运"]):
        lines.append("存在驾驶、运输或频繁差旅线索，需关注交通暴露与工作职责是否叠加。")
    if any(word in text for word in ["兼职", "第二职业", "副业"]):
        lines.append("存在兼职或第二职业线索，主职业信息可能不足以完整反映职业暴露。")
    if any(word in text for word in ["不一致", "冲突", "备注", "补充说明", "管理人员", "项目管理"]):
        lines.append("存在职业申报与补充资料之间的差异，需核实申报岗位与实际作业是否一致。")
    lines.extend(topic_risks[:3])
    return lines or ["当前未见明确高风险模式或一致性问题描述，或材料不足以判断。"]


def build_classification_focus(text: str) -> list[str]:
    lines = []
    if any(word in text for word in ["办公室", "行政", "财务", "文员", "研发"]):
        lines.append("职业描述更接近常规室内岗位，但仍需确认是否存在外勤或现场职责。")
    if any(word in text for word in ["现场", "施工", "驾驶", "运输", "设备操作", "高空", "危化"]):
        lines.append("职业整体风险判断高度依赖岗位细分、现场参与程度和环境暴露情况，当前需结合规则进一步核查。")
    if any(word in text for word in ["管理人员", "项目管理", "自由职业", "个体经营", "工人", "技术人员"]):
        lines.append("职业申报较笼统，单凭当前描述不足以直接支持职业分级判断。")
    if any(word in text for word in ["兼职", "第二职业", "副业"]):
        lines.append("第二职业或兼职可能改变整体职业暴露水平，建议一并纳入职业分级关注范围。")
    return lines or ["当前职业分级判断依据有限，建议补充岗位职责、作业场景和交通暴露后再进一步核查。"]


def build_focus_lines(text: str) -> list[str]:
    lines = []
    if any(word in text for word in ["高空", "井下", "海上", "危化", "施工", "爆破"]):
        lines.append("资料存在高危职业或危险作业线索，可能显著提高职业核保关注度。")
    if any(word in text for word in ["驾驶", "运输", "长途", "差旅", "营运"]):
        lines.append("资料存在频繁交通暴露线索，需核实驾驶性质、频率和是否属于营运或长途运输。")
    if any(word in text for word in ["兼职", "第二职业", "副业"]):
        lines.append("资料存在兼职或第二职业线索，需确认是否增加额外职业风险暴露。")
    if any(word in text for word in ["不一致", "冲突", "备注", "补充说明", "管理人员"]):
        lines.append("职业申报与其他资料存在差异或描述过于笼统，真实性和完整性需进一步核实。")
    return lines or ["当前未见明确高关注职业风险信号，但仍需结合原件和资料完整度复核。"]


def build_followups(text: str) -> list[str]:
    questions = ["请补充当前实际岗位名称、主要工作职责、工作场所和日常作业内容。"]
    if any(word in text for word in ["高空", "施工", "现场", "井下", "海上", "危化", "设备操作"]):
        questions.append("请补充是否长期进入施工、厂区、仓储、高空、井下或其他危险作业现场，以及大致时间占比。")
    if any(word in text for word in ["驾驶", "运输", "出差", "差旅", "货运", "营运"]):
        questions.append("请补充驾驶或差旅频率、单次时长、是否长途或营运，以及是否进入高风险地区或复杂交通场景。")
    if any(word in text for word in ["兼职", "第二职业", "副业"]):
        questions.append("请补充是否存在兼职或第二职业，各自职责、时间占比和实际工作环境。")
    if any(word in text for word in ["不一致", "冲突", "备注", "补充说明", "管理人员", "项目管理"]):
        questions.append("请核实不同资料中的职业信息是否一致，并补充申报职业与实际作业内容的说明。")
    questions.append("请补充职业说明、岗位职责证明、工作证明或差旅说明等能支持职业判断的资料。")
    return questions


def build_next_steps(text: str, topic_risks: list[str]) -> list[str]:
    steps = ["建议补充说明岗位职责、作业场景、危险暴露、交通差旅和是否存在兼职后再做进一步判断。"]
    if topic_risks or any(word in text for word in ["高空", "井下", "海上", "危化", "运输", "长途", "兼职", "第二职业", "不一致"]):
        steps.append("建议补充职业说明、岗位职责证明、工作证明、差旅说明或其他职业资料。")
        steps.append("建议重点人工审核，并结合职业分类规则、岗位说明或其他资料进一步判断。")
    else:
        steps.append("当前可进入下一环节核保审查，但建议保留对职业信息完整度的复核。")
    steps.append("本结果仅用于职业风险识别与补查准备，不替代正式核保决定。")
    return steps


def render_report(data: dict[str, Any]) -> str:
    text = data.get("_raw_text", "")
    basic = extract_basic_info(data)
    topic_risks = collect_topic_risks(text)
    summary = build_summary(text, topic_risks)
    duty_points = build_duty_points(basic, text)
    pattern_lines = build_pattern_lines(text, topic_risks)
    classification_lines = build_classification_focus(text)
    focus_lines = build_focus_lines(text)
    followups = build_followups(text)
    next_steps = build_next_steps(text, topic_risks)

    lines = [
        "# 职业风险识别结果",
        "",
        "一、职业基本信息",
        f"- 被保人基本信息：{basic['person_info']}",
        f"- 职业名称/岗位名称：{basic['occupation_name']} / {basic['job_title']}",
        f"- 行业或工作单位类型：{basic['industry']}",
        f"- 工作年限或当前工作状态：{basic['work_years']}",
        f"- 材料来源或文本类型：{basic['source_type']}",
        "",
        "二、职业风险识别结论摘要",
    ]
    lines.extend(f"- {item}" for item in summary)
    lines.extend(["", "三、岗位职责与作业内容要点提取"])
    lines.extend(f"- {item}" for item in duty_points)
    lines.extend(["", "四、高风险模式与职业暴露识别"])
    lines.extend(f"- {item}" for item in pattern_lines)
    lines.extend(["", "五、职业分级关注点梳理"])
    lines.extend(f"- {item}" for item in classification_lines)
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

