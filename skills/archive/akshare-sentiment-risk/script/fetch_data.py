from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional
    import akshare as ak

import inspect
import pandas as pd
def _call_akshare(func_name: str, **kwargs):
    func = getattr(ak, func_name, None)
    if func is None:
        return None
    sig = inspect.signature(func)
    accepted = {k: v for k, v in kwargs.items() if k in sig.parameters}
        return func(**accepted)
def fetch_stock_news(symbol: str, stock_name: Optional[str] = None, limit: int = 50) -> pd.DataFrame:
    """
    尝试调用 stock_news_em 获取个股新闻。
    若接口参数不兼容，则回退为抓取后按代码/名称过滤。
    """
    candidates = []

    direct = _call_akshare("stock_news_em", symbol=symbol)
    if isinstance(direct, pd.DataFrame) and not direct.empty:
        candidates.append(direct)

    generic = _call_akshare("stock_news_em")
    if isinstance(generic, pd.DataFrame) and not generic.empty:
        candidates.append(generic)

    if not candidates:
        return pd.DataFrame()

    df = pd.concat(candidates, ignore_index=True).drop_duplicates()
    df.columns = [str(col).strip() for col in df.columns]

    code_cols = [c for c in df.columns if "代码" in c or c.lower() in {"code", "symbol"}]
    name_cols = [c for c in df.columns if "名称" in c or "简称" in c or c.lower() == "name"]

    if code_cols:
        mask = False
        for col in code_cols:
            mask = mask | (df[col].astype(str).str.contains(symbol, na=False))
        df = df[mask]

    if df.empty and stock_name and name_cols:
        mask = False
        for col in name_cols:
            mask = mask | (df[col].astype(str).str.contains(stock_name, na=False))
        df = df[mask]

    datetime_cols = [c for c in df.columns if "时间" in c or "日期" in c or c.lower() in {"date", "datetime", "pub_time"}]
    if datetime_cols:
        sort_col = datetime_cols[0]
        df[sort_col] = pd.to_datetime(df[sort_col], errors="coerce")
        df = df.sort_values(sort_col, ascending=False)

    return df.head(limit).reset_index(drop=True)


def fetch_weibo_hotness(stock_name: str) -> Optional[float]:
    time_period = "CNHOUR24"
    df = _call_akshare("stock_js_weibo_report", time_period=time_period)
    if not isinstance(df, pd.DataFrame) or df.empty:
        return None
    df.columns = [str(col).strip() for col in df.columns]
    if "name" not in df.columns or "rate" not in df.columns:
        return None
    matched = df[df["name"].astype(str).str.contains(stock_name, na=False)]
    if matched.empty:
        return None
    rate_raw = str(matched.iloc[0]["rate"])
        return float(rate_raw)
def infer_date_range(days: int = 30) -> tuple[str, str]:
    end = datetime.now().date()
    start = end - timedelta(days=days)
    return start.strftime("%Y%m%d"), end.strftime("%Y%m%d")
