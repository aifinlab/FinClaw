from __future__ import annotations

from bs4 import BeautifulSoup
from common import FetchError, http_get, polite_sleep, pretty_print
from typing import Any, Dict, List, Optional

import argparse

import re


def infer_exchange(symbol: str) -> str:
    if symbol.startswith(("600", "601", "603", "605", "688", "900")):
        return "SSE"
    return "SZSE"


def sina_company_profile_url(symbol: str) -> str:
    prefix = "sh" if infer_exchange(symbol) == "SSE" else "sz"
    return f"https://vip.stock.finance.sina.com.cn/corp/go.php/vCI_CorpInfo/stockid/{symbol}.phtml"


def extract_by_label(text: str, labels: List[str]) -> Optional[str]:
    for label in labels:
        pattern = rf"{re.escape(label)}[:：]?\s*([^\n\r]+)"
        m = re.search(pattern, text, flags=re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return None


def fetch_from_sina(symbol: str) -> Dict[str, Any]:
    url = sina_company_profile_url(symbol)
    html = http_get(url)
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text("\n", strip=True)

    data = {
        "source": "新浪财经公司资料页",
        "source_url": url,
        "company_name": extract_by_label(text, ["公司名称", "中文名称"]),
        "symbol": symbol,
        "legal_representative": extract_by_label(text, ["法人代表", "法定代表人"]),
        "registered_address": extract_by_label(text, ["注册地址", "公司注册地址"]),
        "office_address": extract_by_label(text, ["办公地址", "公司办公地址"]),
        "registered_capital": extract_by_label(text, ["注册资本"]),
        "established_date": extract_by_label(text, ["成立日期"]),
        "listed_date": extract_by_label(text, ["上市日期"]),
        "industry": extract_by_label(text, ["行业类别", "所属行业"]),
    }
    return data


def latest_announcements_page(symbol: str, exchange: str) -> str:
    exchange = exchange.upper()
    if exchange == "SSE":
        return f"https://www.sse.com.cn/disclosure/listedinfo/announcement/index.shtml?productId={symbol}"
    return f"https://www.szse.cn/disclosure/listed/bulletinDetail/index.html?stockCode={symbol}"


def fetch_announcement_hints(symbol: str, exchange: str) -> Dict[str, Any]:
    url = latest_announcements_page(symbol, exchange)
    try:
        html = http_get(url)
    except Exception as exc:  # noqa: BLE001
        return {
            "source": "交易所公告页",
            "source_url": url,
            "recent_change_hints": [],
            "note": f"公告页抓取失败：{exc}",
        }

    polite_sleep(0.5)
    text = BeautifulSoup(html, "html.parser").get_text("\n", strip=True)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    keywords = ["变更公司名称", "变更法定代表人", "变更注册地址", "变更注册资本", "工商变更登记"]
    hints = []
    for line in lines:
        if any(keyword in line for keyword in keywords):
            hints.append(line)
    return {
        "source": "交易所公告页",
        "source_url": url,
        "recent_change_hints": hints[:20],
    }


def fetch_company_profile(symbol: str, exchange: Optional[str] = None) -> Dict[str, Any]:
    symbol = symbol.strip()
    exchange = (exchange or infer_exchange(symbol)).upper()
    profile = fetch_from_sina(symbol)
    profile["exchange"] = exchange
    profile["announcement_hints"] = fetch_announcement_hints(symbol, exchange)
    return profile


def main() -> None:
    parser = argparse.ArgumentParser(description="抓取上市公司公开资料页字段")
    parser.add_argument("--symbol", required=True, help="股票代码，例如 600519")
    parser.add_argument("--exchange", default=None, help="交易所：SSE 或 SZSE，可选")
    args = parser.parse_args()

    try:
        result = fetch_company_profile(args.symbol, args.exchange)
    except Exception as exc:  # noqa: BLE001
        raise FetchError(f"抓取失败: {exc}") from exc

    pretty_print(result)


if __name__ == "__main__":
    main()
