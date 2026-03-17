# -*- coding: utf-8 -*-
"""Field name mapping tables for unified cn-stock-data layer.

All sources map to unified English snake_case field names.
Dates are normalized to YYYY-MM-DD format.
"""
import pandas as pd

# ── Kline field mappings ──────────────────────────────────────────────
KLINE_FIELDS = {
    "efinance": {
        "日期": "date", "开盘": "open", "收盘": "close", "最高": "high",
        "最低": "low", "成交量": "volume", "成交额": "amount",
        "振幅": "amplitude", "涨跌幅": "pct_change", "涨跌额": "change",
        "换手率": "turnover_rate",
    },
    "akshare": {
        "日期": "date", "开盘": "open", "收盘": "close", "最高": "high",
        "最低": "low", "成交量": "volume", "成交额": "amount",
        "振幅": "amplitude", "涨跌幅": "pct_change", "涨跌额": "change",
        "换手率": "turnover_rate",
    },
    "adata": {
        "trade_date": "date", "open": "open", "close": "close",
        "high": "high", "low": "low", "volume": "volume",
        "amount": "amount", "change_pct": "pct_change",
        "turnover_ratio": "turnover_rate",
    },
    "ashare": {
        # ashare returns: index='', columns=[open, close, high, low, volume]
        # index is the date; no amount/pct_change
        "open": "open", "close": "close", "high": "high",
        "low": "low", "volume": "volume",
    },
    "snowball": {
        "timestamp": "date", "open": "open", "close": "close",
        "high": "high", "low": "low", "volume": "volume",
        "amount": "amount", "percent": "pct_change",
        "turnover_rate": "turnover_rate",
    },
}

# ── Realtime quote field mappings ─────────────────────────────────────
QUOTE_FIELDS = {
    "efinance": {
        "股票代码": "code", "股票名称": "name", "最新价": "price",
        "涨跌幅": "pct_change", "涨跌额": "change",
        "今开": "open", "最高": "high", "最低": "low",
        "昨日收盘": "pre_close", "成交量": "volume", "成交额": "amount",
        "换手率": "turnover_rate", "量比": "volume_ratio",
        "动态市盈率": "pe_ttm", "总市值": "market_cap",
        "流通市值": "float_market_cap",
    },
    "adata": {
        "stock_code": "code", "short_name": "name", "trade_price": "price",
        "change_pct": "pct_change", "open": "open", "high": "high",
        "low": "low", "pre_close": "pre_close", "volume": "volume",
        "amount": "amount", "turnover_ratio": "turnover_rate",
    },
    "snowball": {
        "symbol": "code", "name": "name", "current": "price",
        "percent": "pct_change", "chg": "change",
        "open": "open", "high": "high", "low": "low",
        "last_close": "pre_close", "volume": "volume", "amount": "amount",
        "turnover_rate": "turnover_rate", "market_capital": "market_cap",
        "float_market_capital": "float_market_cap",
    },
}

# ── Fund flow field mappings ──────────────────────────────────────────
FUND_FLOW_FIELDS = {
    "efinance": {
        "日期": "date", "主力净流入": "main_net_inflow",
        "小单净流入": "small_net_inflow", "中单净流入": "mid_net_inflow",
        "大单净流入": "large_net_inflow", "超大单净流入": "xlarge_net_inflow",
    },
    "adata": {
        "trade_date": "date", "main_net_inflow": "main_net_inflow",
        "net_inflow_rate": "net_inflow_rate",
    },
    "snowball": {
        "timestamp": "date", "net_amount": "main_net_inflow",
    },
}

# ── Finance field mappings (adata 43-field is already English) ────────
FINANCE_FIELDS = {
    "adata": {},  # already English snake_case, pass through
    "akshare": {},  # varies by report type, handled in adapter
    "snowball": {},  # handled in adapter
}

# ── North flow field mappings ─────────────────────────────────────────
NORTH_FLOW_FIELDS = {
    "adata": {
        "trade_date": "date", "net_hgt": "net_hgt",
        "net_sgt": "net_sgt", "net_tgt": "net_total",
    },
}


def map_fields(df: pd.DataFrame, mapping: dict) -> pd.DataFrame:
    """Rename DataFrame columns using a mapping dict. Unknown columns kept."""
    if not mapping:
        return df
    return df.rename(columns=mapping)


def normalize_date(df: pd.DataFrame, date_col: str = "date") -> pd.DataFrame:
    """Normalize date column to YYYY-MM-DD string format."""
    if date_col in df.columns:
        df[date_col] = pd.to_datetime(df[date_col]).dt.strftime("%Y-%m-%d")
    return df
