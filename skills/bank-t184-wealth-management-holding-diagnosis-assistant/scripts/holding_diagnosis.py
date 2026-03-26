from pathlib import Path
from typing import Any, Dict, List, Tuple
import json


def validate_input(data: dict) -> dict:
    """验证输入参数"""
    if not isinstance(data, dict):
        raise ValueError("输入必须是字典类型")

    required_fields = []  # 添加必填字段
    for field in required_fields:
        if field not in data:
            raise ValueError(f"缺少必填字段: {field}")

    return data




RISK_MAP = {
    "保守": 1,
    "低": 1,
    "稳健": 2,
    "中低": 2,
    "平衡": 3,
    "中": 3,
    "中高": 4,
    "进取": 5,
    "高": 5,
}

LIQUIDITY_MAP = {"高": 3, "中": 2, "低": 1}


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


def build_gaps(payload: Dict[str, Any]) -> List[str]:
    gaps: List[str] = []
    profile = payload.get("client_profile") or {}
    if not profile.get("risk_level"):
        gaps.append("缺少客户风险等级/风险偏好。")
    if not profile.get("investment_horizon_months"):
        gaps.append("缺少投资期限或持有周期。")
    if not profile.get("liquidity_need"):
        gaps.append("缺少流动性需求说明。")
    holdings = payload.get("holdings")
    if not isinstance(holdings, list) or not holdings:
        gaps.append("缺少持仓明细，无法做结构与集中度诊断。")
    return gaps


def build_allocation(holdings: List[Dict[str, Any]]) -> Dict[str, int]:
    totals: Dict[str, float] = {}
    total_value = 0.0
    for row in holdings:
        asset_class = str(row.get("asset_class") or "未标注")
        value = to_float(row.get("market_value"))
        if value <= 0:
            continue
        totals[asset_class] = totals.get(asset_class, 0.0) + value
        total_value += value
    if total_value <= 0:
        return {}
    allocation: Dict[str, int] = {}
    for asset, value in totals.items():
        allocation[asset] = int(round(value / total_value * 100))
    return allocation


