"""渲染贷前风险扫描报告为 Markdown。"""

from __future__ import annotations

from typing import Dict, List


def render_markdown(report: Dict) -> str:
    def bullets(items: List[str]) -> str:
        return "\n".join(f"- {x}" for x in items) if items else "- 无"

    sections = [
        "# 贷前风险扫描报告",
        "",
        "## 一、任务说明",
        f"- 扫描对象：{report.get('scan_target', '未提供')}",
        f"- 申请场景：{report.get('application_context', '未提供')}",
        "",
        "## 二、风险信号总览",
        "### 高优先级风险",
        bullets(report.get("risk_overview", {}).get("high_priority", [])),
        "",
        "### 中优先级风险",
        bullets(report.get("risk_overview", {}).get("medium_priority", [])),
        "",
        "### 一般关注事项",
        bullets(report.get("risk_overview", {}).get("general_items", [])),
        "",
        "## 三、关键红旗清单",
        bullets(report.get("red_flags", [])),
        "",
        "## 四、待核验事项",
        bullets(report.get("pending_verifications", [])),
        "",
        "## 五、补充材料建议",
        bullets(report.get("required_documents", [])),
        "",
        "## 六、初步风险等级与处理建议",
        f"- 初步风险等级：{report.get('preliminary_risk_level', '暂无法判断')}",
        f"- 建议动作：{report.get('recommended_action', '未提供')}",
        "",
        "## 七、结论边界说明",
        bullets(report.get("boundary_notes", [])),
        "",
    ]
    return "\n".join(sections)


if __name__ == "__main__":
    demo = {
        "scan_target": "某企业客户",
        "application_context": "流动资金贷款",
        "risk_overview": {
            "high_priority": ["存在被执行记录", "存在多头借贷迹象"],
            "medium_priority": ["经营现金流偏弱"],
            "general_items": ["客户集中度较高"],
        },
        "red_flags": ["存在被执行记录，需重点关注司法与履约风险。"],
        "pending_verifications": ["补充近12个月银行流水", "核验主要合同真实性"],
        "required_documents": ["征信明细", "用途证明"],
        "preliminary_risk_level": "高风险",
        "recommended_action": "建议升级审查并完成补充核验后再决定是否推进。",
        "boundary_notes": ["当前未获取完整财务报表", "尚未完成现场走访"],
    }
    print(render_markdown(demo))
