
from common import get_text, html_to_text, now_iso, save_json, sha256_text
from typing import Dict, List
import argparse
import os

import re


def chunk_text(text: str, max_chars: int = 800, overlap: int = 100) -> List[Dict]:
    text = re.sub(r"
{3,}", "

", text.strip())
    chunks = []
    start = 0
    idx = 0
    while start < len(text):
        end = min(len(text), start + max_chars)
        body = text[start:end]
        chunks.append({
            "chunk_id": f"chunk_{idx:04d}",
            "start": start,
            "end": end,
            "text": body,
            "sha256": sha256_text(body),
        })
        if end == len(text):
            break
        start = max(0, end - overlap)
        idx += 1
    return chunks


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--mode", default="general")
    parser.add_argument("--output", default="output/chunks.json")
    args = parser.parse_args()

    html = get_text(args.url)
    text = html_to_text(html)
    chunks = chunk_text(text)
    payload = {
        "source_url": args.url,
        "mode": args.mode,
        "fetched_at": now_iso(),
        "doc_sha256": sha256_text(text),
        "chunk_count": len(chunks),
        "chunks": chunks,
    }
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    save_json(args.output, payload)
    print(f"saved to {args.output}")


if __name__ == "__main__":
    main()
