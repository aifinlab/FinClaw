"""Data loading layer built on top of AKShare."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from utils import normalize_symbol, pick_first_existing, safe_to_datetime

    import akshare as ak
import pandas as pd
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
            df = ak.stock_news_em(symbol=self.symbol)
            return df.copy()
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
