#!/usr/bin/env python3
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List
import argparse
import json
import re
import sys


DEFAULT_KEYWORDS = {
    "repayment_negative": ["尚未落实", "拟", "预计", "依赖再融资", "单一客户", "待处置"],
    "repayment_positive": ["已签约", "监管账户", "回款锁定", "第三方担保", "现金流覆盖"],
    "compliance_negative": ["未取得", "处罚", "整改中", "争议", "违规"],
}


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
    for key in ("repayment_negative", "repayment_positive", "compliance_negative"):
        values = data.get(key, DEFAULT_KEYWORDS[key])
        if not isinstance(values, list):
            raise ValueError(f"keywords.{key} must be a list.")
        out[key] = [str(v) for v in values if str(v).strip()]
    return out


def count_hits(text: str, words: List[str]) -> int:
    total = 0
    for w in words:
        total += len(re.findall(re.escape(w), text, flags=re.IGNORECASE))
    return total


def classify(score: int) -> str:
    if score >= 75:
        return "feasible"
    if score >= 55:
        return "conditional"
    return "not_feasible"


def evaluate_project(item: Dict[str, Any], keywords: Dict[str, List[str]]) -> Dict[str, Any]:
    score = 70
    adjustments: List[str] = []
    missing: List[str] = []

    project_name = str(item.get("project_name", "(未命名项目)") or "(未命名项目)")
    borrower_name = str(item.get("borrower_name", "") or "")
    industry = str(item.get("industry", "") or "")

    expected_irr = to_float(item.get("expected_irr"))
    tenor_months = to_float(item.get("tenor_months"))
    collateral_coverage_ratio = to_float(item.get("collateral_coverage_ratio"))
    historical_default_rate = to_float(item.get("historical_default_rate"))
    sponsor_strength_score = to_float(item.get("sponsor_strength_score"))
    data_completeness = to_float(item.get("data_completeness"))

    repayment_source_text = str(item.get("repayment_source_text", "") or "")
    compliance_status_text = str(item.get("compliance_status_text", "") or "")

    if collateral_coverage_ratio is None:
        missing.append("collateral_coverage_ratio")
    else:
        if collateral_coverage_ratio < 1.0:
            score -= 20
            adjustments.append(f"担保覆盖不足（{collateral_coverage_ratio:.2f}）-20")
        elif collateral_coverage_ratio < 1.2:
            score -= 10
            adjustments.append(f"担保覆盖偏低（{collateral_coverage_ratio:.2f}）-10")
        elif collateral_coverage_ratio >= 1.5:
            score += 5
            adjustments.append(f"担保覆盖较好（{collateral_coverage_ratio:.2f}）+5")

    if expected_irr is None:
        missing.append("expected_irr")
    else:
        if expected_irr < 0.05:
            score -= 8
            adjustments.append(f"收益率偏低（{expected_irr:.1%}）-8")
        elif expected_irr <= 0.15:
            score += 4
            adjustments.append(f"收益率处于合理区间（{expected_irr:.1%}）+4")
        elif expected_irr > 0.25:
            score -= 6
            adjustments.append(f"收益率假设偏激进（{expected_irr:.1%}）-6")

    if tenor_months is None:
        missing.append("tenor_months")
    else:
        if tenor_months > 60:
            score -= 5
            adjustments.append(f"期限较长（{int(tenor_months)}月）-5")
        elif tenor_months <= 24:
            score += 3
            adjustments.append(f"期限适中（{int(tenor_months)}月）+3")

    if historical_default_rate is None:
        missing.append("historical_default_rate")
    else:
        if historical_default_rate > 0.08:
            score -= 15
            adjustments.append(f"历史违约率较高（{historical_default_rate:.1%}）-15")
        elif historical_default_rate > 0.03:
            score -= 8
            adjustments.append(f"历史违约率偏高（{historical_default_rate:.1%}）-8")

    if sponsor_strength_score is None:
        missing.append("sponsor_strength_score")
    else:
        if sponsor_strength_score < 40:
            score -= 12
            adjustments.append(f"发起方实力偏弱（{sponsor_strength_score:.0f}）-12")
        elif sponsor_strength_score < 60:
            score -= 5
            adjustments.append(f"发起方实力一般（{sponsor_strength_score:.0f}）-5")
        elif sponsor_strength_score >= 75:
            score += 6
            adjustments.append(f"发起方实力较强（{sponsor_strength_score:.0f}）+6")

    if data_completeness is None:
        missing.append("data_completeness")
    else:
        if data_completeness < 0.5:
            score -= 15
            adjustments.append(f"数据完整性不足（{data_completeness:.0%}）-15")
        elif data_completeness < 0.7:
            score -= 8
            adjustments.append(f"数据完整性偏低（{data_completeness:.0%}）-8")
        elif data_completeness >= 0.9:
            score += 3
            adjustments.append(f"数据完整性较好（{data_completeness:.0%}）+3")

    neg_repay_hits = count_hits(repayment_source_text, keywords["repayment_negative"])
    pos_repay_hits = count_hits(repayment_source_text, keywords["repayment_positive"])
    compliance_hits = count_hits(compliance_status_text, keywords["compliance_negative"])

    if neg_repay_hits:
        delta = min(neg_repay_hits * 4, 12)
        score -= delta
        adjustments.append(f"回款来源不确定信号（{neg_repay_hits}次）-{delta}")
    if pos_repay_hits:
        delta = min(pos_repay_hits * 2, 6)
        score += delta
        adjustments.append(f"回款保障信号（{pos_repay_hits}次）+{delta}")
    if compliance_hits:
        delta = min(compliance_hits * 5, 15)
        score -= delta
        adjustments.append(f"合规负面信号（{compliance_hits}次）-{delta}")

    if len(missing) >= 4:
        score -= 8
        adjustments.append("关键字段缺失较多 -8")
    elif len(missing) >= 2:
        score -= 4
        adjustments.append("存在部分关键字段缺失 -4")

    final_score = max(0, min(int(round(score)), 100))
    return {
        "project_name": project_name,
        "borrower_name": borrower_name,
        "industry": industry,
        "score": final_score,
        "level": classify(final_score),
        "adjustments": adjustments,
        "missing_fields": sorted(set(missing)),
    }


