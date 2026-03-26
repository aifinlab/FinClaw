
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from typing import Any, Dict, List
import hashlib
import json

import re
import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; GlobalSkillBot/1.0; +https://openai.com)"
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()


def get_json(url: str, **kwargs) -> Any:
    r = requests.get(url, headers=HEADERS, timeout=30, **kwargs)
    r.raise_for_status()
    return r.json()


def get_text(url: str, **kwargs) -> str:
    r = requests.get(url, headers=HEADERS, timeout=30, **kwargs)
    r.raise_for_status()
    return r.text


def html_to_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    text = soup.get_text("
")
    text = re.sub(r"
{2,}", "

", text)
    return text.strip()


def save_json(path: str, payload: Any) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
