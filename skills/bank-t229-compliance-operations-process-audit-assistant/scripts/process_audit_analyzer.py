from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Dict, List
import argparse
import json

import pandas as pd


def load_table(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)
    if path.suffix.lower() in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    raise ValueError("仅支持 CSV 或 Excel 文件")


def load_flow_definition(path: Path) -> List[str]:
    definition = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(definition, list):
        raise ValueError("流程定义应为 JSON 数组，如 [\"受理\",\"初审\",...] ")
    return [str(item) for item in definition]


def check_sequence(actual: List[str], expected: List[str]) -> List[Dict[str, object]]:
    issues = []
    expected_index = {name: idx for idx, name in enumerate(expected)}
    last_idx = -1
    for node in actual:
        if node not in expected_index:
            issues.append({"type": "unknown_node", "node": node, "detail": "节点不在流程定义中"})
            continue
        idx = expected_index[node]
        if idx < last_idx:
            issues.append(
                {
                    "type": "sequence_error",
                    "node": node,
                    "detail": "节点顺序异常",
                }
            )
        last_idx = max(last_idx, idx)

    missing = [node for node in expected if node not in actual]
    for node in missing:
        issues.append({"type": "missing_node", "node": node, "detail": "缺失节点"})

    return issues


def main() -> None:
    parser = argparse.ArgumentParser(description="审批流日志审计分析")
    parser.add_argument("--log", required=True, help="审批流日志 CSV/Excel")
    parser.add_argument("--flow", required=True, help="流程定义 JSON 文件")
    parser.add_argument("--case-id", default="case_id", help="流程实例ID字段")
    parser.add_argument("--node", default="node", help="节点字段")
    parser.add_argument("--output", required=True, help="输出 JSON 文件")
    args = parser.parse_args()

    df = load_table(Path(args.log))
    expected = load_flow_definition(Path(args.flow))

    if args.case_id not in df.columns or args.node not in df.columns:
        raise ValueError("日志缺少 case_id 或 node 字段")

    issues = []
    for case_id, group in df.groupby(args.case_id):
        actual = [str(value) for value in group.sort_index()[args.node].tolist()]
        case_issues = check_sequence(actual, expected)
        if case_issues:
            issues.append({"case_id": case_id, "issues": case_issues})

    payload = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "case_count": int(df[args.case_id].nunique()),
        "exception_cases": len(issues),
        "details": issues,
    }
    Path(args.output).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
