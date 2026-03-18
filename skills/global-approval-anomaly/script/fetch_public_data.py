"""Fetch public, reviewable data for listed-company approval anomaly analysis.

This module uses public web pages and APIs where available. It is designed as a
research-oriented example rather than a guaranteed production integration.
"""
from __future__ import annotations

import datetime as dt
import json
import time
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional

import requests
from bs4 import BeautifulSoup


DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
}


@dataclass
class EventRecord:
    date: str
    title: str
    source_type: str
    url: str
    body: str = ""

    def to_dict(self) -> Dict[str, str]:
        return {
            "date": self.date,
            "title": self.title,
            "source_type": self.source_type,
            "url": self.url,
            "body": self.body,
        }


class PublicDataFetcher:
    """Fetches announcements and regulatory information from public sources.

    Supported sources:
    - CNINFO announcement search (public market disclosure portal)
    - CSRC and local bureau penalty/administrative pages via keyword search pages
    """

    def __init__(self, timeout: int = 20, sleep_seconds: float = 0.5) -> None:
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)
        self.timeout = timeout
        self.sleep_seconds = sleep_seconds

    def fetch_cninfo_announcements(
        self,
        symbol: str,
        pages: int = 3,
        page_size: int = 30,
        keywords: Optional[Iterable[str]] = None,
    ) -> List[EventRecord]:
        """Fetch announcement metadata from CNINFO's public search endpoint.

        Notes:
        - Endpoint conventions may change over time.
        - The implementation intentionally keeps parsing lightweight and reviewable.
        - Users should validate accessibility and compliance before large-scale use.
        """
        results: List[EventRecord] = []
        keywords = list(keywords or [])

        endpoint = "https://www.cninfo.com.cn/new/hisAnnouncement/query"
        for page in range(1, pages + 1):
            payload = {
                "stock": f"{symbol},",
                "tabName": "fulltext",
                "pageSize": page_size,
                "pageNum": page,
                "column": "szse",
                "plate": "",
                "category": "",
                "trade": "",
                "seDate": "2000-01-01~2099-12-31",
                "searchkey": " ".join(keywords),
                "secid": "",
                "sortName": "",
                "sortType": "",
                "isHLtitle": "true",
            }
            try:
                resp = self.session.post(endpoint, data=payload, timeout=self.timeout)
                resp.raise_for_status()
                data = resp.json()
            except Exception:
                continue

            announcements = data.get("announcements", [])
            for row in announcements:
                adjunct_url = row.get("adjunctUrl", "")
                url = (
                    f"https://static.cninfo.com.cn/{adjunct_url}"
                    if adjunct_url
                    else "https://www.cninfo.com.cn/"
                )
                results.append(
                    EventRecord(
                        date=row.get("announcementTime", "")[:10],
                        title=row.get("announcementTitle", ""),
                        source_type="cninfo_announcement",
                        url=url,
                        body=row.get("announcementTitle", ""),
                    )
                )
            time.sleep(self.sleep_seconds)
        return results

    def fetch_csrc_search_results(self, company: str, max_pages: int = 2) -> List[EventRecord]:
        """Fetch potentially relevant CSRC/public regulatory records through site search pages.

        This function uses a simple HTML search pattern that can be adapted if the
        site structure changes.
        """
        base = "https://www.csrc.gov.cn/searchList"
        query = f"{company} 审批程序 对外担保 关联交易 行政处罚"
        results: List[EventRecord] = []

        for page in range(1, max_pages + 1):
            params = {"q": query, "pageNo": page}
            try:
                resp = self.session.get(base, params=params, timeout=self.timeout)
                resp.raise_for_status()
            except Exception:
                continue

            soup = BeautifulSoup(resp.text, "lxml")
            for link in soup.select("a"):
                text = " ".join(link.get_text(" ", strip=True).split())
                href = link.get("href") or ""
                if not text:
                    continue
                if company not in text and "处罚" not in text and "担保" not in text:
                    continue
                if href.startswith("/"):
                    href = f"https://www.csrc.gov.cn{href}"
                results.append(
                    EventRecord(
                        date=dt.date.today().isoformat(),
                        title=text,
                        source_type="csrc_search",
                        url=href,
                        body=text,
                    )
                )
            time.sleep(self.sleep_seconds)
        return deduplicate_events(results)


def deduplicate_events(events: List[EventRecord]) -> List[EventRecord]:
    seen = set()
    out: List[EventRecord] = []
    for event in events:
        key = (event.date, event.title, event.url)
        if key in seen:
            continue
        seen.add(key)
        out.append(event)
    return out


def export_events_json(events: List[EventRecord], path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump([e.to_dict() for e in events], f, ensure_ascii=False, indent=2)
