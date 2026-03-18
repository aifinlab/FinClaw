from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any


@dataclass
class Signal:
    signal_code: str
    signal_name: str
    level: str
    score: int
    evidence: str


HIGH_RISK_REGIONS = {"高风险地区A", "高风险地区B", "高风险地区C"}


def _to_float(v: Any) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def load_transactions(path: str) -> list[dict[str, Any]]:
    p = Path(path)
    if p.suffix.lower() == ".json":
        return json.loads(p.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []
    with p.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(dict(row))
    return rows


def scan_patterns(transactions: list[dict[str, Any]]) -> dict[str, Any]:
    if not transactions:
        return {"signals": [], "summary": {"message": "无可分析交易数据"}}

    amounts = [_to_float(t.get("amount")) for t in transactions]
    counterparties = [str(t.get("counterparty", "")).strip() for t in transactions if str(t.get("counterparty", "")).strip()]
    hours = [str(t.get("hour", "")).strip() for t in transactions]
    regions = [str(t.get("region", "")).strip() for t in transactions]

    signals: list[Signal] = []

    total_amount = sum(amounts)
    max_amount = max(amounts) if amounts else 0.0
    small_count = sum(1 for a in amounts if 0 < a <= 10000)
    late_count = sum(1 for h in hours if h.isdigit() and (int(h) >= 22 or int(h) <= 5))
    risky_region_count = sum(1 for r in regions if r in HIGH_RISK_REGIONS)
    cp_counter = Counter(counterparties)

    if len(transactions) >= 20 and small_count / max(len(transactions), 1) >= 0.7:
        signals.append(Signal(
            signal_code="SPLIT_TXN",
            signal_name="疑似分拆交易",
            level="中",
            score=20,
            evidence=f"共 {len(transactions)} 笔交易，其中 {small_count} 笔为小额交易，占比偏高。",
        ))

    if len(transactions) >= 10 and late_count / max(len(transactions), 1) >= 0.3:
        signals.append(Signal(
            signal_code="LATE_NIGHT_PATTERN",
            signal_name="夜间异常交易活跃",
            level="中",
            score=15,
            evidence=f"共 {late_count} 笔交易发生于深夜或凌晨时段。",
        ))

    if risky_region_count >= 3:
        signals.append(Signal(
            signal_code="RISKY_REGION",
            signal_name="高风险地区交易较多",
            level="高",
            score=25,
            evidence=f"识别到 {risky_region_count} 笔涉及高风险地区的交易。",
        ))

    if cp_counter:
        top_cp, top_cnt = cp_counter.most_common(1)[0]
        if top_cnt >= max(5, len(transactions) // 2):
            signals.append(Signal(
                signal_code="COUNTERPARTY_CONCENTRATION",
                signal_name="对手方集中度异常",
                level="中",
                score=15,
                evidence=f"对手方 {top_cp} 出现 {top_cnt} 次，集中度较高。",
            ))

    if total_amount > 0 and max_amount / total_amount >= 0.5 and len(transactions) >= 5:
        signals.append(Signal(
            signal_code="LARGE_SINGLE_TXN",
            signal_name="单笔大额占比异常",
            level="中",
            score=10,
            evidence=f"最大单笔金额占总交易金额比例较高，最大单笔金额为 {max_amount:.2f}。",
        ))

    total_score = sum(s.score for s in signals)
    if total_score >= 50:
        risk_level = "高度可疑"
    elif total_score >= 25:
        risk_level = "中度可疑"
    elif total_score > 0:
        risk_level = "低度可疑"
    else:
        risk_level = "暂未发现明显异常"

    return {
        "signals": [asdict(s) for s in signals],
        "summary": {
            "transaction_count": len(transactions),
            "total_amount": total_amount,
            "risk_level": risk_level,
            "total_score": total_score,
            "note": "该结果仅基于内部交易行为规则扫描，若缺少行业数据与外部名单，应谨慎解释。",
        },
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="可疑交易模式扫描")
    parser.add_argument("input", help="输入 CSV 或 JSON 文件")
    parser.add_argument("-o", "--output", help="输出 JSON 文件", default="scan_result.json")
    args = parser.parse_args()

    transactions = load_transactions(args.input)
    result = scan_patterns(transactions)
    Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"已输出到 {args.output}")
