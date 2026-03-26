# -*- coding: utf-8 -*-
"""efinance adapter for cn-stock-data unified layer."""
import os
import sys
import pandas as pd
import efinance as ef
import efinance
from code_converter import to_efinance
from field_mapper import KLINE_FIELDS, QUOTE_FIELDS, FUND_FLOW_FIELDS, map_fields, normalize_date
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


class EfinanceAdapter:
    name = "efinance"

    @staticmethod
    def is_available():
        try:

            return True
        except ImportError:
            return False

    def get_kline(
            self,
            code: str,
            freq: str = "daily",
            start: str = "",
            end: str = "",
            count: int = 0) -> pd.DataFrame:

        bare = to_efinance(code)
        klt_map = {
            "daily": 101, "weekly": 102, "monthly": 103,
            "5min": 5, "15min": 15, "30min": 30, "60min": 60,
        }
        klt = klt_map.get(freq, 101)
        kwargs = {"stock_codes": bare, "klt": klt}
        if start:
            kwargs["beg"] = start.replace("-", "")
        if end:
            kwargs["end"] = end.replace("-", "")
        df = ef.stock.get_quote_history(**kwargs)
        if isinstance(df, dict):
            df = df.get(bare, pd.DataFrame())
        if df.empty:
            return df
        df = map_fields(df, KLINE_FIELDS["efinance"])
        df = normalize_date(df)
        if count > 0:
            df = df.tail(count)
        return df.reset_index(drop=True)

    def get_quote(self, codes: list) -> pd.DataFrame:

        bare_codes = [to_efinance(c) for c in codes]
        df = ef.stock.get_realtime_quotes(bare_codes)
        if df.empty:
            return df
        df = map_fields(df, QUOTE_FIELDS["efinance"])
        return df.reset_index(drop=True)

    def get_fund_flow(self, code: str, days: int = 30) -> pd.DataFrame:

        bare = to_efinance(code)
        df = ef.stock.get_history_bill(bare)
        if df.empty:
            return df
        df = map_fields(df, FUND_FLOW_FIELDS["efinance"])
        df = normalize_date(df)
        if days > 0:
            df = df.tail(days)
        return df.reset_index(drop=True)
