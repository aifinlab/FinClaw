#!/usr/bin/env python3
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Tuple
import argparse
import json
import re
import statistics
import sys


def load_records(path: Path) -> List[Dict[str, Any]]:
    raw = path.read_text(encoding="utf-8").strip()
    if not raw:
        return []

    if raw.lstrip().startswith("["):
        data = json.loads(raw)
        if not isinstance(data, list):
            raise ValueError("JSON input must be an array.")
        return [x for x in data if isinstance(x, dict)]

    items = []
    for idx, line in enumerate(raw.splitlines(), start=1):
        text = line.strip()
        if not text:
            continue
        obj = json.loads(text)
        if not isinstance(obj, dict):
            raise ValueError(f"JSONL line {idx} must be object.")
        items.append(obj)
    return items


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def to_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def matches_rule(value: float, rule: Dict[str, Any]) -> bool:
    if "gte" in rule and not (value >= float(rule["gte"])):
        return False
    if "gt" in rule and not (value > float(rule["gt"])):
        return False
    if "lte" in rule and not (value <= float(rule["lte"])):
        return False
    if "lt" in rule and not (value < float(rule["lt"])):
        return False
    return True


def count_hits(text: str, keywords: List[str]) -> int:
    total = 0
    for kw in keywords:
        if not kw:
            continue
        total += len(re.findall(re.escape(kw), text, flags=re.IGNORECASE))
    return total


def classify_level(score: int, cuts: Dict[str, Any]) -> str:
    stable_cut = int(cuts.get("stable", 80))
    controlled_cut = int(cuts.get("controlled", 65))
    watch_cut = int(cuts.get("watch", 50))

    if score >= stable_cut:
        return "stable"
    if score >= controlled_cut:
        return "controlled"
    if score >= watch_cut:
        return "watch"
    return "high_risk"


def apply_numeric_metric(
    metric_name: str,
    value: float | None,
    rules: Dict[str, List[Dict[str, Any]]],
) -> Tuple[int, List[str], List[str]]:
    delta = 0
    flags: List[str] = []
    facts: List[str] = []

    if value is None:
        facts.append(f"{metric_name}=N/A")
        return delta, flags, facts

    facts.append(f"{metric_name}={value:.4f}")
    for rule in rules.get(metric_name, []):
        if matches_rule(value, rule):
            delta += int(rule.get("delta", 0))
            flag = str(rule.get("flag", ""))
            if flag:
                flags.append(flag)
            # 命中第一条后退出，避免重复叠加
            break
    return delta, flags, facts


def evaluate_record(
    item: Dict[str, Any],
    rules: Dict[str, Any],
) -> Dict[str, Any]:
    score = int(rules.get("score_base", 60))

    numeric_rules = rules.get("numeric_rules", {})
    keyword_scoring = rules.get("keyword_scoring", {})

    metrics = {
        "debt_to_revenue": to_float(item.get("debt_to_revenue")),
        "debt_to_fiscal_expenditure": to_float(item.get("debt_to_fiscal_expenditure")),
        "debt_service_coverage": to_float(item.get("debt_service_coverage")),
        "cash_to_short_debt": to_float(item.get("cash_to_short_debt")),
        "revenue_growth": to_float(item.get("revenue_growth")),
        "self_sufficiency_ratio": to_float(item.get("self_sufficiency_ratio")),
        "data_completeness": to_float(item.get("data_completeness")),
    }

    facts: List[str] = []
    flags: List[str] = []

    for metric_name, value in metrics.items():
        delta, metric_flags, metric_facts = apply_numeric_metric(metric_name, value, numeric_rules)
        score += delta
        flags.extend(metric_flags)
        facts.extend(metric_facts)

    text = " ".join(
        [
            str(item.get("policy_support_text", "") or ""),
            str(item.get("event_text", "") or ""),
            str(item.get("fiscal_status_text", "") or ""),
        ]
    )

    positive_keywords = [str(x) for x in rules.get("positive_keywords", [])]
    negative_keywords = [str(x) for x in rules.get("negative_keywords", [])]
    pos_hits = count_hits(text, positive_keywords)
    neg_hits = count_hits(text, negative_keywords)

    pos_per_hit = int(keyword_scoring.get("positive_per_hit", 2))
    pos_cap = int(keyword_scoring.get("positive_cap", 10))
    neg_per_hit = int(keyword_scoring.get("negative_per_hit", -4))
    neg_cap = int(keyword_scoring.get("negative_cap", -20))

    pos_delta = min(pos_hits * pos_per_hit, pos_cap)
    neg_delta = max(neg_hits * neg_per_hit, neg_cap)
    score += pos_delta + neg_delta

    facts.append(f"policy_positive_hits={pos_hits}")
    facts.append(f"risk_negative_hits={neg_hits}")
    if pos_hits > 0:
        flags.append(f"政策支持信号命中 {pos_hits} 次")
    if neg_hits > 0:
        flags.append(f"风险事件信号命中 {neg_hits} 次")

    final_score = max(0, min(score, 100))
    level = classify_level(final_score, rules.get("level_cutoffs", {}))

    return {
        "entity_name": str(item.get("entity_name", "(未命名主体)") or "(未命名主体)"),
        "region": str(item.get("region", "") or ""),
        "as_of_date": str(item.get("as_of_date", "") or ""),
        "score": final_score,
        "level": level,
        "flags": flags,
        "facts": facts,
    }


