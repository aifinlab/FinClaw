from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple
import akshare as ak

import pandas as pd
import re


@dataclass
class CompanyProfile:
    name: str
    code: str
    market_symbol: str


def _normalize_code(code: str) -> str:
    code = str(code).strip().upper()
    if re.match(r'^(SH|SZ|BJ)\d{6}$', code):
        return code
    if re.match(r'^\d{6}$', code):
        if code.startswith(('6', '9')):
            return f'SH{code}'
        return f'SZ{code}'
    raise ValueError(f'无法识别股票代码: {code}')


def resolve_company(name_or_code: str) -> CompanyProfile:
    raw = str(name_or_code).strip()
    try:
        symbol = _normalize_code(raw)
        spot = ak.stock_zh_a_spot_em()
        code_only = symbol[-6:]
        matched = spot[spot['代码'].astype(str) == code_only]
        if not matched.empty:
            row = matched.iloc[0]
            return CompanyProfile(name=str(row['名称']), code=code_only, market_symbol=symbol)
        return CompanyProfile(name=code_only, code=code_only, market_symbol=symbol)
    except ValueError:
        spot = ak.stock_zh_a_spot_em()
        matched = spot[spot['名称'].astype(str) == raw]
        if matched.empty:
            fuzzy = spot[spot['名称'].astype(str).str.contains(raw, regex=False, na=False)]
            if fuzzy.empty:
                raise ValueError(f'未在 A 股列表中找到企业: {raw}')
            matched = fuzzy
        row = matched.iloc[0]
        code = str(row['代码']).zfill(6)
        symbol = _normalize_code(code)
        return CompanyProfile(name=str(row['名称']), code=code, market_symbol=symbol)


def fetch_financial_statements(symbol: str) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    market_symbol = _normalize_code(symbol)
    balance = ak.stock_balance_sheet_by_report_em(symbol=market_symbol)
    profit = ak.stock_profit_sheet_by_report_em(symbol=market_symbol)
    cashflow = ak.stock_cash_flow_sheet_by_report_em(symbol=market_symbol)
    return balance, profit, cashflow


if __name__ == '__main__':
    profile = resolve_company('荣盛发展')
    bs, ps, cfs = fetch_financial_statements(profile.market_symbol)
    print(profile)
    print(bs.head())
    print(ps.head())
    print(cfs.head())
