"""Fetch public, reviewable data for listed-company approval anomaly analysis.

This module uses public web pages and APIs where available. It is designed as a
research-oriented example rather than a guaranteed production integration.
"""
from __future__ import annotations

from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional
import datetime as dt
import json

import requests
import time
# ===== AkShare开源数据支持（新增） =====
from skillsChoice.common.unified_data_api import (
    get_data_api,
    get_financial_report,
    get_index_quote,
)
# ====================================


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
                resp = self.session.post(endpoint, data=payload, timeout=self.timeout)
                resp.raise_for_status()
                data = resp.json()
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
