#!/usr/bin/env python3
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List
import argparse
import json
import re
import statistics
import sys


DEFAULT_KEYWORDS = {
    "legal": ["查封", "冻结", "权属争议", "诉讼", "仲裁", "被执行", "无证"],
    "cashflow": ["回款延迟", "逾期", "展期", "违约", "停付", "无法兑付"],
    "collateral": ["瑕疵", "抵押冲突", "重复抵押", "产权不清", "无法处置"],
}


def to_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def to_bool(value: Any) -> bool | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "y", "是"}:
        return True
    if text in {"0", "false", "no", "n", "否"}:
        return False
    return None


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


def load_keywords(path: Path | None) -> Dict[str, List[str]]:
    if path is None:
        return DEFAULT_KEYWORDS
    data = json.loads(path.read_text(encoding="utf-8"))
    out: Dict[str, List[str]] = {}
    for key in ("legal", "cashflow", "collateral"):
        values = data.get(key, [])
        if not isinstance(values, list):
            raise ValueError(f"keywords.{key} must be a list.")
        out[key] = [str(v) for v in values if str(v).strip()]
    return out


def count_hits(text: str, words: List[str]) -> int:
    if not text:
        return 0
    total = 0
    for w in words:
        total += len(re.findall(re.escape(w), text, flags=re.IGNORECASE))
    return total


def level_from_score(score: int) -> str:
    if score >= 55:
        return "high"
    if score >= 30:
        return "medium"
    if score >= 15:
        return "watch"
    return "low"


