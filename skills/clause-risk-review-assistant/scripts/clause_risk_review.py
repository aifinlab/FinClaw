#!/usr/bin/env python3
import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List


DEFAULT_RULES = [
    {
        "name": "single_side_decision",
        "severity": "high",
        "patterns": ["单方有权", "自行决定", "无需通知", "甲方有权随时"],
        "suggestion": "增加双方协商或通知机制，限制单方自由裁量。",
    },
    {
        "name": "unlimited_liability",
        "severity": "high",
        "patterns": ["承担全部责任", "无限连带责任", "所有损失均由"],
        "suggestion": "限定责任边界、责任期间及损失范围。",
    },
    {
        "name": "waive_core_rights",
        "severity": "high",
        "patterns": ["放弃追索", "不可撤销放弃", "不得主张任何抗辩"],
        "suggestion": "删除绝对放弃表述，保留法定救济权利。",
    },
    {
        "name": "vague_timeline",
        "severity": "medium",
        "patterns": ["尽快", "合理期限", "视情况", "必要时"],
        "suggestion": "补充明确时点与履约触发条件。",
    },
    {
        "name": "penalty_imbalance",
        "severity": "high",
        "patterns": ["违约金由甲方单方确定", "乙方承担全部违约责任"],
        "suggestion": "设置对等违约责任条款，明确违约金计算公式。",
    },
    {
        "name": "broad_force_majeure",
        "severity": "medium",
        "patterns": ["包括但不限于市场波动", "经营困难亦属不可抗力"],
        "suggestion": "收窄不可抗力定义，排除可归责经营风险。",
    },
]

SEVERITY_WEIGHT = {"high": 8, "medium": 4, "low": 2}


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


def load_rules(path: Path | None) -> List[Dict[str, Any]]:
    if path is None:
        return DEFAULT_RULES
    data = json.loads(path.read_text(encoding="utf-8"))
    rules = data.get("rules", data)
    if not isinstance(rules, list):
        raise ValueError("Rules must be a JSON array or {'rules': [...]}.")

    normalized = []
    for rule in rules:
        if not isinstance(rule, dict):
            continue
        patterns = rule.get("patterns", [])
        if not isinstance(patterns, list):
            continue
        normalized.append(
            {
                "name": str(rule.get("name", "custom_rule")),
                "severity": str(rule.get("severity", "medium")).lower(),
                "patterns": [str(p) for p in patterns if str(p).strip()],
                "suggestion": str(rule.get("suggestion", "建议补充清晰、对等、可执行的条款表述。")),
            }
        )
    return normalized or DEFAULT_RULES


def risk_level(score: int) -> str:
    if score >= 12:
        return "high"
    if score >= 6:
        return "medium"
    if score > 0:
        return "low"
    return "none"


def analyze(items: List[Dict[str, Any]], rules: List[Dict[str, Any]]) -> Dict[str, Any]:
    records = []
    level_counts = Counter()
    rule_hits = Counter()

    for idx, item in enumerate(items, start=1):
        clause_no = str(item.get("clause_no", idx))
        title = str(item.get("clause_title", "") or "")
        text = str(item.get("clause_text", "") or "")
        contract_name = str(item.get("contract_name", "") or "")
        full = f"{title} {text}"

        score = 0
        hits = []
        suggestions = []

        for rule in rules:
            matched_patterns = [p for p in rule["patterns"] if re.search(re.escape(p), full, flags=re.IGNORECASE)]
            if not matched_patterns:
                continue
            severity = rule.get("severity", "medium")
            weight = SEVERITY_WEIGHT.get(severity, 4)
            delta = weight + max(0, len(matched_patterns) - 1)
            score += delta
            rule_hits[rule["name"]] += len(matched_patterns)
            hits.append(
                {
                    "rule": rule["name"],
                    "severity": severity,
                    "patterns": matched_patterns,
                    "delta": delta,
                }
            )
            suggestions.append(rule["suggestion"])

        level = risk_level(score)
        level_counts[level] += 1
        records.append(
            {
                "contract_name": contract_name,
                "clause_no": clause_no,
                "title": title or "(无标题)",
                "score": score,
                "level": level,
                "hits": hits,
                "suggestions": sorted(set(suggestions)),
            }
        )

    return {
        "records": sorted(records, key=lambda x: x["score"], reverse=True),
        "level_counts": level_counts,
        "rule_hits": rule_hits,
    }


def render_report(result: Dict[str, Any], top_n: int) -> str:
    lines: List[str] = []
    lines.append("# 条款风险审查报告")
    lines.append("")
    lines.append("## 一、风险概览")
    lines.append(f"- 条款总数: {len(result['records'])}")
    lines.append(f"- 高风险(high): {result['level_counts'].get('high', 0)}")
    lines.append(f"- 中风险(medium): {result['level_counts'].get('medium', 0)}")
    lines.append(f"- 低风险(low): {result['level_counts'].get('low', 0)}")
    lines.append(f"- 无明显风险(none): {result['level_counts'].get('none', 0)}")
    lines.append("")

    lines.append("## 二、规则命中统计")
    if not result["rule_hits"]:
        lines.append("- 无")
    else:
        for rule, cnt in result["rule_hits"].most_common():
            lines.append(f"- {rule}: {cnt}")
    lines.append("")

    lines.append("## 三、高风险条款")
    top_records = result["records"][:top_n]
    if not top_records:
        lines.append("- 无")
    else:
        for rec in top_records:
            if rec["level"] == "none":
                continue
            line = f"- 条款{rec['clause_no']}《{rec['title']}》 | score={rec['score']} | level={rec['level']}"
            if rec["contract_name"]:
                line += f" | contract={rec['contract_name']}"
            lines.append(line)
            for hit in rec["hits"]:
                lines.append(
                    f"  - 命中规则: {hit['rule']} ({hit['severity']}) | patterns={', '.join(hit['patterns'])} | +{hit['delta']}"
                )
            for s in rec["suggestions"][:3]:
                lines.append(f"  - 修订建议: {s}")

    lines.append("")
    lines.append("## 四、方法与限制")
    lines.append("- 本报告基于关键词规则，不替代律师逐条审阅。")
    lines.append("- 高风险条款需结合交易背景确认法律效力与可执行性。")
    lines.append("- 本工具不构成法律意见。")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Contract clause risk reviewer.")
    parser.add_argument("--input", required=True, help="Input JSON array or JSONL file.")
    parser.add_argument("--output", help="Output markdown path (default: stdout).")
    parser.add_argument("--rules", help="Custom rules JSON path.")
    parser.add_argument("--top", type=int, default=20, help="Top risky clauses to display.")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    items = load_items(input_path)
    rules = load_rules(Path(args.rules)) if args.rules else load_rules(None)
    result = analyze(items, rules)
    report = render_report(result, args.top)

    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
    else:
        sys.stdout.write(report + "\n")


if __name__ == "__main__":
    main()
