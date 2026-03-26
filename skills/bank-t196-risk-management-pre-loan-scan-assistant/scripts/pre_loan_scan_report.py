from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, Tuple
import argparse
import csv
import json
import os


SEVERITY_ORDER = {
    "high": 3,
    "medium": 2,
    "low": 1,
}

DEFAULT_SEVERITY_BY_TYPE = {
    "负面舆情": "high",
    "涉诉/失信": "high",
    "反洗钱名单": "high",
    "经营异常": "medium",
    "资金用途偏离": "medium",
    "交易异常": "medium",
    "押品瑕疵": "medium",
    "资料缺失": "low",
}


@dataclass
class Signal:
    rule_id: str
    rule_name: str
    risk_type: str
    severity: str
    threshold: Optional[str]
    evidence: str
    occurred_at: Optional[str]
    source: str

    @classmethod
    def from_dict(cls, raw: Dict[str, Any]) -> "Signal":
        rule_id = str(raw.get("rule_id") or raw.get("规则ID") or raw.get("ruleId") or "")
        rule_name = str(raw.get("rule_name") or raw.get("规则名称") or raw.get("ruleName") or "")
        risk_type = str(raw.get("risk_type") or raw.get("风险类型") or raw.get("type") or "")
        severity = str(raw.get("severity") or raw.get("风险等级") or raw.get("level") or "").lower()
        threshold = raw.get("threshold") or raw.get("阈值")
        evidence = str(raw.get("evidence") or raw.get("证据") or raw.get("note") or "")
        occurred_at = raw.get("occurred_at") or raw.get("发生时间") or raw.get("time")
        source = str(raw.get("source") or raw.get("来源") or "未知来源")

        if not severity:
            severity = DEFAULT_SEVERITY_BY_TYPE.get(risk_type, "medium")

        return cls(
            rule_id=rule_id,
            rule_name=rule_name,
            risk_type=risk_type or "未分类风险",
            severity=severity,
            threshold=str(threshold) if threshold is not None else None,
            evidence=evidence or "未提供证据描述",
            occurred_at=str(occurred_at) if occurred_at else None,
            source=source,
        )


@dataclass
class SummaryItem:
    risk_type: str
    severity: str
    signal_count: int
    latest_occurred_at: Optional[str]
    key_evidence: List[str]


@dataclass
class Report:
    risk_level: str
    priority: str
    summary: List[SummaryItem]
    blocking_items: List[Signal]
    verify_items: List[Signal]
    watch_items: List[Signal]


