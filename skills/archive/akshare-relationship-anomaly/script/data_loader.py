from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

import akshare as ak
import pandas as pd


@dataclass
class DataBundle:
    symbol: str
    hist: pd.DataFrame
    lhb_detail: pd.DataFrame
    lhb_stat: pd.DataFrame
    hold_change: pd.DataFrame
    disclosure: pd.DataFrame


class AkshareADataLoader:
    """Wrapper around AKShare interfaces used by this skill."""

    def get_universe(self, limit: Optional[int] = None) -> pd.DataFrame:
        df = ak.stock_zh_a_spot_em()
        df = df.copy()
        if "代码" in df.columns:
            df["代码"] = df["代码"].astype(str).str.zfill(6)
        if limit:
            df = df.head(limit)
        return df

    def get_hist(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        df = ak.stock_zh_a_hist(
            symbol=symbol,
            period="daily",
            start_date=start_date,
            end_date=end_date,
            adjust="qfq",
        )
        return _normalize_hist(df)

    def get_lhb_detail(self, start_date: str, end_date: str) -> pd.DataFrame:
        try:
            df = ak.stock_lhb_detail_em(start_date=start_date, end_date=end_date)
            return df.copy()
        except Exception:
            return pd.DataFrame()

    def get_lhb_stat(self, symbol: str) -> pd.DataFrame:
        try:
            df = ak.stock_lhb_stock_statistic_em(symbol=symbol)
            return df.copy()
        except Exception:
            return pd.DataFrame()

    def get_hold_change(self, symbol: str) -> pd.DataFrame:
        try:
            df = ak.stock_share_hold_change_sse(symbol=symbol)
            return df.copy()
        except Exception:
            return pd.DataFrame()

    def get_disclosure(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        try:
            df = ak.stock_zh_a_disclosure_relation_cninfo(
                symbol=symbol,
                market="沪深京",
                start_date=start_date,
                end_date=end_date,
            )
            return df.copy()
        except Exception:
            return pd.DataFrame()

    def load_symbol_bundle(self, symbol: str, start_date: str, end_date: str) -> DataBundle:
        lhb_detail = self.get_lhb_detail(start_date=start_date, end_date=end_date)
        if not lhb_detail.empty and "代码" in lhb_detail.columns:
            lhb_detail = lhb_detail[lhb_detail["代码"].astype(str).str.zfill(6) == symbol]

        return DataBundle(
            symbol=symbol,
            hist=self.get_hist(symbol=symbol, start_date=start_date, end_date=end_date),
            lhb_detail=lhb_detail,
            lhb_stat=self.get_lhb_stat(symbol=symbol),
            hold_change=self.get_hold_change(symbol=symbol),
            disclosure=self.get_disclosure(symbol=symbol, start_date=start_date, end_date=end_date),
        )


def _normalize_hist(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame(
            columns=["日期", "开盘", "收盘", "最高", "最低", "成交量", "成交额", "振幅", "涨跌幅", "换手率"]
        )
    out = df.copy()
    if "日期" in out.columns:
        out["日期"] = pd.to_datetime(out["日期"])
    numeric_cols = ["开盘", "收盘", "最高", "最低", "成交量", "成交额", "振幅", "涨跌幅", "换手率"]
    for col in numeric_cols:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")
    out = out.sort_values("日期").reset_index(drop=True)
    return out
