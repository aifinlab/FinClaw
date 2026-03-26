from __future__ import annotations
from typing import Any, Dict, List
import json

def calibrate(record: Dict[str, Any], benchmark: Dict[str, Any]) -> Dict[str, Any]:
    calibrated_score = record.get("score", 0)
    notes: List[str] = []

    industry_click_rate = benchmark.get("industry_click_rate")
    customer_click_rate = benchmark.get("customer_click_rate")
    if industry_click_rate is not None and customer_click_rate is not None:
        if customer_click_rate > industry_click_rate:
            calibrated_score += 5
            notes.append("客户活动响应高于行业均值。")
        else:
            notes.append("客户活动响应未明显高于行业均值。")

    region_penetration = benchmark.get("region_penetration_rate")
    if region_penetration is not None:
        if region_penetration < 0.55 and "首卡获客" in record.get("opportunity_types", []):
            calibrated_score += 4
            notes.append("所在区域信用卡渗透率相对较低，首卡拓展空间较大。")

    channel_conversion = benchmark.get("preferred_channel_conversion")
    if channel_conversion is not None and channel_conversion < 0.03:
        calibrated_score -= 3
        notes.append("当前建议渠道行业转化基准偏低，需谨慎排序。")

    level = "低"
    if calibrated_score >= 50:
        level = "高"
    elif calibrated_score >= 28:
        level = "中"

    result = dict(record)
    result["calibrated_score"] = calibrated_score
    result["calibrated_level"] = level
    result["benchmark_notes"] = notes if notes else ["行业基准信息不足，仅保留内部信号判断。"]
    return result

def run(records: List[Dict[str, Any]], benchmark: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [calibrate(r, benchmark) for r in records]

if __name__ == "__main__":
    demo_records = [{"customer_id": "C001", "score": 46, "opportunity_types": ["首卡获客"]}]
    demo_benchmark = {
        "industry_click_rate": 0.12,
        "customer_click_rate": 0.21,
        "region_penetration_rate": 0.50,
        "preferred_channel_conversion": 0.028
    }
    print(json.dumps(run(demo_records, demo_benchmark), ensure_ascii=False, indent=2))
