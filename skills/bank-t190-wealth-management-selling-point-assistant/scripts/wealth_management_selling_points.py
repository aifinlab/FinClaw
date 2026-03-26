from pathlib import Path
from typing import Any, Dict, List, Tuple
import json


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
        ("client_profile.risk_level", "缺少客户风险等级/风险偏好。"),
        ("client_profile.investment_horizon_months", "缺少投资期限或持有周期。"),
        ("client_profile.liquidity_need", "缺少流动性需求说明。"),
        ("client_profile.goals", "缺少客户目标或资金用途。"),
        ("product.name", "缺少产品名称。"),
        ("product.risk_level", "缺少产品风险等级。"),
        ("product.term_months", "缺少产品期限。"),
        ("product.liquidity", "缺少产品流动性说明。"),
        ("product.key_risks", "缺少产品关键风险。"),
    ]
    gaps: List[str] = []
    for dotted, msg in required:
        value = get_path(payload, dotted)
        if value in (None, "", [], {}):
            gaps.append(msg)
    return gaps


def build_profile_snapshot(payload: Dict[str, Any]) -> Dict[str, Any]:
    profile = payload.get("client_profile") or {}
    return {
        "name": profile.get("name") or "未命名客户",
        "risk_level": profile.get("risk_level") or "待补充",
        "investment_horizon_months": profile.get("investment_horizon_months"),
        "liquidity_need": profile.get("liquidity_need"),
        "goals": profile.get("goals") or [],
        "constraints": profile.get("constraints") or [],
        "experience_level": profile.get("experience_level"),
        "communication_preference": profile.get("communication_preference"),
    }


def suitability_check(payload: Dict[str, Any]) -> Tuple[str, List[str]]:
    profile = payload.get("client_profile") or {}
    product = payload.get("product") or {}
    reasons: List[str] = []

    client_risk = normalize_risk(profile.get("risk_level"))
    product_risk = normalize_risk(product.get("risk_level"))
    if product_risk > client_risk:
        reasons.append("产品风险等级高于客户风险承受能力。")

    horizon = to_int(profile.get("investment_horizon_months"))
    term = to_int(product.get("term_months"))
    if horizon and term and horizon < term:
        reasons.append("产品期限与客户持有周期不匹配。")

    liquidity_need = normalize_liquidity(profile.get("liquidity_need"))
    liquidity_text = str(product.get("liquidity") or "")
    if liquidity_need >= 3 and ("封闭" in liquidity_text or "不可赎回" in liquidity_text):
        reasons.append("客户流动性需求较高，产品流动性限制较强。")

    if reasons:
        if len(reasons) >= 2:
            return "不适配", reasons
        return "需谨慎", reasons
    return "适配", ["风险等级、期限与流动性要求基本匹配。"]


def build_selling_points(payload: Dict[str, Any]) -> List[Dict[str, str]]:
    product = payload.get("product") or {}
    profile = payload.get("client_profile") or {}
    points: List[Dict[str, str]] = []

    highlights = product.get("selling_highlights") or []
    if isinstance(highlights, str):
        highlights = [highlights]

    def add_point(point: str, evidence: str, suitable_for: str, boundary: str) -> None:
        points.append(
            {
                "point": point,
                "evidence": evidence,
                "suitable_for": suitable_for,
                "boundary": boundary,
            }
        )

    if highlights:
        for item in highlights:
            add_point(
                f"{item}，强调与客户目标匹配的价值点。",
                "产品说明书/产品亮点披露。",
                "风险等级匹配且具备相应期限承受能力的客户。",
                "需确认客户已理解风险与期限限制。",
            )

    strategy = product.get("strategy")
    if strategy:
        add_point(
            f"策略结构：{strategy}，可作为稳健配置的核心或补充。",
            "策略说明与投资范围披露。",
            "追求稳健增值、接受适度波动的客户。",
            "需披露策略的适用市场环境与潜在波动。",
        )

    performance = product.get("performance_features")
    if performance:
        add_point(
            f"历史表现特征：{performance}，用于解释波动管理。",
            "历史净值数据与回撤指标（仅作说明，不构成承诺）。",
            "关注回撤控制与波动管理的客户。",
            "历史表现不代表未来收益，需提示波动风险。",
        )

    if product.get("liquidity"):
        add_point(
            f"流动性安排：{product.get('liquidity')}，可匹配客户现金流节奏。",
            "产品条款与开放期说明。",
            "具备中长期配置需求的客户。",
            "需确认客户资金用途与期限匹配。",
        )

    if product.get("expected_return_range"):
        add_point(
            f"收益结构说明：{product.get('expected_return_range')} 为区间参考，强调收益来源。",
            "产品收益说明与风险揭示。",
            "关注收益区间但能接受波动的客户。",
            "不可使用承诺性表述，需同步风险披露。",
        )

    if not points:
        goals = ",".join(profile.get("goals") or []) or "客户目标"
        add_point(
            f"围绕{goals}提供适配方案，强调稳健与风险平衡。",
            "基于客户目标描述与适当性信息。",
            "风险等级匹配且期限匹配的客户。",
            "需补充产品亮点与条款证据。",
        )

    return points[:6]


