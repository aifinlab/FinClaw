#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List, Dict
import json

def score_solution(item: Dict) -> int:
    score = 0
    score += int(item.get("需求匹配度", 0)) * 4
    score += int(item.get("落地可行性", 0)) * 3
    score += int(item.get("客户价值", 0)) * 2
    score += int(item.get("合规清晰度", 0)) * 2
    score -= int(item.get("实施复杂度", 0)) * 2
    return score

def rank_solutions(items: List[Dict]) -> List[Dict]:
    enriched = []
    for item in items:
        item = dict(item)
        item["综合评分"] = score_solution(item)
        enriched.append(item)
    enriched.sort(key=lambda x: x["综合评分"], reverse=True)
    return enriched

if __name__ == "__main__":
    import sys
    data = json.load(sys.stdin)
    print(json.dumps(rank_solutions(data), ensure_ascii=False, indent=2))
