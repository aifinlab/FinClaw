from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import pandas as pd


SEVERITY_MAP = {
    "missing": "critical",
    "out_of_range": "high",
    "inconsistent": "high",
    "format_error": "medium",
    "duplicate": "medium",
}


def load_table(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)
    if path.suffix.lower() in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    raise ValueError("仅支持 CSV 或 Excel 文件")


def load_rules(path: Path) -> Dict[str, Dict[str, object]]:
    if path.suffix.lower() == ".json":
        return json.loads(path.read_text(encoding="utf-8"))
    if path.suffix.lower() in {".yml", ".yaml"}:
        import yaml  # type: ignore

        return yaml.safe_load(path.read_text(encoding="utf-8"))
    raise ValueError("规则文件仅支持 JSON/YAML")


def check_missing(df: pd.DataFrame, required_fields: List[str]) -> List[Dict[str, object]]:
    issues = []
    for field in required_fields:
        if field not in df.columns:
            issues.append({"field": field, "issue": "missing_field", "detail": "字段缺失"})
            continue
        missing_count = int(df[field].isna().sum())
        if missing_count:
            issues.append(
                {
                    "field": field,
                    "issue": "missing",
                    "detail": f"缺失 {missing_count} 条",
                }
            )
    return issues


def check_duplicates(df: pd.DataFrame, key_fields: List[str]) -> List[Dict[str, object]]:
    if not key_fields:
        return []
    dup_count = int(df.duplicated(subset=key_fields).sum())
    if dup_count == 0:
        return []
    return [
        {
            "field": ",".join(key_fields),
            "issue": "duplicate",
            "detail": f"重复记录 {dup_count} 条",
        }
    ]


def check_ranges(df: pd.DataFrame, range_rules: Dict[str, Dict[str, float]]) -> List[Dict[str, object]]:
    issues = []
    for field, rule in range_rules.items():
        if field not in df.columns:
            continue
        min_value = rule.get("min")
        max_value = rule.get("max")
        if min_value is not None:
            count = int((df[field] < min_value).sum())
            if count:
                issues.append(
                    {
                        "field": field,
                        "issue": "out_of_range",
                        "detail": f"低于最小值 {min_value} 的记录 {count} 条",
                    }
                )
        if max_value is not None:
            count = int((df[field] > max_value).sum())
            if count:
                issues.append(
                    {
                        "field": field,
                        "issue": "out_of_range",
                        "detail": f"高于最大值 {max_value} 的记录 {count} 条",
                    }
                )
    return issues


def check_consistency(df: pd.DataFrame, pairs: List[List[str]]) -> List[Dict[str, object]]:
    issues = []
    for left, right in pairs:
        if left not in df.columns or right not in df.columns:
            continue
        mismatch = int((df[left] != df[right]).sum())
        if mismatch:
            issues.append(
                {
                    "field": f"{left} vs {right}",
                    "issue": "inconsistent",
                    "detail": f"不一致记录 {mismatch} 条",
                }
            )
    return issues


def build_issue_records(issues: List[Dict[str, object]]) -> List[Dict[str, object]]:
    records = []
    for issue in issues:
        issue_type = issue["issue"]
        records.append(
            {
                "field": issue["field"],
                "issue": issue_type,
                "severity": SEVERITY_MAP.get(issue_type, "low"),
                "detail": issue["detail"],
            }
        )
    return records


def main() -> None:
    parser = argparse.ArgumentParser(description="监管报送口径校验脚本")
    parser.add_argument("--data", required=True, help="报送数据文件")
    parser.add_argument("--rules", required=True, help="规则 JSON/YAML 文件")
    parser.add_argument("--output", required=True, help="输出文件路径（json/csv）")
    args = parser.parse_args()

    data_path = Path(args.data)
    rules_path = Path(args.rules)
    output_path = Path(args.output)

    df = load_table(data_path)
    rules = load_rules(rules_path)

    required_fields = rules.get("required_fields", [])
    key_fields = rules.get("key_fields", [])
    range_rules = rules.get("range_rules", {})
    consistency_pairs = rules.get("consistency_pairs", [])

    issues = []
    issues.extend(check_missing(df, required_fields))
    issues.extend(check_duplicates(df, key_fields))
    issues.extend(check_ranges(df, range_rules))
    issues.extend(check_consistency(df, consistency_pairs))

    records = build_issue_records(issues)
    payload = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "summary": {
            "issue_count": len(records),
            "critical": sum(1 for record in records if record["severity"] == "critical"),
            "high": sum(1 for record in records if record["severity"] == "high"),
            "medium": sum(1 for record in records if record["severity"] == "medium"),
            "low": sum(1 for record in records if record["severity"] == "low"),
        },
        "issues": records,
    }

    if output_path.suffix.lower() == ".csv":
        pd.DataFrame(records).to_csv(output_path, index=False)
    else:
        output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
