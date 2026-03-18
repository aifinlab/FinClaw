#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""根据简单规则为风格漂移信号打分。"""
from __future__ import annotations
import json
import sys
from pathlib import Path
from typing import Any, Dict, List


def load_payload(path: str) -> Dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def score(payload: Dict[str, Any]) -> Dict[str, Any]:
    metrics = payload.get("metrics", {})
    score_total = 0
    signals: List[str] = []

    def add_signal(condition: bool, points: int, text: str) -> None:
        nonlocal score_total
        if condition:
            score_total += points
            signals.append(text)

    add_signal(abs(metrics.get("size_shift", 0)) >= 0.15, 2, "市值风格变化幅度较大")
    add_signal(abs(metrics.get("growth_value_shift", 0)) >= 0.15, 2, "成长/价值风格发生显著切换")
    add_signal(abs(metrics.get("industry_concentration_shift", 0)) >= 0.12, 2, "行业集中度变化较大")
    add_signal(abs(metrics.get("top10_concentration_shift", 0)) >= 0.10, 1, "前十大持仓集中度变化明显")
    add_signal(abs(metrics.get("turnover_shift", 0)) >= 0.20, 1, "换手率变化明显")
    add_signal(bool(metrics.get("manager_changed")), 1, "存在基金经理变更事件")
    add_signal(bool(metrics.get("prospectus_positioning_mismatch")), 3, "实际持仓与产品定位持续不一致")
    add_signal(metrics.get("duration_quarters", 0) >= 2, 2, "偏离持续时间达到两个季度及以上")

    if score_total <= 2:
        level = "未发现明显漂移"
    elif score_total <= 4:
        level = "存在轻度漂移迹象"
    elif score_total <= 7:
        level = "存在中度漂移，需持续跟踪"
    else:
        level = "存在显著漂移，需重点提示"

    return {
        "score": score_total,
        "level": level,
        "signals": signals,
        "note": "该结果为规则化初筛结果，正式结论仍需结合产品定位、历史窗口和市场环境进行人工复核。",
    }


def main() -> None:
    if len(sys.argv) < 2:
        print("用法：python drift_signal_scoring.py 输入.json", file=sys.stderr)
        sys.exit(1)
    payload = load_payload(sys.argv[1])
    print(json.dumps(score(payload), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
