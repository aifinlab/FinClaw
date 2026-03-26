from pathlib import Path
from typing import Dict, List, Any
import argparse
import csv
import json


def load_records(path: Path) -> List[Dict[str, Any]]:
    if path.suffix.lower() == ".json":
        return json.loads(path.read_text(encoding="utf-8"))
    with path.open("r", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def summarize(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    summary = {
        "total": len(records),
        "risk_items": [],
        "actions": [],
    }
    for record in records:
        if record.get("risk_flag") in {"high", "yes", "1"}:
            summary["risk_items"].append(record)
        if record.get("action_required") in {"yes", "1", "true"}:
            summary["actions"].append(record)
    return summary


def render_markdown(summary: Dict[str, Any]) -> str:
    lines = ["# 合规运营日报", "", f"- 总记录数: {summary['total']}"]
    lines.append("\n## 风险事项")
    if not summary["risk_items"]:
        lines.append("- 无显性高风险事项")
    else:
        for item in summary["risk_items"]:
            lines.append(f"- {item.get('item_id', 'unknown')} | {item.get('title', '')}")

    lines.append("\n## 行动项")
    if not summary["actions"]:
        lines.append("- 无行动项")
    else:
        for item in summary["actions"]:
            lines.append(f"- {item.get('item_id', 'unknown')} | {item.get('title', '')}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="合规运营日报生成")
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
