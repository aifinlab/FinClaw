from __future__ import annotations
import json

from pathlib import Path
from typing import Any
import argparse


def calibrate_with_industry(
        scan_result: dict[str, Any], industry_context: dict[str, Any]) -> dict[str, Any]:
    result = dict(scan_result)
    summary = dict(result.get("summary", {}))

    has_industry = bool(industry_context.get("has_industry_data"))
    has_watchlist = bool(industry_context.get("has_watchlist"))
    peer_deviation = float(industry_context.get("peer_deviation_score", 0))

    adjustments: list[str] = []
    calibrated_score = float(summary.get("total_score", 0))

    if has_industry:
        if peer_deviation >= 20:
            calibrated_score += 15
            adjustments.append("行业偏离度较高，上调风险分值。")
        elif peer_deviation <= 5:
            calibrated_score -= 5
            adjustments.append("行业偏离度较低，下调部分风险分值。")
    else:
        adjustments.append("未提供行业数据，仅能基于内部行为特征解释结果。")

    if has_watchlist:
        calibrated_score += 10
        adjustments.append("存在外部风险名单或敏感名单辅助信息，上调关注等级。")
    else:
        adjustments.append("未提供外部名单数据，无法判断是否存在名单命中。")

    if calibrated_score >= 55:
        level = "高度可疑"
    elif calibrated_score >= 30:
        level = "中度可疑"
    elif calibrated_score > 0:
        level = "低度可疑"
    else:
        level = "暂未发现明显异常"

    summary["calibrated_score"] = round(calibrated_score, 2)
    summary["risk_level_after_calibration"] = level
    summary["calibration_notes"] = adjustments
    result["summary"] = summary
    return result


if __name__ == "__main__":

   parser = argparse.ArgumentParser(description="行业与外部风险信息校准")
   parser.add_argument("scan_result", help="基础扫描 JSON 文件")
   parser.add_argument("industry_context", help="行业上下文 JSON 文件")
   parser.add_argument(
       "-o",
       "--output",
       default="calibrated_result.json",
       help="输出 JSON 文件")
   args = parser.parse_args()

   scan_result = json.loads(
       Path(
           args.scan_result).read_text(
           encoding="utf-8"))
   industry_context = json.loads(
       Path(
           args.industry_context).read_text(
           encoding="utf-8"))
   output = calibrate_with_industry(scan_result, industry_context)
   Path(
       args.output).write_text(
       json.dumps(
           output,
           ensure_ascii=False,
           indent=2),
       encoding="utf-8")
   print(f"已输出到 {args.output}")
