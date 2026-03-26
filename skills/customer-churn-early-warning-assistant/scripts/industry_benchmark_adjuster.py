from __future__ import annotations

from typing import Any, Dict
import json


def apply_industry_adjustment(result: Dict[str, Any], benchmark: Dict[str, Any]) -> Dict[str, Any]:
    """
    根据行业基线对预警分数做轻量校准。
    benchmark 示例：
    {
      "available": true,
      "aum_drop_market_avg": -18,
      "txn_drop_market_avg": -15,
      "support_level": "强",
      "note": "同区域同客群近 90 天平均资产回撤较明显"
    }
    """
    adjusted = dict(result)
    available = bool(benchmark.get("available", False))

    support = {
        "available": available,
        "support_level": benchmark.get("support_level", "弱" if not available else "中"),
        "note": benchmark.get("note", "未提供行业校准说明"),
    }

    score = int(adjusted.get("overall_score", 0))
    if available:
        aum_market_avg = float(benchmark.get("aum_drop_market_avg", 0))
        txn_market_avg = float(benchmark.get("txn_drop_market_avg", 0))

        # 市场整体下行较明显时，适度降低预警强度，避免过度告警
        if aum_market_avg <= -15:
            score -= 5
        if txn_market_avg <= -15:
            score -= 3
        score = max(score, 0)
    else:
        support["note"] = "缺少行业数据，仅支持内部相对预警，结论强度应适度下调。"

    if score >= 70:
        level = "紧急"
    elif score >= 45:
        level = "高"
    elif score >= 20:
        level = "中"
    else:
        level = "低"

    adjusted["overall_score"] = score
    adjusted["warning_level"] = level
    adjusted["industry_support"] = support
    return adjusted


if __name__ == "__main__":
    result = {"customer_id": "C001", "warning_level": "高", "overall_score": 48, "signals": []}
    benchmark = {
        "available": True,
        "aum_drop_market_avg": -20,
        "txn_drop_market_avg": -16,
        "support_level": "强",
        "note": "同区域同客群近 90 天整体偏弱",
    }
    print(json.dumps(apply_industry_adjustment(result, benchmark), ensure_ascii=False, indent=2))