def build_objection_handling(objections: List[str]) -> List[Dict[str, str]]:
    responses: List[Dict[str, str]] = []
    for obj in objections:
        if "波动" in obj or "亏" in obj:
            responses.append(
                {
                    "objection": obj,
                    "response": "强调产品风险等级与波动区间，说明回撤控制机制与配置目的。",
                    "risk_note": "提醒历史表现不代表未来收益。",
                }
            )
        elif "封闭" in obj or "流动性" in obj:
            responses.append(
                {
                    "objection": obj,
                    "response": "解释封闭期安排与现金流匹配逻辑，必要时提供流动性更强的备选。",
                    "risk_note": "确认客户资金用途与可承受期限。",
                }
            )
        elif "收益" in obj:
            responses.append(
                {
                    "objection": obj,
                    "response": "说明收益为区间参考，重点解释收益来源与风险承担。",
                    "risk_note": "不得承诺收益。",
                }
            )
        else:
            responses.append(
                {
                    "objection": obj,
                    "response": "先确认客户疑虑点，再补充条款证据与风险提示。",
                    "risk_note": "必要时升级合规审核。",
                }
            )
    return responses


def build_comparison(payload: Dict[str, Any]) -> Dict[str, Any]:
    product = payload.get("product") or {}
    pool = payload.get("product_pool") or []
    profile = payload.get("client_profile") or {}
    client_risk = normalize_risk(profile.get("risk_level"))
    horizon = to_int(profile.get("investment_horizon_months"))

    alternatives: List[str] = []
    not_recommended: List[str] = []
    for item in pool:
        if not isinstance(item, dict):
            continue
        name = item.get("name") or "未命名产品"
        item_risk = normalize_risk(item.get("risk_level"))
        item_term = to_int(item.get("term_months"))
        if item_risk <= client_risk and (not horizon or horizon >= item_term):
            alternatives.append(name)
        else:
            not_recommended.append(name)

    return {
        "primary": f"{product.get('name') or '主推荐产品'}：聚焦核心卖点与适配理由。",
        "alternatives": alternatives[:3],
        "not_recommended": not_recommended[:3],
    }


def build_risk_disclosures(payload: Dict[str, Any]) -> List[str]:
    product = payload.get("product") or {}
    risks = product.get("key_risks") or []
    if isinstance(risks, str):
        risks = [risks]
    disclosures = ["产品风险等级需与客户风险承受能力匹配。"]
    disclosures.extend([str(r) for r in risks][:5])
    disclosures.append("历史表现仅供参考，不代表未来收益。")
    return disclosures


def build_talking_points(payload: Dict[str, Any]) -> List[str]:
    product = payload.get("product") or {}
    market = payload.get("market_view") or {}
    points = [
        "先确认客户目标与风险边界，再解释产品价值点。",
        f"强调产品策略与资产类别：{product.get('asset_class') or '未标注'}。",
    ]
    if market.get("trend_summary"):
        points.append(f"结合市场趋势：{market.get('trend_summary')}。")
    points.append("说明卖点与风险提示并重，避免收益承诺。")
    return points


def build_follow_up(gaps: List[str]) -> List[str]:
    steps = []
    if gaps:
        steps.append("补齐关键资料后再锁定最终话术与方案。")
    steps.extend([
        "确认客户风险等级、期限与流动性匹配。",
        "发送卖点简报与风险提示材料并留痕。",
        "安排二次沟通或复访时间。",
    ])
    return steps


