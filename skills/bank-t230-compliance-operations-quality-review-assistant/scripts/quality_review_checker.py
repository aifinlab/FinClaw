from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import argparse
import csv
import json

REQUIRED_FIELDS = [
    "record_id",
    "channel",
    "agent_id",
    "customer_id",
    "call_time",
    "issue_type",
    "resolution",
]

SEVERITY_RULES = {
    "missing_required": "high",
    "inconsistent": "medium",
    "suspicious": "high",
    "minor": "low",
}


def load_records(path: Path) -> List[Dict[str, Any]]:
    if path.suffix.lower() == ".json":
        return json.loads(path.read_text(encoding="utf-8"))
    with path.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader)


def check_completeness(record: Dict[str, Any]) -> List[str]:
    missing = [field for field in REQUIRED_FIELDS if not str(record.get(field, "")).strip()]
    return missing


def check_consistency(record: Dict[str, Any]) -> List[str]:
    issues = []
    if record.get("resolution") and record.get("issue_type"):
        if record["issue_type"] == "投诉" and record["resolution"] == "已解决":
            issues.append("投诉类需留存升级记录")
    if record.get("call_time"):
        try:
            datetime.fromisoformat(record["call_time"])
        except ValueError:
            issues.append("通话时间格式不符合 ISO")
    return issues


def check_authenticity_flags(record: Dict[str, Any]) -> List[str]:
    flags = []
    if record.get("call_duration"):
        try:
            duration = float(record["call_duration"])
            if duration < 10:
                flags.append("通话时长异常偏短")
        except ValueError:
            flags.append("通话时长非数值")
    if record.get("audio_hash") and len(str(record["audio_hash"])) < 16:
        flags.append("录音哈希长度异常")
    return flags


def classify_issue(issue_type: str) -> str:
    return SEVERITY_RULES.get(issue_type, "medium")


def review_records(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    issues = []
    for record in records:
        record_id = record.get("record_id") or "unknown"
        missing = check_completeness(record)
        if missing:
            issues.append({
                "record_id": record_id,
                "issue": f"缺失字段: {', '.join(missing)}",
                "type": "missing_required",
                "severity": classify_issue("missing_required"),
            })
        for item in check_consistency(record):
            issues.append({
                "record_id": record_id,
                "issue": item,
                "type": "inconsistent",
                "severity": classify_issue("inconsistent"),
            })
        for item in check_authenticity_flags(record):
            issues.append({
                "record_id": record_id,
                "issue": item,
                "type": "suspicious",
                "severity": classify_issue("suspicious"),
            })
    summary = {
        "total_records": len(records),
        "issue_count": len(issues),
        "severity_breakdown": {
            "high": sum(1 for i in issues if i["severity"] == "high"),
            "medium": sum(1 for i in issues if i["severity"] == "medium"),
            "low": sum(1 for i in issues if i["severity"] == "low"),
        },
    }
    return {"summary": summary, "issues": issues}


def render_markdown(report: Dict[str, Any]) -> str:
    lines = ["# 质检核验摘要", "", "## 总览"]
    summary = report["summary"]
    lines.append(f"- 抽样数量: {summary['total_records']}")
    lines.append(f"- 异常数量: {summary['issue_count']}")
    lines.append(
        "- 严重度: 高 {high} / 中 {medium} / 低 {low}".format(**summary["severity_breakdown"])
    )
    lines.append("\n## 异常项")
    if not report["issues"]:
        lines.append("- 无异常")
        return "\n".join(lines)
    for issue in report["issues"]:
        lines.append(
            f"- 记录 {issue['record_id']} | {issue['issue']} | 严重度: {issue['severity']}"
        )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="质检抽样核验")
    parser.add_argument("input", type=Path, help="输入CSV或JSON")
    parser.add_argument("--json-out", type=Path, help="输出JSON报告")
    parser.add_argument("--md-out", type=Path, help="输出Markdown摘要")
    args = parser.parse_args()

    records = load_records(args.input)
    report = review_records(records)

    if args.json_out:
        args.json_out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.md_out:
        args.md_out.write_text(render_markdown(report), encoding="utf-8")

    if not args.json_out and not args.md_out:
        print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
