from __future__ import annotations

from typing import Any, Dict, List, Optional
    import akshare as ak

import inspect


class DataFetchError(RuntimeError):
    pass
import pandas as pd
else:
    _IMPORT_ERROR = None



def _ensure_akshare() -> None:
    if ak is None:
        raise DataFetchError(
            f"akshare 导入失败: {_IMPORT_ERROR}. 请先执行 pip install akshare"
        )



def _safe_call(func_name: str, **kwargs) -> pd.DataFrame:
    _ensure_akshare()
    func = getattr(ak, func_name, None)
    if func is None:
        raise DataFetchError(f"当前 akshare 版本不包含接口: {func_name}")
        sig = inspect.signature(func)
        allowed = {k: v for k, v in kwargs.items() if k in sig.parameters}
        return func(**allowed)
def get_financial_abstract(symbol: str) -> pd.DataFrame:
    """优先使用财务摘要接口。"""
    for name in ["stock_financial_abstract", "stock_financial_abstract_ths"]:
            df = _safe_call(name, symbol=symbol, stock=symbol)
            if isinstance(df, pd.DataFrame) and not df.empty:
                return df
def get_financial_indicator(symbol: str) -> pd.DataFrame:
    """兼容不同版本的财务指标接口名称。"""
    for name in [
        "stock_financial_analysis_indicator",
        "stock_financial_analysis_indicator_em",
    ]:
            df = _safe_call(name, symbol=symbol, stock=symbol)
            if isinstance(df, pd.DataFrame) and not df.empty:
                return df
def get_business_structure(symbol: str) -> pd.DataFrame:
    for name in ["stock_zygc_ym", "stock_zygc_em"]:
            df = _safe_call(name, symbol=symbol)
            if isinstance(df, pd.DataFrame) and not df.empty:
                return df
def get_mda(symbol: str) -> pd.DataFrame:
    for name in ["stock_mda_ym"]:
            df = _safe_call(name, symbol=symbol)
            if isinstance(df, pd.DataFrame) and not df.empty:
                return df
def get_news(symbol: str, company_name: Optional[str] = None) -> pd.DataFrame:
    """新闻接口在 akshare 不同版本里参数可能不同，做兼容处理。"""
    candidates: List[Dict[str, Any]] = []
    if company_name:
        candidates.extend([
            {"symbol": company_name},
            {"keyword": company_name},
            {"stock": company_name},
            {"name": company_name},
        ])
    candidates.extend([
        {"symbol": symbol},
        {"keyword": symbol},
        {"stock": symbol},
        {"name": symbol},
    ])

    for kwargs in candidates:
            df = _safe_call("stock_news_em", **kwargs)
            if isinstance(df, pd.DataFrame) and not df.empty:
                return df
def load_company_dataset(symbol: str, company_name: Optional[str] = None) -> Dict[str, pd.DataFrame]:
    return {
        "financial_abstract": get_financial_abstract(symbol),
        "financial_indicator": get_financial_indicator(symbol),
        "business_structure": get_business_structure(symbol),
        "mda": get_mda(symbol),
        "news": get_news(symbol, company_name=company_name),
    }
