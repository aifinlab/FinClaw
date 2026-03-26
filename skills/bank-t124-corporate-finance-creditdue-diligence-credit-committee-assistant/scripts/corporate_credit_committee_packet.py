from pathlib import Path
from typing import Any, Dict, List
import argparse
import json


REQUIRED_TOP_LEVEL = [
    "company",
    "application",
    "materials",
    "committee_goals",
]

CORE_MATERIALS = [
    "营业执照",
    "近三年审计报告",
    "近6个月主要账户流水",
    "前五大客户销售合同",
    "存量借款与担保明细",
]


def load_input(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def dedupe(items: List[str]) -> List[str]:
    seen = set()
    result: List[str] = []
    for item in items:
        text = str(item).strip()
        if text and text not in seen:
            seen.add(text)
            result.append(text)
    return result


def material_index(materials: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    return {str(item.get("name", "")).strip(): item for item in materials if item.get("name")}


def build_evidence_gaps(payload: Dict[str, Any]) -> List[str]:
    gaps: List[str] = []
    materials = material_index(payload.get("materials", []))
    for name in CORE_MATERIALS:
        if name not in materials or not materials[name].get("provided"):
            gaps.append(f"缺少{name}，会议证据链不完整。")

    application = payload.get("application", {})
    if not application.get("purpose"):
        gaps.append("融资用途不清，难以形成会议审议基础。")
    if not application.get("repayment_source"):
        gaps.append("第一还款来源不清，暂不具备充分讨论条件。")
    return dedupe(gaps)


def build_hard_stoppers(payload: Dict[str, Any], evidence_gaps: List[str]) -> List[str]:
    stoppers: List[str] = []
    company = payload.get("company", {})
    application = payload.get("application", {})
    external = payload.get("external_risks", {})

    if not company.get("name"):
        stoppers.append("申请主体不明确，不宜上会。")
    if not application.get("amount_mn"):
        stoppers.append("授信金额未明确，不具备拍板基础。")
    if not application.get("repayment_source"):
        stoppers.append("第一还款来源缺失，不宜上会拍板。")
    if external.get("dishonest_status"):
        stoppers.append("主体存在失信状态，应先完成专项核查。")
    if len(evidence_gaps) >= 5:
        stoppers.append("核心证据缺口较大，建议暂缓上会。")
    return dedupe(stoppers)


def build_supporting_points(payload: Dict[str, Any]) -> List[str]:
    points: List[str] = []
    application = payload.get("application", {})
    operations = payload.get("operations", {})
    collateral = payload.get("collateral", {})

    points.append(f"融资用途“{application.get('purpose', '待补充')}”与经营周转场景存在匹配基础。")
    if operations.get("order_backlog_mn"):
        points.append(f"在手订单规模约{operations.get('order_backlog_mn')}百万元，对资金需求有一定支撑。")
    if operations.get("contract_match_status") and "可对应" in str(operations.get("contract_match_status")):
        points.append("合同与订单链条总体可对应，具备一定交易真实性基础。")
    if collateral.get("ownership_clear"):
        points.append("押品权属已明确，具备一定增信支撑。")
    return dedupe(points)


def build_opposing_points(payload: Dict[str, Any]) -> List[str]:
    points: List[str] = []
    financials = payload.get("financials", {})
    operations = payload.get("operations", {})
    external = payload.get("external_risks", {})
    credit = payload.get("credit_exposure", {})

    if financials.get("net_profit_mn", 0) > 0 and financials.get("operating_cash_flow_mn", 0) <= 0.35 * max(financials.get("net_profit_mn", 1), 1):
        points.append("利润与经营现金流偏离，回款兑现能力需审慎评估。")
    if financials.get("accounts_receivable_mn", 0) > 0 and financials.get("revenue_mn", 0) > 0:
        if financials.get("accounts_receivable_mn", 0) / max(financials.get("revenue_mn", 1), 1) > 0.2:
            points.append("应收账款占比较高，存在回款波动风险。")
    if operations.get("bank_flow_match_status") and "待解释" in str(operations.get("bank_flow_match_status")):
        points.append("流水仍有大额往来待解释，交易闭环尚不完整。")
    if external.get("litigation_cases", 0):
        points.append("存在涉诉事项，需评估对回款和经营的影响。")
    if external.get("cross_guarantee_risk"):
        points.append("关联担保风险可能向申请主体传导。")
    if credit.get("overdue_history") and "续作" in str(credit.get("overdue_history")):
        points.append("历史短期续作记录提示融资依赖度偏高。")
    return dedupe(points)


def build_key_disputes(supporting_points: List[str], opposing_points: List[str], evidence_gaps: List[str]) -> List[str]:
    disputes: List[str] = []
    if supporting_points and opposing_points:
        disputes.append("项目具备一定经营与交易基础，但现金流质量和风险暴露仍存在争议。")
    if evidence_gaps:
        disputes.append("核心争议点之一是证据缺口较多，是否满足上会拍板的信息充分性。")
    disputes.append("争议焦点在于‘先上会附条件推进’还是‘先补证据再上会’。")
    return dedupe(disputes)


def build_vote_items(payload: Dict[str, Any], hard_stoppers: List[str]) -> List[str]:
    application = payload.get("application", {})
    items: List[str] = [
        "是否同意本项目进入本次审批会讨论并形成会议意见。",
        f"是否同意授信金额按{application.get('amount_mn', '待确认')}百万元方案审议。",
        "是否要求附加回款监管、提款节奏控制或补担保条件。",
        "是否要求会后补充专项核验并设定复核节点。",
    ]
    if hard_stoppers:
        items.insert(0, "是否暂缓上会，待阻断项解除后再行审议。")
    return dedupe(items)


def build_committee_questions(payload: Dict[str, Any]) -> List[str]:
    questions: List[str] = []
    application = payload.get("application", {})
    external = payload.get("external_risks", {})

    questions.append(f"本次申请{application.get('amount_mn', '待确认')}百万元的测算依据是否可拆解到订单和回款节点？")
    questions.append(f"第一还款来源“{application.get('repayment_source', '待补充')}”在压力场景下是否仍可覆盖本息？")
    questions.append("当前待补材料对会议结论影响有多大，是否可通过附条件方式管理？")
    if external.get("litigation_cases", 0):
        questions.append("涉诉事项是否可能影响核心客户合作、回款节奏或资产可执行性？")
    if external.get("cross_guarantee_risk"):
        questions.append("关联担保风险是否已穿透核查，是否需要限制新增对外担保？")
    return dedupe(questions)


def build_conditional_approval_terms(payload: Dict[str, Any], evidence_gaps: List[str], opposing_points: List[str]) -> List[str]:
    terms: List[str] = []
    application = payload.get("application", {})

    if evidence_gaps:
        terms.append("首次提款前补齐核心缺失材料并通过复核。")
    if opposing_points:
        terms.append("放款前完成争议事项专项核验，核验未通过则暂停提款。")
    terms.append("设置分笔提款和用途核验机制，确保资金按申报用途使用。")
    terms.append("建立回款归集或监管安排，动态监控第一还款来源。")
    if application.get("guarantee_mode"):
        terms.append("落实增信条件生效后方可提款，包括保证责任和押品权属复核。")
    return dedupe(terms)


def build_initial_committee_suggestion(hard_stoppers: List[str], evidence_gaps: List[str], opposing_points: List[str]) -> str:
    if hard_stoppers:
        return "暂缓上会"
    if len(evidence_gaps) >= 3 or len(opposing_points) >= 4:
        return "审慎上会"
    if evidence_gaps or opposing_points:
        return "有条件上会"
    return "建议上会审议"


def build_next_steps(suggestion: str, hard_stoppers: List[str]) -> List[str]:
    steps: List[str] = []
    if hard_stoppers:
        steps.append("先解除阻断项并补齐核心材料，再安排上会。")
    elif suggestion == "审慎上会":
        steps.append("上会前完成关键争议补证据并形成专项说明。")
    elif suggestion == "有条件上会":
        steps.append("提前确认有条件通过条款文本和执行责任人。")
    else:
        steps.append("按会议议程准备一页纸和争议矩阵，组织会前沟通。")

    steps.append("会议结束后按拍板结果更新补件、核验和放款前置条件。")
    steps.append("明确责任岗和时点，形成可追踪的会后执行清单。")
    return dedupe(steps)


def build_summary(payload: Dict[str, Any], suggestion: str, hard_stoppers: List[str], evidence_gaps: List[str], key_disputes: List[str]) -> str:
    company = payload.get("company", {})
    application = payload.get("application", {})
    goals = payload.get("committee_goals", {})
    parts = [
        f"{company.get('name', '该企业')}当前处于{goals.get('committee_stage', '上会前准备')}阶段，会议目标为{goals.get('task_type', '审批会材料准备')}。",
        f"本次申请为{application.get('product_type', '授信')}，金额约{application.get('amount_mn', '待确认')}百万元。",
        f"初步会议建议为“{suggestion}”。",
    ]
    if hard_stoppers:
        parts.append(f"已识别{len(hard_stoppers)}项阻断因素，应优先处理。")
    if evidence_gaps:
        parts.append(f"当前仍有{len(evidence_gaps)}项关键证据缺口。")
    if key_disputes:
        parts.append(f"另有{len(key_disputes)}项核心争议建议纳入会上拍板。")
    parts.append("该结果仅用于会议准备和讨论，不替代最终审批结论。")
    return "".join(parts)


def build_packet(payload: Dict[str, Any]) -> Dict[str, Any]:
    missing_top = [key for key in REQUIRED_TOP_LEVEL if key not in payload]
    if missing_top:
        raise ValueError(f"输入缺少顶层字段: {', '.join(missing_top)}")

    evidence_gaps = build_evidence_gaps(payload)
    hard_stoppers = build_hard_stoppers(payload, evidence_gaps)
    supporting_points = build_supporting_points(payload)
    opposing_points = build_opposing_points(payload)
    key_disputes = build_key_disputes(supporting_points, opposing_points, evidence_gaps)
    suggestion = build_initial_committee_suggestion(hard_stoppers, evidence_gaps, opposing_points)

    return {
        "skill_name": "bank-t124-corporate-finance-creditdue-diligence-credit-committee-assistant",
        "company_name": payload.get("company", {}).get("name", "未命名企业"),
        "committee_stage": payload.get("committee_goals", {}).get("committee_stage", "上会前准备"),
        "hard_stoppers": hard_stoppers,
        "supporting_points": supporting_points,
        "opposing_points": opposing_points,
        "key_disputes": key_disputes,
        "vote_items": build_vote_items(payload, hard_stoppers),
        "evidence_gaps": evidence_gaps,
        "committee_questions": build_committee_questions(payload),
        "conditional_approval_terms": build_conditional_approval_terms(payload, evidence_gaps, opposing_points),
        "initial_committee_suggestion": suggestion,
        "next_steps": build_next_steps(suggestion, hard_stoppers),
        "summary": build_summary(payload, suggestion, hard_stoppers, evidence_gaps, key_disputes),
    }


def render_markdown(packet: Dict[str, Any]) -> str:
    sections = [
        f"# {packet['company_name']} 审批会材料包",
        "",
        f"- Skill: `{packet['skill_name']}`",
        f"- 阶段: {packet['committee_stage']}",
        f"- 初步会议建议: {packet['initial_committee_suggestion']}",
        "",
        "## 摘要",
        packet["summary"],
        "",
    ]

    mapping = [
        ("hard_stoppers", "上会阻断项"),
        ("supporting_points", "支持理由"),
        ("opposing_points", "反对理由"),
        ("key_disputes", "核心争议点"),
        ("vote_items", "待拍板事项"),
        ("evidence_gaps", "证据缺口"),
        ("committee_questions", "会议提问清单"),
        ("conditional_approval_terms", "有条件通过条款"),
        ("next_steps", "下一步动作"),
    ]

    for key, title in mapping:
        sections.append(f"## {title}")
        items = packet.get(key, [])
        if items:
            sections.extend([f"- {item}" for item in items])
        else:
            sections.append("- 暂无")
        sections.append("")

    return "\n".join(sections)


def save_output(content: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate corporate credit committee packet.")
    parser.add_argument("--input", required=True, help="Path to input JSON")
    parser.add_argument("--output", required=True, help="Path to output file")
    parser.add_argument("--format", choices=["json", "markdown"], default="markdown")
    args = parser.parse_args()

    payload = load_input(Path(args.input))
    packet = build_packet(payload)

    if args.format == "json":
        content = json.dumps(packet, ensure_ascii=False, indent=2)
    else:
        content = render_markdown(packet)

    save_output(content, Path(args.output))


if __name__ == "__main__":
    main()