def load_signals(path: str) -> List[Signal]:
    if path.lower().endswith(".json"):
        with open(path, "r", encoding="utf-8") as handle:
            raw_data = json.load(handle)
        if isinstance(raw_data, dict):
            raw_rows = raw_data.get("signals") or raw_data.get("data") or []
        else:
            raw_rows = raw_data
        return [Signal.from_dict(row) for row in raw_rows]

    if path.lower().endswith(".csv"):
        with open(path, "r", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            return [Signal.from_dict(row) for row in reader]

    raise ValueError("仅支持 JSON 或 CSV 输入")


def severity_score(severity: str) -> int:
    return SEVERITY_ORDER.get(severity.lower(), 2)


def classify_signal(signal: Signal) -> str:
    if severity_score(signal.severity) >= 3:
        return "blocking"
    if severity_score(signal.severity) == 2:
        return "verify"
    return "watch"


def summarize(signals: Iterable[Signal]) -> List[SummaryItem]:
    buckets: Dict[Tuple[str, str], List[Signal]] = {}
    for signal in signals:
        key = (signal.risk_type, signal.severity)
        buckets.setdefault(key, []).append(signal)

    summary_items: List[SummaryItem] = []
    for (risk_type, severity), items in sorted(
        buckets.items(), key=lambda item: (-severity_score(item[0][1]), item[0][0])
    ):
        latest_time = None
        for signal in items:
            if signal.occurred_at:
                if not latest_time or signal.occurred_at > latest_time:
                    latest_time = signal.occurred_at
        key_evidence = []
        for signal in items[:3]:
            key_evidence.append(f"{signal.rule_name or signal.rule_id}：{signal.evidence}")
        summary_items.append(
            SummaryItem(
                risk_type=risk_type,
                severity=severity,
                signal_count=len(items),
                latest_occurred_at=latest_time,
                key_evidence=key_evidence,
            )
        )
    return summary_items


def infer_risk_level(signals: Iterable[Signal]) -> str:
    max_score = 0
    for signal in signals:
        max_score = max(max_score, severity_score(signal.severity))
    if max_score >= 3:
        return "高"
    if max_score == 2:
        return "中"
    return "低"


def infer_priority(blocking: List[Signal], verify: List[Signal]) -> str:
    if blocking:
        return "立即处理"
    if len(verify) >= 3:
        return "优先核验"
    if verify:
        return "常规核验"
    return "持续关注"


def build_report(signals: List[Signal]) -> Report:
    classified = {"blocking": [], "verify": [], "watch": []}
    for signal in signals:
        classified[classify_signal(signal)].append(signal)

    return Report(
        risk_level=infer_risk_level(signals),
        priority=infer_priority(classified["blocking"], classified["verify"]),
        summary=summarize(signals),
        blocking_items=classified["blocking"],
        verify_items=classified["verify"],
        watch_items=classified["watch"],
    )


def serialize_signal(signal: Signal) -> Dict[str, Any]:
    return {
        "rule_id": signal.rule_id,
        "rule_name": signal.rule_name,
        "risk_type": signal.risk_type,
        "severity": signal.severity,
        "threshold": signal.threshold,
        "evidence": signal.evidence,
        "occurred_at": signal.occurred_at,
        "source": signal.source,
    }


def write_json(report: Report, output_path: str) -> None:
    payload = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "risk_level": report.risk_level,
        "priority": report.priority,
        "summary": [
            {
                "risk_type": item.risk_type,
                "severity": item.severity,
                "signal_count": item.signal_count,
                "latest_occurred_at": item.latest_occurred_at,
                "key_evidence": item.key_evidence,
            }
            for item in report.summary
        ],
        "blocking_items": [serialize_signal(item) for item in report.blocking_items],
        "verify_items": [serialize_signal(item) for item in report.verify_items],
        "watch_items": [serialize_signal(item) for item in report.watch_items],
    }
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)


def format_signal_lines(title: str, signals: List[Signal]) -> List[str]:
    if not signals:
        return [f"- {title}：无"]
    lines = [f"- {title}：{len(signals)} 项"]
    for signal in signals:
        parts = [signal.risk_type, signal.rule_name or signal.rule_id]
        if signal.occurred_at:
            parts.append(f"时间 {signal.occurred_at}")
        parts.append(f"证据 {signal.evidence}")
        lines.append("  - " + " | ".join(parts))
    return lines


def write_markdown(report: Report, output_path: str) -> None:
    lines = [
        "# 贷前扫描风险摘要",
        "",
        f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        f"风险等级：{report.risk_level}",
        f"优先级：{report.priority}",
        "",
        "## 风险摘要",
    ]
    for item in report.summary:
        evidence = "；".join(item.key_evidence)
        lines.extend(
            [
                f"- {item.risk_type}（{item.severity}）：{item.signal_count} 项",
                f"  - 最近发生时间：{item.latest_occurred_at or '未提供'}",
                f"  - 关键证据：{evidence or '未提供'}",
            ]
        )

    lines.extend(
        [
            "",
            "## 风险问题清单",
            *format_signal_lines("阻断项", report.blocking_items),
            *format_signal_lines("重点核验项", report.verify_items),
            *format_signal_lines("一般关注项", report.watch_items),
            "",
            "## 建议动作",
            "- 明确补充材料与核验路径",
            "- 对阻断项先补查再进入后续流程",
            "- 若核验无法完成，建议暂缓推进",
        ]
    )

    with open(output_path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))


def ensure_output_dir(path: str) -> None:
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="贷前扫描信号汇总与风险摘要生成")
    parser.add_argument("input", help="输入文件路径（JSON 或 CSV）")
    parser.add_argument("--output-json", default="report.json", help="输出 JSON 文件路径")
    parser.add_argument("--output-md", default="report.md", help="输出 Markdown 文件路径")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    signals = load_signals(args.input)
    if not signals:
        raise SystemExit("未读取到有效信号")

    report = build_report(signals)
    ensure_output_dir(args.output_json)
    ensure_output_dir(args.output_md)
    write_json(report, args.output_json)
    write_markdown(report, args.output_md)


if __name__ == "__main__":
    main()
