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
        "id": "r_info_disclosure",
        "name": "信息披露义务",
        "required": True,
        "keywords": ["信息披露", "定期报告", "重大事项", "信息报送"],
        "jurisdictions": ["CN"],
        "suggestion": "补充定期与重大事项信息披露条款。",
    },
    {
        "id": "r_fund_use",
        "name": "资金用途管理",
        "required": True,
        "keywords": ["资金用途", "专款专用", "用途监管", "挪用"],
        "jurisdictions": ["CN"],
        "suggestion": "补充资金用途边界与监管账户机制。",
    },
    {
        "id": "r_risk_isolation",
        "name": "风险隔离要求",
        "required": True,
        "keywords": ["风险隔离", "资产独立", "不得混同", "破产隔离"],
        "jurisdictions": ["CN"],
        "suggestion": "补充资产独立性和风险隔离约定。",
    },
    {
        "id": "r_dispute",
        "name": "争议解决机制",
        "required": True,
        "keywords": ["争议解决", "仲裁", "管辖法院", "适用法律"],
        "jurisdictions": ["CN"],
        "suggestion": "补充争议解决路径与适用法律条款。",
    },
    {
        "id": "r_aml",
        "name": "反洗钱与客户识别",
        "required": False,
        "keywords": ["反洗钱", "客户身份识别", "可疑交易", "受益所有人"],
        "jurisdictions": ["CN"],
        "suggestion": "补充反洗钱与客户识别义务条款。",
    },
    {
        "id": "r_data_privacy",
        "name": "数据与隐私保护",
        "required": False,
        "keywords": ["个人信息", "数据安全", "保密", "数据合规"],
        "jurisdictions": ["CN"],
        "suggestion": "补充数据处理边界与隐私保护责任。",
    },
]


def load_items(path: Path) -> List[Dict[str, Any]]:
    raw = path.read_text(encoding="utf-8").strip()
    if not raw:
        return []
    if raw.lstrip().startswith("["):
        arr = json.loads(raw)
        if not isinstance(arr, list):
            raise ValueError("JSON input must be an array.")
        return [x for x in arr if isinstance(x, dict)]

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


def load_rules(path: Path | None) -> List[Dict[str, Any]]:
    if path is None:
        return DEFAULT_RULES
    data = json.loads(path.read_text(encoding="utf-8"))
    rules = data.get("rules", data)
    if not isinstance(rules, list):
        raise ValueError("Rules must be list or {'rules': [...]}.")

    normalized = []
    for r in rules:
        if not isinstance(r, dict):
            continue
        kws = r.get("keywords", [])
        if not isinstance(kws, list):
            continue
        jurisdictions = r.get("jurisdictions", [])
        if jurisdictions is None:
            jurisdictions = []
        if not isinstance(jurisdictions, list):
            jurisdictions = []

        normalized.append(
            {
                "id": str(r.get("id", "custom_rule")),
                "name": str(r.get("name", "自定义规则")),
                "required": bool(r.get("required", False)),
                "keywords": [str(x) for x in kws if str(x).strip()],
                "jurisdictions": [str(j).upper() for j in jurisdictions],
                "suggestion": str(r.get("suggestion", "建议补充该监管义务对应条款。")),
            }
        )
    return normalized or DEFAULT_RULES


def applicable(rule: Dict[str, Any], jurisdiction: str) -> bool:
    allowed = rule.get("jurisdictions", [])
    if not allowed:
        return True
    return jurisdiction.upper() in allowed


def kw_hits(text: str, keywords: List[str]) -> int:
    total = 0
    for kw in keywords:
        total += len(re.findall(re.escape(kw), text, flags=re.IGNORECASE))
    return total


def coverage_level(ratio: float) -> str:
    if ratio >= 0.8:
        return "low"
    if ratio >= 0.5:
        return "medium"
    return "high"


