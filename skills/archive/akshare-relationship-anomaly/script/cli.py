    from .pipeline import run_batch_scan, run_single_symbol_scan, run_universe_scan

from __future__ import annotations
from pathlib import Path
    from script.pipeline import run_batch_scan, run_single_symbol_scan, run_universe_scan
import argparse

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parent.parent))
import json
else:
import sys


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="A股关系网络异常识别 Skill CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    single = subparsers.add_parser("single", help="扫描单只股票")
    single.add_argument("--symbol", required=True, help="6位股票代码")
    single.add_argument("--start-date", required=True, help="开始日期，格式 YYYYMMDD")
    single.add_argument("--end-date", required=True, help="结束日期，格式 YYYYMMDD")
    single.add_argument("--output-dir", required=True, help="输出目录")

    batch = subparsers.add_parser("batch", help="扫描多只股票")
    batch.add_argument("--symbols", required=True, help="逗号分隔的股票代码列表")
    batch.add_argument("--start-date", required=True, help="开始日期，格式 YYYYMMDD")
    batch.add_argument("--end-date", required=True, help="结束日期，格式 YYYYMMDD")
    batch.add_argument("--output-dir", required=True, help="输出目录")

    universe = subparsers.add_parser("universe", help="从A股股票池中抽样扫描")
    universe.add_argument("--limit", type=int, default=100, help="扫描股票数量上限")
    universe.add_argument("--start-date", required=True, help="开始日期，格式 YYYYMMDD")
    universe.add_argument("--end-date", required=True, help="结束日期，格式 YYYYMMDD")
    universe.add_argument("--output-dir", required=True, help="输出目录")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "single":
        result = run_single_symbol_scan(
            symbol=args.symbol,
            start_date=args.start_date,
            end_date=args.end_date,
            output_dir=args.output_dir,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
        return

    if args.command == "batch":
        symbols = [item.strip() for item in args.symbols.split(",") if item.strip()]
        result = run_batch_scan(
            symbols=symbols,
            start_date=args.start_date,
            end_date=args.end_date,
            output_dir=args.output_dir,
        )
        print(result.to_json(orient="records", force_ascii=False, indent=2))
        return

    if args.command == "universe":
        result = run_universe_scan(
            limit=args.limit,
            start_date=args.start_date,
            end_date=args.end_date,
            output_dir=args.output_dir,
        )
        print(result.to_json(orient="records", force_ascii=False, indent=2))
        return


if __name__ == "__main__":
    main()
