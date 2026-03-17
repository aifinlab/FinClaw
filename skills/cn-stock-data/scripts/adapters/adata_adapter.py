# -*- coding: utf-8 -*-
"""adata adapter for cn-stock-data unified layer."""
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from code_converter import to_adata
from field_mapper import KLINE_FIELDS, QUOTE_FIELDS, FUND_FLOW_FIELDS, NORTH_FLOW_FIELDS, map_fields, normalize_date


class AdataAdapter:
    name = "adata"

    @staticmethod
    def is_available():
        try:
            import adata
            return True
        except ImportError:
            return False

    def get_kline(self, code: str, freq: str = "daily", start: str = "", end: str = "", count: int = 0) -> pd.DataFrame:
        import adata
        bare = to_adata(code)
        if freq not in ("daily",):
            raise ValueError(f"adata only supports daily kline, got freq={freq}")
        kwargs = {"stock_code": bare}
        if start:
            kwargs["start_date"] = start
        df = adata.stock.market.get_market(**kwargs)
        if df is None or df.empty:
            return pd.DataFrame()
        df = map_fields(df, KLINE_FIELDS["adata"])
        df = normalize_date(df)
        if end:
            df = df[df["date"] <= end]
        if count > 0:
            df = df.tail(count)
        return df.reset_index(drop=True)

    def get_quote(self, codes: list) -> pd.DataFrame:
        import adata
        bare_codes = [to_adata(c) for c in codes]
        df = adata.stock.market.list_market_current()
        if df is None or df.empty:
            return pd.DataFrame()
        df = df[df["stock_code"].isin(bare_codes)]
        df = map_fields(df, QUOTE_FIELDS["adata"])
        return df.reset_index(drop=True)

    def get_fund_flow(self, code: str, days: int = 30) -> pd.DataFrame:
        import adata
        bare = to_adata(code)
        df = adata.stock.market.get_capital_flow(stock_code=bare)
        if df is None or df.empty:
            return pd.DataFrame()
        df = map_fields(df, FUND_FLOW_FIELDS["adata"])
        df = normalize_date(df)
        if days > 0:
            df = df.tail(days)
        return df.reset_index(drop=True)

    def get_finance(self, code: str) -> pd.DataFrame:
        import adata
        bare = to_adata(code)
        df = adata.stock.finance.get_core_index(stock_code=bare)
        if df is None or df.empty:
            return pd.DataFrame()
        return df.reset_index(drop=True)

    def get_north_flow(self) -> pd.DataFrame:
        import adata
        df = adata.sentiment.north.north_flow()
        if df is None or df.empty:
            return pd.DataFrame()
        df = map_fields(df, NORTH_FLOW_FIELDS["adata"])
        df = normalize_date(df)
        return df.reset_index(drop=True)
