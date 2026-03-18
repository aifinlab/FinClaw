import argparse
import json
from pathlib import Path
from typing import Any, Dict, List


REQUIRED_TOP_LEVEL = [
    "company",
    "application",
    "materials",
    "manager_goals",
]


def load_input(path: Path) -> Dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    return json.loads(text)


def material_map(materials: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    return {str(item.get("name", "")).strip(): item for item in materials if item.get("name")}


def assess_data_gaps(payload: Dict[str, Any]) -> List[str]:
    gaps: List[str] = []
    company = payload.get("company", {})
    application = payload.get("application", {})
    financials = payload.get("financials", {})
    operations = payload.get("operations", {})
    materials = payload.get("materials", [])

    if not company.get("name"):
        gaps.append("缺少企业名称，无法形成尽调对象识别。")
    if not application.get("product_type"):
        gaps.append("缺少授信品种，无法判断尽调重点和授信逻辑。")
    if application.get("amount_mn") in (None, ""):
        gaps.append("缺少授信金额，无法衡量融资诉求与经营规模是否匹配。")
    if not application.get("purpose"):
        gaps.append("缺少具体融资用途，无法设计补件和访谈核查动作。")
    if not application.get("repayment_source"):
        gaps.append("缺少第一还款来源描述，无法判断还款闭环。")
    if not financials:
        gaps.append("缺少财务数据，无法判断收入、利润、现金流和债务压力。")
    if not operations:
        gaps.append("缺少业务经营信息，无法核对客户、供应商、订单与回款链条。")

    if materials:
        missing_materials = [m.get("name") for m in materials if not m.get("provided") and m.get("name")]
        gaps.extend([f"关键材料未提供：{name}。" for name in missing_materials[:8]])
    else:
        gaps.append("未提供材料清单，无法判断当前尽调缺口。")
    return gaps


def build_supplement_list(payload: Dict[str, Any]) -> List[str]:
    application = payload.get("application", {})
    financials = payload.get("financials", {})
    operations = payload.get("operations", {})
    external = payload.get("external_risks", {})
    materials = material_map(payload.get("materials", []))

    suggestions: List[str] = []
    required_materials = [
        "营业执照",
        "近三年财报",
        "近6个月银行流水",
        "前五大客户销售合同",
        "前五大供应商采购合同",
        "存量借款明细",
    ]
    for name in required_materials:
        if name not in materials or not materials[name].get("provided"):
            suggestions.append(f"补充{name}，用于核验主体、业务闭环或债务压力。")

    if application.get("guarantee_mode"):
        suggestions.append("补充增信方案对应资料，包括保证人财力、抵押物权属或质押物控制条件。")
    if financials.get("accounts_receivable_mn"):
        suggestions.append("补充应收账款账龄、前十大应收客户及回款记录，用于验证回款质量。")
    if financials.get("inventory_mn"):
        suggestions.append("补充存货明细、库龄和主要库存对应订单，用于判断备货真实性和跌价风险。")
    if operations.get("top_customers"):
        suggestions.append("补充前五大客户销售合同、发票样本和回款凭证，形成合同至回款闭环。")
    if external.get("litigation_cases", 0):
        suggestions.append("补充涉诉事项清单、案件进展及对经营影响说明。")
    if external.get("cross_guarantee_risk"):
        suggestions.append("补充关联企业与担保链情况说明，核查是否存在交叉担保或资金混同。")
    return dedupe(suggestions)


def build_interview_questions(payload: Dict[str, Any]) -> List[str]:
    questions: List[str] = []
    application = payload.get("application", {})
    financials = payload.get("financials", {})
    operations = payload.get("operations", {})
    external = payload.get("external_risks", {})

    questions.extend([
        f"本次申请{application.get('product_type', '授信')}的直接触发原因是什么，金额{application.get('amount_mn', '待确认')}百万元如何测算出来？",
        "请按订单获取、采购备货、生产交付、开票回款的顺序说明经营闭环。",
        f"请具体说明第一还款来源“{application.get('repayment_source', '待补充')}”对应的客户、订单或现金流证据。",
        "当前主要客户和供应商分别是谁，合作稳定性和集中度情况如何？",
    ])

    if financials.get("operating_cash_flow_mn") is not None and financials.get("net_profit_mn") is not None:
        questions.append("利润与经营现金流存在差异的主要原因是什么，应收、存货和预付款变化如何解释？")
    if financials.get("interest_bearing_debt_mn"):
        questions.append("现有有息负债结构、到期分布和续作安排如何，是否存在短期集中偿付压力？")
    if operations.get("order_backlog_mn"):
        questions.append("在手订单的客户名称、金额、交付节奏和预计回款时间分别是什么？")
    if external.get("litigation_cases", 0):
        questions.append("涉诉事项的起因、进展、涉案金额和对经营回款的影响分别是什么？")
    if external.get("cross_guarantee_risk"):
        questions.append("关联企业之间是否存在担保、借款、资金拆借或共用账户情形？")
    return dedupe(questions)


def build_site_visit_focus(payload: Dict[str, Any]) -> List[str]:
    company = payload.get("company", {})
    operations = payload.get("operations", {})
    financials = payload.get("financials", {})
    focus = [
        f"核验{company.get('name', '企业')}办公、生产或经营场地是否真实存在，场地主体与申请主体是否一致。",
        "抽样核对合同、发票、出库单、物流单和回款记录，验证交易闭环。",
        "观察管理层、财务和业务负责人对融资用途、客户结构和账期的表述是否一致。",
    ]
    if operations.get("main_products"):
        focus.append("查看主要产品、产线或服务交付场景，判断实际经营内容是否与申报一致。")
    if financials.get("inventory_mn"):
        focus.append("查看库存状态、库龄和周转情况，确认库存与订单及报表是否大体匹配。")
    if operations.get("top_customers"):
        focus.append("核查是否存在为单一客户备货或依赖少数客户回款的情况。")
    return dedupe(focus)


def build_risk_hypotheses(payload: Dict[str, Any]) -> List[str]:
    hypotheses: List[str] = []
    financials = payload.get("financials", {})
    operations = payload.get("operations", {})
    external = payload.get("external_risks", {})
    site_visit = payload.get("site_visit", {})

    if financials.get("operating_cash_flow_mn") is not None and financials.get("net_profit_mn") is not None:
        if financials.get("net_profit_mn", 0) > 0 and financials.get("operating_cash_flow_mn", 0) <= 0.4 * max(financials.get("net_profit_mn", 0), 1):
            hypotheses.append("存在利润兑现为现金能力偏弱的风险，需要重点验证应收账款回收与库存占压。")
    if financials.get("accounts_receivable_mn", 0) > 0 and financials.get("revenue_mn", 0) > 0:
        if financials.get("accounts_receivable_mn", 0) / max(financials.get("revenue_mn", 1), 1) > 0.2:
            hypotheses.append("应收账款占收入比例偏高，存在客户集中回款波动或账期拉长风险。")
    if financials.get("inventory_mn", 0) > 0 and financials.get("revenue_mn", 0) > 0:
        if financials.get("inventory_mn", 0) / max(financials.get("revenue_mn", 1), 1) > 0.12:
            hypotheses.append("存货占用较高，需要核验库存真实状态、库龄和订单对应关系。")
    if operations.get("bank_flow_match_status") and "进一步" in str(operations.get("bank_flow_match_status")):
        hypotheses.append("合同、流水或往来款项之间仍有待解释的大额差异，需补做穿透核验。")
    if external.get("litigation_cases", 0):
        hypotheses.append("涉诉事项可能影响经营稳定性、回款节奏或资产可执行性，需要尽快核实。")
    if external.get("cross_guarantee_risk"):
        hypotheses.append("关联企业或担保链风险可能导致申请主体承担额外偿债压力。")
    if str(site_visit.get("visit_status", "")) == "待安排":
        hypotheses.append("现场经营真实性尚未核验，当前判断仍高度依赖客户口径和书面材料。")
    return dedupe(hypotheses)


def build_internal_alerts(payload: Dict[str, Any]) -> List[str]:
    alerts: List[str] = []
    external = payload.get("external_risks", {})
    site_visit = payload.get("site_visit", {})
    materials = payload.get("materials", [])
    missing_count = sum(1 for item in materials if not item.get("provided"))

    if missing_count >= 2:
        alerts.append("当前关键材料缺口较多，内部流转时应明确本次仅为前端尽调准备，暂不视为材料齐备。")
    if external.get("litigation_cases", 0):
        alerts.append("项目存在涉诉记录，建议在与审查接口沟通时提前说明案件性质、金额和最新进展。")
    if external.get("cross_guarantee_risk"):
        alerts.append("建议内部提前关注关联企业和潜在担保链风险，必要时升级做关联交易和资金往来穿透。")
    if str(site_visit.get("visit_status", "")) != "已完成":
        alerts.append("现场尽调尚未完成，当前判断不宜直接替代完整现场核查结论。")
    return dedupe(alerts)


def build_next_steps(payload: Dict[str, Any], gaps: List[str], hypotheses: List[str]) -> List[str]:
    steps: List[str] = []
    if gaps:
        steps.append("先按补件清单收齐主体、合同、流水、借款和增信资料，再进入内部深度分析。")
    steps.append("安排管理层访谈，优先核验融资用途、订单回款和现有债务压力。")
    steps.append("组织一次现场核查，重点看经营真实性、库存状态和单据闭环。")
    if hypotheses:
        steps.append("针对当前风险假设逐条补证据，不以客户口头解释替代核验。")
    steps.append("形成客户经理尽调纪要，并将需审查关注的问题提前同步内部接口人。")
    return dedupe(steps)


def build_summary(payload: Dict[str, Any], gaps: List[str], hypotheses: List[str]) -> str:
    company = payload.get("company", {})
    application = payload.get("application", {})
    goals = payload.get("manager_goals", {})
    parts = [
        f"{company.get('name', '该企业')}当前处于客户经理尽调阶段，主要任务为{goals.get('task_type', '尽调推进')}。",
        f"本次申请为{application.get('product_type', '授信')}，金额约{application.get('amount_mn', '待确认')}百万元，用途为{application.get('purpose', '待补充')}。",
    ]
    if gaps:
        parts.append(f"当前仍存在{len(gaps)}项关键信息缺口，需优先补齐材料并通过访谈和现场核查验证。")
    if hypotheses:
        parts.append(f"已形成{len(hypotheses)}项重点风险假设，建议作为下一步尽调的优先验证方向。")
    parts.append("输出重点应放在补件、访谈、现场核查和内部提示四类动作，不应直接替代最终审批判断。")
    return "".join(parts)


def dedupe(items: List[str]) -> List[str]:
    seen = set()
    result: List[str] = []
    for item in items:
        text = str(item).strip()
        if text and text not in seen:
            seen.add(text)
            result.append(text)
    return result


def build_packet(payload: Dict[str, Any]) -> Dict[str, Any]:
    missing_top = [key for key in REQUIRED_TOP_LEVEL if key not in payload]
    if missing_top:
        raise ValueError(f"输入缺少顶层字段: {', '.join(missing_top)}")

    data_gaps = assess_data_gaps(payload)
    risk_hypotheses = build_risk_hypotheses(payload)
    packet = {
        "skill_name": "bank-t122-corporate-finance-creditdue-diligence-rm-assistant",
        "company_name": payload.get("company", {}).get("name", "未命名企业"),
        "due_diligence_stage": "客户经理尽调",
        "data_gaps": data_gaps,
        "supplement_list": build_supplement_list(payload),
        "management_interview_questions": build_interview_questions(payload),
        "site_visit_focus": build_site_visit_focus(payload),
        "risk_hypotheses": risk_hypotheses,
        "internal_alerts": build_internal_alerts(payload),
        "next_steps": build_next_steps(payload, data_gaps, risk_hypotheses),
        "summary": build_summary(payload, data_gaps, risk_hypotheses),
    }
    return packet


def render_markdown(packet: Dict[str, Any]) -> str:
    sections = [
        f"# {packet['company_name']} 客户经理尽调动作包",
        "",
        f"- Skill: `{packet['skill_name']}`",
        f"- 阶段: {packet['due_diligence_stage']}",
        "",
        "## 摘要",
        packet["summary"],
        "",
    ]
    mapping = [
        ("data_gaps", "关键信息缺口"),
        ("supplement_list", "补件清单"),
        ("management_interview_questions", "管理层访谈提纲"),
        ("site_visit_focus", "现场核查重点"),
        ("risk_hypotheses", "风险假设"),
        ("internal_alerts", "内部提示"),
        ("next_steps", "下一步建议"),
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


def save_output(content: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a customer-manager due diligence packet.")
    parser.add_argument("--input", required=True, help="Path to input JSON file")
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
