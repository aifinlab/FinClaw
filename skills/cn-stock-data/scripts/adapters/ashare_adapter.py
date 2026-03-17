# -*- coding: utf-8 -*-
"""ashare adapter for cn-stock-data unified layer (lightweight Sina+Tencent)."""
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from code_converter import to_ashare
from field_mapper import KLINE_FIELDS, map_fields


class AshareAdapter:
    name = "ashare"

    @staticmethod
    def is_available():
        try:
            # Ashare.py lives in the same scripts/ directory
            scripts_dir = os.path.dirname(os.path.dirname(__file__))
            sys.path.insert(0, scripts_dir)
            from Ashare import get_price
            return True
        except ImportError:
            return False

    def get_kline(self, code: str, freq: str = "daily", start: str = "", end: str = "", count: int = 0) -> pd.DataFrame:
        scripts_dir = os.path.dirname(os.path.dirname(__file__))
        sys.path.insert(0, scripts_dir)
        from Ashare import get_price

        ashare_code = to_ashare(code)
        freq_map = {
            "daily": "1d", "weekly": "1w", "monthly": "1M",
            "1min": "1m", "5min": "5m", "15min": "15m", "30min": "30m", "60min": "60m",
        }
        ashare_freq = freq_map.get(freq)
        if not ashare_freq:
            raise ValueError(f"ashare does not support freq={freq}")

        n = count if count > 0 else 100
        kwargs = {"code": ashare_code, "frequency": ashare_freq, "count": n}
        if end:
            kwargs["end_date"] = end

        df = get_price(**kwargs)
        if df is None or df.empty:
            return pd.DataFrame()

        # ashare returns date as index (unnamed)
        df = df.reset_index()
        df.columns = ["date" if c == "" or c == "index" else c for c in df.columns]
        # first column is date regardless of name
        if df.columns[0] != "date":
            df = df.rename(columns={df.columns[0]: "date"})

        df = map_fields(df, KLINE_FIELDS["ashare"])
        df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
        if start:
            df = df[df["date"] >= start]
        return df.reset_index(drop=True)
