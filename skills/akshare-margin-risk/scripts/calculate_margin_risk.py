#!/usr/bin/env python3
"""A-share margin and risk exposure calculator based on AkShare.

Usage:
    python scripts/calculate_margin_risk.py --portfolio portfolio.json
    python scripts/calculate_margin_risk.py --portfolio portfolio.json --output result.json
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional
import akshare as ak
import argparse

import json
import numpy as np
import pandas as pd


@dataclass
class Assumptions:
    long_margin_ratio: float = 1.0
    short_margin_ratio: float = 1.0
    maintenance_margin_ratio: float = 1.3
    default_price_shock: float = -0.05


class MarginRiskError(Exception):
    """Custom exception for margin-risk workflow."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AkShare A股保证金与风险敞口计算")
    parser.add_argument("--portfolio", required=True, help="JSON 持仓文件路径")
    parser.add_argument("--output", required=False, help="结果输出路径(JSON)")
    return parser.parse_args()


def normalize_trade_date(value: str) -> str:
    return str(value).replace("-", "")


def load_portfolio(path: str) -> Dict[str, Any]:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"未找到持仓文件: {file_path}")
    with file_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if "positions" not in data or not isinstance(data["positions"], list):
        raise MarginRiskError("持仓文件缺少 positions 列表")
    return data


def load_assumptions(raw: Optional[Dict[str, Any]]) -> Assumptions:
    raw = raw or {}
    return Assumptions(
        long_margin_ratio=float(raw.get("long_margin_ratio", 1.0)),
        short_margin_ratio=float(raw.get("short_margin_ratio", 1.0)),
        maintenance_margin_ratio=float(raw.get("maintenance_margin_ratio", 1.3)),
        default_price_shock=float(raw.get("default_price_shock", -0.05)),
    )


def infer_market(symbol: str) -> str:
    symbol = str(symbol)
    if symbol.startswith(("600", "601", "603", "605", "688", "689", "510", "511", "512", "513", "515", "518", "588")):
        return "SSE"
    return "SZSE"


def fetch_close_price(symbol: str, trade_date: str) -> float:
    df = ak.stock_zh_a_hist(
        symbol=str(symbol),
        period="daily",
        start_date=trade_date,
        end_date=trade_date,
        adjust="",
    )
    if df.empty:
        raise MarginRiskError(f"未获取到 {symbol} 在 {trade_date} 的行情数据")
    close_col = "收盘"
    if close_col not in df.columns:
        raise MarginRiskError(f"{symbol} 行情缺少收盘价字段")
    return float(df.iloc[-1][close_col])


def fetch_sse_margin_detail(trade_date: str) -> pd.DataFrame:
    df = ak.stock_margin_detail_sse(date=trade_date)
    rename_map = {
        "标的证券代码": "symbol",
        "标的证券简称": "name",
        "融资余额": "market_financing_balance",
        "融资买入额": "market_financing_buy",
        "融资偿还额": "market_financing_repay",
        "融券余量": "market_short_balance_volume",
        "融券卖出量": "market_short_sell_volume",
        "融券偿还量": "market_short_repay_volume",
    }
    for old, new in rename_map.items():
        if old in df.columns:
            df[new] = df[old]
    keep_cols = [c for c in ["symbol", "name", "market_financing_balance", "market_financing_buy", "market_financing_repay", "market_short_balance_volume", "market_short_sell_volume", "market_short_repay_volume"] if c in df.columns]
    out = df[keep_cols].copy()
    out["symbol"] = out["symbol"].astype(str).str.zfill(6)
    out["exchange"] = "SSE"
    return out.drop_duplicates(subset=["symbol"])


def fetch_szse_margin_detail(trade_date: str) -> pd.DataFrame:
    df = ak.stock_margin_detail_szse(date=trade_date)
    rename_map = {
        "证券代码": "symbol",
        "证券简称": "name",
        "融资余额": "market_financing_balance",
        "融资买入额": "market_financing_buy",
        "融券余量": "market_short_balance_volume",
        "融券卖出量": "market_short_sell_volume",
        "融券余额": "market_short_balance_amount",
        "融资融券余额": "market_margin_balance_total",
    }
    for old, new in rename_map.items():
        if old in df.columns:
            df[new] = df[old]
    keep_cols = [c for c in ["symbol", "name", "market_financing_balance", "market_financing_buy", "market_short_balance_volume", "market_short_sell_volume", "market_short_balance_amount", "market_margin_balance_total"] if c in df.columns]
    out = df[keep_cols].copy()
    out["symbol"] = out["symbol"].astype(str).str.zfill(6)
    out["exchange"] = "SZSE"
    return out.drop_duplicates(subset=["symbol"])


