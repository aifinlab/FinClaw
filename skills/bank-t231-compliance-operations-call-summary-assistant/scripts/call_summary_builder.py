import argparse
import json
import re
from pathlib import Path
from typing import Dict, List

SPEAKER_RE = re.compile(r"^(?P<speaker>\S+)[：: ](?P<content>.+)$")


def split_lines(text: str) -> List[Dict[str, str]]:
    items: List[Dict[str, str]] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        match = SPEAKER_RE.match(line)
        if match:
            items.append({"speaker": match.group("speaker"), "content": match.group("content")})
        else:
            items.append({"speaker": "unknown", "content": line})
    return items


def extract_keywords(text: str) -> Dict[str, List[str]]:
    risk_words = ["投诉", "升级", "监管", "欺诈", "异常", "拒绝", "无法", "泄露"]
    action_words = ["回访", "核实", "补充", "提交", "升级处理", "工单", "登记"]

    risks = sorted({w for w in risk_words if w in text})
    actions = sorted({w for w in action_words if w in text})
    return {"risks": risks, "actions": actions}


def build_summary(lines: List[Dict[str, str]]) -> Dict[str, object]:
    full_text = "\n".join([f"{x['speaker']}: {x['content']}" for x in lines])
    keywords = extract_keywords(full_text)

    customer_requests = [x["content"] for x in lines if "客户" in x["speaker"] or "客户" in x["content"]]
    agent_actions = [x["content"] for x in lines if "坐席" in x["speaker"] or "客服" in x["speaker"]]

    # very lightweight heuristic: first 3 lines as background
    background = [x["content"] for x in lines[:3]]

    return {
        "background": background,
        "customer_requests": customer_requests[:5],
        "agent_actions": agent_actions[:5],
        "risk_keywords": keywords["risks"],
        "action_keywords": keywords["actions"],
        "raw_line_count": len(lines),
    }


def render_markdown(summary: Dict[str, object]) -> str:
    lines = ["# 录音摘要", "", "## 背景"]
    for item in summary["background"]:
        lines.append(f"- {item}")

    lines.append("\n## 客户诉求")
    if summary["customer_requests"]:
        for item in summary["customer_requests"]:
            lines.append(f"- {item}")
    else:
        lines.append("- （未识别到明确诉求，建议人工复核）")

    lines.append("\n## 坐席处理动作")
    if summary["agent_actions"]:
        for item in summary["agent_actions"]:
            lines.append(f"- {item}")
    else:
        lines.append("- （未识别到明确处理动作，建议人工复核）")

    lines.append("\n## 风险提示")
    if summary["risk_keywords"]:
        lines.append("- 关键词: " + ", ".join(summary["risk_keywords"]))
    else:
        lines.append("- 未发现明显风险关键词（仍需结合业务判断）")

    lines.append("\n## 后续建议")
    if summary["action_keywords"]:
        lines.append("- 建议动作: " + ", ".join(summary["action_keywords"]))
    else:
        lines.append("- 建议补充：确认客户诉求、是否需升级处理、工单是否闭环")

    lines.append("\n---")
    lines.append(f"原始行数: {summary['raw_line_count']}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="录音转写摘要生成")
    parser.add_argument("input", type=Path, help="输入txt或json")
    parser.add_argument("--md-out", type=Path, help="输出markdown")
    parser.add_argument("--json-out", type=Path, help="输出json")
    args = parser.parse_args()

    if args.input.suffix.lower() == ".json":
        raw = json.loads(args.input.read_text(encoding="utf-8"))
        text = raw.get("text", "") if isinstance(raw, dict) else "\n".join([str(x) for x in raw])
    else:
        text = args.input.read_text(encoding="utf-8")

    lines = split_lines(text)
    summary = build_summary(lines)

    if args.json_out:
        args.json_out.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.md_out:
        args.md_out.write_text(render_markdown(summary), encoding="utf-8")

    if not args.json_out and not args.md_out:
        print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
