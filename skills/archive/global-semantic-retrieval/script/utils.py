from __future__ import annotations
from bs4 import BeautifulSoup
from dataclasses import dataclass, asdict
from pathlib import Path
from pypdf import PdfReader
from typing import List, Dict, Any
import json
import math
import re
import requests
# ===== AkShare开源数据支持（新增） =====
from skillsChoice.common.unified_data_api import (
    get_data_api,
)
# ====================================

DEFAULT_SOURCES = [
    {
        "id": "law_disclosure_2025",
        "title": "上市公司信息披露管理办法（2025）",
        "url": "https://www.csrc.gov.cn/csrc/c101953/c7547359/content.shtml",
        "type": "html",
        "source": "中国证监会",
    },
    {
        "id": "law_annual_report_format_2021",
        "title": "公开发行证券的公司信息披露内容与格式准则第2号—年度报告的内容与格式（2021年修订）",
        "url": "https://www.csrc.gov.cn/csrc/c101864/c6df1268b5b294448bdec7e010d880a01/6df1268b5b294448bdec7e010d880a01/files/%E9%99%84%E4%BB%B61%EF%BC%9A%E5%85%AC%E5%BC%80%E5%8F%91%E8%A1%8C%E8%AF%81%E5%88%B8%E7%9A%84%E5%85%AC%E5%8F%B8%E4%BF%A1%E6%81%AF%E6%8A%AB%E9%9C%B2%E5%86%85%E5%AE%B9%E4%B8%8E%E6%A0%BC%E5%BC%8F%E5%87%86%E5%88%99%E7%AC%AC2%E5%8F%B7%E2%80%94%E5%B9%B4%E5%BA%A6%E6%8A%A5%E5%91%8A%E7%9A%84%E5%86%85%E5%AE%B9%E4%B8%8E%E6%A0%BC%E5%BC%8F%EF%BC%882021%E5%B9%B4%E4%BF%AE%E8%AE%A2%EF%BC%89.pdf",
        "type": "pdf",
        "source": "中国证监会",
    },
    {
        "id": "company_luxshare_h1_2025",
        "title": "立讯精密工业股份有限公司2025年半年度报告",
        "url": "https://static.cninfo.com.cn/finalpage/2025-08-26/1224571100.PDF",
        "type": "pdf",
        "source": "巨潮资讯",
    },
    {
        "id": "company_luxshare_forecast_2025h1",
        "title": "立讯精密工业股份有限公司2025年半年度业绩预告",
        "url": "https://static.cninfo.com.cn/finalpage/2025-04-26/1223326842.PDF",
        "type": "pdf",
        "source": "巨潮资讯",
    },
]

@dataclass
class Chunk:
    chunk_id: str
    doc_id: str
    title: str
    source: str
    url: str
    section: str
    page: int
    text: str

def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)

def clean_text(text: str) -> str:
    text = text.replace("\u3000", " ").replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def chunk_text(doc_id: str, title: str, source: str, url: str, text: str, page: int = 0, max_chars: int = 500, overlap: int = 80):
    text = clean_text(text)
    if not text:
        return []
    chunks = []
    start = 0
    idx = 0
    while start < len(text):
        end = min(len(text), start + max_chars)
        snippet = text[start:end]
        section = f"page_{page}" if page else "body"
        chunks.append(Chunk(
            chunk_id=f"{doc_id}_{page}_{idx}",
            doc_id=doc_id,
            title=title,
            source=source,
            url=url,
            section=section,
            page=page,
            text=snippet
        ))
        idx += 1
        if end == len(text):
            break
        start = max(0, end - overlap)
    return chunks

def fetch_url(url: str, timeout: int = 40) -> bytes:
    resp = requests.get(url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0 skill-demo"})
    resp.raise_for_status()
    return resp.content

def extract_html_text(content: bytes) -> str:
    soup = BeautifulSoup(content, "html.parser")
    return clean_text(soup.get_text("\n"))

def extract_pdf_pages(pdf_path: Path):
    reader = PdfReader(str(pdf_path))
    pages = []
    for page in reader.pages:
        try:
            pages.append(clean_text(page.extract_text() or ""))
        except Exception:
            pages.append("")
    return pages

def build_corpus(data_dir: Path, sources=None) -> Path:
    ensure_dir(data_dir)
    raw_dir = data_dir / "raw"
    ensure_dir(raw_dir)
    corpus_path = data_dir / "corpus.jsonl"
    sources = sources or DEFAULT_SOURCES
    all_chunks = []
    for src in sources:
        if src["type"] == "html":
            html = fetch_url(src["url"])
            (raw_dir / f"{src['id']}.html").write_bytes(html)
            text = extract_html_text(html)
            all_chunks.extend(chunk_text(src["id"], src["title"], src["source"], src["url"], text))
        elif src["type"] == "pdf":
            pdf_bytes = fetch_url(src["url"])
            pdf_path = raw_dir / f"{src['id']}.pdf"
            pdf_path.write_bytes(pdf_bytes)
            pages = extract_pdf_pages(pdf_path)
            for i, page_text in enumerate(pages, start=1):
                if page_text:
                    all_chunks.extend(chunk_text(src["id"], src["title"], src["source"], src["url"], page_text, page=i))
        else:
            raise ValueError(src["type"])
    with corpus_path.open("w", encoding="utf-8") as f:
        for c in all_chunks:
            f.write(json.dumps(asdict(c), ensure_ascii=False) + "\n")
    return corpus_path

def load_corpus(corpus_path: Path):
    rows = []
    with corpus_path.open("r", encoding="utf-8") as f:
        for line in f:
            rows.append(json.loads(line))
    return rows

def print_results(results, top_k: int = 5) -> None:
    for item in results[:top_k]:
        print("=" * 80)
        print(f"[{item.get('rank', '-')}] score={item.get('score', 0):.4f} | {item['title']} | page={item.get('page', 0)}")
        print(f"url: {item['url']}")
        print(item['text'][:400].replace("\n", " "))
        if item.get("matched_terms"):
            print(f"matched_terms: {', '.join(item['matched_terms'])}")

def normalize_scores(scores):
    if not scores:
        return []
    lo, hi = min(scores), max(scores)
    if math.isclose(lo, hi):
        return [1.0 for _ in scores]
    return [(x - lo) / (hi - lo) for x in scores]
