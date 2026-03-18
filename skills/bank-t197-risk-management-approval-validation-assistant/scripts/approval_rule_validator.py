import argparse
import json
from dataclasses import dataclass
from typing import Dict, List, Any, Optional

import pandas as pd


@dataclass
class RuleResult:
    rule_id: str
    rule_name: str
    priority: str
    hit_count: int
    hit_samples: List[str]
    reason: str


PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2}


def load_rules(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    rules = payload.get("rules", []) if isinstance(payload, dict) else payload
    if not isinstance(rules, list):
        raise ValueError("rules.json 必须是包含 rules 列表的对象或规则数组")
    return rules


def validate_rules(rules: List[Dict[str, Any]], samples: pd.DataFrame) -> List[RuleResult]:
    results: List[RuleResult] = []
    for rule in rules:
        rule_id = str(rule.get("rule_id", ""))
        rule_name = str(rule.get("rule_name", ""))
        metric = rule.get("metric")
        comparator = rule.get("comparator")
        threshold = rule.get("threshold")
        priority = str(rule.get("priority", "P2")).upper()
        reason = str(rule.get("reason", ""))

        if metric not in samples.columns:
            results.append(
                RuleResult(
                    rule_id=rule_id,
                    rule_name=rule_name,
                    priority=priority,
                    hit_count=0,
                    hit_samples=[],
                    reason=f"样本中缺少指标字段: {metric}",
                )
            )
            continue

        if comparator not in {">", ">=", "<", "<=", "==", "!="}:
            results.append(
                RuleResult(
                    rule_id=rule_id,
                    rule_name=rule_name,
                    priority=priority,
                    hit_count=0,
                    hit_samples=[],
                    reason="不支持的比较符",
                )
            )
            continue

        series = samples[metric]
        mask = _compare(series, comparator, threshold)
        hit_samples = samples.loc[mask, "sample_id"].astype(str).tolist() if "sample_id" in samples.columns else []
        hit_count = int(mask.sum())

        results.append(
            RuleResult(
                rule_id=rule_id,
                rule_name=rule_name,
                priority=priority,
                hit_count=hit_count,
                hit_samples=hit_samples,
                reason=reason or _default_reason(metric, comparator, threshold),
            )
        )

    return results


def _compare(series: pd.Series, comparator: str, threshold: Any) -> pd.Series:
    if comparator == ">":
        return series > threshold
    if comparator == ">=":
        return series >= threshold
    if comparator == "<":
        return series < threshold
    if comparator == "<=":
        return series <= threshold
    if comparator == "==":
        return series == threshold
    if comparator == "!=":
        return series != threshold
    return pd.Series([False] * len(series))


def _default_reason(metric: str, comparator: str, threshold: Any) -> str:
    return f"{metric} {comparator} {threshold}"


def summarize(results: List[RuleResult]) -> Dict[str, Any]:
    summary = {"P0": [], "P1": [], "P2": []}
    for result in results:
        priority = result.priority if result.priority in summary else "P2"
        summary[priority].append(result)

    def to_item(item: RuleResult) -> Dict[str, Any]:
        return {
            "rule_id": item.rule_id,
            "rule_name": item.rule_name,
            "hit_count": item.hit_count,
            "hit_samples": item.hit_samples,
            "reason": item.reason,
        }

    ordered = []
    for priority in sorted(summary.keys(), key=lambda k: PRIORITY_ORDER.get(k, 2)):
        ordered.append(
            {
                "priority": priority,
                "rules": [to_item(item) for item in summary[priority]],
            }
        )

    total_hits = sum(item.hit_count for item in results)

    return {
        "total_hits": total_hits,
        "priorities": ordered,
    }


def build_checklist(results: List[RuleResult]) -> List[Dict[str, Any]]:
    checklist = []
    for result in results:
        if result.hit_count == 0:
            continue
        checklist.append(
            {
                "rule_id": result.rule_id,
                "rule_name": result.rule_name,
                "priority": result.priority,
                "reason": result.reason,
                "action": "建议补件/补查并升级审查",
            }
        )
    return checklist


def generate_report(rules_path: str, samples_path: str, output_path: str) -> None:
    rules = load_rules(rules_path)
    samples = pd.read_csv(samples_path)
    results = validate_rules(rules, samples)
    report = {
        "summary": summarize(results),
        "checklist": build_checklist(results),
    }

    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(description="贷中审批规则校验生成器")
    parser.add_argument("--rules", required=True, help="规则定义文件 rules.json")
    parser.add_argument("--samples", required=True, help="样本指标文件 samples.csv")
    parser.add_argument("--output", required=True, help="输出报告 validation_report.json")
    args = parser.parse_args()

    generate_report(args.rules, args.samples, args.output)


if __name__ == "__main__":
    main()