def evaluate_asset(item: Dict[str, Any], keywords: Dict[str, List[str]]) -> Dict[str, Any]:
    score = 0
    hits: List[str] = []
    missing: List[str] = []

    asset_id = str(item.get("asset_id", "") or "(unknown)")
    asset_type = str(item.get("asset_type", "") or "")
    obligor_name = str(item.get("obligor_name", "") or "(unknown obligor)")
    industry = str(item.get("industry", "") or "")
    region = str(item.get("region", "") or "")
    as_of_date = str(item.get("as_of_date", "") or "")

    outstanding_amount = to_float(item.get("outstanding_amount"))
    source_amount = to_float(item.get("source_system_amount"))
    trustee_amount = to_float(item.get("trustee_file_amount"))
    overdue_days = to_float(item.get("overdue_days"))
    maturity_days = to_float(item.get("maturity_days"))
    collateral_value = to_float(item.get("collateral_value"))
    ltv_ratio = to_float(item.get("ltv_ratio"))
    docs_missing_count = to_float(item.get("docs_missing_count"))
    chain_complete = to_bool(item.get("chain_complete"))
    relation_party_flag = to_bool(item.get("relation_party_flag"))
    transfer_restriction_flag = to_bool(item.get("transfer_restriction_flag"))

    legal_status_text = str(item.get("legal_status_text", "") or "")
    collateral_status_text = str(item.get("collateral_status_text", "") or "")
    cashflow_status_text = str(item.get("cashflow_status_text", "") or "")

    if source_amount is not None and trustee_amount is not None:
        gap = abs(source_amount - trustee_amount) / max(abs(source_amount), 1.0)
        if gap >= 0.20:
            score += 12
            hits.append(f"系统与托管口径差异较大（{gap:.1%}）")
        elif gap >= 0.10:
            score += 6
            hits.append(f"系统与托管口径存在差异（{gap:.1%}）")
    else:
        missing.extend(["source_system_amount", "trustee_file_amount"])

    if overdue_days is not None:
        if overdue_days >= 90:
            score += 15
            hits.append(f"逾期天数较高（{int(overdue_days)}天）")
        elif overdue_days >= 30:
            score += 8
            hits.append(f"逾期风险需关注（{int(overdue_days)}天）")
        elif overdue_days > 0:
            score += 3
            hits.append(f"存在短期逾期（{int(overdue_days)}天）")
    else:
        missing.append("overdue_days")

    inferred_ltv: float | None = ltv_ratio
    if inferred_ltv is None and outstanding_amount is not None and collateral_value is not None and collateral_value > 0:
        inferred_ltv = outstanding_amount / collateral_value
    if inferred_ltv is not None:
        if inferred_ltv >= 0.90:
            score += 10
            hits.append(f"LTV偏高（{inferred_ltv:.1%}）")
        elif inferred_ltv >= 0.75:
            score += 5
            hits.append(f"LTV处于关注区间（{inferred_ltv:.1%}）")
    else:
        missing.extend(["ltv_ratio", "collateral_value"])

    if docs_missing_count is not None:
        if docs_missing_count >= 3:
            score += 10
            hits.append(f"缺失材料较多（{int(docs_missing_count)}项）")
        elif docs_missing_count > 0:
            score += 4
            hits.append(f"存在缺失材料（{int(docs_missing_count)}项）")
    else:
        missing.append("docs_missing_count")

    if chain_complete is False:
        score += 8
        hits.append("资产链路不完整（穿透关系缺失）")
    elif chain_complete is None:
        missing.append("chain_complete")

    if relation_party_flag is True:
        score += 6
        hits.append("存在关联方资产信号")
    elif relation_party_flag is None:
        missing.append("relation_party_flag")

    if transfer_restriction_flag is True:
        score += 6
        hits.append("存在转让限制或处置限制")

    legal_hits = count_hits(f"{legal_status_text} {collateral_status_text}", keywords.get("legal", []))
    collateral_hits = count_hits(collateral_status_text, keywords.get("collateral", []))
    cashflow_hits = count_hits(cashflow_status_text, keywords.get("cashflow", []))

    if legal_hits >= 3:
        score += 12
        hits.append(f"权属/涉诉关键词命中较多（{legal_hits}次）")
    elif legal_hits >= 1:
        score += 5
        hits.append(f"权属/涉诉关键词命中（{legal_hits}次）")

    if collateral_hits >= 2:
        score += 8
        hits.append(f"担保物异常关键词命中（{collateral_hits}次）")
    elif collateral_hits == 1:
        score += 4
        hits.append("担保物存在瑕疵信号")

    if cashflow_hits >= 3:
        score += 10
        hits.append(f"回款异常关键词命中较多（{cashflow_hits}次）")
    elif cashflow_hits >= 1:
        score += 4
        hits.append(f"回款存在异常信号（{cashflow_hits}次）")

    if maturity_days is not None and maturity_days <= 30:
        score += 3
        hits.append(f"短期到期压力（{int(maturity_days)}天）")

    unique_missing = sorted(set(missing))
    if len(unique_missing) >= 6:
        score += 8
        hits.append("关键字段缺失较多，穿透结果稳定性不足")
    elif len(unique_missing) >= 3:
        score += 4
        hits.append("存在多项关键字段缺失")

    final_score = min(score, 100)
    return {
        "asset_id": asset_id,
        "asset_type": asset_type,
        "obligor_name": obligor_name,
        "industry": industry,
        "region": region,
        "as_of_date": as_of_date,
        "score": final_score,
        "level": level_from_score(final_score),
        "hits": hits,
        "missing_fields": unique_missing,
        "outstanding_amount": outstanding_amount or 0.0,
    }


