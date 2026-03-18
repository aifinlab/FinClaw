from __future__ import annotations

from typing import Any, Dict, List


def generate_companion_content(context: Dict[str, Any]) -> Dict[str, Any]:
    holdings = context.get("holdings", [])
    channel = context.get("channel", "微信")
    goal = context.get("communication_goal", "持仓陪伴")
    market_summary = context.get("market_summary", "")

    concentration_flag = any(h.get("weight", 0) >= 0.5 for h in holdings)
    equity_flag = any("权益" in str(h.get("product_type", "")) for h in holdings)

    key_messages: List[str] = []
    if market_summary:
        key_messages.append(f"近期变化与市场环境有关：{market_summary}")
    if concentration_flag:
        key_messages.append("当前持仓存在一定集中度，需要同时关注单一资产波动对整体体验的影响。")
    if equity_flag:
        key_messages.append("权益类资产短期波动通常更明显，应结合持有期限与配置角色综合看待。")
    if not key_messages:
        key_messages.append("建议先从客户持仓结构、产品定位和近期波动来源三个角度进行解释。")

    action_suggestions = [
        "先帮助客户理解波动来源与产品定位，避免直接围绕短期收益展开争论。",
        "结合客户流动性需求与风险承受能力，判断是否需要做再平衡沟通。",
        "约定后续跟进时间，形成持续陪伴，而不是一次性触达后结束。",
    ]

    tone = "稳健、共情、解释型"
    if goal and ("安抚" in goal or "稳定" in goal):
        tone = "稳健、安抚、解释型"

    content = _render_channel_content(channel, key_messages, goal)

    return {
        "recommended_tone": tone,
        "key_messages": key_messages,
        "action_suggestions": action_suggestions,
        "channel_content": content,
        "risk_notice": [
            "沟通中不得承诺收益或保证回本。",
            "如客户风险承受能力与持仓风险不匹配，应优先提示适当性关注。",
        ],
        "missing_information": context.get("missing_information", []),
    }


def _render_channel_content(channel: str, key_messages: List[str], goal: str) -> str:
    head = f"本次沟通目标：{goal}。"
    if channel == "电话":
        return "\n".join([
            head,
            "建议先确认客户当前最关注的问题，再依次解释市场变化、持仓定位和后续观察点。",
            *[f"- {m}" for m in key_messages],
            "最后给出后续跟进安排与观察建议。",
        ])
    if channel == "短信":
        short_msg = key_messages[0] if key_messages else "近期市场存在波动，建议从持仓结构和产品定位综合看待。"
        return f"{head}{short_msg} 如您方便，我们可进一步为您梳理当前持仓关注点。"
    return "\n".join([
        head,
        *key_messages,
        "如果您愿意，我可以进一步结合您当前持仓，帮您梳理接下来更值得关注的几个点。",
    ])
