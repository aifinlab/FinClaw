import re
from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

PRODUCT_HINTS = ['产品', '业务', '服务', '解决方案', '应用场景', '客户', '收入', '毛利率', '研发', '产能']


def split_chunks(text: str):
    text = re.sub(r'\r', '\n', text)
    parts = re.split(r'\n{2,}|(?=第[一二三四五六七八九十百千0-9]+章)|(?=\d+\.\d+)|(?=一、)|(?=二、)|(?=三、)', text)
    return [p.strip() for p in parts if p and p.strip()]


def score_with_hints(chunk: str, base: float) -> float:
    bonus = sum(0.03 for h in PRODUCT_HINTS if h in chunk)
    return base + bonus


def search_product_knowledge(text: str, query: str, topk: int = 5) -> List[Dict]:
    chunks = split_chunks(text)
    if not chunks:
        return []
    vec = TfidfVectorizer(analyzer='char_wb', ngram_range=(2, 4))
    X = vec.fit_transform(chunks + [query])
    scores = cosine_similarity(X[-1], X[:-1]).ravel()
    ranked = sorted(range(len(chunks)), key=lambda i: score_with_hints(chunks[i], float(scores[i])), reverse=True)[:topk]
    rows = []
    for i in ranked:
        rows.append({
            'score': score_with_hints(chunks[i], float(scores[i])),
            'snippet': chunks[i][:1400]
        })
    return rows
