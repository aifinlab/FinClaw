#!/usr/bin/env python3
"""将重疾险投保问卷整理为标准化分析报告。"""

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
    "肿瘤风险": ["肿瘤", "癌", "原位癌", "结节", "包块", "肿块", "占位", "病理"],
    "心脑血管风险": ["冠心病", "心梗", "脑梗", "脑出血", "胸痛", "心律失常", "支架", "搭桥"],
    "神经系统风险": ["癫痫", "脑部", "神经", "瘫痪", "卒中"],
    "器官功能风险": ["肝功能", "肾功能", "蛋白尿", "血尿", "呼吸功能", "器官异常"],
    "家族史风险": ["父亲", "母亲", "兄弟", "姐妹", "子女", "家族史", "遗传"],
}

VISIT_KEYWORDS = {
    "门诊情况": ["门诊", "复诊", "专科"],
    "住院情况": ["住院", "出院"],
    "手术情况": ["手术", "切除", "术后"],
    "重大检查或专项检查异常": ["体检", "CT", "MRI", "彩超", "病理", "影像", "异常", "指标"],
    "随访复查或长期治疗情况": ["复查", "随访", "长期治疗", "长期服药", "长期用药"],
}

CONTROL_KEYWORDS = ["控制", "稳定", "复查", "随访", "服药"]
HIGH_RISK_WORDS = ["肿瘤", "癌", "结节", "占位", "胸痛", "住院", "手术", "长期服药", "病理", "遗传"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成重疾险问卷分析报告")
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
            findings.append(f"{topic}：识别到 {('、'.join(hits))} 相关线索，需结合诊断、时间、结果和当前状态进一步判断。")
    return findings


def extract_key_points(text: str) -> list[str]:
    points = []
    mapping = [
        ("结节", "问卷披露结节或占位相关线索，需核实部位、分级及复查结果。"),
        ("肿瘤", "问卷涉及肿瘤相关信息，需核实诊断性质、时间及当前状态。"),
        ("住院", "问卷涉及住院相关信息，需核实住院原因、诊断及出院结论。"),
        ("手术", "问卷涉及手术相关信息，需核实手术名称、原因及病理或术后结论。"),
        ("复查", "问卷涉及复查或随访线索，需核实持续时间及最近结果。"),
        ("服药", "问卷涉及长期服药或治疗线索，需核实药物名称和控制情况。"),
        ("父亲", "问卷涉及直系亲属家族史，需核实亲属关系、疾病类型及发病年龄。"),
        ("母亲", "问卷涉及直系亲属家族史，需核实亲属关系、疾病类型及发病年龄。"),
    ]
    for keyword, message in mapping:
        if keyword in text:
            points.append(message)
    return list(dict.fromkeys(points))


def collect_visit_info(text: str) -> dict[str, str]:
    result = {}
    for title, keywords in VISIT_KEYWORDS.items():
        hits = [keyword for keyword in keywords if keyword in text]
        result[title] = f"识别到 {('、'.join(hits))} 相关线索，需结合具体时间、原因和结论核实。" if hits else "未见明确相关信息，或当前材料不足以确认。"
    return result


def build_control_status(text: str) -> str:
    hits = [keyword for keyword in CONTROL_KEYWORDS if keyword in text]
    if hits:
        return f"识别到 {('、'.join(hits))} 相关描述，但当前控制情况是否稳定仍需结合最近复查或治疗记录确认。"
    return "当前材料未见明确疾病控制情况，或不足以确认。"


def build_summary(text: str, topic_risks: list[str]) -> list[str]:
    summary = []
    if topic_risks:
        summary.append("已识别出需重点关注的重大病史、家族史或检查异常，建议结合补问或补件进一步判断。")
    else:
        summary.append("当前未见明确重大疾病风险事实，但仍需结合材料完整度审视。")
    if any(word in text for word in ["结节", "住院", "手术", "复查", "长期服药", "病理", "家族史", "父亲", "母亲"]):
        summary.append("问卷中存在重大异常、家族史或持续管理线索，建议重点核实当前状态和完整依据。")
    if any(word in text for word in HIGH_RISK_WORDS):
        summary.append("存在可能显著影响重疾险核保判断的高风险信号，建议补问、补件或重点人工审核。")
    return summary[:3]


def build_followups(text: str) -> list[str]:
    questions = []
    if any(word in text for word in ["结节", "包块", "肿块", "占位"]):
        questions.append("请补充结节、包块或占位的发现时间、部位、影像或病理结论、分级情况及最近一次复查结果。")
    if any(word in text for word in ["肿瘤", "癌", "原位癌"]):
        questions.append("请补充肿瘤相关诊断名称、确诊时间、治疗经过、病理结论及当前随访情况。")
    if any(word in text for word in ["胸痛", "冠心病", "心梗", "脑梗", "脑出血"]):
        questions.append("请补充心脑血管相关异常的发生时间、明确诊断、住院治疗情况及目前控制状态。")
    if any(word in text for word in ["住院", "手术"]):
        questions.append("请补充住院或手术的时间、原因、出院诊断、术后结论及当前恢复情况。")
    if any(word in text for word in ["长期服药", "长期用药", "服药", "治疗"]):
        questions.append("请补充长期治疗或用药对应的疾病名称、药物名称、用药时长、频率及控制效果。")
    if any(word in text for word in ["父亲", "母亲", "兄弟", "姐妹", "子女", "家族史", "遗传"]):
        questions.append("请补充家族史中患病亲属与被保人关系、疾病名称、发病年龄及目前情况。")
    if not questions:
        questions.append("当前材料未见明确补问方向，建议核对原件后再做人工审查。")
    return questions


def build_next_steps(text: str, topic_risks: list[str]) -> list[str]:
    steps = []
    if topic_risks or any(word in text for word in ["复查", "异常", "住院", "手术", "家族史"]):
        steps.append("建议补充说明关键重大病史、家族史、检查异常或治疗经过后再做进一步判断。")
    if any(word in text for word in ["结节", "肿瘤", "癌", "病理", "住院", "手术", "胸痛", "脑梗", "长期服药"]):
        steps.append("建议补充病理、影像、出院小结、专科复查或长期治疗记录等相关材料。")
        steps.append("建议重点人工审核，并结合病理、影像、体检、住院等资料进一步判断。")
    if not steps:
        steps.append("当前可进入下一环节核保审查。")
    steps.append("本结果仅用于重疾险问卷分析与补问准备，不替代正式核保决定。")
    return steps


def render_report(data: dict[str, Any]) -> str:
    text = data.get("_raw_text", "")
    basic = extract_basic_info(data)
    topic_risks = collect_topic_risks(text)
    key_points = extract_key_points(text)
    visits = collect_visit_info(text)
    control_status = build_control_status(text)
    summary = build_summary(text, topic_risks)
    followups = build_followups(text)
    next_steps = build_next_steps(text, topic_risks)

    abnormal_items = topic_risks or ["当前未识别到明确重大病史、家族史风险或高风险检查异常，或材料不足以确认。"]

    focus_lines = []
    if any(word in text for word in HIGH_RISK_WORDS):
        focus_lines.append("问卷存在肿瘤、结节、住院、重大症状、长期治疗或家族史等高关注线索，需进一步核实具体诊断、时间和当前状态。")
    if "未说明" in text or "不明确" in text or "待查" in text:
        focus_lines.append("部分重大健康信息或家族史表述不完整，当前不足以支持完整重疾险核保判断。")
    if not focus_lines:
        focus_lines.append("当前未见明确高严重性信号，但仍需结合原件和材料完整度复核。")

    lines = [
        "# 重疾险问卷分析结果",
        "",
        "一、问卷基本信息",
        f"- 险种/产品：{basic['insurance_type']} / {basic['product_name']}",
        f"- 被保人基本信息：{basic['insured_info']}",
        f"- 问卷类型：{basic['questionnaire_type']}",
        f"- 材料来源或文本类型：{basic['source_type']}",
        "",
        "二、重疾险核保结论摘要",
    ]
    lines.extend(f"- {item}" for item in summary)
    lines.extend([
        "",
        "三、重疾相关健康告知要点提取",
    ])
    lines.extend(f"- {item}" for item in (key_points or ["当前可确认的重疾相关健康告知要点有限，建议核对原始问卷。"]))
    lines.extend([
        "",
        "四、重大异常病史与家族史识别",
    ])
    lines.extend(f"- {item}" for item in abnormal_items)
    lines.extend([
        "",
        "五、就医与治疗情况梳理",
        f"- 门诊情况：{visits['门诊情况']}",
        f"- 住院情况：{visits['住院情况']}",
        f"- 手术情况：{visits['手术情况']}",
        f"- 重大检查或专项检查异常：{visits['重大检查或专项检查异常']}",
        f"- 随访复查或长期治疗情况：{visits['随访复查或长期治疗情况']}",
        f"- 疾病当前控制情况：{control_status}",
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
