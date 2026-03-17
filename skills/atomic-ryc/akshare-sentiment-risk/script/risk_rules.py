from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Dict, Tuple
import math
import re

NEGATIVE_KEYWORDS: Dict[str, int] = {
    "立案": 10,
    "处罚": 9,
    "证监会": 7,
    "问询": 6,
    "关注函": 8,
    "监管": 5,
    "退市": 10,
    "违约": 10,
    "暴雷": 10,
    "亏损": 6,
    "下滑": 4,
    "减持": 5,
    "质押": 5,
    "冻结": 8,
    "诉讼": 8,
    "仲裁": 7,
    "涉嫌": 8,
    "欺诈": 10,
    "虚假陈述": 10,
    "造假": 10,
    "失信": 9,
    "破产": 10,
    "停牌": 6,
    "风险提示": 7,
    "经营异常": 8,
    "债务": 7,
    "裁员": 4,
    "商誉减值": 7,
    "被执行人": 9,
    "股权冻结": 9,
    "终止": 5,
    "下修": 4,
    "跳水": 5,
    "爆仓": 9,
    "欠薪": 8,
    "事故": 8,
    "污染": 8,
    "召回": 7,
    "安全": 4,
}

POSITIVE_KEYWORDS: Dict[str, int] = {
    "增长": 3,
    "预增": 5,
    "扭亏": 5,
    "中标": 4,
    "回购": 3,
    "增持": 4,
    "分红": 3,
    "创新高": 4,
    "盈利": 3,
    "合作": 2,
    "突破": 2,
    "订单": 2,
    "扩产": 2,
}

SEVERE_PATTERNS: Tuple[str, ...] = (
    r"被.*立案",
    r"收到.*处罚",
    r"涉嫌.*违法",
    r"股票.*退市",
    r"实控人.*失联",
    r"债务.*违约",
    r"重大.*诉讼",
)


@dataclass
class ArticleScore:
    risk_score: float
    level: str
    negative_hits: List[str]
    positive_hits: List[str]
    reason: str


def normalize_text(text: str) -> str:
    text = text or ""
    text = re.sub(r"\s+", " ", str(text))
    return text.strip()


def score_text(text: str) -> ArticleScore:
    text = normalize_text(text)
    if not text:
        return ArticleScore(0.0, "low", [], [], "空文本")

    neg_hits: List[str] = []
    pos_hits: List[str] = []
    score = 0.0

    for kw, weight in NEGATIVE_KEYWORDS.items():
        if kw in text:
            neg_hits.append(kw)
            score += weight

    for kw, weight in POSITIVE_KEYWORDS.items():
        if kw in text:
            pos_hits.append(kw)
            score -= weight * 0.4

    severe = any(re.search(pattern, text) for pattern in SEVERE_PATTERNS)
    if severe:
        score += 8

    unique_neg = len(set(neg_hits))
    score += min(unique_neg, 6) * 0.8

    score = max(0.0, min(100.0, round(score * 3.2, 2)))

    if score >= 65:
        level = "high"
    elif score >= 35:
        level = "medium"
    else:
        level = "low"

    if severe:
        reason = "命中高危监管/违约/退市类模式"
    elif neg_hits:
        reason = f"命中负面关键词: {', '.join(sorted(set(neg_hits))[:6])}"
    else:
        reason = "未命中显著风险词"

    return ArticleScore(
        risk_score=score,
        level=level,
        negative_hits=sorted(set(neg_hits)),
        positive_hits=sorted(set(pos_hits)),
        reason=reason,
    )


def aggregate_scores(article_scores: Iterable[ArticleScore], hotness_rank: float | None = None) -> dict:
    scores = list(article_scores)
    if not scores:
        return {
            "overall_risk_score": 0.0,
            "overall_risk_level": "low",
            "article_count": 0,
            "high_risk_count": 0,
            "medium_risk_count": 0,
            "hotness_adjustment": 0.0,
        }

    values = [item.risk_score for item in scores]
    mean_score = sum(values) / len(values)
    high_risk_count = sum(1 for item in scores if item.level == "high")
    medium_risk_count = sum(1 for item in scores if item.level == "medium")
    max_score = max(values)

    hotness_adjustment = 0.0
    if hotness_rank is not None and hotness_rank > 0:
        hotness_adjustment = max(0.0, 10 - math.log(hotness_rank + 1, 2))

    overall = round(min(100.0, mean_score * 0.55 + max_score * 0.25 + high_risk_count * 5 + medium_risk_count * 2 + hotness_adjustment), 2)

    if overall >= 70:
        level = "high"
    elif overall >= 40:
        level = "medium"
    else:
        level = "low"

    return {
        "overall_risk_score": overall,
        "overall_risk_level": level,
        "article_count": len(scores),
        "high_risk_count": high_risk_count,
        "medium_risk_count": medium_risk_count,
        "hotness_adjustment": round(hotness_adjustment, 2),
    }
