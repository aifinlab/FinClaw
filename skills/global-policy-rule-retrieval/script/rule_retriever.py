import re
from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

RULE_HINTS = ['应当', '不得', '可以', '负责', '程序', '审批', '披露', '董事会', '股东会', '监事会', '审议']


def split_chunks(text: str):
    text = re.sub(r'\r', '\n', text)
    parts = re.split(r'\n{2,}|(?=第[一二三四五六七八九十百千0-9]+条)|(?=第[一二三四五六七八九十百千0-9]+章)', text)
    return [p.strip() for p in parts if p and p.strip()]


def search_rules(text: str, query: str, topk: int = 5) -> List[Dict]:
    chunks = split_chunks(text)
    if not chunks:
        return []
    vec = TfidfVectorizer(analyzer='char_wb', ngram_range=(2, 4))
    X = vec.fit_transform(chunks + [query])
    base_scores = cosine_similarity(X[-1], X[:-1]).ravel()
    rescored = []
    for idx, chunk in enumerate(chunks):
        bonus = sum(0.02 for h in RULE_HINTS if h in chunk)
        rescored.append((idx, float(base_scores[idx]) + bonus))
    rescored.sort(key=lambda x: x[1], reverse=True)
    rows = []
    for idx, score in rescored[:topk]:
        label = ''
        m = re.search(r'(第[一二三四五六七八九十百千0-9]+条)', chunks[idx])
        if m:
            label = m.group(1)
        rows.append({'score': score, 'clause_hint': label, 'snippet': chunks[idx][:1400]})
    return rows
