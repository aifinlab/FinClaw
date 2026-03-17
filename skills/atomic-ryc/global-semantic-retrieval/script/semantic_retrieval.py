from __future__ import annotations
import argparse
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils import load_corpus, print_results

def semantic_search(query, corpus, top_k=5):
    texts = [row["text"] for row in corpus]
    vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4), min_df=1)
    matrix = vectorizer.fit_transform(texts)
    qv = vectorizer.transform([query])
    sims = cosine_similarity(qv, matrix).ravel()
    order = sims.argsort()[::-1][:top_k]
    results = []
    for rank, idx in enumerate(order, start=1):
        row = dict(corpus[idx])
        row["score"] = float(sims[idx])
        row["rank"] = rank
        results.append(row)
    return results

def main():
    parser = argparse.ArgumentParser(description="语意检索")
    parser.add_argument("--corpus", default="data/corpus.jsonl")
    parser.add_argument("--query", required=True)
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()
    corpus = load_corpus(Path(args.corpus))
    print_results(semantic_search(args.query, corpus, args.top_k), args.top_k)

if __name__ == "__main__":
    main()
