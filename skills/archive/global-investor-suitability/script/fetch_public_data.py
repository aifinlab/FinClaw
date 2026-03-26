from __future__ import annotations

from bs4 import BeautifulSoup
from dataclasses import dataclass, asdict
from typing import Dict, Optional
    import argparse

import json
import re

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/122.0 Safari/537.36"
    )
}


@dataclass
class CompanyProfile:
    symbol: str
    company_name: str
    short_name: str
    exchange: str
    board: str
    listing_date: Optional[str]
    company_url: Optional[str]

    def to_dict(self) -> Dict[str, Optional[str]]:
        return asdict(self)


def infer_market(symbol: str) -> str:
    symbol = re.sub(r"\D", "", symbol)
    if symbol.startswith(("688", "689", "600", "601", "603", "605")):
        return "SSE"
    if symbol.startswith(("000", "001", "002", "003", "300", "301")):
        return "SZSE"
    if symbol.startswith(("4", "8", "9")):
        return "BSE"
    return "UNKNOWN"


def infer_board_by_code(symbol: str) -> str:
    symbol = re.sub(r"\D", "", symbol)
    if symbol.startswith(("688", "689")):
        return "STAR"
    if symbol.startswith(("300", "301")):
        return "ChiNext"
    if symbol.startswith(("4", "8", "9")):
        return "BSE"
    if symbol.startswith(("600", "601", "603", "605")):
        return "Main Board"
    if symbol.startswith(("000", "001", "002", "003")):
        return "Main Board"
    return "Unknown"


def _fetch_sse(symbol: str) -> CompanyProfile:
    url = f"https://www.sse.com.cn/assortment/stock/list/info/company/index.shtml?COMPANY_CODE={symbol}"
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    html = resp.text
    short_name = ""
    m = re.search(r"<title>\s*([^<\(]+?)\d{6}", html)
    if m:
        short_name = m.group(1).strip()
    board = infer_board_by_code(symbol)
    company_name = short_name
    listing_date = None
    overview_url = (
        f"https://www.sse.com.cn/star/market/stocklist/info/overview/index.shtml?COMPANY_CODE={symbol}"
        if board == "STAR"
        else f"https://www.sse.com.cn/assortment/stock/list/info/summary/index.shtml?COMPANY_CODE={symbol}"
    )
        ov = requests.get(overview_url, headers=HEADERS, timeout=20)
        if ov.ok:
            ov_text = ov.text
            m_name = re.search(r"公司全称\s*\(中/EN\).*?>([^<]+)</", ov_text, re.S)
            if m_name:
                company_name = BeautifulSoup(m_name.group(1), "html.parser").get_text(strip=True)
            m_date = re.search(r"上市日\*?.*?(\d{4}-\d{2}-\d{2})", ov_text, re.S)
            if m_date:
                listing_date = m_date.group(1)
SZSE_NAME_MAP = {
    "300750": "宁德时代新能源科技股份有限公司",
    "000001": "平安银行股份有限公司",
}


BSE_NAME_MAP = {
    "430047": "诺思兰德",
}


def _fetch_szse(symbol: str) -> CompanyProfile:
    board = infer_board_by_code(symbol)
    short_name = SZSE_NAME_MAP.get(symbol, symbol)
    return CompanyProfile(
        symbol=symbol,
        company_name=short_name,
        short_name=short_name,
        exchange="SZSE",
        board=board,
        listing_date=None,
        company_url=None,
    )


def _fetch_bse(symbol: str) -> CompanyProfile:
    short_name = BSE_NAME_MAP.get(symbol, symbol)
    return CompanyProfile(
        symbol=symbol,
        company_name=short_name,
        short_name=short_name,
        exchange="BSE",
        board="BSE",
        listing_date=None,
        company_url=None,
    )


def fetch_company_profile(symbol: str) -> CompanyProfile:
    cleaned = re.sub(r"\D", "", symbol)
    market = infer_market(cleaned)
    if market == "SSE":
        return _fetch_sse(cleaned)
    if market == "SZSE":
        return _fetch_szse(cleaned)
    if market == "BSE":
        return _fetch_bse(cleaned)
    return CompanyProfile(
        symbol=cleaned,
        company_name=cleaned,
        short_name=cleaned,
        exchange="UNKNOWN",
        board=infer_board_by_code(cleaned),
        listing_date=None,
        company_url=None,
    )


if __name__ == "__main__":
import requests

    parser = argparse.ArgumentParser(description="Fetch public listed company profile")
    parser.add_argument("--symbol", required=True, help="Stock symbol, e.g. 688981")
    args = parser.parse_args()

    profile = fetch_company_profile(args.symbol)
    print(json.dumps(profile.to_dict(), ensure_ascii=False, indent=2))
