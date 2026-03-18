"""Utility helpers."""

from __future__ import annotations

from typing import Iterable, List

import pandas as pd


def safe_to_datetime(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, errors="coerce")


def pick_first_existing(df: pd.DataFrame, candidates: Iterable[str]) -> str | None:
    for name in candidates:
        if name in df.columns:
            return name
    return None


def normalize_symbol(symbol: str) -> tuple[str, str]:
    clean = symbol.strip().upper()
    digits = "".join(ch for ch in clean if ch.isdigit())
    if len(digits) != 6:
        raise ValueError(f"Invalid A-share symbol: {symbol}")

    if clean.startswith(("SH", "SZ", "BJ")):
        market_symbol = clean
    elif digits.startswith(("600", "601", "603", "605", "688", "689")):
        market_symbol = f"SH{digits}"
    elif digits.startswith(("000", "001", "002", "003", "300", "301")):
        market_symbol = f"SZ{digits}"
    else:
        market_symbol = f"BJ{digits}"
    return digits, market_symbol


def split_keywords(text: str | None) -> List[str]:
    if not text:
        return []
    return [item.strip() for item in text.split(",") if item.strip()]
