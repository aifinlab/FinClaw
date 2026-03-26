"""合规禁用表述扫描器

功能：
- 扫描话术文本中的禁用/高风险措辞
- 输出替换建议与风险等级

使用：
python scripts/phrase_guard.py --input input.json --output output.json

输入格式示例：
{
"phrases": ["话术1", "话术2"],
"prohibited_phrases": ["保本", "保证收益"],
"risky_phrases": ["稳赚", "必赚"],
"suggestions": {
    "保本": "请改为“关注本金安全性要求”",
    "保证收益": "请改为“历史表现不代表未来收益”"
}
}
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List
import argparse
import json


def validate_input(data: dict) -> dict:
    """验证输入参数"""
    if not isinstance(data, dict):
        raise ValueError("输入必须是字典类型")

    required_fields = []  # 添加必填字段
    for field in required_fields:
        if field not in data:
            raise ValueError(f"缺少必填字段: {field}")

    return data




@dataclass
class PhraseScanInput:
    phrases: List[str]
    prohibited_phrases: List[str] = field(default_factory=list)
    risky_phrases: List[str] = field(default_factory=list)
    suggestions: Dict[str, str] = field(default_factory=dict)


def load_input(path: Path) -> PhraseScanInput:
    data = json.loads(path.read_text(encoding="utf-8"))
    return PhraseScanInput(
        phrases=data.get("phrases", []),
        prohibited_phrases=data.get("prohibited_phrases", []),
        risky_phrases=data.get("risky_phrases", []),
        suggestions=data.get("suggestions", {}),
    )


def scan_phrase(phrase: str, scan_input: PhraseScanInput) -> List[Dict[str, str]]:
    hits: List[Dict[str, str]] = []
    for item in scan_input.prohibited_phrases:
        if item in phrase:
            hits.append(
                {
                    "phrase": phrase,
                    "hit": item,
                    "risk_level": "禁止",
                    "suggestion": scan_input.suggestions.get(item, "请删除或替换该表述"),
                }
            )
    for item in scan_input.risky_phrases:
        if item in phrase:
            hits.append(
                {
                    "phrase": phrase,
                    "hit": item,
                    "risk_level": "高风险",
                    "suggestion": scan_input.suggestions.get(item, "请补充风险提示或降低确定性措辞"),
                }
            )
    return hits


def build_report(scan_input: PhraseScanInput) -> Dict[str, List[Dict[str, str]]]:
    report: List[Dict[str, str]] = []
    for phrase in scan_input.phrases:
        report.extend(scan_phrase(phrase, scan_input))
    return {"hits": report}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="合规禁用表述扫描器")
    parser.add_argument("--input", required=True, help="输入JSON路径")
    parser.add_argument("--output", required=True, help="输出JSON路径")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)

    scan_input = load_input(input_path)
    report = build_report(scan_input)

    output_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
