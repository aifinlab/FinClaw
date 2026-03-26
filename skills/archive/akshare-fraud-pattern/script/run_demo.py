"""运行示例：默认分析康美药业（600518）。"""

from __future__ import annotations

from fetch_akshare_data import fetch_all, save_outputs
from fraud_signals import build_feature_frame, evaluate_signals, save_analysis

from pathlib import Path
import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="AKShare 企业欺诈模式识别示例")
    parser.add_argument("--symbol", default="600518", help="股票代码，默认 600518")
    parser.add_argument("--name", default="康美药业", help="企业名称，仅用于展示")
    args = parser.parse_args()

    print(f"开始分析: {args.name} ({args.symbol})")
    data_map = fetch_all(args.symbol)
    save_outputs(data_map)

    feature = build_feature_frame(
        indicators=data_map["financial_indicator"],
        balance_sheet=data_map["balance_sheet"],
        income_statement=data_map["income_statement"],
        cashflow_statement=data_map["cashflow_statement"],
    )
    signal_df, summary = evaluate_signals(feature)
    save_analysis(feature, signal_df, summary, output_dir=Path("output"))

    print("\n=== 风险信号 ===")
    print(signal_df.to_string(index=False))
    print("\n=== 结论摘要 ===")
    print(summary)
    print("\n输出目录: output/")


if __name__ == "__main__":
    main()
