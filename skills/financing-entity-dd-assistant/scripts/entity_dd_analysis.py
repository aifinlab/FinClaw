#!/usr/bin/env python3
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Tuple
import argparse
import json
import re
import statistics
import sys


DEFAULT_KEYWORDS = {
    "litigation": [
        "被执行",
        "失信",
        "合同纠纷",
        "借贷纠纷",
        "票据纠纷",
        "仲裁",
        "强制执行",
    ],
    "negative_news": [
        "造假",
        "违约",
        "处罚",
        "暴雷",
        "监管问询",
        "停产",
        "欠薪",
    ],
}

STATUS_RISK_PATTERNS: List[Tuple[re.Pattern[str], int, str]] = [
    (re.compile(r"吊销|注销|清算"), 20, "工商状态出现吊销/注销/清算信号"),
    (re.compile(r"经营异常|列入异常"), 10, "工商状态出现经营异常信号"),
    (re.compile(r"严重违法|失联|迁出"), 8, "工商状态出现严重违法/失联/迁出信号"),
]


def to_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
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

    items = []
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
    out = {}
    for key in ("litigation", "negative_news"):
        values = data.get(key, [])
        if not isinstance(values, list):
            raise ValueError(f"keywords.{key} must be a list.")
        out[key] = [str(v) for v in values if str(v).strip()]
    return out


def collect_text_from_news(news_value: Any) -> str:
    if news_value is None:
        return ""
    chunks = []
    if isinstance(news_value, list):
        for item in news_value:
            if isinstance(item, dict):
                chunks.append(str(item.get("title", "")))
                chunks.append(str(item.get("content", "")))
                chunks.append(str(item.get("summary", "")))
            else:
                chunks.append(str(item))
    elif isinstance(news_value, dict):
        chunks.append(str(news_value.get("title", "")))
        chunks.append(str(news_value.get("content", "")))
        chunks.append(str(news_value.get("summary", "")))
    else:
        chunks.append(str(news_value))
    return " ".join(chunks)


def count_keyword_hits(text: str, words: List[str]) -> int:
    if not text:
        return 0
    total = 0
    for w in words:
        if not w:
            continue
        total += len(re.findall(re.escape(w), text, flags=re.IGNORECASE))
    return total


def level_from_score(score: int) -> str:
    if score >= 70:
        return "high"
    if score >= 40:
        return "medium"
    if score >= 20:
        return "watch"
    return "low"


