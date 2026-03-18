import argparse
import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

STATUS_ORDER = ["未开始", "进行中", "已完成", "超期"]


def load_records(path: Path) -> List[Dict[str, Any]]:
    if path.suffix.lower() == ".json":
        return json.loads(path.read_text(encoding="utf-8"))
    with path.open("r", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def detect_overdue(record: Dict[str, Any], today: datetime) -> bool:
    due = record.get("due_date")
    if not due:
        return False
    try:
        due_date = datetime.fromisoformat(due)
    except ValueError:
        return False
    return due_date < today and record.get("status") != "已完成"


def summarize(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    today = datetime.now()
    overview = {status: 0 for status in STATUS_ORDER}
    overdue = []
    for record in records:
        status = record.get("status") or "未开始"
        if detect_overdue(record, today):
            status = "超期"
            overdue.append(record)
        overview[status] = overview.get(status, 0) + 1
    return {"overview": overview, "overdue": overdue}


def render_markdown(summary: Dict[str, Any]) -> str:
    lines = ["# 整改催办汇总", "", "## 状态概览"]
    for status, count in summary["overview"].items():
        lines.append(f"- {status}: {count}")
    lines.append("\n## 超期清单")
    if not summary["overdue"]:
        lines.append("- 无超期事项")
        return "\n".join(lines)
    for item in summary["overdue"]:
        lines.append(f"- {item.get('item_id', 'unknown')} | {item.get('title', '')} | {item.get('owner', '')}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="整改催办汇总")
    parser.add_argument("input", type=Path, help="输入CSV或JSON")
    parser.add_argument("--md-out", type=Path, help="输出markdown")
    parser.add_argument("--json-out", type=Path, help="输出json")
    args = parser.parse_args()

    records = load_records(args.input)
    summary = summarize(records)

    if args.json_out:
        args.json_out.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.md_out:
        args.md_out.write_text(render_markdown(summary), encoding="utf-8")

    if not args.json_out and not args.md_out:
        print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
