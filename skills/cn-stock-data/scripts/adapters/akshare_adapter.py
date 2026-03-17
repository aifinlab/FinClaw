# -*- coding: utf-8 -*-
"""akshare adapter for cn-stock-data unified layer."""
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from code_converter import to_akshare
from field_mapper import KLINE_FIELDS, map_fields, normalize_date


class AkshareAdapter:
    name = "akshare"

    @staticmethod
    def is_available():
        try:
            import akshare
            return True
        except ImportError:
            return False

    def get_kline(self, code: str, freq: str = "daily", start: str = "", end: str = "", count: int = 0) -> pd.DataFrame:
        import akshare as ak
        bare = to_akshare(code)
        period_map = {
            "daily": "daily", "weekly": "weekly", "monthly": "monthly",
        }
        period = period_map.get(freq)
        if not period:
            raise ValueError(f"akshare does not support freq={freq}, use daily/weekly/monthly")
        kwargs = {"symbol": bare, "period": period, "adjust": "qfq"}
        if start:
            kwargs["start_date"] = start.replace("-", "")
        if end:
            kwargs["end_date"] = end.replace("-", "")
        df = ak.stock_zh_a_hist(**kwargs)
        if df.empty:
            return df
        df = map_fields(df, KLINE_FIELDS["akshare"])
        df = normalize_date(df)
        if count > 0:
            df = df.tail(count)
        return df.reset_index(drop=True)

    def get_quote(self, codes: list) -> pd.DataFrame:
        """akshare realtime returns full market; filter by codes."""
        import akshare as ak
        bare_codes = [to_akshare(c) for c in codes]
        df = ak.stock_zh_a_spot_em()
        if df.empty:
            return df
        df = df[df["代码"].isin(bare_codes)]
        rename = {
            "代码": "code", "名称": "name", "最新价": "price",
            "涨跌幅": "pct_change", "涨跌额": "change",
            "今开": "open", "最高": "high", "最低": "low",
            "昨收": "pre_close", "成交量": "volume", "成交额": "amount",
            "换手率": "turnover_rate", "市盈率-动态": "pe_ttm",
            "总市值": "market_cap", "流通市值": "float_market_cap",
        }
        df = df.rename(columns=rename)
        return df.reset_index(drop=True)

    def get_finance(self, code: str) -> pd.DataFrame:
        """Get financial indicator data via akshare."""
        import akshare as ak
        bare = to_akshare(code)
        try:
            df = ak.stock_financial_abstract_ths(symbol=bare)
            return df.reset_index(drop=True)
        except Exception:
            return pd.DataFrame()
