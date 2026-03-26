from bs4 import BeautifulSoup
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pypdf import PdfReader
from typing import Dict, List, Optional
import argparse
import hashlib
import json
import os

import re
import requests
import time
# ===== AkShare开源数据支持（新增） =====
from skillsChoice.common.unified_data_api import (
    get_data_api,
    get_index_quote,
)
# ====================================

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"
}


@dataclass
class TraceRecord:
    source_url: str
    fetched_at: str
    sha256: str
    parser: str
    content_type: Optional[str] = None
    note: Optional[str] = None


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def ensure_parent_dir(path: str) -> None:
    parent = os.path.dirname(os.path.abspath(path))
    if parent:
        os.makedirs(parent, exist_ok=True)


def save_json(data: Dict, output: str) -> None:
    ensure_parent_dir(output)
    with open(output, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_json(path: str) -> Dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def fetch_url(url: str, timeout: int = 30) -> requests.Response:
    resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
    resp.raise_for_status()
    return resp


def fetch_text(url: str, timeout: int = 30) -> Dict:
    resp = fetch_url(url, timeout=timeout)
    text = resp.text
    trace = TraceRecord(
        source_url=url,
        fetched_at=utc_now_iso(),
        sha256=sha256_bytes(resp.content),
        parser="html",
        content_type=resp.headers.get("Content-Type"),
    )
    return {"text": html_to_text(text), "html": text, "trace": asdict(trace)}


def fetch_pdf_text(url: str, timeout: int = 60) -> Dict:
    resp = fetch_url(url, timeout=timeout)
    tmp_path = "/tmp/current_skill_pdf.pdf"
    with open(tmp_path, "wb") as f:
        f.write(resp.content)
    reader = PdfReader(tmp_path)
    texts: List[str] = []
    for page in reader.pages:
        try:
            texts.append(page.extract_text() or "")
        except Exception:
            texts.append("")
    trace = TraceRecord(
        source_url=url,
        fetched_at=utc_now_iso(),
        sha256=sha256_bytes(resp.content),
        parser="pdf",
        content_type=resp.headers.get("Content-Type"),
    )
    return {"text": "\n".join(texts), "trace": asdict(trace)}


def html_to_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = soup.get_text("\n")
    text = re.sub(r"\n{2,}", "\n", text)
    return text.strip()


def clean_text(text: str) -> str:
    text = text.replace("\u3000", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_first(patterns: List[str], text: str, flags: int = re.I) -> Optional[str]:
    for pattern in patterns:
        match = re.search(pattern, text, flags)
        if match:
            return clean_text(match.group(1))
    return None


def keyword_hits(text: str, keywords: List[str], window: int = 60) -> List[Dict]:
    results = []
    for keyword in keywords:
        for match in re.finditer(re.escape(keyword), text, re.I):
            start = max(0, match.start() - window)
            end = min(len(text), match.end() + window)
            snippet = clean_text(text[start:end])
            results.append({"keyword": keyword, "snippet": snippet})
    return results


def parse_args_common(description: str):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--output", required=True, help="输出 JSON 文件路径")
    return parser
