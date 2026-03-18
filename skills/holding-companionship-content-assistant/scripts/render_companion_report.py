from __future__ import annotations

from typing import Any, Dict, List


def render_markdown_report(context: Dict[str, Any], content: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# 持仓陪伴内容建议报告")
    lines.append("")
    lines.append("## 一、客户情况概述")
    lines.append(f"- 客户分层：{context.get('customer_segment', '未提供')}")
    lines.append(f"- 风险承受能力：{context.get('risk_profile', '未提供')}")
    lines.append(f"- 投资期限偏好：{context.get('investment_horizon', '未提供')}")
    lines.append(f"- 流动性偏好：{context.get('liquidity_preference', '未提供')}")
    lines.append(f"- 沟通目标：{context.get('communication_goal', '未提供')}")
    lines.append(f"- 推荐渠道：{context.get('channel', '未提供')}")
    lines.append("")
    lines.append("## 二、持仓摘要")
    for h in context.get("holdings", []):
        lines.append(
            f"- {h.get('product_name')}｜{h.get('product_type')}｜金额 {h.get('amount')}｜占比 {h.get('weight')}｜盈亏 {h.get('profit_loss')}"
        )
    if not context.get("holdings"):
        lines.append("- 未提供持仓明细")
    lines.append("")
    lines.append("## 三、建议沟通主线")
    for m in content.get("key_messages", []):
        lines.append(f"- {m}")
    lines.append("")
    lines.append("## 四、推荐语气")
    lines.append(f"- {content.get('recommended_tone', '稳健')}")
    lines.append("")
    lines.append("## 五、建议动作")
    for a in content.get("action_suggestions", []):
        lines.append(f"- {a}")
    lines.append("")
    lines.append("## 六、建议输出内容")
    lines.append(content.get("channel_content", "未生成内容"))
    lines.append("")
    lines.append("## 七、风险提示")
    for r in content.get("risk_notice", []):
        lines.append(f"- {r}")
    lines.append("")
    lines.append("## 八、待补充信息")
    missing = content.get("missing_information", []) or context.get("missing_information", [])
    if missing:
        for item in missing:
            lines.append(f"- {item}")
    else:
        lines.append("- 暂无")
    lines.append("")
    return "\n".join(lines)
