#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""客户持仓波动解释脚本。"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Tuple
import argparse
import json


def load_payload(path: Path) -> Dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".jsonl":
        first = next((line for line in text.splitlines() if line.strip()), "{}")
        return json.loads(first)
    return json.loads(text)


def safe_float(value: Any) -> float | None:
    if value in (None, "", "NA", "N/A"):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def pct(value: float | None, digits: int = 2) -> str:
    if value is None:
        return "未提供"
    return f"{value * 100:.{digits}f}%"


def collect_missing(payload: Dict[str, Any]) -> List[str]:
    missing = []
    client = payload.get("client", {})
    portfolio = payload.get("portfolio", {})
    if not client.get("risk_profile"):
        missing.append("客户风险偏好未提供")
    if not client.get("investment_goal"):
        missing.append("投资目标未提供")
    if not portfolio.get("as_of_date"):
        missing.append("诊断时点未提供")
    positions = portfolio.get("positions", [])
    if not positions:
        missing.append("持仓明细为空")
    if portfolio.get("period") is None:
        missing.append("波动观察区间未提供")
    return missing


def compute_portfolio_return(positions: List[Dict[str, Any]]) -> float | None:
    total = 0.0
    has_value = False
    for pos in positions:
        weight = safe_float(pos.get("weight"))
        ret = safe_float(pos.get("return_pct"))
        if weight is None or ret is None:
            continue
        total += weight * ret
        has_value = True
    return total if has_value else None


def aggregate_by_key(positions: List[Dict[str, Any]], key: str) -> List[Dict[str, Any]]:
    bucket: Dict[str, Dict[str, Any]] = {}
    for pos in positions:
        bucket_key = str(pos.get(key, "未分类"))
        weight = safe_float(pos.get("weight")) or 0.0
        ret = safe_float(pos.get("return_pct")) or 0.0
        contribution = weight * ret
        entry = bucket.setdefault(
            bucket_key,
            {"name": bucket_key, "weight": 0.0, "contribution": 0.0},
        )
        entry["weight"] += weight
        entry["contribution"] += contribution
    return sorted(bucket.values(), key=lambda item: abs(item["contribution"]), reverse=True)


def pick_top_movers(positions: List[Dict[str, Any]], limit: int = 5) -> List[Dict[str, Any]]:
    scored = []
    for pos in positions:
        weight = safe_float(pos.get("weight"))
        ret = safe_float(pos.get("return_pct"))
        if weight is None or ret is None:
            continue
        contribution = weight * ret
        scored.append({
            "name": pos.get("name", "未命名资产"),
            "asset_class": pos.get("asset_class", "未分类"),
            "weight": weight,
            "return_pct": ret,
            "contribution": contribution,
        })
    scored.sort(key=lambda item: abs(item["contribution"]), reverse=True)
    return scored[:limit]


def detect_concentration(positions: List[Dict[str, Any]]) -> List[str]:
    alerts = []
    for pos in positions:
        weight = safe_float(pos.get("weight"))
        if weight is None:
            continue
        if weight >= 0.2:
            alerts.append(f"单一资产 {pos.get('name', '未命名')} 权重达到 {pct(weight)}，集中度偏高。")
    return alerts


def build_driver_summary(
    asset_class_breakdown: List[Dict[str, Any]],
    top_movers: List[Dict[str, Any]],
) -> Tuple[List[str], List[str]]:
    drivers = []
    questions = []
    if asset_class_breakdown:
        main = asset_class_breakdown[0]
        drivers.append(
            f"主要波动贡献来自 {main['name']}，贡献约为 {pct(main['contribution'])}。"
        )
    if top_movers:
        lead = top_movers[0]
        drivers.append(
            f"单品种中 {lead['name']} 贡献最大，权重 {pct(lead['weight'])}，区间收益 {pct(lead['return_pct'])}。"
        )
        questions.append("是否存在集中度过高或非计划性持仓偏离？")
    questions.append("客户风险承受能力与当前波动幅度是否匹配？")
    questions.append("该波动是否属于短期事件驱动，还是趋势性调整？")
    return drivers, questions


