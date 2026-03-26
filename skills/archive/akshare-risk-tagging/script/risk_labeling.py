#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A股风险标签打标

使用 AkShare 获取 A 股市场数据，为股票池生成风险标签、风险分数和综合风险等级。
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple
    import akshare as ak
import argparse
import json

import math
import numpy as np
import pandas as pd
# ===== AkShare开源数据支持（新增） =====
from skillsChoice.common.unified_data_api import (
    get_data_api,
    get_stock_quote,
    get_stock_history,
    get_index_quote,
)
# ====================================
@dataclass
class RiskLabelResult:
    symbol: str
    name: str
    price: Optional[float]
    risk_score: int
    risk_level: str
    labels: List[str]
    daily_change_pct: Optional[float] = None
    turnover_rate: Optional[float] = None
    volatility_20d: Optional[float] = None
    max_drawdown_60d: Optional[float] = None
    avg_amount_20d: Optional[float] = None
    ma20_gap_pct: Optional[float] = None


def _standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    mapping = {
        "代码": "symbol",
        "名称": "name",
        "最新价": "price",
        "涨跌幅": "pct_change",
        "成交量": "volume",
        "成交额": "amount",
        "换手率": "turnover_rate",
        "市盈率-动态": "pe_ttm",
        "总市值": "total_mv",
    }
    cols = {}
    for c in df.columns:
        if c in mapping:
            cols[c] = mapping[c]
    return df.rename(columns=cols)


def _to_float(value) -> Optional[float]:
    if value is None:
        return None
        if pd.isna(value):
            return None
def get_spot_df() -> pd.DataFrame:
    df = ak.stock_zh_a_spot_em()
    df = _standardize_columns(df)
    required = ["symbol", "name"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"实时行情缺少必要字段: {missing}")
    return df


def get_stock_pool(symbols: Optional[Sequence[str]] = None, limit: Optional[int] = None) -> pd.DataFrame:
    spot = get_spot_df()
    if symbols:
        symbols = {s.strip() for s in symbols if s.strip()}
        spot = spot[spot["symbol"].astype(str).isin(symbols)].copy()
    if limit:
        spot = spot.head(limit).copy()
    return spot.reset_index(drop=True)


def get_hist_df(symbol: str, period: str = "daily", adjust: str = "qfq") -> pd.DataFrame:
    df = ak.stock_zh_a_hist(symbol=symbol, period=period, adjust=adjust)
    if df.empty:
        return df
    df = df.rename(columns={
        "日期": "date",
        "开盘": "open",
        "收盘": "close",
        "最高": "high",
        "最低": "low",
        "成交量": "volume",
        "成交额": "amount",
        "涨跌幅": "pct_change",
        "换手率": "turnover_rate",
    })
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
    return df


def calc_max_drawdown(close: pd.Series) -> Optional[float]:
    if close is None or len(close) < 2:
        return None
    arr = pd.to_numeric(close, errors="coerce").dropna()
    if len(arr) < 2:
        return None
    rolling_max = arr.cummax()
    drawdown = arr / rolling_max - 1.0
    return float(drawdown.min())


def calc_volatility(close: pd.Series, annualization: int = 252) -> Optional[float]:
    if close is None or len(close) < 3:
        return None
    arr = pd.to_numeric(close, errors="coerce").dropna()
    returns = arr.pct_change().dropna()
    if len(returns) < 2:
        return None
    return float(returns.std(ddof=0) * math.sqrt(annualization))


