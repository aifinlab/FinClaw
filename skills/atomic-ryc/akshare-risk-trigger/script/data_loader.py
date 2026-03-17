"""Data loading layer built on top of AKShare."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from utils import normalize_symbol, pick_first_existing, safe_to_datetime

try:
    import akshare as ak
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "AKShare is required. Install dependencies first: pip install -r requirements.txt"
    ) from exc


@dataclass
class LoadedData:
    price: pd.DataFrame
    news: pd.DataFrame
    hot_rank: pd.DataFrame
    hot_rank_detail: pd.DataFrame
    pledge: pd.DataFrame
    goodwill: pd.DataFrame
    comment: pd.DataFrame


class AkshareRiskDataLoader:
    def __init__(self, symbol: str, start_date: str, end_date: str, report_date: str | None = None):
        self.symbol, self.market_symbol = normalize_symbol(symbol)
        self.start_date = start_date
        self.end_date = end_date
        self.report_date = report_date

    def load(self) -> LoadedData:
        return LoadedData(
            price=self.get_price_history(),
            news=self.get_news(),
            hot_rank=self.get_hot_rank_snapshot(),
            hot_rank_detail=self.get_hot_rank_detail(),
            pledge=self.get_pledge_ratio(),
            goodwill=self.get_goodwill_warning(),
            comment=self.get_comment_snapshot(),
        )

    def get_price_history(self) -> pd.DataFrame:
        df = ak.stock_zh_a_hist(
            symbol=self.symbol,
            period="daily",
            start_date=self.start_date,
            end_date=self.end_date,
            adjust="",
        )
        if df.empty:
            raise ValueError(f"No price data found for {self.symbol}")
        df = df.copy()
        date_col = pick_first_existing(df, ["日期", "date"])
        if date_col is None:
            raise ValueError("Price dataframe is missing date column")
        df[date_col] = safe_to_datetime(df[date_col])
        df = df.sort_values(date_col).reset_index(drop=True)
        return df

    def get_news(self) -> pd.DataFrame:
        try:
            df = ak.stock_news_em(symbol=self.symbol)
            return df.copy()
        except Exception:
            return pd.DataFrame()

    def get_hot_rank_snapshot(self) -> pd.DataFrame:
        try:
            df = ak.stock_hot_rank_em()
            return df.copy()
        except Exception:
            return pd.DataFrame()

    def get_hot_rank_detail(self) -> pd.DataFrame:
        try:
            df = ak.stock_hot_rank_detail_em(symbol=self.market_symbol)
            if not df.empty:
                time_col = pick_first_existing(df, ["时间", "date"])
                if time_col:
                    df[time_col] = safe_to_datetime(df[time_col])
                    df = df.sort_values(time_col).reset_index(drop=True)
            return df.copy()
        except Exception:
            return pd.DataFrame()

    def get_pledge_ratio(self) -> pd.DataFrame:
        if not self.end_date:
            return pd.DataFrame()
        try:
            df = ak.stock_gpzy_pledge_ratio_em(date=self.end_date)
            return df.copy()
        except Exception:
            return pd.DataFrame()

    def get_goodwill_warning(self) -> pd.DataFrame:
        if not self.report_date:
            return pd.DataFrame()
        try:
            df = ak.stock_sy_yq_em(date=self.report_date)
            return df.copy()
        except Exception:
            return pd.DataFrame()

    def get_comment_snapshot(self) -> pd.DataFrame:
        try:
            df = ak.stock_comment_em()
            return df.copy()
        except Exception:
            return pd.DataFrame()


def filter_row_by_symbol(df: pd.DataFrame, symbol: str, candidates: list[str]) -> dict[str, Any] | None:
    if df.empty:
        return None
    col = pick_first_existing(df, candidates)
    if col is None:
        return None
    match = df[df[col].astype(str).str.zfill(6) == symbol]
    if match.empty:
        return None
    return match.iloc[0].to_dict()
