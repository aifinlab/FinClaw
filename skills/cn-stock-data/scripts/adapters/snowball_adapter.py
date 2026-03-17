# -*- coding: utf-8 -*-
"""pysnowball adapter for cn-stock-data unified layer."""
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from code_converter import to_snowball
from field_mapper import KLINE_FIELDS, QUOTE_FIELDS, FUND_FLOW_FIELDS, map_fields, normalize_date


def _has_token():
    """Check if pysnowball token is configured."""
    try:
        import pysnowball as ball
        # Try a simple call that needs token
        return hasattr(ball, '_token') and ball._token
    except Exception:
        return False


class SnowballAdapter:
    name = "snowball"

    @staticmethod
    def is_available():
        try:
            import pysnowball
            return True
        except ImportError:
            return False

    def _needs_token(self):
        """Check if token-required operations are available."""
        try:
            import pysnowball as ball
            return bool(getattr(ball, '_token', None))
        except Exception:
            return False

    def get_kline(self, code: str, freq: str = "daily", start: str = "", end: str = "", count: int = 0) -> pd.DataFrame:
        if not self._needs_token():
            raise RuntimeError("pysnowball kline requires token")
        import pysnowball as ball
        symbol = to_snowball(code)
        period_map = {"daily": "day", "weekly": "week", "monthly": "month"}
        period = period_map.get(freq, "day")
        result = ball.kline(symbol, period=period)
        if not result or "data" not in str(result):
            return pd.DataFrame()
        # Parse the nested structure
        items = result.get("data", {}).get("item", [])
        columns = result.get("data", {}).get("column", [])
        if not items or not columns:
            return pd.DataFrame()
        df = pd.DataFrame(items, columns=columns)
        df = map_fields(df, KLINE_FIELDS["snowball"])
        # Convert timestamp ms to date
        if "date" in df.columns and df["date"].dtype in ("int64", "float64"):
            df["date"] = pd.to_datetime(df["date"], unit="ms").dt.strftime("%Y-%m-%d")
        if start:
            df = df[df["date"] >= start]
        if end:
            df = df[df["date"] <= end]
        if count > 0:
            df = df.tail(count)
        return df.reset_index(drop=True)

    def get_quote(self, codes: list) -> pd.DataFrame:
        import pysnowball as ball
        symbols = ",".join(to_snowball(c) for c in codes)
        result = ball.quotec(symbols)
        if not result or "data" not in str(result):
            return pd.DataFrame()
        data = result.get("data", [])
        if not data:
            return pd.DataFrame()
        df = pd.DataFrame(data)
        df = map_fields(df, QUOTE_FIELDS["snowball"])
        return df.reset_index(drop=True)

    def get_fund_flow(self, code: str, days: int = 30) -> pd.DataFrame:
        if not self._needs_token():
            raise RuntimeError("pysnowball fund_flow requires token")
        import pysnowball as ball
        symbol = to_snowball(code)
        result = ball.capital_flow(symbol)
        if not result:
            return pd.DataFrame()
        data = result.get("data", [])
        if not data:
            return pd.DataFrame()
        df = pd.DataFrame(data)
        df = map_fields(df, FUND_FLOW_FIELDS["snowball"])
        if "date" in df.columns and df["date"].dtype in ("int64", "float64"):
            df["date"] = pd.to_datetime(df["date"], unit="ms").dt.strftime("%Y-%m-%d")
        if days > 0:
            df = df.tail(days)
        return df.reset_index(drop=True)

    def get_finance(self, code: str) -> pd.DataFrame:
        if not self._needs_token():
            raise RuntimeError("pysnowball finance requires token")
        import pysnowball as ball
        symbol = to_snowball(code)
        result = ball.indicator(symbol)
        if not result:
            return pd.DataFrame()
        data = result.get("data", {}).get("list", [])
        if not data:
            return pd.DataFrame()
        return pd.DataFrame(data).reset_index(drop=True)
