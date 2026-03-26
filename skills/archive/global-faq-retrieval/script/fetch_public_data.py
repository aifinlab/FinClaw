from bs4 import BeautifulSoup

from pathlib import Path
from pypdf import PdfReader
import io
import re
import requests

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; GlobalSkillBot/1.0; +https://example.com)"
}


def fetch_url_text(url: str, timeout: int = 25) -> str:
    resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
    resp.raise_for_status()
    ctype = resp.headers.get("Content-Type", "").lower()
    if "pdf" in ctype or url.lower().endswith('.pdf'):
        return pdf_bytes_to_text(resp.content)
    return html_to_text(resp.text)


def pdf_bytes_to_text(data: bytes) -> str:
    reader = PdfReader(io.BytesIO(data))
    parts = []
    for page in reader.pages:
        parts.append(page.extract_text() or "")
    return "\n".join(parts)


def html_to_text(html: str) -> str:
    soup = BeautifulSoup(html, 'lxml')
    for tag in soup(['script', 'style', 'noscript']):
        tag.extract()
    text = soup.get_text("\n")
    text = re.sub(r'\n{2,}', '\n\n', text)
    return text.strip()


def read_local_text(path: str) -> str:
    p = Path(path)
    suffix = p.suffix.lower()
    if suffix == '.pdf':
        return pdf_bytes_to_text(p.read_bytes())
    return p.read_text(encoding='utf-8', errors='ignore')


def load_document(source: str) -> str:
    if source.startswith('http://') or source.startswith('https://'):
        return fetch_url_text(source)
    return read_local_text(source)
