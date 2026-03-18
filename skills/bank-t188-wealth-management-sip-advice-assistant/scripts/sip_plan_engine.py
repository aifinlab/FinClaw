import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple


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

VOLATILITY_MAP = {"低": 1, "中": 2, "高": 3}

ASSET_CLASS_TARGETS = {
    "conservative": {"fixed_income": 70, "equity": 20, "cash": 10},
    "balanced": {"fixed_income": 40, "equity": 45, "cash": 15},
    "aggressive": {"fixed_income": 20, "equity": 70, "cash": 10},
}

ASSET_CLASS_ALIAS = {
    "权益": "equity",
    "股票": "equity",
    "混合": "equity",
    "固收": "fixed_income",
    "债券": "fixed_income",
    "货币": "cash",
    "现金": "cash",
}


@dataclass
class ScoreResult:
    product_id: str
    name: str
    asset_class: str
    risk_level: Any
    min_holding_months: Any
    fee_rate: Any
    volatility_level: Any
    status: str
    score: float
    reasons: List[str]


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


def normalize_volatility(value: Any) -> int:
    if isinstance(value, (int, float)):
        return max(1, min(3, int(value)))
    if isinstance(value, str):
        return VOLATILITY_MAP.get(value.strip(), 2)
    return 2


def normalize_asset_class(value: Any) -> str:
    if not value:
        return "unknown"
    raw = str(value).strip()
    return ASSET_CLASS_ALIAS.get(raw, raw.lower())


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
        ("product_pool", "缺少可选产品池，无法做定投产品匹配。"),
    ]
    gaps: List[str] = []
    for dotted, msg in required:
        value = get_path(payload, dotted)
        if value in (None, "", [], {}):
            gaps.append(msg)

    sip_plan = payload.get("sip_plan") or {}
    if not sip_plan.get("monthly_amount") and not sip_plan.get("target_amount"):
        gaps.append("缺少定投月度金额或目标金额，无法校验可行性。")
    if not sip_plan.get("duration_months"):
        gaps.append("缺少定投期限（月），无法推导目标匹配。")
    return gaps


def evaluate_product(client: Dict[str, Any], product: Dict[str, Any]) -> ScoreResult:
    client_risk = normalize_risk(client.get("risk_level"))
    horizon = to_int(client.get("investment_horizon_months"))
    drawdown_tolerance = normalize_volatility(client.get("max_drawdown_tolerance"))

    product_risk = normalize_risk(product.get("risk_level"))
    product_vol = normalize_volatility(product.get("volatility_level"))
    min_months = to_int(product.get("min_holding_months"))

    reasons: List[str] = []
    risk_ok = product_risk <= client_risk
    if not risk_ok:
        reasons.append("产品风险等级高于客户风险承受能力。")
    horizon_ok = horizon == 0 or horizon >= min_months
    if not horizon_ok:
        reasons.append("产品最低持有期高于客户可接受期限。")
    vol_ok = product_vol <= drawdown_tolerance
    if not vol_ok:
        reasons.append("产品波动水平高于客户可承受回撤。")

    fee_rate = to_float(product.get("fee_rate"))
    fee_score = 10 if fee_rate == 0 else max(0, 10 - fee_rate * 2)

    goal_tags = set(client.get("goals") or [])
    product_tags = set(product.get("tags") or [])
    tag_score = 6 if goal_tags.intersection(product_tags) else 0

    score = 40.0
    score += 20 if risk_ok else 0
    score += 15 if horizon_ok else 0
    score += 10 if vol_ok else 0
    score += fee_score
    score += tag_score

    status = "适配"
    if not risk_ok or not horizon_ok:
        status = "不适配"
    elif not vol_ok:
        status = "需谨慎"

    return ScoreResult(
        product_id=product.get("product_id") or "unknown",
        name=product.get("name") or "未命名产品",
        asset_class=normalize_asset_class(product.get("asset_class")),
        risk_level=product.get("risk_level"),
        min_holding_months=product.get("min_holding_months"),
        fee_rate=product.get("fee_rate"),
        volatility_level=product.get("volatility_level"),
        status=status,
        score=round(score, 1),
        reasons=reasons,
    )


