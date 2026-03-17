"""
抓取公网可查的上市公司公告与法规元数据。
"""
from __future__ import annotations

import datetime as dt
import json
import re
from dataclasses import dataclass
from typing import Dict, List, Optional

import requests


DEFAULT_TIMEOUT = 20


@dataclass
class Announcement:
    title: str
    publish_time: str
    adjunct_url: str
    source: str = "cninfo"
    raw: Optional[dict] = None


def _session() -> requests.Session:
    s = requests.Session()
    s.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/123.0 Safari/537.36"
            ),
            "Accept": "application/json, text/plain, */*",
            "Referer": "https://www.cninfo.com.cn/",
            "Origin": "https://www.cninfo.com.cn",
        }
    )
    return s


def infer_cninfo_column(company_code: str) -> str:
    """
    粗略推断公告市场栏目。
    仅用于 CNINFO hisAnnouncement 接口中的 column 字段。
    """
    if company_code.startswith(("600", "601", "603", "605", "688", "900")):
        return "sse"
    if company_code.startswith(("000", "001", "002", "003", "300", "301", "200")):
        return "szse"
    if company_code.startswith(("430", "830", "831", "832", "833", "834", "835", "836", "837", "838", "839", "870", "871", "872", "873", "874", "875", "876", "877", "878", "879")):
        return "bj"
    return "szse"


def fetch_cninfo_announcements(
    company_code: str,
    company_name: str = "",
    year: Optional[int] = None,
    page_size: int = 50,
    max_pages: int = 3,
) -> List[Announcement]:
    """
    使用巨潮资讯历史公告查询接口抓取公告标题。
    该接口为公开网页使用的接口，网页结构变更后可能需要调整参数。
    """
    sess = _session()
    url = "https://www.cninfo.com.cn/new/hisAnnouncement/query"

    start_date = f"{year}-01-01" if year else "2000-01-01"
    end_date = f"{year}-12-31" if year else dt.date.today().isoformat()

    column = infer_cninfo_column(company_code)
    results: List[Announcement] = []

    for page_num in range(1, max_pages + 1):
        payload = {
            "pageNum": page_num,
            "pageSize": page_size,
            "column": column,
            "tabName": "fulltext",
            "plate": "",
            "stock": f"{company_code},{company_name}".strip(","),
            "searchkey": "",
            "secid": "",
            "category": "",
            "trade": "",
            "seDate": f"{start_date}~{end_date}",
            "sortName": "",
            "sortType": "",
            "isHLtitle": "true",
        }
        resp = sess.post(url, data=payload, timeout=DEFAULT_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()

        anns = data.get("announcements", []) or []
        if not anns:
            break

        for item in anns:
            adjunct = item.get("adjunctUrl") or ""
            full_url = (
                f"https://static.cninfo.com.cn/{adjunct.lstrip('/')}"
                if adjunct and not adjunct.startswith("http")
                else adjunct
            )
            results.append(
                Announcement(
                    title=item.get("announcementTitle", ""),
                    publish_time=(item.get("announcementTime") or "")[:10],
                    adjunct_url=full_url,
                    raw=item,
                )
            )

    return results


def search_official_rule_sources() -> Dict[str, Dict[str, str]]:
    """
    规则来源元数据，便于结果报告追溯。
    """
    return {
        "securities_law": {
            "name": "中华人民共和国证券法",
            "source": "国家法律法规数据库",
            "url": "https://flk.npc.gov.cn/",
        },
        "csrc_disclosure_measures_2025": {
            "name": "上市公司信息披露管理办法（2025 修订）",
            "source": "中国证监会",
            "url": "https://www.csrc.gov.cn/",
        },
        "annual_report_format_2021": {
            "name": "公开发行证券的公司信息披露内容与格式准则第2号——年度报告的内容与格式（2021年修订）",
            "source": "中国证监会",
            "url": "https://www.csrc.gov.cn/",
        },
        "semiannual_report_format_2021": {
            "name": "公开发行证券的公司信息披露内容与格式准则第3号——半年度报告的内容与格式（2021年修订）",
            "source": "中国证监会",
            "url": "https://www.csrc.gov.cn/",
        },
        "sse_announcement_guide_2025": {
            "name": "上海证券交易所上市公司自律监管指南第1号——公告格式（2025年修订）",
            "source": "上海证券交易所",
            "url": "https://www.sse.com.cn/",
        },
        "szse_announcement_guide_2025": {
            "name": "深圳证券交易所上市公司自律监管指南第2号——公告格式（2025年修订）",
            "source": "深圳证券交易所",
            "url": "https://www.szse.cn/",
        },
    }


def filter_announcements_by_year(announcements: List[Announcement], year: int) -> List[Announcement]:
    filtered = []
    for ann in announcements:
        if ann.publish_time.startswith(str(year)):
            filtered.append(ann)
    return filtered


def normalize_title(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text or "")
    text = text.replace(" ", "").replace("　", "")
    return text.lower()
