from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


@dataclass
class RiskSignal:
    signal_id: str
    object_id: str
    object_name: str
    source: str
    severity: int
    hit_time: str
    description: str


@dataclass
class AggregatedRisk:
    object_id: str
    object_name: str
    signal_count: int
    max_severity: int
    first_hit: str
    last_hit: str
    sources: List[str]
    evidence: List[str]
    priority: str
    pending_items: List[str]
    recommended_actions: List[str]


def load_signals(path: Path) -> List[RiskSignal]:
    data = json.loads(path.read_text(encoding="utf-8"))
    signals = []
    for item in data.get("signals", []):
        signals.append(
            RiskSignal(
                signal_id=str(item.get("signal_id", "")),
                object_id=str(item.get("object_id", "")),
                object_name=str(item.get("object_name", "")),
                source=str(item.get("source", "unknown")),
                severity=int(item.get("severity", 0)),
                hit_time=str(item.get("hit_time", "")),
                description=str(item.get("description", "")),
            )
        )
    return signals


def _parse_time(ts: str) -> datetime:
    return datetime.strptime(ts, "%Y-%m-%d")


def aggregate_signals(signals: Iterable[RiskSignal]) -> List[AggregatedRisk]:
    grouped: Dict[str, List[RiskSignal]] = {}
    for signal in signals:
        grouped.setdefault(signal.object_id, []).append(signal)

    aggregated: List[AggregatedRisk] = []
    for object_id, items in grouped.items():
        items_sorted = sorted(items, key=lambda s: _parse_time(s.hit_time))
        max_severity = max(s.severity for s in items_sorted)
        signal_count = len(items_sorted)
        sources = sorted({s.source for s in items_sorted})
        evidence = [s.description for s in items_sorted[:3] if s.description]
        priority = determine_priority(max_severity, signal_count)
        pending_items = build_pending_items(items_sorted)
        recommended_actions = build_recommended_actions(priority)
        aggregated.append(
            AggregatedRisk(
                object_id=object_id,
                object_name=items_sorted[0].object_name,
                signal_count=signal_count,
                max_severity=max_severity,
                first_hit=items_sorted[0].hit_time,
                last_hit=items_sorted[-1].hit_time,
                sources=sources,
                evidence=evidence,
                priority=priority,
                pending_items=pending_items,
                recommended_actions=recommended_actions,
            )
        )
    return sorted(aggregated, key=lambda r: (r.priority, -r.max_severity))


def determine_priority(max_severity: int, signal_count: int) -> str:
    if max_severity >= 4 or signal_count >= 5:
        return "高"
    if max_severity >= 2 or signal_count >= 3:
        return "中"
    return "低"


def build_pending_items(signals: List[RiskSignal]) -> List[str]:
    pending = []
    if any(s.source == "external" for s in signals):
        pending.append("核验外部名单/舆情来源与更新时间")
    pending.append("确认关联关系是否完整")
    if any(not s.description for s in signals):
        pending.append("补充规则命中说明与明细证据")
    return pending


def build_recommended_actions(priority: str) -> List[str]:
    if priority == "高":
        return [
            "立即升级至风险经理复核",
            "安排专项排查并记录处置进度",
            "确认是否触发冻结/限额预案",
        ]
    if priority == "中":
        return [
            "纳入重点跟踪清单",
            "补充客户访谈或业务核验",
            "准备升级条件与补件清单",
        ]
    return ["保持监测频率", "记录异常并等待下一周期复核"]


def render_report(aggregated: List[AggregatedRisk]) -> Dict[str, object]:
    return {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "risk_objects": [
            {
                "object_id": item.object_id,
                "object_name": item.object_name,
                "signal_count": item.signal_count,
                "max_severity": item.max_severity,
                "first_hit": item.first_hit,
                "last_hit": item.last_hit,
                "sources": item.sources,
                "evidence": item.evidence,
                "priority": item.priority,
                "pending_items": item.pending_items,
                "recommended_actions": item.recommended_actions,
            }
            for item in aggregated
        ],
    }


def main(input_path: str, output_path: Optional[str] = None) -> None:
    signals = load_signals(Path(input_path))
    aggregated = aggregate_signals(signals)
    report = render_report(aggregated)
    if output_path:
        Path(output_path).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    else:
        print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Aggregate risk signals into a report.")
    parser.add_argument("input", help="Path to risk signal json file")
    parser.add_argument("--output", help="Optional output json path")
    args = parser.parse_args()

    main(args.input, args.output)
