from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict
import re

QUESTION_HINTS = ['是否', '怎么', '如何', '需不需要', '可以吗', '由谁', '多久', '条件']


def split_chunks(text: str):
    text = re.sub(r'\r', '\n', text)
    parts = re.split(r'\n{2,}|(?=第[一二三四五六七八九十百千0-9]+条)|(?=问：)|(?=Q[:：])', text)
    return [p.strip() for p in parts if p and p.strip()]


def normalize_question(q: str) -> str:
    q = q.strip()
    if not any(h in q for h in QUESTION_HINTS):
        q = '如何 ' + q
    return q


def search_faq(text: str, question: str, topk: int = 5) -> List[Dict]:
    chunks = split_chunks(text)
    if not chunks:
        return []
    query = normalize_question(question)
    vec = TfidfVectorizer(analyzer='char_wb', ngram_range=(2, 4))
    X = vec.fit_transform(chunks + [query])
    scores = cosine_similarity(X[-1], X[:-1]).ravel()
    order = scores.argsort()[::-1][:topk]
    rows = []
    for idx in order:
        rows.append({
            'score': float(scores[idx]),
            'answer_evidence': chunks[idx][:1400]
        })
    return rows