def fetch_margin_market_snapshot(trade_date: str) -> Dict[str, Any]:
    snapshot: Dict[str, Any] = {"trade_date": trade_date}
    try:
        sse = ak.stock_margin_sse(start_date=trade_date, end_date=trade_date)
        snapshot["sse_summary"] = [] if sse.empty else sse.to_dict(orient="records")
    except Exception as exc:  # noqa: BLE001
        snapshot["sse_summary_error"] = str(exc)

    try:
        szse = ak.stock_margin_szse(date=trade_date)
        snapshot["szse_summary"] = [] if szse.empty else szse.to_dict(orient="records")
    except Exception as exc:  # noqa: BLE001
        snapshot["szse_summary_error"] = str(exc)

    return snapshot


def fetch_underlying_info_szse(trade_date: str) -> pd.DataFrame:
    try:
        df = ak.stock_margin_underlying_info_szse(date=trade_date)
    except Exception:
        return pd.DataFrame(columns=["symbol", "szse_is_financing_underlying", "szse_is_short_underlying", "szse_can_finance_today", "szse_can_short_today", "szse_limit_pct"])

    rename_map = {
        "证券代码": "symbol",
        "融资标的": "szse_is_financing_underlying",
        "融券标的": "szse_is_short_underlying",
        "当日可融资": "szse_can_finance_today",
        "当日可融券": "szse_can_short_today",
        "涨跌幅限制": "szse_limit_pct",
    }
    for old, new in rename_map.items():
        if old in df.columns:
            df[new] = df[old]
    keep_cols = [c for c in ["symbol", "szse_is_financing_underlying", "szse_is_short_underlying", "szse_can_finance_today", "szse_can_short_today", "szse_limit_pct"] if c in df.columns]
    out = df[keep_cols].copy()
    out["symbol"] = out["symbol"].astype(str).str.zfill(6)
    return out.drop_duplicates(subset=["symbol"])


def build_position_frame(portfolio: Dict[str, Any], assumptions: Assumptions) -> pd.DataFrame:
    positions = pd.DataFrame(portfolio["positions"])
    if positions.empty:
        raise MarginRiskError("positions 为空")

    positions["symbol"] = positions["symbol"].astype(str).str.zfill(6)
    positions["name"] = positions.get("name", pd.Series([None] * len(positions)))
    positions["side"] = positions["side"].astype(str).str.lower()
    positions["shares"] = positions["shares"].astype(float)
    positions["financed_shares"] = positions.get("financed_shares", 0).fillna(0).astype(float)
    positions["exchange"] = positions.get("exchange", positions["symbol"].map(infer_market))

    trade_date = normalize_trade_date(str(portfolio["trade_date"]))
    prices: List[float] = []
    for symbol in positions["symbol"].tolist():
        prices.append(fetch_close_price(symbol=symbol, trade_date=trade_date))
    positions["close_price"] = prices

    positions["gross_market_value"] = positions["shares"] * positions["close_price"]
    positions["long_exposure"] = np.where(positions["side"] == "long", positions["gross_market_value"], 0.0)
    positions["short_exposure"] = np.where(positions["side"] == "short", positions["gross_market_value"], 0.0)
    positions["net_exposure"] = positions["long_exposure"] - positions["short_exposure"]

    positions["financing_liability"] = np.where(
        positions["side"] == "long",
        np.minimum(positions["financed_shares"], positions["shares"]) * positions["close_price"],
        0.0,
    )
    positions["short_liability"] = np.where(
        positions["side"] == "short",
        positions["shares"] * positions["close_price"],
        0.0,
    )

    positions["initial_margin_required"] = (
        positions["financing_liability"] * assumptions.long_margin_ratio
        + positions["short_liability"] * assumptions.short_margin_ratio
    )
    return positions


def enrich_market_data(positions: pd.DataFrame, trade_date: str) -> pd.DataFrame:
    sse_symbols = positions.loc[positions["exchange"] == "SSE", "symbol"].tolist()
    szse_symbols = positions.loc[positions["exchange"] == "SZSE", "symbol"].tolist()

    merged = positions.copy()

    if sse_symbols:
        sse_detail = fetch_sse_margin_detail(trade_date)
        merged = merged.merge(sse_detail, how="left", on=["symbol", "exchange"], suffixes=("", "_mkt"))

    if szse_symbols:
        szse_detail = fetch_szse_margin_detail(trade_date)
        underlying = fetch_underlying_info_szse(trade_date)
        merged = merged.merge(szse_detail, how="left", on=["symbol", "exchange"], suffixes=("", "_mkt"))
        merged = merged.merge(underlying, how="left", on="symbol")

    return merged


