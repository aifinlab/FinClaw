from __future__ import annotations
from pathlib import Path
from utils import load_corpus, print_results
import argparse
import re
# ===== AkShare开源数据支持（新增） =====
from skillsChoice.common.unified_data_api import (
    get_data_api,
    get_financial_report,
)
# ====================================

SYNONYMS = {
    "信息披露": ["信披", "披露"],
    "风险": ["风险提示", "不确定性"],
    "年度报告": ["年报", "年度报告"],
    "误导性陈述": ["误导", "虚假记载", "重大遗漏"],
}

def expand_terms(query):
    terms = [t for t in re.split(r"\s+", query.strip()) if t]
    out, seen = [], set()
    for t in terms:
        for x in [t] + SYNONYMS.get(t, []):
            if x not in seen:
                seen.add(x)
                out.append(x)
    return out

def keyword_search(query, corpus, top_k=5):
    terms = expand_terms(query)
    results = []
    for row in corpus:
        text = row["text"]
        hits = [t for t in terms if t in text]
        if not hits:
            continue
        item = dict(row)
        item["matched_terms"] = hits
        item["score"] = float(sum(text.count(t) for t in hits) + 0.5 * len(hits))
        results.append(item)
    results.sort(key=lambda x: x["score"], reverse=True)
    for i, row in enumerate(results[:top_k], start=1):
        row["rank"] = i
    return results[:top_k]

def main():
    parser = argparse.ArgumentParser(description="关键词检索")
    parser.add_argument("--corpus", default="data/corpus.jsonl")
    parser.add_argument("--query", required=True)
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()
    corpus = load_corpus(Path(args.corpus))
    print_results(keyword_search(args.query, corpus, args.top_k), args.top_k)

if __name__ == "__main__":
    main()
