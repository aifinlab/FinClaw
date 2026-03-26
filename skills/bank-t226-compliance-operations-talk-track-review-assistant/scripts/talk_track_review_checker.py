from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Dict, List
import argparse
import json


def load_json(path: Path) -> Dict[str, List[str]]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def check_terms(text: str, terms: List[str]) -> List[str]:
    hits = []
    for term in terms:
        if term and term in text:
            hits.append(term)
    return hits


def build_report(text: str, rules: Dict[str, List[str]]) -> Dict[str, object]:
    prohibited_hits = check_terms(text, rules.get("prohibited", []))
    promise_hits = check_terms(text, rules.get("promise", []))
    required_prompts = rules.get("required_prompts", [])
    missing_prompts = [prompt for prompt in required_prompts if prompt not in text]

    issues = []
    for term in prohibited_hits:
        issues.append({"type": "prohibited", "detail": term, "severity": "critical"})
    for term in promise_hits:
        issues.append({"type": "promise", "detail": term, "severity": "high"})
    for prompt in missing_prompts:
        issues.append({"type": "missing_prompt", "detail": prompt, "severity": "medium"})

    return {
        "issue_count": len(issues),
        "issues": issues,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="话术合规审查脚本")
    parser.add_argument("--text", required=True, help="话术文本文件")
    parser.add_argument("--rules", required=True, help="规则 JSON 文件")
    parser.add_argument("--output", required=True, help="输出 JSON 文件")
    args = parser.parse_args()

    text = load_text(Path(args.text))
    rules = load_json(Path(args.rules))
    report = build_report(text, rules)

    payload = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "report": report,
    }
    Path(args.output).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
