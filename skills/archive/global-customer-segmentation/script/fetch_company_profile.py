
from common import get_text, html_to_text, now_iso, sha256_text
from typing import Dict, List


def build_cninfo_search_keyword(company: str, ticker: str = "") -> str:
    return f"{company} {ticker}".strip()


def fetch_company_public_page(url: str) -> Dict:
    html = get_text(url)
    text = html_to_text(html)
    return {
        "url": url,
        "fetched_at": now_iso(),
        "sha256": sha256_text(text),
        "text": text[:50000],
    }


def build_company_seed_urls(company: str, ticker: str = "", market: str = "cn") -> List[str]:
    urls = []
    if market.lower() == "cn":
        urls.extend([
            "https://www.cninfo.com.cn/",
            "https://www.sse.com.cn/",
            "https://www.szse.cn/",
        ])
    else:
        urls.append("https://www.sec.gov/edgar/search/")
    return urls