def analyze(items: List[Dict[str, Any]], rules: List[Dict[str, Any]]) -> Dict[str, Any]:
    records = []
    rule_coverage_counter = Counter()
    gap_counter = Counter()
    level_counter = Counter()

    for idx, item in enumerate(items, start=1):
        item_id = str(item.get("item_id", f"I{idx:03d}"))
        scenario = str(item.get("scenario", "") or "")
        jurisdiction = str(item.get("jurisdiction", "CN") or "CN").upper()
        clause_text = str(item.get("clause_text", "") or "")
        asset_type = str(item.get("asset_type", "") or "")

        matched = []
        gaps = []

        required_total = 0
        required_hit = 0

        for rule in rules:
            if not applicable(rule, jurisdiction):
                continue

            hits = kw_hits(clause_text, rule["keywords"])
            if rule.get("required"):
                required_total += 1
                if hits > 0:
                    required_hit += 1

            if hits > 0:
                matched.append({"rule": rule["name"], "hits": hits})
                rule_coverage_counter[rule["name"]] += 1
            elif rule.get("required"):
                gaps.append({"rule": rule["name"], "suggestion": rule["suggestion"]})
                gap_counter[rule["name"]] += 1

        ratio = required_hit / max(required_total, 1)
        level = coverage_level(ratio)
        level_counter[level] += 1

        records.append(
            {
                "item_id": item_id,
                "scenario": scenario,
                "jurisdiction": jurisdiction,
                "asset_type": asset_type,
                "coverage_ratio": ratio,
                "level": level,
                "matched": matched,
                "gaps": gaps,
            }
        )

    records.sort(key=lambda x: (x["coverage_ratio"], len(x["gaps"])))
    return {
        "records": records,
        "rule_coverage_counter": rule_coverage_counter,
        "gap_counter": gap_counter,
        "level_counter": level_counter,
    }


def render_report(result: Dict[str, Any], top_n: int) -> str:
    lines: List[str] = []
    lines.append("# 法规匹配与缺口识别报告")
    lines.append("")
    lines.append("## 一、总体概览")
    lines.append(f"- 条目总数: {len(result['records'])}")
    lines.append(f"- 高缺口风险(high): {result['level_counter'].get('high', 0)}")
    lines.append(f"- 中缺口风险(medium): {result['level_counter'].get('medium', 0)}")
    lines.append(f"- 低缺口风险(low): {result['level_counter'].get('low', 0)}")
    lines.append("")

    lines.append("## 二、法规覆盖统计")
    if not result["rule_coverage_counter"]:
        lines.append("- 无")
    else:
        for rule, cnt in result["rule_coverage_counter"].most_common():
            lines.append(f"- {rule}: 覆盖 {cnt} 条")
    lines.append("")

    lines.append("## 三、重点缺口条目")
    top_items = result["records"][:top_n]
    if not top_items:
        lines.append("- 无")
    else:
        for rec in top_items:
            lines.append(
                f"- {rec['item_id']} | coverage={rec['coverage_ratio']:.1%} | level={rec['level']} | jurisdiction={rec['jurisdiction']}"
            )
            if rec["scenario"]:
                lines.append(f"  - 场景: {rec['scenario']}")
            if rec["asset_type"]:
                lines.append(f"  - 资产类型: {rec['asset_type']}")
            if rec["matched"]:
                matched_text = ", ".join(f"{m['rule']}({m['hits']})" for m in rec["matched"])
                lines.append(f"  - 已匹配: {matched_text}")
            if rec["gaps"]:
                for g in rec["gaps"][:5]:
                    lines.append(f"  - 缺口: {g['rule']} | 建议: {g['suggestion']}")

    lines.append("")
    lines.append("## 四、方法与限制")
    lines.append("- 本报告基于关键词匹配，不替代正式法规检索与律师审查。")
    lines.append("- 法规适用需结合业务实质、法域与最新监管口径确认。")
    lines.append("- 本工具不构成法律意见。")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Regulation matcher for legal/compliance checks.")
    parser.add_argument("--input", required=True, help="Input JSON array or JSONL file.")
    parser.add_argument("--output", help="Output markdown path (default: stdout).")
    parser.add_argument("--rules", help="Custom regulation rules JSON path.")
    parser.add_argument("--top", type=int, default=20, help="Top items to display.")
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
