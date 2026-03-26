from __future__ import annotations

from bs4 import BeautifulSoup
from legal_rules import DEFAULT_COMPANY, LEGAL_BASES
from pathlib import Path
from pypdf import PdfReader
from typing import Any

import argparse
import io
import json

import requests

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; public-disclosure-skill/1.0)",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}


def fetch_text_from_url(url: str, timeout: int = 30) -> str:
    response = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
    response.raise_for_status()
    content_type = response.headers.get("Content-Type", "").lower()

    if ".pdf" in url.lower() or "application/pdf" in content_type:
        reader = PdfReader(io.BytesIO(response.content))
        texts: list[str] = []
        for page in reader.pages:
            page_text = page.extract_text() or ""
            texts.append(page_text)
        return "\n".join(texts)

    response.encoding = response.apparent_encoding or response.encoding or "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.extract()
    text = soup.get_text("\n")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)


def collect_sources() -> list[dict[str, Any]]:
    sources: list[dict[str, Any]] = []
    for item in LEGAL_BASES:
        sources.append(
            {
                "group": "laws",
                "label": item["name"],
                "url": item["url"],
                "source": item["source"],
            }
        )
    for item in DEFAULT_COMPANY["public_sources"]:
        sources.append(
            {
                "group": "company",
                "label": item["label"],
                "url": item["url"],
                "source": DEFAULT_COMPANY["name"],
            }
        )
    return sources


def main() -> None:
    parser = argparse.ArgumentParser(description="抓取法规与上市公司公开文本")
    parser.add_argument("--out-dir", default="fetched_data", help="输出目录")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest: list[dict[str, Any]] = []
    for idx, source in enumerate(collect_sources(), start=1):
        text = fetch_text_from_url(source["url"])
        file_name = f"{idx:02d}_{source['group']}_{source['label'].replace('/', '_')}.txt"
        file_path = out_dir / file_name
        file_path.write_text(text, encoding="utf-8")
        manifest.append({**source, "saved_to": str(file_path)})
        print(f"saved: {file_path}")

    (out_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"manifest: {out_dir / 'manifest.json'}")


if __name__ == "__main__":
    main()