def evaluate_entity(record: Dict[str, Any], keywords: Dict[str, List[str]]) -> Dict[str, Any]:
    score = 0
    hits: List[str] = []
    missing: List[str] = []

    # Financial checks
    reported_revenue = to_float(record.get("reported_revenue"))
    tax_revenue = to_float(record.get("tax_revenue"))
    debt_asset_ratio = to_float(record.get("debt_asset_ratio"))
    net_profit_margin = to_float(record.get("net_profit_margin"))
    net_profit = to_float(record.get("net_profit"))
    operating_cashflow = to_float(record.get("operating_cashflow"))
    current_ratio = to_float(record.get("current_ratio"))

    if reported_revenue is not None and tax_revenue is not None and max(abs(reported_revenue), 1.0) > 0:
        gap_ratio = abs(reported_revenue - tax_revenue) / max(abs(reported_revenue), 1.0)
        if gap_ratio >= 0.30:
            score += 15
            hits.append(f"财务口径差异较大（营收差异率 {gap_ratio:.1%}）")
        elif gap_ratio >= 0.15:
            score += 8
            hits.append(f"财务口径存在差异（营收差异率 {gap_ratio:.1%}）")
    else:
        missing.extend(["reported_revenue", "tax_revenue"])

    if debt_asset_ratio is not None:
        if debt_asset_ratio >= 0.80:
            score += 12
            hits.append(f"资产负债率偏高（{debt_asset_ratio:.1%}）")
        elif debt_asset_ratio >= 0.65:
            score += 6
            hits.append(f"资产负债率处于关注区间（{debt_asset_ratio:.1%}）")
    else:
        missing.append("debt_asset_ratio")

    if net_profit_margin is not None:
        if net_profit_margin < 0:
            score += 10
            hits.append(f"净利率为负（{net_profit_margin:.1%}）")
        elif net_profit_margin < 0.03:
            score += 5
            hits.append(f"净利率偏低（{net_profit_margin:.1%}）")
    else:
        missing.append("net_profit_margin")

    if operating_cashflow is not None and net_profit is not None:
        if operating_cashflow < 0 and net_profit > 0:
            score += 10
            hits.append("存在利润为正但经营现金流为负的背离")
    else:
        missing.extend(["operating_cashflow", "net_profit"])

    if current_ratio is not None:
        if current_ratio < 1:
            score += 6
            hits.append(f"流动比率偏低（{current_ratio:.2f}）")
    else:
        missing.append("current_ratio")

    # Registry checks
    status_text = str(record.get("business_status_text", "") or "")
    for pattern, pts, note in STATUS_RISK_PATTERNS:
        if pattern.search(status_text):
            score += pts
            hits.append(note)

    abnormal_operation_count = to_float(record.get("abnormal_operation_count"))
    if abnormal_operation_count is not None:
        if abnormal_operation_count > 0:
            pts = min(int(abnormal_operation_count) * 3, 12)
            score += pts
            hits.append(f"经营异常记录 {int(abnormal_operation_count)} 条")
    else:
        missing.append("abnormal_operation_count")

    admin_penalty_count = to_float(record.get("admin_penalty_count"))
    if admin_penalty_count is not None:
        if admin_penalty_count >= 3:
            score += 10
            hits.append(f"行政处罚记录较多（{int(admin_penalty_count)} 条）")
        elif admin_penalty_count > 0:
            score += 4
            hits.append(f"存在行政处罚记录（{int(admin_penalty_count)} 条）")
    else:
        missing.append("admin_penalty_count")

    share_pledge_ratio = to_float(record.get("share_pledge_ratio"))
    if share_pledge_ratio is not None:
        if share_pledge_ratio >= 0.50:
            score += 8
            hits.append(f"股权质押比例偏高（{share_pledge_ratio:.1%}）")
        elif share_pledge_ratio >= 0.20:
            score += 4
            hits.append(f"存在一定股权质押压力（{share_pledge_ratio:.1%}）")

    # Litigation checks
    litigation_count = to_float(record.get("litigation_count"))
    if litigation_count is not None:
        if litigation_count >= 20:
            score += 15
            hits.append(f"涉诉数量较高（{int(litigation_count)} 件）")
        elif litigation_count >= 5:
            score += 8
            hits.append(f"涉诉数量偏多（{int(litigation_count)} 件）")
        elif litigation_count > 0:
            score += 3
            hits.append(f"存在涉诉记录（{int(litigation_count)} 件）")
    else:
        missing.append("litigation_count")

    dishonest_executed_count = to_float(record.get("dishonest_executed_count"))
    if dishonest_executed_count is not None:
        if dishonest_executed_count > 0:
            score += 15
            hits.append(f"存在失信被执行记录（{int(dishonest_executed_count)} 条）")
    else:
        missing.append("dishonest_executed_count")

    executed_amount = to_float(record.get("executed_amount"))
    if executed_amount is not None:
        if executed_amount >= 10_000_000:
            score += 10
            hits.append(f"执行标的金额较大（{executed_amount:,.0f}）")
        elif executed_amount >= 1_000_000:
            score += 5
            hits.append(f"执行标的金额需要关注（{executed_amount:,.0f}）")
    else:
        missing.append("executed_amount")

    litigation_text = str(record.get("litigation_text", "") or "")
    lit_hits = count_keyword_hits(litigation_text, keywords.get("litigation", []))
    if lit_hits >= 4:
        score += 10
        hits.append(f"涉诉文本命中高风险关键词 {lit_hits} 次")
    elif lit_hits >= 1:
        score += 4
        hits.append(f"涉诉文本命中关键词 {lit_hits} 次")

    # Public opinion checks
    news_text = collect_text_from_news(record.get("news"))
    opinion_text = str(record.get("public_opinion_text", "") or "")
    combined = f"{news_text} {opinion_text}".strip()
    news_hits = count_keyword_hits(combined, keywords.get("negative_news", []))
    if news_hits >= 5:
        score += 12
        hits.append(f"负面舆情关键词命中 {news_hits} 次")
    elif news_hits >= 2:
        score += 6
        hits.append(f"舆情存在负面信号（命中 {news_hits} 次）")

    # Missing key data penalty
    unique_missing = sorted(set(missing))
    if len(unique_missing) >= 6:
        score += 8
        hits.append("关键字段缺失较多，尽调结论不稳定")
    elif len(unique_missing) >= 3:
        score += 4
        hits.append("存在多项关键字段缺失")

    final_score = min(score, 100)
    return {
        "entity_name": str(record.get("entity_name", "") or "(未命名主体)"),
        "industry": str(record.get("industry", "") or ""),
        "as_of_date": str(record.get("as_of_date", "") or ""),
        "score": final_score,
        "level": level_from_score(final_score),
        "hits": hits,
        "missing_fields": unique_missing,
    }


