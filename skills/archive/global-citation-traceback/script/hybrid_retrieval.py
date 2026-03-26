from __future__ import annotations
from keyword_retrieval import expand_terms
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils import load_corpus, print_results, normalize_scores
import argparse

def hybrid_search(query, corpus, top_k=5, alpha=0.55):
    texts = [row["text"] for row in corpus]
    vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4), min_df=1)
    matrix = vectorizer.fit_transform(texts)
    qv = vectorizer.transform([query])
    sem_scores = cosine_similarity(qv, matrix).ravel().tolist()
    terms = expand_terms(query)
    kw_scores, matched_terms = [], []
    for row in corpus:
        hits = [t for t in terms if t in row["text"]]
        matched_terms.append(hits)
        kw_scores.append(sum(row["text"].count(t) for t in hits) + 0.5 * len(hits))
    sem_n = normalize_scores(sem_scores)
    kw_n = normalize_scores(kw_scores)
    fused = [alpha*s + (1-alpha)*k for s, k in zip(sem_n, kw_n)]
    order = sorted(range(len(corpus)), key=lambda i: fused[i], reverse=True)[:top_k]
    results = []
    for rank, idx in enumerate(order, start=1):
        row = dict(corpus[idx])
        row["score"] = float(fused[idx])
        row["semantic_score"] = float(sem_n[idx])
        row["keyword_score"] = float(kw_n[idx])
        row["matched_terms"] = matched_terms[idx]
        row["rank"] = rank
        results.append(row)
    return results

def main():
    parser = argparse.ArgumentParser(description="混合检索")
    parser.add_argument("--corpus", default="data/corpus.jsonl")
    parser.add_argument("--query", required=True)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--alpha", type=float, default=0.55)
    args = parser.parse_args()
    corpus = load_corpus(Path(args.corpus))
    print_results(hybrid_search(args.query, corpus, args.top_k, args.alpha), args.top_k)

if __name__ == "__main__":
    main()
