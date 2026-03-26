"""Public data source adapters.

These adapters use public web pages that are commonly reachable without login.
Parsing logic is intentionally simple and defensive because official websites
change frequently.
"""
from __future__ import annotations

from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import List, Dict, Optional
import re
import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; reporting-caliber-validator/1.0)"
}


@dataclass
class SourceRecord:
    title: str
    url: str
    publisher: str
    date: Optional[str] = None
    snippet: str = ""


class CninfoAdapter:
    """Fetch public announcements by keyword from cninfo fulltext endpoint."""

    SEARCH_URL = "https://www.cninfo.com.cn/new/hisAnnouncement/query"

    def search_announcements(
        self,
        keyword: str,
        stock_code: str = "",
        page_num: int = 1,
        page_size: int = 10,
    ) -> List[SourceRecord]:
        payload = {
            "pageNum": page_num,
            "pageSize": page_size,
            "tabName": "fulltext",
            "column": "szse",
            "stock": stock_code,
            "searchkey": keyword,
            "secid": "",
            "plate": "",
            "category": "",
            "trade": "",
            "seDate": "",
            "sortName": "",
            "sortType": "",
            "isHLtitle": True,
        }
        try:
            resp = requests.post(self.SEARCH_URL, data=payload, headers=HEADERS, timeout=20)
            resp.raise_for_status()
            data = resp.json()
        except Exception:
            return []
        out: List[SourceRecord] = []
        for item in data.get("announcements", []) or []:
            adjunct = item.get("adjunctUrl", "")
            url = f"https://static.cninfo.com.cn/{adjunct}" if adjunct else "https://www.cninfo.com.cn/"
            out.append(
                SourceRecord(
                    title=re.sub(r"<[^>]+>", "", item.get("announcementTitle", "")),
                    url=url,
                    publisher="巨潮资讯",
                    date=item.get("announcementTime"),
                    snippet=item.get("announcementTitle", ""),
                )
            )
        return out


class GenericPageExtractor:
    def fetch_text(self, url: str) -> str:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        if "text/html" not in resp.headers.get("Content-Type", ""):
            return ""
        soup = BeautifulSoup(resp.text, "lxml")
        return "\n".join(x.get_text(" ", strip=True) for x in soup.find_all(["h1", "h2", "h3", "p", "li"]))


def build_default_source_registry() -> List[Dict[str, str]]:
    return [
        {
            "name": "国家法律法规数据库",
            "url": "https://flk.npc.gov.cn/",
            "notes": "国家法律、行政法规、监察法规、司法解释等检索入口",
        },
        {
            "name": "中国证监会证券期货法规数据库",
            "url": "https://neris.csrc.gov.cn/falvfagui/",
            "notes": "证券期货规章、规范性文件、信息披露准则检索入口",
        },
        {
            "name": "上海证券交易所规则与指南",
            "url": "https://www.sse.com.cn/lawandrules/",
            "notes": "股票上市规则、公告格式、自律监管指南",
        },
        {
            "name": "深圳证券交易所规则与指南",
            "url": "https://www.szse.cn/lawrules/index.html",
            "notes": "股票上市规则、公告格式、业务办理规则",
        },
        {
            "name": "巨潮资讯",
            "url": "https://www.cninfo.com.cn/",
            "notes": "上市公司公告、年报、临时公告公开检索",
        },
    ]
