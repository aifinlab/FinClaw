from __future__ import annotations
from typing import Any, Dict, List
import json

def render(records: List[Dict[str, Any]], task_name: str = "信用卡营销机会识别") -> str:
    lines: List[str] = []
    lines.append(f"# {task_name}报告")
    lines.append("")
    lines.append("## 一、识别结果总览")
    lines.append(f"- 样本数量：{len(records)}")
    high = sum(1 for r in records if r.get("calibrated_level", r.get("opportunity_level")) == "高")
    mid = sum(1 for r in records if r.get("calibrated_level", r.get("opportunity_level")) == "中")
    low = sum(1 for r in records if r.get("calibrated_level", r.get("opportunity_level")) == "低")
    lines.append(f"- 高机会数量：{high}")
    lines.append(f"- 中机会数量：{mid}")
    lines.append(f"- 低机会数量：{low}")
    lines.append("")
    lines.append("## 二、重点客户明细")

    for r in records:
        lines.append(f"### 客户 {r.get('customer_id', '未知')}")
        lines.append(f"- 机会等级：{r.get('calibrated_level', r.get('opportunity_level', '未知'))}")
        lines.append(f"- 原始评分：{r.get('score', '未知')}")
        if r.get("calibrated_score") is not None:
            lines.append(f"- 校准后评分：{r.get('calibrated_score')}")
        lines.append(f"- 机会类型：{', '.join(r.get('opportunity_types', [])) or '未识别'}")
        lines.append(f"- 推荐渠道：{r.get('primary_channel', '待定')}")
        reasons = r.get("reasons", [])
        if reasons:
            lines.append("- 推荐理由：")
            for reason in reasons:
                lines.append(f"  - {reason}")
        notes = r.get("benchmark_notes", [])
        if notes:
            lines.append("- 行业基准说明：")
            for note in notes:
                lines.append(f"  - {note}")
        lines.append("")

    lines.append("## 三、结论提示")
    lines.append("- 本报告用于营销机会识别，不代表审批结论。")
    lines.append("- 当行业数据不足时，仅可将结果视为内部信号提示。")
    return "\n".join(lines)

if __name__ == "__main__":
    demo = [{
        "customer_id": "C001",
        "score": 46,
        "calibrated_score": 52,
        "opportunity_level": "高",
        "calibrated_level": "高",
        "opportunity_types": ["首卡获客"],
        "primary_channel": "App站内推荐",
        "reasons": ["借记卡活跃度较高。"],
        "benchmark_notes": ["客户活动响应高于行业均值。"],
    }]
    print(render(demo))