def build_top_holdings(holdings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    total_value = sum(to_float(h.get("market_value")) for h in holdings)
    if total_value <= 0:
        return []
    rows = []
    for h in holdings:
        value = to_float(h.get("market_value"))
        if value <= 0:
            continue
        rows.append(
            {
                "asset_name": h.get("asset_name") or "未命名资产",
                "issuer": h.get("issuer"),
                "weight": round(value / total_value * 100, 1),
            }
        )
    rows.sort(key=lambda x: x["weight"], reverse=True)
    return rows[:6]


def build_concentration_risks(
    holdings: List[Dict[str, Any]], constraints: Dict[str, Any]
) -> List[str]:
    risks: List[str] = []
    total_value = sum(to_float(h.get("market_value")) for h in holdings)
    if total_value <= 0:
        return risks
    max_single_product = to_float(constraints.get("max_single_product_pct"))
    max_single_issuer = to_float(constraints.get("max_single_issuer_pct"))

    issuer_totals: Dict[str, float] = {}
    for h in holdings:
        value = to_float(h.get("market_value"))
        if value <= 0:
            continue
        name = h.get("asset_name") or "未命名产品"
        weight = value / total_value * 100
        if max_single_product and weight > max_single_product:
            risks.append(f"单一产品 {name} 占比 {weight:.1f}%，超过阈值 {max_single_product}%。")
        issuer = h.get("issuer")
        if issuer:
            issuer_totals[issuer] = issuer_totals.get(issuer, 0.0) + value

    if max_single_issuer:
        for issuer, value in issuer_totals.items():
            weight = value / total_value * 100
            if weight > max_single_issuer:
                risks.append(f"发行人 {issuer} 占比 {weight:.1f}%，超过阈值 {max_single_issuer}%。")
    return risks


def build_performance_drivers(holdings: List[Dict[str, Any]]) -> List[str]:
    drivers: List[str] = []
    total_value = sum(to_float(h.get("market_value")) for h in holdings)
    if total_value <= 0:
        return drivers

    contributions: List[Tuple[str, float]] = []
    for h in holdings:
        ret = to_float(h.get("return_12m"))
        value = to_float(h.get("market_value"))
        if value <= 0:
            continue
        contributions.append((h.get("asset_name") or "未命名资产", ret * value))

    if contributions:
        contributions.sort(key=lambda x: x[1], reverse=True)
        top = contributions[:2]
        bottom = contributions[-2:]
        for name, contrib in top:
            drivers.append(f"主要贡献来自 {name}（贡献值约 {contrib:.1f}）。")
        for name, contrib in bottom:
            drivers.append(f"主要拖累来自 {name}（贡献值约 {contrib:.1f}）。")
    else:
        drivers.append("缺少区间收益数据，无法做定量归因。")
    return drivers


def build_mismatch_points(payload: Dict[str, Any]) -> List[str]:
    points: List[str] = []
    profile = payload.get("client_profile") or {}
    client_risk = normalize_risk(profile.get("risk_level"))
    client_liquidity = normalize_liquidity(profile.get("liquidity_need"))
    holdings = payload.get("holdings") or []
    for h in holdings:
        product_risk = normalize_risk(h.get("risk_level"))
        if product_risk > client_risk:
            points.append("存在风险等级高于客户承受能力的产品，需要复核适当性。")
            break
    for h in holdings:
        liquidity = normalize_liquidity(h.get("liquidity"))
        if liquidity < client_liquidity:
            points.append("部分持仓流动性低于客户需求，需要确认可接受持有期。")
            break
    return points


def build_actions(payload: Dict[str, Any], gaps: List[str], risks: List[str]) -> List[str]:
    actions: List[str] = []
    if gaps:
        actions.append("优先补齐关键信息后再锁定结论。")
    if risks:
        actions.append("对集中度超阈值的持仓制定分散或替换方案。")
    actions.append("准备客户沟通话术，解释收益来源与风险边界。")
    actions.append("设置复盘节点，跟踪调整后的表现与风险变化。")
    return actions


def build_communication_points(payload: Dict[str, Any]) -> List[str]:
    return [
        "先确认客户当前目标与风险边界，再解释诊断逻辑。",
        "强调收益来源与限制条件，避免收益承诺。",
        "说明调整路径与触发条件，避免一次性大幅变动。",
    ]


def build_packet(payload: Dict[str, Any]) -> Dict[str, Any]:
    holdings = payload.get("holdings") or []
    gaps = build_gaps(payload)
    allocation = build_allocation(holdings)
    top_holdings = build_top_holdings(holdings)
    constraints = payload.get("constraints") or {}
    risks = build_concentration_risks(holdings, constraints)
    drivers = build_performance_drivers(holdings)
    mismatch = build_mismatch_points(payload)

    profile = payload.get("client_profile") or {}
    packet = {
        "summary": "已完成持仓结构、集中度与绩效驱动初步诊断。",
        "profile_snapshot": {
            "client": profile.get("name") or "未命名客户",
            "risk_level": profile.get("risk_level") or "待补充",
            "investment_horizon_months": profile.get("investment_horizon_months"),
            "liquidity_need": profile.get("liquidity_need"),
        },
        "allocation_snapshot": {
            "by_asset_class": allocation,
            "top_holdings": top_holdings,
        },
        "concentration_risks": risks,
        "performance_drivers": drivers,
        "mismatch_points": mismatch,
        "actions": build_actions(payload, gaps, risks),
        "communication_points": build_communication_points(payload),
        "data_gaps": gaps,
        "compliance_notes": [
            "诊断仅基于当前披露信息，不构成收益承诺或投资建议。",
            "如涉及估值或外部材料需标注来源并复核。",
        ],
    }
    return packet


def render_markdown(packet: Dict[str, Any]) -> str:
    lines = [
        "# 客户持仓诊断简报",
        "",
        "## 客户画像摘要",
        f"- 客户: {packet['profile_snapshot'].get('client')}",
        f"- 风险等级: {packet['profile_snapshot'].get('risk_level')}",
        f"- 投资期限(月): {packet['profile_snapshot'].get('investment_horizon_months') or '待补充'}",
        f"- 流动性需求: {packet['profile_snapshot'].get('liquidity_need') or '待补充'}",
        "",
        "## 诊断摘要",
        packet.get("summary") or "",
        "",
        "## 结构与集中度",
    ]
    allocation = packet.get("allocation_snapshot", {}).get("by_asset_class") or {}
    if allocation:
        for asset, pct in allocation.items():
            lines.append(f"- {asset}: {pct}%")
    else:
        lines.append("- 暂无结构数据")
    top_holdings = packet.get("allocation_snapshot", {}).get("top_holdings") or []
    if top_holdings:
        lines.append("- Top持仓:")
        for row in top_holdings:
            lines.append(f"  - {row.get('asset_name')} {row.get('weight')}%")
    lines.append("")

    for key, title in (
        ("concentration_risks", "集中度风险"),
        ("performance_drivers", "绩效驱动"),
        ("mismatch_points", "匹配度偏差"),
        ("actions", "行动建议"),
        ("communication_points", "沟通要点"),
        ("data_gaps", "信息缺口"),
        ("compliance_notes", "合规提示"),
    ):
        lines.append(f"## {title}")
        items = packet.get(key) or []
        if items:
            lines.extend([f"- {x}" for x in items])
        else:
            lines.append("- 暂无")
        lines.append("")
    return "\n".join(lines)