def analyze_concentration(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = sum(max(r["outstanding_amount"], 0.0) for r in results)
    if total <= 0:
        return {
            "total_outstanding": total,
            "top_obligors": [],
            "top_industries": [],
            "top_regions": [],
        }

    by_obligor = defaultdict(float)
    by_industry = defaultdict(float)
    by_region = defaultdict(float)
    for r in results:
        amt = max(r["outstanding_amount"], 0.0)
        by_obligor[r["obligor_name"]] += amt
        by_industry[r["industry"] or "(unknown)"] += amt
        by_region[r["region"] or "(unknown)"] += amt

    def top_share(mapping: Dict[str, float], n: int = 5) -> List[Dict[str, Any]]:
        rows = []
        for key, value in sorted(mapping.items(), key=lambda x: x[1], reverse=True)[:n]:
            share = value / total if total > 0 else 0
            rows.append({"name": key, "amount": value, "share": share})
        return rows

    return {
        "total_outstanding": total,
        "top_obligors": top_share(by_obligor),
        "top_industries": top_share(by_industry),
        "top_regions": top_share(by_region),
    }


def summarize(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    levels = Counter(r["level"] for r in results)
    scores = [r["score"] for r in results]
    avg_score = statistics.mean(scores) if scores else 0.0
    return {
        "total_assets": len(results),
        "avg_score": avg_score,
        "level_counts": levels,
    }


def render_top_rows(rows: List[Dict[str, Any]]) -> List[str]:
    if not rows:
        return ["- 无数据"]
    lines = []
    for row in rows:
        lines.append(f"- {row['name']}: {row['amount']:,.0f} ({row['share']:.1%})")
    return lines


def render_report(summary: Dict[str, Any], concentration: Dict[str, Any], results: List[Dict[str, Any]], top_n: int) -> str:
    lines: List[str] = []
    lines.append("# 底层资产穿透尽调初判报告")
    lines.append("")
    lines.append("## 一、资产池概览")
    lines.append(f"- 资产样本数: {summary['total_assets']}")
    lines.append(f"- 平均风险分: {summary['avg_score']:.1f}")
    lines.append(f"- 高风险(high): {summary['level_counts'].get('high', 0)}")
    lines.append(f"- 中风险(medium): {summary['level_counts'].get('medium', 0)}")
    lines.append(f"- 关注(watch): {summary['level_counts'].get('watch', 0)}")
    lines.append(f"- 低风险(low): {summary['level_counts'].get('low', 0)}")
    lines.append(f"- 资产池余额合计: {concentration['total_outstanding']:,.0f}")
    lines.append("")

    lines.append("## 二、集中度分析")
    lines.append("### 债务人集中度（Top5）")
    lines.extend(render_top_rows(concentration["top_obligors"]))
    lines.append("")
    lines.append("### 行业集中度（Top5）")
    lines.extend(render_top_rows(concentration["top_industries"]))
    lines.append("")
    lines.append("### 区域集中度（Top5）")
    lines.extend(render_top_rows(concentration["top_regions"]))
    lines.append("")

    def concentration_warning(rows: List[Dict[str, Any]], label: str, threshold: float) -> List[str]:
        if not rows:
            return []
        top = rows[0]
        if top["share"] >= threshold:
            return [f"- {label}集中度偏高：Top1 {top['name']} 占比 {top['share']:.1%}"]
        return []

    warnings = []
    warnings.extend(concentration_warning(concentration["top_obligors"], "债务人", 0.30))
    warnings.extend(concentration_warning(concentration["top_industries"], "行业", 0.40))
    warnings.extend(concentration_warning(concentration["top_regions"], "区域", 0.45))
    if warnings:
        lines.append("### 集中度预警")
        lines.extend(warnings)
        lines.append("")

    lines.append("## 三、高风险资产清单")
    ranked = sorted(results, key=lambda x: x["score"], reverse=True)
    if not ranked:
        lines.append("- 无可用样本")
    else:
        for r in ranked[:top_n]:
            title = (
                f"- {r['asset_id']} | obligor={r['obligor_name']} | "
                f"score={r['score']} | level={r['level']}"
            )
            if r["asset_type"]:
                title += f" | type={r['asset_type']}"
            if r["as_of_date"]:
                title += f" | as_of={r['as_of_date']}"
            lines.append(title)
            if r["hits"]:
                for hit in r["hits"]:
                    lines.append(f"  - 命中: {hit}")
            else:
                lines.append("  - 命中: 暂未命中明显规则")
            if r["missing_fields"]:
                lines.append("  - 待补字段: " + ", ".join(r["missing_fields"]))
            else:
                lines.append("  - 待补字段: 无")

    lines.append("")
    lines.append("## 四、方法与限制")
    lines.append("- 本报告基于规则与关键词匹配，仅用于资产穿透尽调初筛。")
    lines.append("- 对高风险资产需补充合同链路、权属证明、司法文书进行人工复核。")
    lines.append("- 本工具不构成投资建议、授信意见或法律意见。")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Underlying asset look-through risk analyzer.")
    parser.add_argument("--input", required=True, help="Input JSON array or JSONL file.")
    parser.add_argument("--output", help="Output markdown path (default: stdout).")
    parser.add_argument("--keywords", help="Custom keyword JSON file.")
    parser.add_argument("--top", type=int, default=15, help="Top risky assets to display.")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    items = load_items(input_path)
    keywords = load_keywords(Path(args.keywords)) if args.keywords else load_keywords(None)
    results = [evaluate_asset(item, keywords) for item in items]
    summary = summarize(results)
    concentration = analyze_concentration(results)
    report = render_report(summary, concentration, results, args.top)

    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
    else:
        sys.stdout.write(report + "\n")


if __name__ == "__main__":
    main()
