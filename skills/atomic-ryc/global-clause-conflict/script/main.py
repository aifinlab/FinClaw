from __future__ import annotations

import argparse
import json
from typing import List

from fetch_public_data import load_materials
from law_rules import apply_rules, summarize_findings, risk_level


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="上市企业条款冲突校验")
    parser.add_argument("--company", required=True, help="企业名称")
    parser.add_argument("--material-file", help="主材料文件路径")
    parser.add_argument("--material-url", help="主材料公网链接")
    parser.add_argument("--extra-file", action="append", default=[], help="附加材料文件，可重复传入")
    parser.add_argument("--extra-url", action="append", default=[], help="附加材料链接，可重复传入")
    parser.add_argument("--output", help="输出 JSON 文件路径")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    materials = load_materials(
        primary_file=args.material_file,
        primary_url=args.material_url,
        extra_files=args.extra_file,
        extra_urls=args.extra_url,
    )

    findings = apply_rules(materials)
    result = {
        "company_name": args.company,
        "risk_level": risk_level(findings),
        "summary": summarize_findings(findings),
        "findings": [f.to_dict() for f in findings],
        "sources": [m["source"] for m in materials],
    }

    text = json.dumps(result, ensure_ascii=False, indent=2)
    print(text)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(text)


if __name__ == "__main__":
    main()
