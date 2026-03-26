#!/usr/bin/env python3
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List
import argparse
import json
import re
import sys


DEFAULT_CLAUSE_RULES = {
    "payment": ["支付", "价款", "清偿", "回款", "本金", "利息"],
    "default": ["违约", "违约责任", "提前到期", "救济", "追偿"],
    "guarantee": ["担保", "抵押", "质押", "保证", "反担保"],
    "info_disclosure": ["信息披露", "报告", "通知", "重大事项", "审计"],
    "covenant": ["承诺", "不得", "限制", "约束", "资金用途"],
    "termination": ["解除", "终止", "失效"],
    "dispute_resolution": ["争议解决", "仲裁", "法院", "管辖"],
    "governing_law": ["适用法律", "法律适用", "准据法"],
    "confidentiality": ["保密", "商业秘密", "信息安全"],
}

DEFAULT_REQUIRED = [
    "payment",
    "default",
    "guarantee",
    "info_disclosure",
    "covenant",
    "dispute_resolution",
    "governing_law",
]

AMBIGUOUS_PATTERNS = [
    r"合理(?:期限|时间|范围)",
    r"尽快",
    r"视情况",
    r"另行协商",
    r"必要时",
    r"双方另行约定",
]


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


def load_required(path: Path | None) -> List[str]:
    if path is None:
        return DEFAULT_REQUIRED
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("Required clause file must be a JSON array.")
    return [str(x) for x in data]


def detect_types(text: str) -> List[str]:
    types = []
    for clause_type, keywords in DEFAULT_CLAUSE_RULES.items():
        if any(k in text for k in keywords):
            types.append(clause_type)
    return types


def analyze(items: List[Dict[str, Any]], required: List[str]) -> Dict[str, Any]:
    type_counts = Counter()
    clause_records = []
    ambiguous_records = []
    covered_types = set()
    contract_names = set()

    for idx, item in enumerate(items, start=1):
        contract_name = str(item.get("contract_name", "") or "")
        clause_no = str(item.get("clause_no", f"{idx}") or f"{idx}")
        title = str(item.get("clause_title", "") or "")
        text = str(item.get("clause_text", "") or "")
        full = f"{title} {text}"

        if contract_name:
            contract_names.add(contract_name)

        types = detect_types(full)
        if not types:
            types = ["uncategorized"]
        for t in types:
            type_counts[t] += 1
            covered_types.add(t)

        ambiguous_hits = []
        for pattern in AMBIGUOUS_PATTERNS:
            if re.search(pattern, full):
                ambiguous_hits.append(pattern)

        rec = {
            "clause_no": clause_no,
            "title": title or "(无标题)",
            "types": types,
            "text": text,
            "ambiguous_hits": ambiguous_hits,
        }
        clause_records.append(rec)
        if ambiguous_hits:
            ambiguous_records.append(rec)

    missing_required = [r for r in required if r not in covered_types]
    coverage_ratio = (len(required) - len(missing_required)) / max(len(required), 1)

    return {
        "contract_names": sorted(contract_names),
        "total_clauses": len(clause_records),
        "type_counts": type_counts,
        "clause_records": clause_records,
        "ambiguous_records": ambiguous_records,
        "missing_required": missing_required,
        "coverage_ratio": coverage_ratio,
    }


def render_report(result: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# 合同条款体检报告")
    lines.append("")
    lines.append("## 一、总体概览")
    contract_label = ", ".join(result["contract_names"]) if result["contract_names"] else "(未提供合同名称)"
    lines.append(f"- 合同: {contract_label}")
    lines.append(f"- 条款总数: {result['total_clauses']}")
    lines.append(f"- 关键条款覆盖率: {result['coverage_ratio']:.1%}")
    lines.append("")

    lines.append("## 二、条款分类统计")
    if not result["type_counts"]:
        lines.append("- 无")
    else:
        for t, c in result["type_counts"].most_common():
            lines.append(f"- {t}: {c}")
    lines.append("")

    lines.append("## 三、缺失关键条款")
    if not result["missing_required"]:
        lines.append("- 未发现缺失")
    else:
        for r in result["missing_required"]:
            lines.append(f"- {r}: 建议补充独立条款或明确约定")
    lines.append("")

    lines.append("## 四、需人工复核条款（模糊表达）")
    if not result["ambiguous_records"]:
        lines.append("- 无")
    else:
        for rec in result["ambiguous_records"]:
            lines.append(f"- 条款{rec['clause_no']}《{rec['title']}》 | 命中={len(rec['ambiguous_hits'])}")
            lines.append(f"  - 类型: {', '.join(rec['types'])}")
            lines.append(f"  - 模糊规则: {', '.join(rec['ambiguous_hits'])}")

    lines.append("")
    lines.append("## 五、方法与限制")
    lines.append("- 本报告基于关键词识别与规则检查，仅用于条款体检初筛。")
    lines.append("- 关键条款是否充分有效需由律师结合交易结构判断。")
    lines.append("- 本工具不构成法律意见。")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Contract clause coverage analyzer.")
    parser.add_argument("--input", required=True, help="Input JSON array or JSONL file.")
    parser.add_argument("--output", help="Output markdown path (default: stdout).")
    parser.add_argument("--required", help="Custom required clause types JSON array.")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    items = load_items(input_path)
    required = load_required(Path(args.required)) if args.required else load_required(None)
    result = analyze(items, required)
    report = render_report(result)

    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
    else:
        sys.stdout.write(report + "\n")


if __name__ == "__main__":
    main()
