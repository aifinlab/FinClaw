import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


RISK_MAP = {"保守": 1, "低": 1, "稳健": 2, "中低": 2, "平衡": 3, "中": 3, "中高": 4, "进取": 5, "高": 5}
LIQUIDITY_MAP = {"高": 3, "中": 2, "低": 1}


@dataclass
class OptionItem:
    option: str
    when_to_use: str
    key_message: str
    tradeoffs: str


def load_input(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def to_float(value: Any, default: float = 0.0) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError:
            return default
    return default


def to_int(value: Any, default: int = 0) -> int:
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        try:
            return int(float(value.strip()))
        except ValueError:
            return default
    return default


def normalize_risk(value: Any) -> int:
    if isinstance(value, (int, float)):
        return max(1, min(5, int(value)))
    if isinstance(value, str):
        return RISK_MAP.get(value.strip(), 3)
    return 3


def normalize_liquidity(value: Any) -> int:
    if isinstance(value, (int, float)):
        return max(1, min(3, int(value)))
    if isinstance(value, str):
        return LIQUIDITY_MAP.get(value.strip(), 2)
    return 2


def get_path(payload: Dict[str, Any], dotted: str) -> Any:
    cur: Any = payload
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def build_gaps(payload: Dict[str, Any]) -> List[str]:
    required = [
        ("client_profile.name", "缺少客户姓名或编号。"),
        ("client_profile.risk_level", "缺少客户风险等级。"),
        ("client_profile.investment_horizon_months", "缺少计划持有期限。"),
        ("client_profile.liquidity_need", "缺少流动性需求。"),
        ("redemption_request.reason", "缺少赎回原因说明。"),
        ("redemption_request.requested_amount", "缺少赎回金额。"),
        ("holdings", "缺少持仓明细，无法判断期限与风险匹配。"),
    ]
    gaps: List[str] = []
    for dotted, msg in required:
        value = get_path(payload, dotted)
        if value in (None, "", [], {}):
            gaps.append(msg)
    return gaps


def build_client_snapshot(payload: Dict[str, Any]) -> Dict[str, Any]:
    profile = payload.get("client_profile") or {}
    return {
        "name": profile.get("name") or profile.get("client_id") or "未命名客户",
        "age": profile.get("age"),
        "risk_level": profile.get("risk_level") or "待补充",
        "investment_horizon_months": profile.get("investment_horizon_months"),
        "liquidity_need": profile.get("liquidity_need"),
        "goals": profile.get("goals") or [],
        "communication_preference": profile.get("communication_preference"),
    }


def holding_risk_mismatch(payload: Dict[str, Any]) -> bool:
    profile = payload.get("client_profile") or {}
    client_risk = normalize_risk(profile.get("risk_level"))
    holdings = payload.get("holdings") or []
    for row in holdings:
        if not isinstance(row, dict):
            continue
        product_risk = normalize_risk(row.get("risk_level"))
        if product_risk > client_risk:
            return True
    return False


def build_redemption_drivers(payload: Dict[str, Any]) -> List[str]:
    drivers: List[str] = []
    request = payload.get("redemption_request") or {}
    reason = request.get("reason")
    if reason:
        drivers.append(f"客户主动说明的赎回原因：{reason}")
    urgency = request.get("urgency")
    if urgency:
        drivers.append(f"赎回紧急度：{urgency}")

    holdings = payload.get("holdings") or []
    for row in holdings:
        if not isinstance(row, dict):
            continue
        pnl = to_float(row.get("unrealized_return_pct"), 0.0)
        if pnl <= -3:
            drivers.append(f"持仓 {row.get('name') or '产品'} 浮亏 {pnl:.1f}% 可能触发情绪赎回。")
        lockup = to_int(row.get("lockup_months"))
        if lockup > 0:
            drivers.append(f"持仓 {row.get('name') or '产品'} 存在封闭期/期限限制。")
    if holding_risk_mismatch(payload):
        drivers.append("存在产品风险等级高于客户风险承受能力的情况。")
    return drivers


def build_risk_flags(payload: Dict[str, Any]) -> List[str]:
    flags = [
        "所有沟通需避免收益承诺与保本暗示。",
        "赎回涉及费用或期限限制时必须明确披露。",
    ]
    market = payload.get("market_context") or {}
    if market.get("volatility_level") == "高":
        flags.append("当前市场波动较高，需强调波动来源与持有期限。")
    if holding_risk_mismatch(payload):
        flags.append("适当性匹配存在风险，需要重新确认风险等级与产品匹配。")
    return flags


def build_options(payload: Dict[str, Any]) -> List[OptionItem]:
    options: List[OptionItem] = []
    options.append(
        OptionItem(
            option="部分赎回",
            when_to_use="存在现金需求但不希望完全退出",
            key_message="先满足必要资金需求，保留核心仓位，减少择时风险。",
            tradeoffs="现金到位较慢但可保留潜在收益。",
        )
    )
    options.append(
        OptionItem(
            option="分批赎回/观望复盘",
            when_to_use="情绪驱动较强或市场波动短期放大",
            key_message="分批处理降低一次性决策压力，设定复盘窗口。",
            tradeoffs="需要客户接受阶段性波动。",
        )
    )
    options.append(
        OptionItem(
            option="产品转换/降波动配置",
            when_to_use="客户风险偏好下降或流动性需求提高",
            key_message="在风险等级匹配前提下切换更稳健或更高流动性方案。",
            tradeoffs="可能降低预期收益区间。",
        )
    )
    return options


def build_communication_flow(payload: Dict[str, Any]) -> Dict[str, str]:
    return {
        "opening": "理解您当前对波动的担心，我先把事实和可选方案梳理清楚。",
        "facts": "目前持仓期限与净值波动情况如下，需结合资金用途判断最合适的节奏。",
        "boundaries": "以下为情景分析，不构成收益承诺，需在风险等级匹配后执行。",
        "options": "我们可以考虑部分赎回、分批赎回或转换为更高流动性配置。",
        "confirmation": "我整理确认清单，确认风险等级与期限后再落地方案。",
    }


def build_compliance_notes(payload: Dict[str, Any]) -> Dict[str, Any]:
    constraints = payload.get("compliance_constraints") or {}
    return {
        "must_disclose": constraints.get("must_disclose") or ["投资有风险，净值可能波动"],
        "forbidden_phrases": constraints.get("forbidden_phrases") or ["保本保收益", "一定赚钱"],
        "wording_tips": ["使用'情景分析'替代'预测'", "强调'风险等级匹配后执行'"] ,
    }


def build_follow_up(payload: Dict[str, Any], gaps: List[str]) -> List[str]:
    steps = [
        "确认风险等级、期限与流动性要求并留痕。",
        "复核赎回费用与产品条款，向客户说明。",
        "确认客户最终选择并设定复盘节点。",
    ]
    if gaps:
        steps.insert(0, "补齐关键信息后再确定最终方案。")
    return steps


def build_packet(payload: Dict[str, Any]) -> Dict[str, Any]:
    gaps = build_gaps(payload)
    client_snapshot = build_client_snapshot(payload)
    drivers = build_redemption_drivers(payload)
    options = build_options(payload)
    packet = {
        "summary": "已生成赎回挽留沟通主线与可选方案，请结合客户确认信息落地。",
        "gaps": gaps,
        "client_snapshot": client_snapshot,
        "redemption_drivers": drivers,
        "risk_flags": build_risk_flags(payload),
        "retention_options": [o.__dict__ for o in options],
        "communication_flow": build_communication_flow(payload),
        "compliance_notes": build_compliance_notes(payload),
        "follow_up_plan": build_follow_up(payload, gaps),
    }
    return packet


def render_markdown(packet: Dict[str, Any]) -> str:
    lines = ["# 赎回挽留动作包", "", "## 摘要", packet.get("summary", ""), ""]
    snapshot = packet.get("client_snapshot") or {}
    lines.append("## 客户画像")
    lines.extend(
        [
            f"- 客户: {snapshot.get('name')}",
            f"- 风险等级: {snapshot.get('risk_level')}",
            f"- 持有期限(月): {snapshot.get('investment_horizon_months') or '待补充'}",
            f"- 流动性需求: {snapshot.get('liquidity_need') or '待补充'}",
        ]
    )
    if snapshot.get("goals"):
        lines.append(f"- 目标: {'、'.join(snapshot.get('goals'))}")
    lines.append("")

    lines.append("## 赎回动因")
    drivers = packet.get("redemption_drivers") or []
    lines.extend([f"- {d}" for d in drivers] if drivers else ["- 暂无"]) 
    lines.append("")

    lines.append("## 沟通主线")
    flow = packet.get("communication_flow") or {}
    for key in ("opening", "facts", "boundaries", "options", "confirmation"):
        if flow.get(key):
            lines.append(f"- {flow[key]}")
    lines.append("")

    lines.append("## 挽留方案选项")
    for option in packet.get("retention_options") or []:
        lines.append(f"- {option.get('option')} | {option.get('key_message')} | {option.get('tradeoffs')}")
    lines.append("")

    lines.append("## 风险提示")
    for item in packet.get("risk_flags") or []:
        lines.append(f"- {item}")
    lines.append("")

    lines.append("## 合规提示")
    compliance = packet.get("compliance_notes") or {}
    must = compliance.get("must_disclose") or []
    forbid = compliance.get("forbidden_phrases") or []
    lines.append("- 必须披露：" + "；".join(must))
    lines.append("- 禁用表述：" + "；".join(forbid))
    lines.append("")

    lines.append("## 信息缺口")
    gaps = packet.get("gaps") or []
    lines.extend([f"- {g}" for g in gaps] if gaps else ["- 暂无"]) 
    lines.append("")

    lines.append("## 跟进动作")
    for step in packet.get("follow_up_plan") or []:
        lines.append(f"- {step}")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Wealth redemption retention assistant")
    parser.add_argument("input", type=str, help="Path to input JSON")
    parser.add_argument("--output", type=str, default="markdown", choices=["markdown", "json"])
    args = parser.parse_args()

    payload = load_input(Path(args.input))
    packet = build_packet(payload)

    if args.output == "json" or (payload.get("output") or {}).get("format") == "json":
        print(json.dumps(packet, ensure_ascii=False, indent=2))
    else:
        print(render_markdown(packet))


if __name__ == "__main__":
    main()