def build_shortlist(payload: Dict[str, Any]) -> Tuple[List[ScoreResult], List[ScoreResult]]:
    pool = payload.get("product_pool")
    if not isinstance(pool, list):
        return [], []
    client = payload.get("client_profile") or {}
    evaluated = [evaluate_product(client, p) for p in pool if isinstance(p, dict)]
    evaluated.sort(key=lambda x: x.score, reverse=True)
    suitable = [p for p in evaluated if p.status in ("适配", "需谨慎")]
    not_suitable = [p for p in evaluated if p.status == "不适配"]
    return suitable, not_suitable


def choose_allocation_bucket(risk_level: int) -> str:
    if risk_level <= 2:
        return "conservative"
    if risk_level == 3:
        return "balanced"
    return "aggressive"


def build_sip_structure(payload: Dict[str, Any]) -> Dict[str, Any]:
    sip_plan = payload.get("sip_plan") or {}
    duration = to_int(sip_plan.get("duration_months"))
    monthly_amount = to_float(sip_plan.get("monthly_amount"))
    target_amount = to_float(sip_plan.get("target_amount"))

    derived_monthly = monthly_amount
    if monthly_amount == 0 and target_amount > 0 and duration > 0:
        derived_monthly = round(target_amount / duration, 2)

    frequency = sip_plan.get("frequency") or "每月"
    start_date = sip_plan.get("start_date")

    return {
        "monthly_amount": derived_monthly if derived_monthly else None,
        "duration_months": duration or None,
        "target_amount": target_amount or None,
        "frequency": frequency,
        "start_date": start_date,
        "step_up_suggestion": "建议每12个月根据收入提升10%-15%逐步加码" if derived_monthly else "待确认",
    }


def group_by_asset_class(items: Iterable[ScoreResult]) -> Dict[str, List[ScoreResult]]:
    grouped: Dict[str, List[ScoreResult]] = {}
    for item in items:
        grouped.setdefault(item.asset_class, []).append(item)
    return grouped


def build_plan_options(payload: Dict[str, Any], shortlist: List[ScoreResult]) -> Dict[str, Any]:
    client = payload.get("client_profile") or {}
    risk_level = normalize_risk(client.get("risk_level"))
    bucket = choose_allocation_bucket(risk_level)
    target = ASSET_CLASS_TARGETS[bucket]

    grouped = group_by_asset_class(shortlist)
    primary: List[Dict[str, Any]] = []
    backup: List[Dict[str, Any]] = []

    for asset_class, weight in target.items():
        candidates = grouped.get(asset_class) or []
        if not candidates:
            continue
        primary.append({
            "asset_class": asset_class,
            "weight": weight,
            "product": candidates[0].name,
            "score": candidates[0].score,
        })
        if len(candidates) > 1:
            backup.append({
                "asset_class": asset_class,
                "weight": weight,
                "product": candidates[1].name,
                "score": candidates[1].score,
            })

    return {
        "risk_bucket": bucket,
        "target_allocation": target,
        "primary_plan": primary,
        "backup_plan": backup,
    }


