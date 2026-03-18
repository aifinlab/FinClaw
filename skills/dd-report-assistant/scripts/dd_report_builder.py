#!/usr/bin/env python3
import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List


SEVERITY_SCORE = {
    "critical": 10,
    "high": 7,
    "medium": 4,
    "low": 1,
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


def normalize_text(value: Any, default: str = "") -> str:
    return str(value if value is not None else default).strip() or default


def summarize_findings(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    severity_counts = Counter()
    category_counts = Counter()
    category_scores = Counter()
    status_counts = Counter()
    top_items = []
    action_items = []
    missing_fields = Counter()

    project_names = set()
    entities = set()

    for idx, item in enumerate(items, start=1):
        project_name = normalize_text(item.get("project_name"))
        entity_name = normalize_text(item.get("entity_name"))
        category = normalize_text(item.get("category"), "other").lower()
        severity = normalize_text(item.get("severity"), "medium").lower()
        finding = normalize_text(item.get("finding"), "(未填写发现内容)")
        evidence = normalize_text(item.get("evidence"))
        recommendation = normalize_text(item.get("recommendation"))
        status = normalize_text(item.get("status"), "open").lower()

        if project_name:
            project_names.add(project_name)
        if entity_name:
            entities.add(entity_name)

        sev_score = SEVERITY_SCORE.get(severity, 4)
        severity_counts[severity] += 1
        category_counts[category] += 1
        category_scores[category] += sev_score
        status_counts[status] += 1

        if not evidence:
            missing_fields["evidence"] += 1
        if not recommendation:
            missing_fields["recommendation"] += 1

        record = {
            "id": f"F{idx:03d}",
            "category": category,
            "severity": severity,
            "sev_score": sev_score,
            "finding": finding,
            "evidence": evidence,
            "recommendation": recommendation,
            "status": status,
            "entity_name": entity_name,
        }
        top_items.append(record)

        if status in {"open", "in_progress", "pending"} and recommendation:
            action_items.append(
                {
                    "severity": severity,
                    "category": category,
                    "entity_name": entity_name,
                    "action": recommendation,
                }
            )

    risk_score = sum(x["sev_score"] for x in top_items) / max(len(top_items), 1)
    if risk_score >= 7:
        overall_level = "high"
    elif risk_score >= 4:
        overall_level = "medium"
    else:
        overall_level = "low"

    return {
        "project_names": sorted(project_names),
        "entities": sorted(entities),
        "severity_counts": severity_counts,
        "category_counts": category_counts,
        "category_scores": category_scores,
        "status_counts": status_counts,
        "top_items": sorted(top_items, key=lambda x: x["sev_score"], reverse=True),
        "action_items": sorted(action_items, key=lambda x: SEVERITY_SCORE.get(x["severity"], 0), reverse=True),
        "missing_fields": missing_fields,
        "overall_level": overall_level,
        "avg_risk_score": risk_score,
    }


def render_report(summary: Dict[str, Any], top_n: int) -> str:
    lines: List[str] = []
    lines.append("# 尽调报告草稿")
    lines.append("")

    lines.append("## 一、执行摘要")
    project_label = ", ".join(summary["project_names"]) if summary["project_names"] else "(未提供项目名称)"
    entity_label = ", ".join(summary["entities"][:5]) if summary["entities"] else "(未提供主体)"
    lines.append(f"- 项目: {project_label}")
    lines.append(f"- 覆盖主体(示例): {entity_label}")
    lines.append(f"- 总体风险等级: {summary['overall_level']}")
    lines.append(f"- 平均风险分: {summary['avg_risk_score']:.2f}")
    lines.append(f"- 关键发现总数: {len(summary['top_items'])}")
    lines.append("")

    lines.append("## 二、风险分布")
    sev = summary["severity_counts"]
    lines.append(f"- critical: {sev.get('critical', 0)}")
    lines.append(f"- high: {sev.get('high', 0)}")
    lines.append(f"- medium: {sev.get('medium', 0)}")
    lines.append(f"- low: {sev.get('low', 0)}")
    lines.append("")

    lines.append("## 三、分类热力")
    if not summary["category_counts"]:
        lines.append("- 无")
    else:
        for category, count in summary["category_counts"].most_common():
            score = summary["category_scores"][category]
            lines.append(f"- {category}: count={count}, score={score}")
    lines.append("")

    lines.append("## 四、重点风险发现")
    top_items = summary["top_items"][:top_n]
    if not top_items:
        lines.append("- 无")
    else:
        for item in top_items:
            title = f"- {item['id']} | severity={item['severity']} | category={item['category']}"
            if item["entity_name"]:
                title += f" | entity={item['entity_name']}"
            lines.append(title)
            lines.append(f"  - 发现: {item['finding']}")
            if item["evidence"]:
                lines.append(f"  - 证据: {item['evidence']}")
            if item["recommendation"]:
                lines.append(f"  - 建议: {item['recommendation']}")
            lines.append(f"  - 状态: {item['status']}")

    lines.append("")
    lines.append("## 五、行动项")
    actions = summary["action_items"][:top_n]
    if not actions:
        lines.append("- 无")
    else:
        for idx, action in enumerate(actions, start=1):
            line = f"- A{idx:03d} | severity={action['severity']} | category={action['category']}"
            if action["entity_name"]:
                line += f" | entity={action['entity_name']}"
            lines.append(line)
            lines.append(f"  - 执行动作: {action['action']}")

    lines.append("")
    lines.append("## 六、数据完整性")
    if not summary["missing_fields"]:
        lines.append("- 未发现明显缺口")
    else:
        for field, cnt in summary["missing_fields"].most_common():
            lines.append(f"- {field}: 缺失 {cnt} 条")

    lines.append("")
    lines.append("## 七、方法与限制")
    lines.append("- 本报告由规则汇总生成，适用于尽调阶段性汇报草稿。")
    lines.append("- 关键结论需由法务、风控、业务联合复核。")
    lines.append("- 本工具不构成投资建议、授信决策或法律意见。")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Due diligence report builder.")
    parser.add_argument("--input", required=True, help="Input JSON array or JSONL file.")
    parser.add_argument("--output", help="Output markdown path (default: stdout).")
    parser.add_argument("--top", type=int, default=15, help="Top findings/actions to display.")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    items = load_items(input_path)
    summary = summarize_findings(items)
    report = render_report(summary, args.top)

    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
    else:
        sys.stdout.write(report + "\n")


if __name__ == "__main__":
    main()