def build_pending_confirmations(payload: Dict[str, Any]) -> List[str]:
    profile = payload.get("client_profile") or {}
    product = payload.get("product") or {}
    return [
        f"客户风险等级：{profile.get('risk_level') or '待确认'}",
        f"投资期限（月）：{profile.get('investment_horizon_months') or '待确认'}",
        f"流动性需求：{profile.get('liquidity_need') or '待确认'}",
        f"产品期限：{product.get('term_months') or '待确认'}",
        "已提示主要风险并确认客户理解。",
    ]


def build_packet(payload: Dict[str, Any]) -> Dict[str, Any]:
    gaps = build_gaps(payload)
    status, rationale = suitability_check(payload)
    objections = payload.get("selling_context", {}).get("objections") or []
    if isinstance(objections, str):
        objections = [objections]

    packet: Dict[str, Any] = {
        "summary": "已生成卖点与沟通要点，可用于客户沟通与合规留痕。",
        "profile_snapshot": build_profile_snapshot(payload),
        "selling_points": build_selling_points(payload),
        "suitability_result": {"status": status, "rationale": rationale, "gaps": gaps},
        "risk_disclosures": build_risk_disclosures(payload),
        "objection_handling": build_objection_handling(objections),
        "talking_points": build_talking_points(payload),
        "comparison_options": build_comparison(payload),
        "follow_up_actions": build_follow_up(gaps),
        "pending_confirmations": build_pending_confirmations(payload),
    }
    return packet


def render_markdown(packet: Dict[str, Any]) -> str:
    lines = ["# 产品卖点沟通包", "", "## 摘要", packet.get("summary") or "", ""]
    profile = packet.get("profile_snapshot") or {}
    lines.extend([
        "## 客户画像摘要",
        f"- 客户: {profile.get('name')}",
        f"- 风险等级: {profile.get('risk_level')}",
        f"- 投资期限(月): {profile.get('investment_horizon_months') or '待补充'}",
        f"- 流动性需求: {profile.get('liquidity_need') or '待补充'}",
        "",
    ])

    lines.append("## 卖点清单")
    for item in packet.get("selling_points") or []:
        lines.append(f"- {item.get('point')}")
        lines.append(f"  - 证据: {item.get('evidence')}")
        lines.append(f"  - 适配: {item.get('suitable_for')}")
        lines.append(f"  - 边界: {item.get('boundary')}")
    if not packet.get("selling_points"):
        lines.append("- 暂无")
    lines.append("")

    suitability = packet.get("suitability_result") or {}
    lines.append("## 适配结论")
    lines.append(f"- 状态: {suitability.get('status')}")
    for reason in suitability.get("rationale") or []:
        lines.append(f"- 理由: {reason}")
    for gap in suitability.get("gaps") or []:
        lines.append(f"- 信息缺口: {gap}")
    lines.append("")

    lines.append("## 风险提示")
    for note in packet.get("risk_disclosures") or []:
        lines.append(f"- {note}")
    lines.append("")

    lines.append("## 异议处理")
    for item in packet.get("objection_handling") or []:
        lines.append(f"- 异议: {item.get('objection')}")
        lines.append(f"  - 回应: {item.get('response')}")
        if item.get("risk_note"):
            lines.append(f"  - 风险提示: {item.get('risk_note')}")
    if not packet.get("objection_handling"):
        lines.append("- 暂无")
    lines.append("")

    lines.append("## 沟通要点")
    for point in packet.get("talking_points") or []:
        lines.append(f"- {point}")
    lines.append("")

    compare = packet.get("comparison_options") or {}
    lines.append("## 方案对比")
    lines.append(f"- 主方案: {compare.get('primary')}")
    lines.append(f"- 备选方案: {', '.join(compare.get('alternatives') or ['暂无'])}")
    lines.append(f"- 不建议方案: {', '.join(compare.get('not_recommended') or ['暂无'])}")
    lines.append("")

    lines.append("## 下一步动作")
    for step in packet.get("follow_up_actions") or []:
        lines.append(f"- {step}")
    lines.append("")

    lines.append("## 待确认清单")
    for item in packet.get("pending_confirmations") or []:
        lines.append(f"- {item}")
    lines.append("")

    return "\n".join(lines)
