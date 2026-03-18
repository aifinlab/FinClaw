from __future__ import annotations

import io
import re
from dataclasses import dataclass

import pdfplumber
import requests
from bs4 import BeautifulSoup

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}


@dataclass
class FetchedDocument:
    url: str
    title: str
    text: str
    content_type: str


def fetch_url(url: str, timeout: int = 30) -> requests.Response:
    resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
    resp.raise_for_status()
    return resp


def extract_text_from_pdf_bytes(data: bytes) -> str:
    text_parts = []
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            if page_text.strip():
                text_parts.append(page_text)
    return "\n".join(text_parts)


def clean_text(text: str) -> str:
    text = text.replace("\xa0", " ").replace("\u3000", " ")
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


def html_to_text(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    selectors = [
        "article", "main", ".article", ".content", ".detail", ".detail-content",
        ".law-content", ".TRS_Editor", ".c-article-content", "#Zoom", ".custom"
    ]
    chunks = []
    for selector in selectors:
        for node in soup.select(selector):
            txt = node.get_text("\n", strip=True)
            if len(txt) > 200:
                chunks.append(txt)
    if not chunks:
        body = soup.body.get_text("\n", strip=True) if soup.body else soup.get_text("\n", strip=True)
        chunks.append(body)
    text = max(chunks, key=len)
    return clean_text(text)


def fetch_document(url: str) -> FetchedDocument:
    resp = fetch_url(url)
    ctype = resp.headers.get("Content-Type", "").lower()
    if "pdf" in ctype or url.lower().endswith(".pdf"):
        text = extract_text_from_pdf_bytes(resp.content)
        title = url.rsplit("/", 1)[-1]
        return FetchedDocument(url=url, title=title, text=clean_text(text), content_type="application/pdf")

    resp.encoding = resp.apparent_encoding or resp.encoding
    html = resp.text
    soup = BeautifulSoup(html, "lxml")
    title = (soup.title.get_text(strip=True) if soup.title else url)[:200]
    text = html_to_text(html)
    return FetchedDocument(url=url, title=title, text=text, content_type="text/html")
