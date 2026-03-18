import argparse
import json
from pathlib import Path
from typing import Dict, List

SECTION_HEADERS = ["议题", "讨论", "结论", "行动项"]


def split_paragraphs(text: str) -> List[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def build_minutes(paragraphs: List[str]) -> Dict[str, object]:
    minutes = {
        "overview": paragraphs[:2],
        "decisions": [],
        "actions": [],
        "risks": [],
    }
    for line in paragraphs:
        if any(key in line for key in ["决定", "同意", "通过", "明确"]):
            minutes["decisions"].append(line)
        if any(key in line for key in ["行动", "负责人", "截止", "跟进"]):
            minutes["actions"].append(line)
        if any(key in line for key in ["风险", "异常", "投诉", "监管"]):
            minutes["risks"].append(line)
    return minutes


def render_markdown(minutes: Dict[str, object]) -> str:
    lines = ["# 会议纪要", "", "## 会议概览"]
    for item in minutes["overview"]:
        lines.append(f"- {item}")

    lines.append("\n## 关键结论")
    if minutes["decisions"]:
        for item in minutes["decisions"]:
            lines.append(f"- {item}")
    else:
        lines.append("- （未识别到明确结论，建议人工补充）")

    lines.append("\n## 行动项")
    if minutes["actions"]:
        for item in minutes["actions"]:
            lines.append(f"- {item}")
    else:
        lines.append("- （未识别到行动项，建议人工补充）")

    lines.append("\n## 风险提示")
    if minutes["risks"]:
        for item in minutes["risks"]:
            lines.append(f"- {item}")
    else:
        lines.append("- 未识别到显性风险提示")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="会议纪要生成")
    parser.add_argument("input", type=Path, help="输入txt或json")
    parser.add_argument("--md-out", type=Path, help="输出markdown")
    parser.add_argument("--json-out", type=Path, help="输出json")
    args = parser.parse_args()

    if args.input.suffix.lower() == ".json":
        raw = json.loads(args.input.read_text(encoding="utf-8"))
        text = raw.get("text", "") if isinstance(raw, dict) else "\n".join([str(x) for x in raw])
    else:
        text = args.input.read_text(encoding="utf-8")

    paragraphs = split_paragraphs(text)
    minutes = build_minutes(paragraphs)

    if args.json_out:
        args.json_out.write_text(json.dumps(minutes, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.md_out:
        args.md_out.write_text(render_markdown(minutes), encoding="utf-8")

    if not args.json_out and not args.md_out:
        print(json.dumps(minutes, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