def compute_summary(positions: pd.DataFrame, cash: float, assumptions: Assumptions) -> Dict[str, Any]:
    long_exposure = float(positions["long_exposure"].sum())
    short_exposure = float(positions["short_exposure"].sum())
    financing_liability = float(positions["financing_liability"].sum())
    short_liability = float(positions["short_liability"].sum())
    total_liability = financing_liability + short_liability

    equity = cash + long_exposure - short_exposure - financing_liability
    if short_liability:
        equity -= 0.0  # short proceeds treatment simplified; retained in cash assumption.

    gross_exposure = long_exposure + short_exposure
    net_exposure = long_exposure - short_exposure
    initial_margin_required = float(positions["initial_margin_required"].sum())
    maintenance_required_equity = total_liability * assumptions.maintenance_margin_ratio
    maintenance_ratio = None if total_liability == 0 else equity / total_liability
    leverage = None if equity == 0 else gross_exposure / equity
    margin_surplus = equity - initial_margin_required
    maintenance_surplus = equity - maintenance_required_equity

    warning_level = "normal"
    if total_liability > 0 and maintenance_ratio is not None:
        if maintenance_ratio < 1.0:
            warning_level = "danger"
        elif maintenance_ratio < assumptions.maintenance_margin_ratio:
            warning_level = "warning"

    return {
        "cash": cash,
        "equity": equity,
        "long_exposure": long_exposure,
        "short_exposure": short_exposure,
        "gross_exposure": gross_exposure,
        "net_exposure": net_exposure,
        "financing_liability": financing_liability,
        "short_liability": short_liability,
        "total_liability": total_liability,
        "initial_margin_required": initial_margin_required,
        "maintenance_required_equity": maintenance_required_equity,
        "maintenance_ratio": maintenance_ratio,
        "leverage": leverage,
        "margin_surplus": margin_surplus,
        "maintenance_surplus": maintenance_surplus,
        "warning_level": warning_level,
    }


def run_stress_test(positions: pd.DataFrame, cash: float, assumptions: Assumptions) -> Dict[str, Any]:
    shock = assumptions.default_price_shock
    stressed = positions.copy()
    stressed["stressed_price"] = stressed["close_price"] * (1.0 + shock)
    stressed["stressed_long_exposure"] = np.where(stressed["side"] == "long", stressed["shares"] * stressed["stressed_price"], 0.0)
    stressed["stressed_short_exposure"] = np.where(stressed["side"] == "short", stressed["shares"] * stressed["stressed_price"], 0.0)
    stressed["stressed_financing_liability"] = np.where(
        stressed["side"] == "long",
        np.minimum(stressed["financed_shares"], stressed["shares"]) * stressed["stressed_price"],
        0.0,
    )
    stressed["stressed_short_liability"] = np.where(
        stressed["side"] == "short",
        stressed["shares"] * stressed["stressed_price"],
        0.0,
    )

    long_exposure = float(stressed["stressed_long_exposure"].sum())
    short_exposure = float(stressed["stressed_short_exposure"].sum())
    financing_liability = float(stressed["stressed_financing_liability"].sum())
    short_liability = float(stressed["stressed_short_liability"].sum())
    total_liability = financing_liability + short_liability
    equity = cash + long_exposure - short_exposure - financing_liability
    maintenance_ratio = None if total_liability == 0 else equity / total_liability
    maintenance_required_equity = total_liability * assumptions.maintenance_margin_ratio

    return {
        "price_shock": shock,
        "equity_after_shock": equity,
        "long_exposure_after_shock": long_exposure,
        "short_exposure_after_shock": short_exposure,
        "financing_liability_after_shock": financing_liability,
        "short_liability_after_shock": short_liability,
        "maintenance_ratio_after_shock": maintenance_ratio,
        "maintenance_required_equity_after_shock": maintenance_required_equity,
        "maintenance_surplus_after_shock": equity - maintenance_required_equity,
    }


def to_serializable_records(df: pd.DataFrame) -> List[Dict[str, Any]]:
    clean_df = df.replace({np.nan: None})
    records = clean_df.to_dict(orient="records")
    return records


def main() -> None:
    args = parse_args()
    portfolio = load_portfolio(args.portfolio)
    assumptions = load_assumptions(portfolio.get("assumptions"))
    trade_date = normalize_trade_date(str(portfolio["trade_date"]))
    cash = float(portfolio.get("cash", 0.0))

    positions = build_position_frame(portfolio=portfolio, assumptions=assumptions)
    positions = enrich_market_data(positions=positions, trade_date=trade_date)

    summary = compute_summary(positions=positions, cash=cash, assumptions=assumptions)
    stress_test = run_stress_test(positions=positions, cash=cash, assumptions=assumptions)
    market_snapshot = fetch_margin_market_snapshot(trade_date=trade_date)

    result = {
        "trade_date": trade_date,
        "assumptions": asdict(assumptions),
        "summary": summary,
        "stress_test": stress_test,
        "positions": to_serializable_records(positions),
        "market_snapshot": market_snapshot,
    }

    output_text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(output_text, encoding="utf-8")
    print(output_text)


if __name__ == "__main__":
    main()