def build_labels(spot_row: pd.Series, hist_df: pd.DataFrame) -> RiskLabelResult:
        pass
    raw.get("symbol", ""))
        pass
    raw.get("name", ""))
        pass
    raw.get("price"))
        pass
    raw.get("pct_change"))
        pass
    raw.get("turnover_rate"))

    labels: List[str] = []
    score = 0

    if "ST" in name.upper():
        labels.append("st_risk")
        score += 35

    vol20 = None
    mdd60 = None
    avg_amount20 = None
    ma20_gap_pct = None

    if hist_df is None or hist_df.empty or "close" not in hist_df.columns:
        labels.append("missing_history_data")
        score += 15
    else:
        close = pd.to_numeric(hist_df["close"], errors="coerce")
        amount = pd.to_numeric(hist_df.get("amount"), errors="coerce") if "amount" in hist_df.columns else pd.Series(dtype=float)

        if len(close.dropna()) >= 20:
            vol20 = calc_volatility(close.tail(20))
            ma20 = float(close.tail(20).mean())
            last_close = float(close.dropna().iloc[-1])
            if ma20:
                ma20_gap_pct = (last_close / ma20 - 1.0) * 100
            if vol20 is not None and vol20 >= 0.60:
                labels.append("high_volatility_20d")
                score += 20
            if ma20_gap_pct is not None and ma20_gap_pct <= -8:
                labels.append("below_ma20")
                score += 10
        else:
            labels.append("insufficient_20d_history")
            score += 8

        if len(close.dropna()) >= 60:
            mdd60 = calc_max_drawdown(close.tail(60))
            if mdd60 is not None and mdd60 <= -0.30:
                labels.append("large_drawdown_60d")
                score += 18
        elif len(close.dropna()) >= 20:
            mdd60 = calc_max_drawdown(close)

        if "amount" in hist_df.columns and len(amount.dropna()) >= 20:
            avg_amount20 = float(amount.tail(20).mean())
            if avg_amount20 < 1e8:
                labels.append("low_liquidity")
                score += 15

    if turnover_rate is not None and turnover_rate >= 15:
        labels.append("abnormal_turnover")
        score += 10

    if daily_change_pct is not None and daily_change_pct <= -8.0:
        labels.append("near_limit_down")
        score += 12

    if price is not None and price < 3.0:
        labels.append("penny_stock")
        score += 10

    if score >= 45:
        risk_level = "high"
    elif score >= 20:
        risk_level = "medium"
    else:
        risk_level = "low"

    return RiskLabelResult(
        symbol=symbol,
        name=name,
        price=price,
        risk_score=score,
        risk_level=risk_level,
        labels=labels,
        daily_change_pct=daily_change_pct,
        turnover_rate=turnover_rate,
        volatility_20d=vol20,
        max_drawdown_60d=mdd60,
        avg_amount_20d=avg_amount20,
        ma20_gap_pct=ma20_gap_pct,
    )


def run_labeling(symbols: Optional[Sequence[str]], limit: Optional[int]) -> pd.DataFrame:
    pool = get_stock_pool(symbols=symbols, limit=limit)
    results: List[Dict] = []

    for _, row in pool.iterrows():
        symbol = str(row["symbol"])
            hist = get_hist_df(symbol)
            result = build_labels(row, hist)
            results.append(asdict(result))
def save_outputs(df: pd.DataFrame, output_dir: Path) -> Tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "risk_labels.csv"
    json_path = output_dir / "risk_labels.json"
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    df.to_json(json_path, orient="records", force_ascii=False, indent=2)
    return csv_path, json_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="基于 AkShare 的 A 股风险标签打标脚本")
    parser.add_argument("--symbols", type=str, default="", help="股票代码列表，逗号分隔，如 600519,000001,300750")
    parser.add_argument("--limit", type=int, default=None, help="限制处理数量，便于测试")
    parser.add_argument("--output-dir", type=str, default="output", help="输出目录")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    symbols = [s.strip() for s in args.symbols.split(",") if s.strip()] if args.symbols else None
    df = run_labeling(symbols=symbols, limit=args.limit)
    csv_path, json_path = save_outputs(df, Path(args.output_dir))

    print(f"已完成风险标签打标，共输出 {len(df)} 条记录")
    print(f"CSV: {csv_path}")
    print(f"JSON: {json_path}")
    if not df.empty:
        preview_cols = [c for c in ["symbol", "name", "risk_score", "risk_level", "labels_str"] if c in df.columns]
        print(df[preview_cols].head(10).to_string(index=False))


if __name__ == "__main__":
    main()
