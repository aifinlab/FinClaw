#!/usr/bin/env python3
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List
import argparse
import json
import re
import sys


DEFAULT_CONFIG = {
    "high_risk_keywords": ["违约", "逾期", "诉讼", "失信", "造假", "处罚", "资金占用", "关联交易"],
    "medium_risk_keywords": ["异常", "波动", "下滑", "延期", "瑕疵", "不一致", "未披露"],
    "question_templates": {
        "finance": "请解释：{issue}。请同步提供近12个月财务明细与银行流水佐证。",
        "legal": "请说明：{issue}。请提供对应法律文书、合同原件及处理进展。",
        "compliance": "请补充说明：{issue}。请提供监管沟通记录及整改闭环材料。",
        "operations": "请说明业务影响与整改计划：{issue}。请提供可量化运营数据。",
        "other": "请进一步核实：{issue}，并提交支持性材料。",
    },
}


def load_items(path: Path) -> List[Dict[str, Any]]:
    raw = path.read_text(encoding="utf-8").strip()
    if not raw:
        return []
    if raw.lstrip().startswith("["):
        data = json.loads(raw)
        if not isinstance(data, list):
            raise ValueError("JSON input must be an array.")
        return [x for x in data if isinstance(x, dict)]

    items: List[Dict[str, Any]] = []
    for idx, line in enumerate(raw.splitlines(), start=1):
        text = line.strip()
        if not text:
            continue
        obj = json.loads(text)
        if not isinstance(obj, dict):
            raise ValueError(f"JSONL line {idx} must be an object.")
        items.append(obj)
    return items


def load_config(path: Path | None) -> Dict[str, Any]:
    if path is None:
        return DEFAULT_CONFIG
    data = json.loads(path.read_text(encoding="utf-8"))
    cfg = {
        "high_risk_keywords": [str(x) for x in data.get("high_risk_keywords", DEFAULT_CONFIG["high_risk_keywords"])],
        "medium_risk_keywords": [str(x) for x in data.get("medium_risk_keywords", DEFAULT_CONFIG["medium_risk_keywords"])],
        "question_templates": DEFAULT_CONFIG["question_templates"].copy(),
    }
    templates = data.get("question_templates", {})
    if isinstance(templates, dict):
        for k, v in templates.items():
            cfg["question_templates"][str(k)] = str(v)
    return cfg


def classify_priority(score: int) -> str:
    if score >= 10:
        return "high"
    if score >= 6:
        return "medium"
    return "low"


def scan_keywords(text: str, words: List[str]) -> int:
    total = 0
    for w in words:
        total += len(re.findall(re.escape(w), text, flags=re.IGNORECASE))
    return total


def ensure_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(x) for x in value if str(x).strip()]
    return [str(value)]


def build_questions(items: List[Dict[str, Any]], config: Dict[str, Any]) -> List[Dict[str, Any]]:
    sev_score = {"high": 6, "medium": 3, "low": 1}
    results = []
    for idx, item in enumerate(items, start=1):
        category = str(item.get("category", "other") or "other").strip().lower()
        if category not in {"finance", "legal", "compliance", "operations", "other"}:
            category = "other"

        issue_text = str(item.get("issue_text", "(未提供问题描述)") or "(未提供问题描述)")
        evidence = str(item.get("evidence", "") or "")
        status = str(item.get("status", "open") or "open").strip().lower()
        severity = str(item.get("severity", "medium") or "medium").strip().lower()
        docs = ensure_list(item.get("missing_docs"))

        combined = f"{issue_text} {evidence}"
        high_hits = scan_keywords(combined, config["high_risk_keywords"])
        med_hits = scan_keywords(combined, config["medium_risk_keywords"])

        score = sev_score.get(severity, 3)
        score += min(high_hits * 2, 6)
        score += min(med_hits, 3)
        score += min(len(docs), 4)
        if status in {"open", "pending"}:
            score += 2

        priority = classify_priority(score)
        template = config["question_templates"].get(category, config["question_templates"]["other"])
        question_text = template.format(issue=issue_text)

        reasons = []
        if severity in sev_score:
            reasons.append(f"severity={severity}")
        if high_hits:
            reasons.append(f"high_kw_hits={high_hits}")
        if med_hits:
            reasons.append(f"medium_kw_hits={med_hits}")
        if docs:
            reasons.append(f"missing_docs={len(docs)}")
        if status:
            reasons.append(f"status={status}")

        results.append(
            {
                "qid": f"Q{idx:03d}",
                "entity_name": str(item.get("entity_name", "") or ""),
                "category": category,
                "priority": priority,
                "score": score,
                "question": question_text,
                "issue": issue_text,
                "evidence": evidence,
                "missing_docs": docs,
                "reason": ", ".join(reasons) if reasons else "rule_based",
            }
        )
    return results


