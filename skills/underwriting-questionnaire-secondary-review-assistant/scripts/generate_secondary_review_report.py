#!/usr/bin/env python3
"""将投保问卷、初审意见和补充资料整理为标准化复核报告。"""

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




HEALTH_KEYWORDS = ["结节", "肿瘤", "癌", "高血压", "糖尿病", "住院", "手术", "复查", "异常", "服药"]
OCCUPATION_KEYWORDS = ["自由职业", "个体经营", "高空", "井下", "危化", "建筑", "施工", "船员", "消防", "驾驶"]
HABIT_KEYWORDS = ["吸烟", "抽烟", "饮酒", "喝酒", "潜水", "跳伞", "攀岩", "赛车"]
BEHAVIOR_KEYWORDS = ["拒保", "延期", "加费", "除外", "投保", "累计保额", "高额", "代填", "代答"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成核保问卷复核报告")
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
        data["_combined_text"] = build_text_from_json(data)
        return data
    return {"questionnaire_text": raw, "_combined_text": raw}


def build_text_from_json(data: dict[str, Any]) -> str:
    parts: list[str] = []
    for key in [
        "insurance_type",
        "product_name",
        "questionnaire_type",
        "source_type",
        "initial_review_conclusion",
        "questionnaire_text",
    ]:
        value = data.get(key)
        if value:
            parts.append(str(value))
    for key in ["initial_review_notes", "supplementary_notes"]:
        value = data.get(key)
        if isinstance(value, list):
            parts.extend(str(item) for item in value if item)
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
        "initial_review_conclusion": str(data.get("initial_review_conclusion") or "未提供"),
        "source_type": str(data.get("source_type") or "未明确"),
    }


def collect_keywords(text: str, keywords: list[str]) -> list[str]:
    hits = []
    for keyword in keywords:
        if keyword in text and keyword not in hits:
            hits.append(keyword)
    return hits


def assess_initial_review(data: dict[str, Any], text: str) -> tuple[list[str], list[str]]:
    notes = data.get("initial_review_notes")
    initial_items = [str(item) for item in notes] if isinstance(notes, list) else []
    findings = []
    if initial_items:
        findings.append("初审已识别问题包括：" + "；".join(initial_items) + "。")
    else:
        findings.append("材料中未见完整初审问题清单，复核依据存在缺口。")

    gaps = []
    if "结节" in text and not any("结节" in item for item in initial_items):
        gaps.append("原始材料含有结节或复查线索，但初审未明确单列，属于初审遗漏。")
    if "自由职业" in text and not any("职业" in item for item in initial_items):
        gaps.append("原始材料职业信息较模糊，但初审未明确要求补充岗位与作业环境，属于弱识别。")
    if ("投保" in text or "延期" in text or "加费" in text) and not any("投保" in item or "延期" in item or "加费" in item for item in initial_items):
        gaps.append("既往投保处理情况相关线索未被初审充分展开，属于初审遗漏。")
    return findings, gaps


def assess_sufficiency(data: dict[str, Any], text: str) -> tuple[list[str], list[str]]:
    notes = data.get("supplementary_notes")
    supplements = [str(item) for item in notes] if isinstance(notes, list) else []
    enough = []
    still_missing = []
    if supplements:
        enough.append("已提供补充说明或补件摘要，但需结合关键疑点判断是否真正覆盖。")
    else:
        still_missing.append("未提供有效补问记录或补件摘要，无法判断关键疑点是否已被覆盖。")

    if "结节" in text and not any("复查" in item or "结果" in item or "诊断" in item for item in supplements):
        still_missing.append("关于结节或体检异常，仅有笼统说明，缺少复查结果或当前状态，属于补件不足。")
    if "自由职业" in text and not any("岗位" in item or "工作" in item or "作业" in item for item in supplements):
        still_missing.append("职业补充仍未明确具体岗位和作业环境，无法支持职业风险复核。")
    if ("投保" in text or "延期" in text or "加费" in text) and not any("延期" in item or "加费" in item or "结论" in item or "原因" in item for item in supplements):
        still_missing.append("既往投保补充未覆盖处理结果及原因，投保行为风险仍不足以判断。")
    if "偶尔" in text and not any("频率" in item or "数量" in item for item in supplements):
        still_missing.append("生活习惯补充仍未明确频率和数量，属于补充后仍不足。")
    return enough, still_missing


def build_risk_review(text: str) -> dict[str, str]:
    risk_flags = {
        "health": collect_keywords(text, HEALTH_KEYWORDS),
        "occupation": collect_keywords(text, OCCUPATION_KEYWORDS),
        "habit": collect_keywords(text, HABIT_KEYWORDS),
        "behavior": collect_keywords(text, BEHAVIOR_KEYWORDS),
    }
    result = {
        "health": "未见明确新增健康高风险结论，但仍需结合补件确认。",
        "occupation": "未见明确新增职业高风险结论，但职业细节可能仍不足。",
        "habit": "未见明确新增生活习惯高风险结论，但相关信息可能仍偏模糊。",
        "behavior": "未见明确新增投保行为高风险结论，但既往投保信息可能仍不足。",
    }
    if risk_flags["health"]:
        result["health"] = "识别到健康相关复核线索：" + "、".join(risk_flags["health"]) + "。如诊断、时间或当前状态仍不明确，需进一步人工核查。"
    if risk_flags["occupation"]:
        result["occupation"] = "识别到职业相关复核线索：" + "、".join(risk_flags["occupation"]) + "。需确认岗位职责和危险暴露情况。"
    if risk_flags["habit"]:
        result["habit"] = "识别到生活习惯复核线索：" + "、".join(risk_flags["habit"]) + "。需确认频率、数量和持续时间。"
    if risk_flags["behavior"]:
        result["behavior"] = "识别到投保行为复核线索：" + "、".join(risk_flags["behavior"]) + "。需确认既往处理结果及原因。"
    return result


