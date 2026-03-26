from __future__ import annotations

from bs4 import BeautifulSoup
from pathlib import Path
from pdfminer.high_level import extract_text
from typing import List

import io
import re
import requests

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0 Safari/537.36"
    )
}


def read_text_from_file(file_path: str) -> str:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")

    suffix = path.suffix.lower()
    if suffix in {".txt", ".md"}:
        return path.read_text(encoding="utf-8", errors="ignore")
    if suffix == ".pdf":
        return extract_text(str(path))
    if suffix in {".html", ".htm"}:
        html = path.read_text(encoding="utf-8", errors="ignore")
        return html_to_text(html)

    raise ValueError(f"暂不支持的文件类型: {suffix}")


def fetch_text_from_url(url: str, timeout: int = 20) -> str:
    resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
    resp.raise_for_status()
    content_type = resp.headers.get("Content-Type", "").lower()

    if "pdf" in content_type or url.lower().endswith(".pdf"):
        return extract_text(io.BytesIO(resp.content))

    resp.encoding = resp.encoding or "utf-8"
    return html_to_text(resp.text)


def html_to_text(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = soup.get_text("\n")
    text = re.sub(r"\n{2,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def load_materials(primary_file: str | None, primary_url: str | None,
                   extra_files: List[str] | None = None,
                   extra_urls: List[str] | None = None) -> List[dict]:
    materials = []

    if primary_file:
        materials.append({
            "source": primary_file,
            "kind": "file",
            "text": read_text_from_file(primary_file),
        })
    if primary_url:
        materials.append({
            "source": primary_url,
            "kind": "url",
            "text": fetch_text_from_url(primary_url),
        })

    for f in extra_files or []:
        materials.append({
            "source": f,
            "kind": "file",
            "text": read_text_from_file(f),
        })

    for u in extra_urls or []:
        materials.append({
            "source": u,
            "kind": "url",
            "text": fetch_text_from_url(u),
        })

    if not materials:
        raise ValueError("至少提供一个 --material-file 或 --material-url")

    return materials