def render_report(questions: List[Dict[str, Any]], top_n: int) -> str:
    priority_counts = Counter(q["priority"] for q in questions)
    category_counts = Counter(q["category"] for q in questions)
    missing_doc_counter = Counter()
    for q in questions:
        missing_doc_counter.update(q["missing_docs"])

    lines: List[str] = []
    lines.append("# 尽调问题清单报告")
    lines.append("")
    lines.append("## 一、问题概览")
    lines.append(f"- 问题总数: {len(questions)}")
    lines.append(f"- 高优先(high): {priority_counts.get('high', 0)}")
    lines.append(f"- 中优先(medium): {priority_counts.get('medium', 0)}")
    lines.append(f"- 低优先(low): {priority_counts.get('low', 0)}")
    lines.append("")

    lines.append("## 二、高优先问题")
    ranked = sorted(questions, key=lambda x: x["score"], reverse=True)
    top_items = ranked[:top_n]
    if not top_items:
        lines.append("- 无")
    else:
        for q in top_items:
            label = f"- {q['qid']} | priority={q['priority']} | score={q['score']} | category={q['category']}"
            if q["entity_name"]:
                label += f" | entity={q['entity_name']}"
            lines.append(label)
            lines.append(f"  - 问题: {q['question']}")
            lines.append(f"  - 依据: {q['issue']}")
            if q["evidence"]:
                lines.append(f"  - 证据: {q['evidence']}")
            lines.append(f"  - 打分依据: {q['reason']}")
            if q["missing_docs"]:
                lines.append("  - 待补资料: " + ", ".join(q["missing_docs"]))

    lines.append("")
    lines.append("## 三、分类分布")
    if not category_counts:
        lines.append("- 无")
    else:
        for k, v in category_counts.most_common():
            lines.append(f"- {k}: {v}")

    lines.append("")
    lines.append("## 四、资料补充清单")
    if not missing_doc_counter:
        lines.append("- 无")
    else:
        for doc, cnt in missing_doc_counter.most_common(20):
            lines.append(f"- {doc}: {cnt}")

    lines.append("")
    lines.append("## 五、方法与限制")
    lines.append("- 本报告基于关键词与规则打分，仅用于尽调问题准备。")
    lines.append("- 高优先问题需结合人工访谈与证据核验。")
    lines.append("- 本工具不构成授信、投资或法律结论。")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Due diligence question list generator.")
    parser.add_argument("--input", required=True, help="Input JSON array or JSONL file.")
    parser.add_argument("--output", help="Output markdown path (default: stdout).")
    parser.add_argument("--keywords", help="Custom keyword/template JSON path.")
    parser.add_argument("--top", type=int, default=20, help="Top questions to display.")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    items = load_items(input_path)
    config = load_config(Path(args.keywords)) if args.keywords else load_config(None)
    questions = build_questions(items, config)
    report = render_report(questions, args.top)

    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
    else:
        sys.stdout.write(report + "\n")


if __name__ == "__main__":
    main()
