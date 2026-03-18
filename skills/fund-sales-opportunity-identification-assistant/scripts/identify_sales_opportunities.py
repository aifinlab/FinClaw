#!/usr/bin/env python3
"""销售机会识别助手 分析脚本。"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

TASK_NAME = "销售机会识别助手"
TASK_SUMMARY = "基于客户持仓、资金变化、市场事件和产品标签，识别基金销售和再沟通机会。"
REQUIRED_INPUTS = json.loads("[\"客户持仓和交易行为\",\"客户分层与风险等级\",\"产品标签和营销主题\",\"近期市场或活动事件\"]")
OUTPUT_SECTIONS = json.loads("[\"机会清单\",\"触发原因\",\"优先级与沟通建议\",\"敏感边界提示\",\"待人工确认项\"]")


def load_input(path: Path) -> Any:
    suffix = path.suffix.lower()
    if suffix == ".json":
        return json.loads(path.read_text(encoding="utf-8"))
    if suffix == ".jsonl":
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if suffix == ".csv":
        with path.open("r", encoding="utf-8-sig", newline="") as fh:
            return list(csv.DictReader(fh))
    raise ValueError(f"Unsupported input format: {suffix}")


def flatten_text(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False)


def detect_missing(payload: Any) -> list[str]:
    haystack = flatten_text(payload)
    missing = []
    for item in REQUIRED_INPUTS:
        if item not in haystack:
            missing.append(item)
    return missing


def build_result(payload: Any) -> dict[str, Any]:
    record_count = len(payload) if isinstance(payload, list) else 1
    missing = detect_missing(payload)
    findings = [
        f"任务名称：{TASK_NAME}",
        f"记录数量：{record_count}",
        f"任务摘要：{TASK_SUMMARY}",
    ]
    if missing:
        findings.append("缺失的关键信息较多，结果应按阶段性版本使用。")
    else:
        findings.append("基础材料覆盖较完整，可进入正式分析和渲染阶段。")

    recommended_actions = []
    if missing:
        recommended_actions.extend([f"优先补充：{item}" for item in missing])
    recommended_actions.append("结合业务口径复核关键结论和敏感表述。")

    return {
        "task_name": TASK_NAME,
        "summary": f"已完成 {TASK_NAME} 的结构化整理，当前结果适合作为中文初稿或分析中间层。",
        "key_findings": findings,
        "risks": ["所有结论均应以已确认材料为准。"],
        "missing_information": missing,
        "recommended_actions": recommended_actions,
        "output_sections": OUTPUT_SECTIONS,
        "raw_preview": payload[:3] if isinstance(payload, list) else payload,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to JSON/JSONL/CSV input.")
    parser.add_argument("--output", help="Optional JSON output path.")
    args = parser.parse_args()

    payload = load_input(Path(args.input))
    result = build_result(payload)
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(text + "\\n", encoding="utf-8")
    else:
        print(text)


if __name__ == "__main__":
    main()
