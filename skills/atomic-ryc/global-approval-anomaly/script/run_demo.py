from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from approval_risk_detector import ApprovalRiskDetector, ensure_output_dir
from fetch_public_data import PublicDataFetcher


DEFAULT_COMPANY = "柏堡龙"
DEFAULT_SYMBOL = "002776"


def write_markdown_report(summary: dict, events_csv_path: str, report_path: str) -> None:
    lines = [
        f"# {summary['company']} 审批异常风险识别报告",
        "",
        f"- 识别事件数：{summary['events']}",
        f"- 总风险分：{summary['total_risk_score']}",
        f"- 最高单事件分：{summary['max_event_score']}",
        f"- 总体等级：{summary['overall_level']}",
        "",
        "## 主要信号",
    ]
    for k, v in summary.get("top_signals", {}).items():
        lines.append(f"- {k}: {v}")
    lines += ["", f"详细事件表：`{events_csv_path}`", ""]

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser(description="上市企业审批异常风险识别 Demo")
    parser.add_argument("--symbol", default=DEFAULT_SYMBOL, help="股票代码，例如 002776")
    parser.add_argument("--company", default=DEFAULT_COMPANY, help="公司简称，例如 柏堡龙")
    parser.add_argument("--pages", type=int, default=3, help="抓取公告页数")
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parent
    out_dir = Path(ensure_output_dir(str(base_dir.parent / "output")))

    fetcher = PublicDataFetcher()
    cninfo_events = fetcher.fetch_cninfo_announcements(
        symbol=args.symbol,
        pages=args.pages,
        keywords=["审批程序", "审议程序", "追认", "担保", "关联交易", "资金占用"],
    )
    csrc_events = fetcher.fetch_csrc_search_results(company=args.company)

    events = [e.to_dict() for e in (cninfo_events + csrc_events)]

    rules_path = base_dir / "fraud_rules.json"
    detector = ApprovalRiskDetector(str(rules_path))
    df = detector.detect(args.company, events)
    summary = detector.summarize(args.company, df)

    events_csv = out_dir / "events.csv"
    summary_json = out_dir / "summary.json"
    evidence_md = out_dir / "evidence.md"

    df.to_csv(events_csv, index=False, encoding="utf-8-sig")
    with open(summary_json, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    write_markdown_report(summary, str(events_csv), str(evidence_md))

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"Saved: {events_csv}")
    print(f"Saved: {summary_json}")
    print(f"Saved: {evidence_md}")


if __name__ == "__main__":
    main()
