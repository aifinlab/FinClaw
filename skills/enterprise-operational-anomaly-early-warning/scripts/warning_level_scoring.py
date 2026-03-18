#!/usr/bin/env python3
"""企业贷后预警等级评分示例脚本。"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

SCORE_MAP = {"低": 1, "中": 2, "高": 3}


def score_warning_level(signals: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not signals:
        return {"预警等级": "正常", "总分": 0, "说明": "暂未识别到明显异常信号"}

    total = sum(SCORE_MAP.get(item.get("严重程度", "低"), 1) for item in signals)
    high_count = sum(1 for item in signals if item.get("严重程度") == "高")

    if high_count >= 2 or total >= 10:
        level = "高预警"
    elif high_count >= 1 or total >= 6:
        level = "预警"
    elif total >= 2:
        level = "关注"
    else:
        level = "正常"

    return {
        "预警等级": level,
        "总分": total,
        "高敏感信号数量": high_count,
        "信号数量": len(signals),
        "说明": "该结果为规则型评分结果，仍需结合人工复核与补充核查。",
    }


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="对预警信号进行分级评分")
    parser.add_argument("input", help="输入 JSON 文件路径")
    parser.add_argument("-o", "--output", help="输出 JSON 文件路径")
    args = parser.parse_args()

    signals = json.loads(Path(args.input).read_text(encoding="utf-8"))
    result = score_warning_level(signals)
    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
    else:
        print(output)


if __name__ == "__main__":
    main()
