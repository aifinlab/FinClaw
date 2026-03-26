from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict
import re


def split_chunks(text: str):
    text = re.sub(r'\r', '\n', text)
    parts = re.split(r'\n{2,}|(?=第[一二三四五六七八九十百千0-9]+条)|(?=第[一二三四五六七八九十百千0-9]+章)', text)
    cleaned = [p.strip() for p in parts if p and p.strip()]
    return cleaned


def infer_clause_label(chunk: str) -> str:
    m = re.search(r'(第[一二三四五六七八九十百千0-9]+条)', chunk)
    if m:
        return m.group(1)
    m = re.search(r'(第[一二三四五六七八九十百千0-9]+章)', chunk)
    if m:
        return m.group(1)
    return ''


def locate_passages(text: str, query: str, topk: int = 5) -> List[Dict]:
    chunks = split_chunks(text)
    if not chunks:
        return []
    vec = TfidfVectorizer(analyzer='char_wb', ngram_range=(2, 4))
    X = vec.fit_transform(chunks + [query])
    scores = cosine_similarity(X[-1], X[:-1]).ravel()
    order = scores.argsort()[::-1][:topk]
    rows = []
    for idx in order:
        rows.append({
            'rank': int(len(rows) + 1),
            'score': float(scores[idx]),
            'clause_hint': infer_clause_label(chunks[idx]),
            'text': chunks[idx][:1200]
        })
    return rows
