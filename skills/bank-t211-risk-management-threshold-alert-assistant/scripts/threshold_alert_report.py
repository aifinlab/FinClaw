from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class ThresholdAlert:
    metric: str
    object_id: str
    object_name: str
    threshold: float
    actual: float
    unit: str
    period: str


def load_alerts(path: Path) -> List[ThresholdAlert]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    alerts: List[ThresholdAlert] = []
    for item in payload.get("alerts", []):
        alerts.append(
            ThresholdAlert(
                metric=str(item.get("metric", "")),
                object_id=str(item.get("object_id", "")),
                object_name=str(item.get("object_name", "")),
                threshold=float(item.get("threshold", 0)),
                actual=float(item.get("actual", 0)),
                unit=str(item.get("unit", "")),
                period=str(item.get("period", "")),
            )
        )
    return alerts


def severity_level(deviation_ratio: float) -> str:
    if deviation_ratio >= 1.5:
        return "高"
    if deviation_ratio >= 1.2:
        return "中"
    return "低"


def recommend_actions(level: str) -> List[str]:
    if level == "高":
        return ["立即复核指标口径", "启动专项排查", "必要时升级" ]
    if level == "中":
        return ["纳入重点跟踪", "核验历史趋势", "补充业务背景"]
    return ["保持监测", "观察下一周期表现"]


def build_report(alerts: List[ThresholdAlert]) -> Dict[str, object]:
    report_rows: List[Dict[str, object]] = []
    for alert in alerts:
        deviation = alert.actual - alert.threshold
        ratio = alert.actual / alert.threshold if alert.threshold else 0
        level = severity_level(ratio)
        report_rows.append(
            {
                "metric": alert.metric,
                "object_id": alert.object_id,
                "object_name": alert.object_name,
                "threshold": alert.threshold,
                "actual": alert.actual,
                "deviation": deviation,
                "unit": alert.unit,
                "period": alert.period,
                "severity": level,
                "actions": recommend_actions(level),
            }
        )
    return {"alerts": report_rows}


def main(input_path: str, output_path: Optional[str] = None) -> None:
    alerts = load_alerts(Path(input_path))
    report = build_report(alerts)
    if output_path:
        Path(output_path).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    else:
        print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate threshold alert report")
    parser.add_argument("input", help="Input alert json file")
    parser.add_argument("--output", help="Output report path")
    args = parser.parse_args()

    main(args.input, args.output)
