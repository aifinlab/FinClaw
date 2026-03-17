"""AKShare 数据抓取模块。

目标：
1. 拉取财务分析指标
2. 拉取资产负债表、利润表、现金流量表
3. 对 AKShare 接口变动做基础兼容处理
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Callable, Iterable

import pandas as pd

try:
    import akshare as ak
except ImportError as exc:  # pragma: no cover
    raise SystemExit("未安装 akshare，请先执行: pip install akshare") from exc


OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


FUNCTION_CANDIDATES: dict[str, list[str]] = {
    "financial_indicator": [
        "stock_financial_analysis_indicator",
        "stock_financial_abstract_ths",
    ],
    "balance_sheet": [
        "stock_balance_sheet_by_report_em",
        "stock_balance_sheet_by_yearly_em",
    ],
    "income_statement": [
        "stock_profit_sheet_by_report_em",
        "stock_profit_sheet_by_yearly_em",
    ],
    "cashflow_statement": [
        "stock_cash_flow_sheet_by_report_em",
        "stock_cash_flow_sheet_by_yearly_em",
    ],
}


def _resolve_function(names: Iterable[str]) -> Callable:
    """按候选函数名顺序查找可用的 akshare 接口。"""
    for name in names:
        func = getattr(ak, name, None)
        if callable(func):
            return func
    raise AttributeError(f"未找到任何可用接口: {list(names)}")


def _try_call(func: Callable, symbol: str) -> pd.DataFrame:
    """尝试不同参数调用风格，提高接口兼容性。"""
    trial_kwargs = [
        {"symbol": symbol},
        {"stock": symbol},
        {"symbol": f"SH{symbol}" if symbol.startswith("6") else f"SZ{symbol}"},
        {"symbol": f"sh{symbol}" if symbol.startswith("6") else f"sz{symbol}"},
    ]

    last_error: Exception | None = None
    for kwargs in trial_kwargs:
        try:
            df = func(**kwargs)
            if isinstance(df, pd.DataFrame) and not df.empty:
                return df
        except Exception as exc:  # noqa: BLE001
            last_error = exc
    raise RuntimeError(f"接口调用失败: {getattr(func, '__name__', func)}") from last_error


def fetch_dataset(symbol: str, dataset_name: str) -> pd.DataFrame:
    """抓取单个数据集。"""
    func = _resolve_function(FUNCTION_CANDIDATES[dataset_name])
    df = _try_call(func, symbol)
    df = df.copy()
    df.columns = [str(col).strip() for col in df.columns]
    return df


def fetch_all(symbol: str) -> dict[str, pd.DataFrame]:
    """抓取所有核心数据表。"""
    result: dict[str, pd.DataFrame] = {}
    for dataset_name in FUNCTION_CANDIDATES:
        result[dataset_name] = fetch_dataset(symbol, dataset_name)
    return result


def save_outputs(data_map: dict[str, pd.DataFrame], output_dir: Path = OUTPUT_DIR) -> None:
    file_map = {
        "financial_indicator": "raw_financial_indicators.csv",
        "balance_sheet": "raw_balance_sheet.csv",
        "income_statement": "raw_income_statement.csv",
        "cashflow_statement": "raw_cashflow_statement.csv",
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    for key, df in data_map.items():
        path = output_dir / file_map[key]
        df.to_csv(path, index=False, encoding="utf-8-sig")


def main() -> None:
    parser = argparse.ArgumentParser(description="使用 AKShare 抓取上市公司财务数据")
    parser.add_argument("--symbol", default="600518", help="股票代码，默认 600518")
    args = parser.parse_args()

    data_map = fetch_all(args.symbol)
    save_outputs(data_map)

    for name, df in data_map.items():
        print(f"[OK] {name}: {df.shape[0]} rows x {df.shape[1]} cols")
    print(f"数据已输出到: {OUTPUT_DIR.resolve()}")


if __name__ == "__main__":
    main()
