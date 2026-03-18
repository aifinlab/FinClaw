import argparse
import json
from datetime import datetime
from pathlib import Path


def _safe_get(d, *keys, default=None):
    cur = d
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur


def load_input(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def detect_missing_fields(payload):
    missing = []
    if not _safe_get(payload, "client_profile", "risk_level"):
        missing.append("client_profile.risk_level")
    if not _safe_get(payload, "client_profile", "horizon"):
        missing.append("client_profile.horizon")
    if not _safe_get(payload, "holdings_summary", "products"):
        missing.append("holdings_summary.products")
    if not _safe_get(payload, "market_context", "event"):
        missing.append("market_context.event")
    if not _safe_get(payload, "touchpoint", "emotion_state"):
        missing.append("touchpoint.emotion_state")
    return missing


def build_talk_track(payload):
    client = payload.get("client_profile", {})
    holdings = payload.get("holdings_summary", {})
    market = payload.get("market_context", {})
    touchpoint = payload.get("touchpoint", {})

    name = client.get("name", "客户")
    risk_level = client.get("risk_level", "未提供")
    horizon = client.get("horizon", "未提供")
    liquidity = client.get("liquidity_need", "未提供")
    emotion = touchpoint.get("emotion_state", "未提供")

    event = market.get("event", "近期市场波动")
    drivers = market.get("drivers", [])
    drivers_text = "、".join(drivers) if drivers else "(待补充驱动因素)"

    products = holdings.get("products", [])
    product_lines = []
    for p in products:
        line = f"- {p.get('name','产品')}（{p.get('type','未知类型')}，风险{p.get('risk_level','未提供')}，占比{p.get('allocation_pct','未提供')}%）"
        product_lines.append(line)

    facts = []
    facts.append(f"事件：{event}")
    data_points = market.get("data_points", [])
    for dp in data_points:
        facts.append(dp)

    talk_track = {
        "opening": f"{name}您好，我理解您对近期波动的担心，我们先把关键事实看清楚。",
        "facts": facts,
        "explain": f"当前波动主要与{drivers_text}有关。您的组合整体风险等级为{risk_level}，期限偏好为{horizon}，流动性要求为{liquidity}。",
        "actions": [
            "先复盘持仓结构与波动来源",
            "如需调整，我们会在适当性范围内评估方案",
            "在情绪波动较大时，优先保证流动性边界"
        ],
        "follow_up": "我会在约定时间回访并补充可验证信息与复盘结果。",
        "products": product_lines,
        "emotion_state": emotion
    }
    return talk_track


def render_markdown(payload, talk_track, missing_fields):
    lines = []
    lines.append(f"# 波动安抚沟通包\n")
    lines.append(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

    lines.append("## 沟通主线")
    lines.append(f"- 开场共情：{talk_track['opening']}")
    lines.append("- 事实澄清：")
    for f in talk_track["facts"]:
        lines.append(f"  - {f}")
    lines.append(f"- 风险解释：{talk_track['explain']}")
    lines.append("- 行动建议：")
    for a in talk_track["actions"]:
        lines.append(f"  - {a}")
    lines.append(f"- 跟进承诺：{talk_track['follow_up']}")

    lines.append("\n## 持仓概览")
    if talk_track["products"]:
        lines.extend(talk_track["products"])
    else:
        lines.append("- (待补充持仓信息)")

    lines.append("\n## 禁用表述提醒")
    lines.append("- 不承诺收益，不暗示回本或抄底时点")
    lines.append("- 不用预测性、诱导性措辞替代事实")

    lines.append("\n## 常见追问建议回应")
    lines.append("- “还会跌吗？”→ 强调不预测短期，回到风险匹配与期限安排")
    lines.append("- “要不要现在卖？”→ 先复盘持仓结构与资金用途，再评估动作")
    lines.append("- “什么时候能回本？”→ 避免时间承诺，说明需要看市场与产品表现")

    if missing_fields:
        lines.append("\n## 待补充关键信息")
        for m in missing_fields:
            lines.append(f"- {m}")

    return "\n".join(lines) + "\n"


def build_output(payload):
    missing = detect_missing_fields(payload)
    talk_track = build_talk_track(payload)
    return {
        "talk_track": talk_track,
        "missing_fields": missing,
        "compliance_notes": [
            "不得承诺收益",
            "不得暗示抄底时点",
            "需明确风险与期限匹配"
        ]
    }


def main():
    parser = argparse.ArgumentParser(description="Generate volatility comfort communication pack")
    parser.add_argument("--input", required=True, help="Path to input JSON")
    parser.add_argument("--output", help="Path to output file")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    args = parser.parse_args()

    payload = load_input(Path(args.input))
    result = build_output(payload)

    if args.format == "json":
        content = json.dumps(result, ensure_ascii=False, indent=2)
    else:
        content = render_markdown(payload, result["talk_track"], result["missing_fields"])

    if args.output:
        Path(args.output).write_text(content, encoding="utf-8")
    else:
        print(content)


if __name__ == "__main__":
    main()
