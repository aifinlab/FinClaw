from __future__ import annotations

import json
import re
import time
import unicodedata
from typing import Any, Dict, Optional

import requests
from bs4 import BeautifulSoup

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}


class FetchError(RuntimeError):
    pass


def http_get(url: str, timeout: int = 20, headers: Optional[Dict[str, str]] = None) -> str:
    merged_headers = dict(DEFAULT_HEADERS)
    if headers:
        merged_headers.update(headers)
    response = requests.get(url, timeout=timeout, headers=merged_headers)
    response.raise_for_status()
    response.encoding = response.apparent_encoding or response.encoding
    return response.text


def soup_from_url(url: str, timeout: int = 20) -> BeautifulSoup:
    html = http_get(url, timeout=timeout)
    return BeautifulSoup(html, "html.parser")


def normalize_text(value: Optional[str]) -> str:
    if value is None:
        return ""
    value = unicodedata.normalize("NFKC", value)
    value = value.replace("\u3000", " ")
    value = re.sub(r"\s+", "", value)
    value = value.strip()
    replacements = {
        "股份有限公司": "股份公司",
        "有限责任公司": "有限公司",
        "（": "(",
        "）": ")",
    }
    for old, new in replacements.items():
        value = value.replace(old, new)
    return value.lower()


def compare_values(left: Optional[str], right: Optional[str]) -> str:
    if not left and not right:
        return "信息缺失"
    if not left or not right:
        return "信息缺失"
    if normalize_text(left) == normalize_text(right):
        return "一致"
    return "疑似不一致"


def safe_find_text(soup: BeautifulSoup, patterns: list[str]) -> Optional[str]:
    text = soup.get_text("\n", strip=True)
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None


def pretty_print(data: Any) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


def polite_sleep(seconds: float = 0.8) -> None:
    time.sleep(seconds)
