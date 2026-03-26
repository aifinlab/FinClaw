from __future__ import annotations
from hybrid_retrieval import hybrid_search
from pathlib import Path
from utils import load_corpus
import argparse

def trace_claim(claim, corpus, top_k=5):
    return hybrid_search(claim, corpus, top_k=top_k)

def main():
    parser = argparse.ArgumentParser(description="引用溯源")
    parser.add_argument("--corpus", default="data/corpus.jsonl")
    parser.add_argument("--claim", required=True)
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()
    corpus = load_corpus(Path(args.corpus))
    results = trace_claim(args.claim, corpus, args.top_k)
    for item in results:
        print("=" * 80)
        print(f"[{item['rank']}] score={item['score']:.4f} | {item['title']} | page={item['page']}")
        print(f"url: {item['url']}")
        print(item['text'][:400].replace("\n", " "))
        if item.get("matched_terms"):
            print(f"matched_terms: {', '.join(item['matched_terms'])}")

if __name__ == "__main__":
    main()