def build_packet(payload: Dict[str, Any]) -> Dict[str, Any]:
    gaps = build_gaps(payload)
    client = payload.get("client_profile") or {}

    sip_structure = build_sip_structure(payload)
    suitable, not_suitable = build_shortlist(payload)
    plan_options = build_plan_options(payload, suitable)

    communication_points = [
        "先确认客户目标与风险边界，再解释定投逻辑。",
        "说明主方案与备选方案的取舍理由与触发条件。",
        "强调定投是长期纪律安排，短期波动不代表策略失效。",
    ]

    risk_notes = [
        "定投建议仅基于当前披露信息，不构成收益承诺或投资建议。",
        "产品风险等级必须不高于客户风险承受能力。",
        "定投频率与金额需与客户现金流和流动性要求一致。",
    ]

    packet = {
        "title": "定投建议输出",
        "profile_snapshot": {
            "name": client.get("name") or "未命名客户",
            "risk_level": client.get("risk_level") or "待补充",
            "investment_horizon_months": client.get("investment_horizon_months") or "待补充",
            "liquidity_need": client.get("liquidity_need") or "待补充",
            "goals": client.get("goals") or [],
            "max_drawdown_tolerance": client.get("max_drawdown_tolerance") or "待补充",
        },
        "sip_structure": sip_structure,
        "plan_options": plan_options,
        "suitable_products": [vars(x) for x in suitable[:8]],
        "not_suitable_products": [vars(x) for x in not_suitable[:6]],
        "gaps": gaps,
        "communication_points": communication_points,
        "risk_notes": risk_notes,
        "follow_up": [
            "补齐关键信息后锁定最终方案。",
            "形成客户确认清单（风险等级、期限、流动性、目标）。",
            "设置季度复盘点，关注目标达成度与策略调整。",
        ],
    }
    return packet


def render_markdown(packet: Dict[str, Any]) -> str:
    lines = [
        f"# {packet['title']}",
        "",
        "## 客户画像摘要",
    ]
    profile = packet.get("profile_snapshot") or {}
    lines.extend(
        [
            f"- 客户: {profile.get('name')}",
            f"- 风险等级: {profile.get('risk_level')}",
            f"- 投资期限(月): {profile.get('investment_horizon_months')}",
            f"- 流动性需求: {profile.get('liquidity_need')}",
            f"- 目标: {', '.join(profile.get('goals') or []) or '待补充'}",
            f"- 可承受回撤: {profile.get('max_drawdown_tolerance')}",
        ]
    )
    lines.append("")

    lines.append("## 定投结构建议")
    sip = packet.get("sip_structure") or {}
    lines.extend(
        [
            f"- 月度金额: {sip.get('monthly_amount') or '待确认'}",
            f"- 定投期限(月): {sip.get('duration_months') or '待确认'}",
            f"- 目标金额: {sip.get('target_amount') or '待确认'}",
            f"- 频率: {sip.get('frequency') or '待确认'}",
            f"- 起投时间: {sip.get('start_date') or '待确认'}",
            f"- 加码建议: {sip.get('step_up_suggestion')}",
        ]
    )
    lines.append("")

    plan = packet.get("plan_options") or {}
    lines.append("## 主方案")
    primary = plan.get("primary_plan") or []
    if primary:
        for item in primary:
            lines.append(
                f"- {item['asset_class']} {item['weight']}% -> {item['product']} (score={item['score']})"
            )
    else:
        lines.append("- 暂无")
    lines.append("")

    lines.append("## 备选方案")
    backup = plan.get("backup_plan") or []
    if backup:
        for item in backup:
            lines.append(
                f"- {item['asset_class']} {item['weight']}% -> {item['product']} (score={item['score']})"
            )
    else:
        lines.append("- 暂无")
    lines.append("")

    lines.append("## 适配产品清单")
    suitable = packet.get("suitable_products") or []
    if suitable:
        for row in suitable:
            lines.append(f"- {row.get('name')} | {row.get('asset_class')} | {row.get('status')} | score={row.get('score')}")
    else:
        lines.append("- 暂无")
    lines.append("")

    lines.append("## 不适配产品")
    not_suitable = packet.get("not_suitable_products") or []
    if not_suitable:
        for row in not_suitable:
            reason = "；".join(row.get("reasons") or [])
            lines.append(f"- {row.get('name')} | {reason or '风险等级/期限不匹配'}")
    else:
        lines.append("- 暂无")
    lines.append("")

    for key, title in (
        ("gaps", "信息缺口"),
        ("risk_notes", "风险提示"),
        ("communication_points", "沟通要点"),
        ("follow_up", "下一步"),
    ):
        lines.append(f"## {title}")
        items = packet.get(key) or []
        lines += [f"- {x}" for x in items] if items else ["- 暂无"]
        lines.append("")
    return "\n".join(lines)
