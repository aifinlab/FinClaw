#!/usr/bin/env python3
import argparse
import json
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Dict, List, Tuple


DEFAULT_KEYWORDS = {
    "high": ["单方有权", "无需通知", "放弃追索", "不可撤销", "无限责任"],
    "medium": ["尽快", "合理期限", "另行协商", "视情况"],
    "protective": ["违约责任", "信息披露", "审计", "提前到期", "追偿", "监管账户"],
}


def load_payload(path: Path) -> List[Dict[str, Any]]:
    raw = path.read_text(encoding="utf-8").strip()
    if not raw:
        return []

    if raw.lstrip().startswith("{"):
        obj = json.loads(raw)
        if not isinstance(obj, dict):
            raise ValueError("JSON object expected.")
        return [obj]

    if raw.lstrip().startswith("["):
        arr = json.loads(raw)
        if not isinstance(arr, list):
            raise ValueError("JSON array expected.")
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


def load_keywords(path: Path | None) -> Dict[str, List[str]]:
    if path is None:
        return DEFAULT_KEYWORDS
    data = json.loads(path.read_text(encoding="utf-8"))
    out = {}
    for key in ("high", "medium", "protective"):
        values = data.get(key, DEFAULT_KEYWORDS[key])
        if not isinstance(values, list):
            raise ValueError(f"keywords.{key} must be a list.")
        out[key] = [str(v) for v in values if str(v).strip()]
    return out


def normalize_clause_list(value: Any) -> List[Dict[str, Any]]:
    if isinstance(value, list):
        return [x for x in value if isinstance(x, dict)]
    return []


def clause_key(clause: Dict[str, Any], fallback_index: int) -> str:
    no = str(clause.get("clause_no", "") or "").strip()
    title = str(clause.get("clause_title", "") or "").strip()
    if no:
        return f"no::{no}"
    if title:
        return f"title::{title}"
    return f"idx::{fallback_index}"


def clause_text(clause: Dict[str, Any]) -> str:
    title = str(clause.get("clause_title", "") or "")
    text = str(clause.get("clause_text", "") or "")
    return f"{title} {text}".strip()


def count_kw(text: str, words: List[str]) -> int:
    total = 0
    for w in words:
        total += len(re.findall(re.escape(w), text, flags=re.IGNORECASE))
    return total


def risk_direction(delta: int) -> str:
    if delta >= 4:
        return "risk_up_high"
    if delta >= 1:
        return "risk_up"
    if delta <= -4:
        return "risk_down_high"
    if delta <= -1:
        return "risk_down"
    return "stable"


def compare_pair(item: Dict[str, Any], keywords: Dict[str, List[str]]) -> Dict[str, Any]:
    contract_name = str(item.get("contract_name", "(未命名合同)") or "(未命名合同)")
    old_clauses = normalize_clause_list(item.get("old_clauses"))
    new_clauses = normalize_clause_list(item.get("new_clauses"))

    old_map = {clause_key(c, i): c for i, c in enumerate(old_clauses, start=1)}
    new_map = {clause_key(c, i): c for i, c in enumerate(new_clauses, start=1)}

    all_keys = sorted(set(old_map) | set(new_map))
    changes = []
    counts = {"added": 0, "removed": 0, "modified": 0, "unchanged": 0}

    for k in all_keys:
        old_clause = old_map.get(k)
        new_clause = new_map.get(k)

        if old_clause is None and new_clause is not None:
            change_type = "added"
            counts["added"] += 1
            old_text = ""
            new_text = clause_text(new_clause)
            similarity = 0.0
        elif new_clause is None and old_clause is not None:
            change_type = "removed"
            counts["removed"] += 1
            old_text = clause_text(old_clause)
            new_text = ""
            similarity = 0.0
        else:
            old_text = clause_text(old_clause or {})
            new_text = clause_text(new_clause or {})
            if old_text == new_text:
                counts["unchanged"] += 1
                continue
            change_type = "modified"
            counts["modified"] += 1
            similarity = SequenceMatcher(None, old_text, new_text).ratio()

        old_high = count_kw(old_text, keywords["high"])
        new_high = count_kw(new_text, keywords["high"])
        old_med = count_kw(old_text, keywords["medium"])
        new_med = count_kw(new_text, keywords["medium"])
        old_protect = count_kw(old_text, keywords["protective"])
        new_protect = count_kw(new_text, keywords["protective"])

        delta = (new_high - old_high) * 3 + (new_med - old_med) + (old_protect - new_protect) * 2
        direction = risk_direction(delta)

        clause_no = ""
        clause_title = ""
        ref = new_clause or old_clause or {}
        clause_no = str(ref.get("clause_no", "") or "")
        clause_title = str(ref.get("clause_title", "") or "")

        reasons = []
        if new_high != old_high:
            reasons.append(f"high_kw: {old_high}->{new_high}")
        if new_med != old_med:
            reasons.append(f"medium_kw: {old_med}->{new_med}")
        if new_protect != old_protect:
            reasons.append(f"protect_kw: {old_protect}->{new_protect}")
        if not reasons:
            reasons.append("text_changed")

        changes.append(
            {
                "key": k,
                "clause_no": clause_no,
                "clause_title": clause_title,
                "change_type": change_type,
                "similarity": similarity,
                "risk_delta": delta,
                "risk_direction": direction,
                "reasons": reasons,
                "old_text": old_text,
                "new_text": new_text,
            }
        )

    changes.sort(key=lambda x: (abs(x["risk_delta"]), 1 - x["similarity"]), reverse=True)
    return {
        "contract_name": contract_name,
        "counts": counts,
        "changes": changes,
    }