def render_report(
    evaluated: List[Dict[str, Any]],
    baseline: Dict[str, Any],
    top_n: int,
) -> str:
    lines: List[str] = []

    scores = [x["score"] for x in evaluated]
    avg_score = statistics.mean(scores) if scores else 0.0
    level_counts = Counter([x["level"] for x in evaluated])

    lines.append("# 政信融资主体尽调报告（自动版）")
    lines.append("")
    lines.append("## 一、样本概览")
    lines.append(f"- 主体样本数: {len(evaluated)}")
    lines.append(f"- 平均评分: {avg_score:.2f}")
    lines.append(f"- stable: {level_counts.get('stable', 0)}")
    lines.append(f"- controlled: {level_counts.get('controlled', 0)}")
    lines.append(f"- watch: {level_counts.get('watch', 0)}")
    lines.append(f"- high_risk: {level_counts.get('high_risk', 0)}")
    lines.append("")

    lines.append("## 二、主体评分排序")
    ranked = sorted(evaluated, key=lambda x: x["score"], reverse=True)
    if not ranked:
        lines.append("- 无数据")
    else:
        for idx, rec in enumerate(ranked[:top_n], start=1):
            line = f"- {idx}. {rec['entity_name']} | score={rec['score']} | level={rec['level']}"
            if rec["region"]:
                line += f" | region={rec['region']}"
            if rec["as_of_date"]:
                line += f" | as_of={rec['as_of_date']}"
            lines.append(line)
    lines.append("")

    lines.append("## 三、重点风险明细")
    risky = sorted(evaluated, key=lambda x: x["score"])[:top_n]
    if not risky:
        lines.append("- 无")
    else:
        for rec in risky:
            lines.append(f"### {rec['entity_name']}（{rec['level']} / {rec['score']}）")
            lines.append("- 事实字段:")
            for fact in rec["facts"][:10]:
                lines.append(f"  - {fact}")
            lines.append("- 规则命中:")
            if rec["flags"]:
                for flag in rec["flags"][:8]:
                    lines.append(f"  - {flag}")
            else:
                lines.append("  - 暂未命中明显风险规则")
            lines.append("- 人工复核建议:")
            lines.append("  - 核验债务口径、财政可持续性与政策支持真实性。")
            lines.append("  - 补充监管披露、审计意见及重大事项进展。")
            lines.append("")

    lines.append("## 四、方法与口径")
    lines.append("- 评分规则来自 config/scoring_rules.json。")
    version = baseline.get("version", "unknown") if isinstance(baseline, dict) else "unknown"
    lines.append(f"- 参考基线版本: {version}")
    if isinstance(baseline, dict):
        benchmark = baseline.get("benchmark", {})
        if benchmark:
            lines.append("- 参考阈值:")
            for k, v in benchmark.items():
                lines.append(f"  - {k}: {v}")
    lines.append("")

    lines.append("## 五、免责声明")
    lines.append("- 本报告由系统自动生成，仅用于尽调初筛。")
    lines.append("- 报告结论需由业务、风控、法务联合人工复核。")
    lines.append("- 本报告不构成投资建议、授信决策或法律意见。")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Gov financing entity due diligence scorer.")
    parser.add_argument("--input", required=True, help="Input JSON array or JSONL file (processed data).")
    parser.add_argument("--rules", required=True, help="Path to scoring rules JSON.")
    parser.add_argument("--baseline", required=True, help="Path to baseline JSON.")
    parser.add_argument("--output", help="Output markdown path (default: stdout).")
    parser.add_argument("--top", type=int, default=15, help="Top entities to display.")
    args = parser.parse_args()

    input_path = Path(args.input)
    rules_path = Path(args.rules)
    baseline_path = Path(args.baseline)

    for p in (input_path, rules_path, baseline_path):
        if not p.exists():
            raise FileNotFoundError(f"File not found: {p}")

    records = load_records(input_path)
    rules = load_json(rules_path)
    baseline = load_json(baseline_path)

    evaluated = [evaluate_record(item, rules) for item in records]
    report = render_report(evaluated, baseline, args.top)

    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
    else:
        sys.stdout.write(report + "\n")


if __name__ == "__main__":
    main()