def summarize(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    level_counts = Counter([r["level"] for r in results])
    scores = [r["score"] for r in results]
    avg_score = statistics.mean(scores) if scores else 0
    return {
        "total": len(results),
        "level_counts": level_counts,
        "avg_score": avg_score,
    }


def render_report(summary: Dict[str, Any], results: List[Dict[str, Any]], top_n: int) -> str:
    lines: List[str] = []
    lines.append("# 融资主体尽调风险初判报告")
    lines.append("")
    lines.append("## 一、总体概览")
    lines.append(f"- 主体样本数: {summary['total']}")
    lines.append(f"- 平均风险分: {summary['avg_score']:.1f}")
    lines.append(f"- 高风险(high): {summary['level_counts'].get('high', 0)}")
    lines.append(f"- 中风险(medium): {summary['level_counts'].get('medium', 0)}")
    lines.append(f"- 关注(watch): {summary['level_counts'].get('watch', 0)}")
    lines.append(f"- 低风险(low): {summary['level_counts'].get('low', 0)}")
    lines.append("")
    lines.append("## 二、主体风险排名")

    ranked = sorted(results, key=lambda x: x["score"], reverse=True)
    if not ranked:
        lines.append("- 无可用样本")
    else:
        for idx, r in enumerate(ranked[:top_n], start=1):
            title = f"{idx}. {r['entity_name']} | score={r['score']} | level={r['level']}"
            if r["industry"]:
                title += f" | industry={r['industry']}"
            if r["as_of_date"]:
                title += f" | as_of={r['as_of_date']}"
            lines.append(f"- {title}")

    lines.append("")
    lines.append("## 三、主体分项结论")
    if not ranked:
        lines.append("- 无")
    else:
        for r in ranked[:top_n]:
            lines.append(f"### {r['entity_name']}（{r['level']} / {r['score']}）")
            if r["hits"]:
                for hit in r["hits"]:
                    lines.append(f"- 风险命中: {hit}")
            else:
                lines.append("- 风险命中: 暂未命中明显规则")
            if r["missing_fields"]:
                lines.append("- 待补字段: " + ", ".join(r["missing_fields"]))
            else:
                lines.append("- 待补字段: 无")
            lines.append("")

    lines.append("## 四、方法与限制")
    lines.append("- 本报告基于规则与关键词匹配，仅用于尽调初筛。")
    lines.append("- 高风险主体应补充工商底档、司法文书、审计报告进行人工复核。")
    lines.append("- 本工具不构成授信建议、投资建议或法律意见。")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Financing entity due diligence risk analyzer.")
    parser.add_argument("--input", required=True, help="Input JSON array or JSONL file.")
    parser.add_argument("--output", help="Output markdown file path (default: stdout).")
    parser.add_argument("--keywords", help="Custom keyword rules JSON file.")
    parser.add_argument("--top", type=int, default=10, help="Top entities to display.")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    items = load_items(input_path)
    keywords = load_keywords(Path(args.keywords)) if args.keywords else load_keywords(None)
    results = [evaluate_entity(item, keywords) for item in items]
    summary = summarize(results)
    report = render_report(summary, results, args.top)

    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
    else:
        sys.stdout.write(report + "\n")


if __name__ == "__main__":
    main()
