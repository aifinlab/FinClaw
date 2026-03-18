from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import List, Dict
import re
import json
import sys

PATTERNS = {
    "收益承诺": [r"保本", r"保收益", r"稳赚", r"稳拿", r"一定赚", r"肯定赚"],
    "绝对化表达": [r"一定", r"肯定", r"绝对", r"必然", r"完全没有问题"],
    "风险弱化": [r"基本不会亏", r"风险很低可以忽略", r"和存款差不多"],
    "诱导交易": [r"赶紧买", r"先买进去", r"错过就没有了", r"现在不上车就晚了"],
}

@dataclass
class RiskHit:
    category: str
    pattern: str
    snippet: str


def scan_text(text: str) -> List[RiskHit]:
    hits: List[RiskHit] = []
    for category, patterns in PATTERNS.items():
        for pattern in patterns:
            for match in re.finditer(pattern, text):
                start = max(0, match.start() - 12)
                end = min(len(text), match.end() + 12)
                hits.append(RiskHit(category, pattern, text[start:end]))
    return hits


def level_from_hits(hits: List[RiskHit]) -> str:
    if len(hits) >= 5:
        return "高"
    if len(hits) >= 2:
        return "中"
    return "低"


def main() -> None:
    text = sys.stdin.read().strip()
    hits = scan_text(text)
    result: Dict[str, object] = {
        "风险等级": level_from_hits(hits),
        "风险点列表": [asdict(h) for h in hits],
        "命中数量": len(hits),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