def render_report(results: List[Dict[str, Any]], top_n: int) -> str:
    level_counts = Counter(r["level"] for r in results)
    lines: List[str] = []
    lines.append("# 项目可行性初判报告")
    lines.append("")
    lines.append("## 一、总体分布")
    lines.append(f"- 项目总数: {len(results)}")
    lines.append(f"- 可行(feasible): {level_counts.get('feasible', 0)}")
    lines.append(f"- 有条件可行(conditional): {level_counts.get('conditional', 0)}")
    lines.append(f"- 暂不可行(not_feasible): {level_counts.get('not_feasible', 0)}")
    lines.append("")

    lines.append("## 二、项目初判结果")
    ranked = sorted(results, key=lambda x: x["score"])  # 按风险从高到低（分数低在前）
    if not ranked:
        lines.append("- 无")
    else:
        for r in ranked[:top_n]:
            label = f"- {r['project_name']} | score={r['score']} | level={r['level']}"
            if r["borrower_name"]:
                label += f" | borrower={r['borrower_name']}"
            if r["industry"]:
                label += f" | industry={r['industry']}"
            lines.append(label)
            if r["adjustments"]:
                for a in r["adjustments"][:8]:
                    lines.append(f"  - 因子: {a}")
            if r["missing_fields"]:
                lines.append("  - 待补字段: " + ", ".join(r["missing_fields"]))

    lines.append("")
    lines.append("## 三、方法与限制")
    lines.append("- 本报告基于规则打分，适用于投前初筛。")
    lines.append("- 初判结果应结合行业研究、法务审查、风控会审进行复核。")
    lines.append("- 本工具不构成授信审批或投资建议。")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Project feasibility precheck analyzer.")
    parser.add_argument("--input", required=True, help="Input JSON array or JSONL file.")
    parser.add_argument("--output", help="Output markdown path (default: stdout).")
    parser.add_argument("--keywords", help="Custom keyword JSON path.")
    parser.add_argument("--top", type=int, default=15, help="Top projects to display.")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    items = load_items(input_path)
    keywords = load_keywords(Path(args.keywords)) if args.keywords else load_keywords(None)
    results = [evaluate_project(item, keywords) for item in items]
    report = render_report(results, args.top)

    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
    else:
        sys.stdout.write(report + "\n")


if __name__ == "__main__":
    main()