def build_summary(initial_gaps: list[str], still_missing: list[str], text: str) -> list[str]:
    summary = []
    if not initial_gaps:
        summary.append("初审意见总体方向基本合理，未见明显重大遗漏。")
    else:
        summary.append("初审意见存在遗漏或识别不充分之处，需结合复核结果修正。")
    if still_missing:
        summary.append("补问与补件对关键疑点覆盖仍不充分，当前尚不足以完全支撑下一步判断。")
    else:
        summary.append("现有补充信息已基本覆盖主要疑点，可结合风险程度判断是否继续流转。")
    if any(word in text for word in ["结节", "住院", "手术", "延期", "加费", "拒保", "高空", "井下"]):
        summary.append("当前仍存在需重点关注的高风险线索，建议视材料完整性决定是否升级人工核查。")
    return summary[:3]


def build_questions(text: str, still_missing: list[str]) -> list[str]:
    questions = []
    if "结节" in text or any("结节" in item or "体检异常" in item for item in still_missing):
        questions.append("请进一步提供异常检查或结节相关的明确诊断、最近一次复查时间、复查结果及当前处理情况。")
    if "自由职业" in text or any("职业" in item for item in still_missing):
        questions.append("请进一步说明被保人当前岗位、主要工作内容、日常作业环境及是否涉及高危作业。")
    if "偶尔" in text or any("生活习惯" in item for item in still_missing):
        questions.append("请进一步说明吸烟、饮酒或危险活动的频率、数量、持续时间及当前是否仍在持续。")
    if any(word in text for word in ["投保", "延期", "加费", "拒保"]):
        questions.append("请补充既往投保公司、险种、时间、处理结果及相应原因说明。")
    if not questions:
        questions.append("当前未见明确继续追问方向，建议核对原件后结合正式核保要求决定下一步。")
    return questions


def build_next_steps(initial_gaps: list[str], still_missing: list[str], text: str) -> list[str]:
    steps = []
    if initial_gaps:
        steps.append("建议补充复核说明，明确初审遗漏点或判断不充分之处。")
    if still_missing:
        steps.append("建议追加补件或退回补问，先补足关键缺口后再决定是否继续流转。")
    if any(word in text for word in ["结节", "住院", "手术", "延期", "加费", "拒保", "高空", "井下"]):
        steps.append("建议对高风险或一致性问题升级人工核查。")
    if not still_missing and not initial_gaps:
        steps.append("当前具备进入正式核保判断的基础。")
    steps.append("本结果仅用于核保问卷复核与流转建议，不替代正式核保决定。")
    return steps


def render_report(data: dict[str, Any]) -> str:
    text = data.get("_combined_text", "")
    basic = extract_basic_info(data)
    initial_findings, initial_gaps = assess_initial_review(data, text)
    sufficiency_ok, sufficiency_gaps = assess_sufficiency(data, text)
    risk = build_risk_review(text)
    summary = build_summary(initial_gaps, sufficiency_gaps, text)
    questions = build_questions(text, sufficiency_gaps)
    next_steps = build_next_steps(initial_gaps, sufficiency_gaps, text)

    lines = [
        "# 核保问卷复核结果",
        "",
        "一、复核对象基本信息",
        f"- 险种/产品：{basic['insurance_type']} / {basic['product_name']}",
        f"- 被保人基本信息：{basic['insured_info']}",
        f"- 问卷类型：{basic['questionnaire_type']}",
        f"- 初审结论：{basic['initial_review_conclusion']}",
        f"- 复核材料来源或文本类型：{basic['source_type']}",
        "",
        "二、复核结论摘要",
    ]
    lines.extend(f"- {item}" for item in summary)
    lines.extend([
        "",
        "三、初审意见复核",
    ])
    lines.extend(f"- {item}" for item in initial_findings)
    lines.extend(f"- {item}" for item in (initial_gaps or ["复核未发现明显初审遗漏，初审识别方向基本合理。"]))
    lines.extend([
        "",
        "四、复核发现的问题",
    ])
    combined_issues = initial_gaps + sufficiency_gaps
    lines.extend(f"- {item}" for item in (combined_issues or ["当前未新增发现明显问题。"]))
    lines.extend([
        "",
        "五、补问与补件充分性检查",
    ])
    lines.extend(f"- {item}" for item in (sufficiency_ok or ["当前未见可确认的有效补充信息。"]))
    lines.extend(f"- {item}" for item in (sufficiency_gaps or ["现有补问与补件对主要疑点覆盖较充分。"]))
    lines.extend([
        "",
        "六、高风险项复核与风险提示",
        f"- 健康风险复核：{risk['health']}",
        f"- 职业风险复核：{risk['occupation']}",
        f"- 生活习惯风险复核：{risk['habit']}",
        f"- 投保行为风险复核：{risk['behavior']}",
        "",
        "七、建议进一步核实的问题",
    ])
    lines.extend(f"- {item}" for item in questions)
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