def short_text(text: str, width: int = 80) -> str:
    text = text.replace("\n", " ").strip()
    if len(text) <= width:
        return text
    return text[: width - 3] + "..."


def render_report(pairs: List[Dict[str, Any]], top_n: int) -> str:
    lines: List[str] = []
    lines.append("# 合同版本差异与风险变化报告")
    lines.append("")

    total_added = sum(p["counts"]["added"] for p in pairs)
    total_removed = sum(p["counts"]["removed"] for p in pairs)
    total_modified = sum(p["counts"]["modified"] for p in pairs)
    total_unchanged = sum(p["counts"]["unchanged"] for p in pairs)

    lines.append("## 一、总体差异概览")
    lines.append(f"- 合同对比组数: {len(pairs)}")
    lines.append(f"- 新增条款: {total_added}")
    lines.append(f"- 删除条款: {total_removed}")
    lines.append(f"- 修改条款: {total_modified}")
    lines.append(f"- 未变化条款: {total_unchanged}")
    lines.append("")

    for idx, pair in enumerate(pairs, start=1):
        lines.append(f"## 二.{idx} {pair['contract_name']}")
        c = pair["counts"]
        lines.append(f"- 新增={c['added']} | 删除={c['removed']} | 修改={c['modified']} | 未变={c['unchanged']}")

        focus = pair["changes"][:top_n]
        if not focus:
            lines.append("- 无重点变化")
            lines.append("")
            continue

        lines.append("### 重点变化")
        for ch in focus:
            clause_ref = ch["clause_no"] or ch["key"]
            title = ch["clause_title"] or "(无标题)"
            lines.append(
                f"- 条款{clause_ref}《{title}》 | type={ch['change_type']} | risk={ch['risk_direction']} | delta={ch['risk_delta']} | sim={ch['similarity']:.2f}"
            )
            lines.append(f"  - 变化依据: {', '.join(ch['reasons'])}")
            if ch["change_type"] != "added":
                lines.append(f"  - old: {short_text(ch['old_text'])}")
            if ch["change_type"] != "removed":
                lines.append(f"  - new: {short_text(ch['new_text'])}")
        lines.append("")

    lines.append("## 三、方法与限制")
    lines.append("- 本报告基于条款文本差异和关键词规则，仅用于版本变更预警。")
    lines.append("- 风险变化方向需由法务结合交易背景复核。")
    lines.append("- 本工具不构成法律意见。")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Contract version comparer.")
    parser.add_argument("--input", required=True, help="Input JSON/JSONL file.")
    parser.add_argument("--output", help="Output markdown path (default: stdout).")
    parser.add_argument("--keywords", help="Custom keyword JSON path.")
    parser.add_argument("--top", type=int, default=30, help="Top changes per pair.")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    payload = load_payload(input_path)
    keywords = load_keywords(Path(args.keywords)) if args.keywords else load_keywords(None)
    pairs = [compare_pair(item, keywords) for item in payload]
    report = render_report(pairs, args.top)

    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
    else:
        sys.stdout.write(report + "\n")


if __name__ == "__main__":
    main()
