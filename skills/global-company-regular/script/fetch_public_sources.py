from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Dict, List, Optional
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}


@dataclass
class SourceItem:
    title: str
    url: str
    source: str
    snippet: str = ""
    publish_date: str = ""

    def as_dict(self) -> Dict[str, str]:
        return {
            "title": self.title,
            "url": self.url,
            "source": self.source,
            "snippet": self.snippet,
            "publish_date": self.publish_date,
        }


class PublicSourceClient:
    """面向上市公司合规校验的公网数据抓取器。

    说明：
    1. 优先使用官方公开网页或公开接口；
    2. 若个别站点接口变更，可通过改写单个方法修复；
    3. 为避免给目标站点造成压力，默认只取少量结果。
    """

    def __init__(self, timeout: int = 20):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)

    def _get(self, url: str, **kwargs) -> requests.Response:
        resp = self.session.get(url, timeout=self.timeout, **kwargs)
        resp.raise_for_status()
        return resp

    def search_csrc_rules(self, keyword: str, limit: int = 10) -> List[Dict[str, str]]:
        """查询证监会证券期货法规数据库。

        站点存在前端渲染/检索参数调整的可能，因此这里同时保留：
        - 数据库入口页
        - 关键字直达检索页（可根据站点实际情况扩展）
        """
        results: List[SourceItem] = []
        entry = f"https://neris.csrc.gov.cn/falvfagui/"
        search_url = (
            "https://neris.csrc.gov.cn/falvfagui/rdqsHeader/lawList?"
            f"keyword={quote(keyword)}"
        )
        results.append(
            SourceItem(
                title=f"证监会法规库入口：{keyword}",
                url=search_url,
                source="中国证监会",
                snippet="进入证监会证券期货法规数据库后继续按关键字检索。",
            )
        )
        results.append(
            SourceItem(
                title="证监会证券期货法规数据库首页",
                url=entry,
                source="中国证监会",
                snippet="用于浏览最新法规、法规体系与综合检索。",
            )
        )
        return [x.as_dict() for x in results[:limit]]

    def search_sse_rules(self, keyword: str, limit: int = 10) -> List[Dict[str, str]]:
        url = f"https://query.sse.com.cn/search/pc/search?searchword={quote(keyword)}"
        return [
            SourceItem(
                title=f"上交所规则/公告检索：{keyword}",
                url=url,
                source="上海证券交易所",
                snippet="用于检索上市规则、自律监管指引、纪律处分、监管问询等。",
            ).as_dict()
        ][:limit]

    def search_szse_rules(self, keyword: str, limit: int = 10) -> List[Dict[str, str]]:
        url = f"https://www.szse.cn/api/search/index?keyword={quote(keyword)}"
        return [
            SourceItem(
                title=f"深交所规则/公告检索：{keyword}",
                url=url,
                source="深圳证券交易所",
                snippet="用于检索股票上市规则、规范运作、监管函件、处分决定等。",
            ).as_dict()
        ][:limit]

    def search_npc_laws(self, keyword: str, limit: int = 10) -> List[Dict[str, str]]:
        url = (
            "https://flk.npc.gov.cn/"
            f"?keyword={quote(keyword)}"
        )
        return [
            SourceItem(
                title=f"国家法律法规数据库检索：{keyword}",
                url=url,
                source="国家法律法规数据库",
                snippet="用于检索公司法、证券法等上位法。",
            ).as_dict()
        ][:limit]

    def search_cninfo_announcements(self, keyword: str, limit: int = 10) -> List[Dict[str, str]]:
        """查询巨潮资讯公告检索。

        CNINFO 存在可公开访问的全文检索接口，但参数和 headers 可能调整。
        这里保留稳定的检索入口链接，并尽量解析公开响应。
        """
        entry_url = (
            "https://www.cninfo.com.cn/new/fulltextSearch?notautosubmit=&keyWord="
            f"{quote(keyword)}"
        )
        items: List[SourceItem] = [
            SourceItem(
                title=f"巨潮资讯公告检索：{keyword}",
                url=entry_url,
                source="巨潮资讯网",
                snippet="用于查询上市公司公告、问询回复、处罚/监管文件等。",
            )
        ]
        try:
            api = "https://www.cninfo.com.cn/new/fulltextSearch/full"
            payload = {
                "searchkey": keyword,
                "pageNum": 1,
                "pageSize": limit,
                "sortName": "nothing",
                "sortType": "desc",
            }
            headers = dict(self.session.headers)
            headers.update({"X-Requested-With": "XMLHttpRequest"})
            resp = self.session.post(api, data=payload, headers=headers, timeout=self.timeout)
            if resp.ok:
                data = resp.json()
                for row in data.get("announcements", [])[:limit]:
                    title = re.sub(r"<[^>]+>", "", row.get("announcementTitle", ""))
                    adjunct = row.get("adjunctUrl", "")
                    url = f"https://static.cninfo.com.cn/{adjunct}" if adjunct else entry_url
                    items.append(
                        SourceItem(
                            title=title or keyword,
                            url=url,
                            source="巨潮资讯网",
                            snippet=row.get("announcementContent", "")[:140],
                            publish_date=row.get("announcementTime", ""),
                        )
                    )
        except Exception:
            pass
        dedup = []
        seen = set()
        for item in items:
            if item.url in seen:
                continue
            dedup.append(item.as_dict())
            seen.add(item.url)
        return dedup[:limit]

    def collect_public_evidence(self, company: str, extra_keywords: Optional[List[str]] = None) -> Dict[str, List[Dict[str, str]]]:
        extra_keywords = extra_keywords or []
        law_keyword = " ".join([company] + extra_keywords).strip()
        return {
            "laws_npc": self.search_npc_laws(law_keyword, limit=5),
            "rules_csrc": self.search_csrc_rules(law_keyword, limit=5),
            "rules_sse": self.search_sse_rules(law_keyword, limit=5),
            "rules_szse": self.search_szse_rules(law_keyword, limit=5),
            "announcements": self.search_cninfo_announcements(law_keyword, limit=8),
        }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="抓取上市公司规则校验所需公网证据")
    parser.add_argument("--company", required=True, help="上市公司名称或简称")
    parser.add_argument("--keywords", nargs="*", default=[], help="附加检索关键词")
    args = parser.parse_args()

    client = PublicSourceClient()
    result = client.collect_public_evidence(args.company, args.keywords)
    print(json.dumps(result, ensure_ascii=False, indent=2))
