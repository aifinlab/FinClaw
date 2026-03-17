from __future__ import annotations

import re
from collections import Counter
from typing import List, Sequence, Tuple

SENTENCE_SPLIT = re.compile(r"(?<=[。！？!?；;])")
STOPWORDS = set("的 了 和 与 及 对 于 在 将 按照 根据 有关 相关 以及 一个 进行 可以 应当 不得 公司 上市 证券 规定 条文 报告".split())


def truncate_text(text: str, max_chars: int = 12000) -> str:
    return text[:max_chars] if len(text) > max_chars else text


def split_sentences(text: str) -> List[str]:
    parts = [p.strip() for p in SENTENCE_SPLIT.split(text) if p.strip()]
    return [p for p in parts if len(p) >= 8]


def keyword_scores(text: str, top_n: int = 20) -> List[Tuple[str, int]]:
    words = re.findall(r"[\u4e00-\u9fffA-Za-z0-9]{2,}", text)
    words = [w for w in words if w not in STOPWORDS and not w.isdigit()]
    return Counter(words).most_common(top_n)


def score_sentences(sentences: Sequence[str], top_keywords: Sequence[Tuple[str, int]]) -> List[Tuple[int, str]]:
    keywords = {k: v for k, v in top_keywords}
    scored = []
    for s in sentences:
        score = sum(v for k, v in keywords.items() if k in s)
        if re.search(r"(应当|不得|负责|披露|公告|审议|实施|生效|适用|风险|处罚|违规)", s):
            score += 3
        scored.append((score, s))
    return sorted(scored, key=lambda x: x[0], reverse=True)


def pick_highlights(text: str, max_sentences: int = 6) -> List[str]:
    sentences = split_sentences(text)
    kw = keyword_scores(text, top_n=25)
    ranked = score_sentences(sentences, kw)
    chosen = [s for _, s in ranked[: max_sentences * 2]]
    uniq = []
    seen = set()
    for s in sentences:
        if s in chosen and s not in seen:
            uniq.append(s)
            seen.add(s)
        if len(uniq) >= max_sentences:
            break
    return uniq


def find_lines(text: str, patterns: Sequence[str], limit: int = 6) -> List[str]:
    sentences = split_sentences(text)
    res = []
    for s in sentences:
        if any(re.search(p, s, re.I) for p in patterns):
            res.append(s)
        if len(res) >= limit:
            break
    return res
