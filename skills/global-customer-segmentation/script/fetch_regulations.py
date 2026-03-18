
from typing import Dict, List
from common import get_text, html_to_text, now_iso, sha256_text

REGULATION_SOURCES = [
    {"name": "国家法律法规数据库", "url": "https://flk.npc.gov.cn/"},
    {"name": "证监会法规", "url": "https://www.csrc.gov.cn/"},
    {"name": "上交所规则", "url": "https://www.sse.com.cn/lawandrules/"},
    {"name": "深交所规则", "url": "https://www.szse.cn/lawrules/"},
    {"name": "SEC EDGAR", "url": "https://www.sec.gov/edgar/search/"},
]


def fetch_regulation_page(url: str) -> Dict:
    html = get_text(url)
    text = html_to_text(html)
    return {
        "url": url,
        "fetched_at": now_iso(),
        "sha256": sha256_text(text),
        "text": text[:30000],
    }


def list_regulation_sources() -> List[Dict]:
    return REGULATION_SOURCES