def build_result(payload: Dict[str, Any]) -> Dict[str, Any]:
    client = payload.get("client", {})
    portfolio = payload.get("portfolio", {})
    positions = portfolio.get("positions", [])
    benchmark = payload.get("benchmark", {})
    market = payload.get("market", {})

    missing = collect_missing(payload)
    portfolio_return = compute_portfolio_return(positions)
    benchmark_return = safe_float(benchmark.get("return_pct"))
    excess_return = None
    if portfolio_return is not None and benchmark_return is not None:
        excess_return = portfolio_return - benchmark_return

    asset_class_breakdown = aggregate_by_key(positions, "asset_class")
    top_movers = pick_top_movers(positions)
    concentration_alerts = detect_concentration(positions)
    driver_summary, follow_questions = build_driver_summary(asset_class_breakdown, top_movers)

    narrative = ""
    if portfolio_return is not None:
        narrative = f"组合区间收益约为 {pct(portfolio_return)}。"
        if benchmark_return is not None:
            narrative += f"相对基准 {benchmark.get('name', '基准')} 超额 {pct(excess_return)}。"
    else:
        narrative = "组合收益数据不完整，需补充持仓权重与收益口径。"

    return {
        "skill_name": "bank-t185-wealth-management-volatility-explanation-assistant",
        "client": {
            "name": client.get("name", ""),
            "risk_profile": client.get("risk_profile", ""),
            "investment_goal": client.get("investment_goal", ""),
            "horizon": client.get("horizon", ""),
            "liquidity_needs": client.get("liquidity_needs", ""),
        },
        "portfolio": {
            "as_of_date": portfolio.get("as_of_date", ""),
            "period": portfolio.get("period", ""),
            "total_value": portfolio.get("total_value", ""),
            "base_currency": portfolio.get("base_currency", ""),
            "return_pct": portfolio_return,
        },
        "benchmark": {
            "name": benchmark.get("name", ""),
            "return_pct": benchmark_return,
            "excess_return_pct": excess_return,
        },
        "market": {
            "key_events": market.get("key_events", []),
            "summary": market.get("summary", ""),
        },
        "asset_class_breakdown": asset_class_breakdown,
        "top_movers": top_movers,
        "driver_summary": driver_summary,
        "concentration_alerts": concentration_alerts,
        "follow_up_questions": follow_questions,
        "missing_fields": missing,
        "narrative_summary": narrative,
    }


def render_markdown(result: Dict[str, Any]) -> str:
    client = result["client"]
    portfolio = result["portfolio"]
    benchmark = result["benchmark"]

    def bullet(items: List[str]) -> List[str]:
        if not items:
            return ["- 暂无"]
        return [f"- {item}" for item in items]

    lines = [
        f"# 持仓波动解释报告 - {client.get('name') or '未命名客户'}",
        "",
        "## 一、客户与诊断背景",
        f"- 风险偏好：{client.get('risk_profile') or '未提供'}",
        f"- 投资目标：{client.get('investment_goal') or '未提供'}",
        f"- 投资期限：{client.get('horizon') or '未提供'}",
        f"- 流动性需求：{client.get('liquidity_needs') or '未提供'}",
        f"- 诊断时点：{portfolio.get('as_of_date') or '未提供'}",
        f"- 观察区间：{portfolio.get('period') or '未提供'}",
        "",
        "## 二、核心结论",
        f"- 组合收益：{pct(portfolio.get('return_pct'))}",
        f"- 基准收益：{pct(benchmark.get('return_pct'))}",
        f"- 超额收益：{pct(benchmark.get('excess_return_pct'))}",
        f"- 摘要：{result.get('narrative_summary')}",
        "",
        "## 三、资产大类贡献",
    ]

    for item in result["asset_class_breakdown"]:
        lines.append(f"- {item['name']}：权重 {pct(item['weight'])}，贡献 {pct(item['contribution'])}")

    lines.extend(
        [
            "",
            "## 四、主要波动来源",
            *bullet(result["driver_summary"]),
            "",
            "## 五、单品种贡献前列",
        ]
    )

    if result["top_movers"]:
        for item in result["top_movers"]:
            lines.append(
                f"- {item['name']}（{item['asset_class']}）权重 {pct(item['weight'])}，"
                f"区间收益 {pct(item['return_pct'])}，贡献 {pct(item['contribution'])}"
            )
    else:
        lines.append("- 暂无")

    lines.extend(
        [
            "",
            "## 六、集中度与风险提示",
            *bullet(result["concentration_alerts"]),
            "",
            "## 七、市场与事件补充",
            *bullet(result["market"].get("key_events", [])),
            "",
            "## 八、后续沟通建议",
            *bullet(result["follow_up_questions"]),
            "",
            "## 九、待补充信息",
            *bullet(result["missing_fields"]),
            "",
            "## 十、结论边界",
            "- 输出用于波动解释与客户沟通，不构成收益承诺或投资建议。",
            "- 缺失信息需补齐后再进行配置调整或适当性判断。",
        ]
    )

    return "\n".join(lines)


def write_output(content: str, output_path: Path | None) -> None:
    if output_path is None:
        print(content)
        return
    output_path.write_text(content, encoding="utf-8")
    print(f"已输出结果: {output_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="客户持仓波动解释脚本")
    parser.add_argument("--input", required=True, help="输入 JSON/JSONL 文件路径")
    parser.add_argument("--output", help="输出文件路径")
    parser.add_argument(
        "--format",
        choices=("json", "markdown"),
        default="markdown",
        help="输出格式，默认 markdown",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = load_payload(Path(args.input))
    result = build_result(payload)

    if args.format == "json":
        content = json.dumps(result, ensure_ascii=False, indent=2)
    else:
        content = render_markdown(result)

    output_path = Path(args.output) if args.output else None
    write_output(content, output_path)


if __name__ == "__main__":
    main()
