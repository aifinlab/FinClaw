from __future__ import annotations

from fetch_public_sources import PublicSourceClient
from pathlib import Path
from rules_engine import RuleEngine
from typing import Any, Dict, List

import argparse
import json


def flatten_text(evidence: Dict[str, List[Dict[str, str]]]) -> str:
    parts: List[str] = []
    for items in evidence.values():
        for item in items:
            parts.extend([
                item.get("title", ""),
                item.get("snippet", ""),
                item.get("publish_date", ""),
            ])
    return "\n".join([p for p in parts if p])


def load_facts(path: str | None) -> Dict[str, Any]:
    if not path:
        return {}
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description="上市企业规则引擎校验")
    parser.add_argument("--company", required=True, help="上市公司名称或证券简称")
    parser.add_argument("--exchange", default="", help="SSE / SZSE / BSE")
    parser.add_argument("--keywords", nargs="*", default=[], help="附加检索关键词，如 关联交易 立案 调查")
    parser.add_argument("--facts", default=None, help="事实输入 JSON 文件路径")
    parser.add_argument("--output", default="report.json", help="输出报告文件")
    args = parser.parse_args()

    facts = load_facts(args.facts)
    facts["exchange"] = facts.get("exchange") or args.exchange

    client = PublicSourceClient()
    evidence = client.collect_public_evidence(args.company, args.keywords)
    facts["public_text_hits"] = flatten_text(evidence)

    engine = RuleEngine()
    report = engine.evaluate(facts)
    report["company"] = args.company
    report["facts"] = facts
    report["evidence"] = evidence

    Path(args.output).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
