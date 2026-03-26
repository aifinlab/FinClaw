from pathlib import Path
from typing import Any, Dict, List
import argparse
import json


REQUIRED_TOP_LEVEL = [
    "company",
    "application",
    "materials",
    "review_goals",
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
    materials = material_index(payload.get("materials", []))
    gaps: List[str] = []
    for name in CORE_MATERIALS:
        if name not in materials or not materials[name].get("provided"):
            gaps.append(f"缺少{name}，当前证据链不完整。")

    application = payload.get("application", {})
    if not application.get("purpose"):
        gaps.append("融资用途不清，无法判断金额和期限匹配性。")
    if not application.get("repayment_source"):
        gaps.append("第一还款来源未明确，无法评估还款闭环。")

    operations = payload.get("operations", {})
    if not operations:
        gaps.append("缺少业务经营资料，无法验证交易真实性。")
    return dedupe(gaps)


def build_inconsistencies(payload: Dict[str, Any]) -> List[str]:
    inconsistencies: List[str] = []
    operations = payload.get("operations", {})
    financials = payload.get("financials", {})
    credit = payload.get("credit_exposure", {})
    collateral = payload.get("collateral", {})

    if operations.get("contract_match_status") and "待" in str(operations.get("contract_match_status")):
        inconsistencies.append("合同链条尚未完全闭合，部分订单或补充协议仍待补充。")
    if operations.get("bank_flow_match_status") and "进一步" in str(operations.get("bank_flow_match_status")):
        inconsistencies.append("银行流水与交易背景之间仍有大额往来待解释。")
    if financials.get("net_profit_mn", 0) > 0 and financials.get("operating_cash_flow_mn", 0) <= 0.35 * max(financials.get("net_profit_mn", 1), 1):
        inconsistencies.append("利润表现与经营现金流不匹配，需核查回款质量和收入兑现能力。")
    if credit.get("overdue_history") and "续作" in str(credit.get("overdue_history")):
        inconsistencies.append("历史短期续作记录提示融资依赖度可能偏高。")
    if collateral.get("ownership_clear") is False:
        inconsistencies.append("押品权属未明确，增信有效性不足。")
    return dedupe(inconsistencies)


def build_hard_stoppers(payload: Dict[str, Any], evidence_gaps: List[str]) -> List[str]:
    stoppers: List[str] = []
    company = payload.get("company", {})
    application = payload.get("application", {})
    external = payload.get("external_risks", {})

    if not company.get("name"):
        stoppers.append("申请主体不明确，不宜进入正常审查流程。")
    if not application.get("amount_mn"):
        stoppers.append("授信金额未明确，无法评估项目规模与风险承受度。")
    if not application.get("repayment_source"):
        stoppers.append("第一还款来源不明确，当前不具备继续推进条件。")
    if external.get("dishonest_status"):
        stoppers.append("主体存在失信状态，应先核实准入影响。")
    if external.get("major_negative_news", 0) >= 2:
        stoppers.append("重大负面舆情较多，需升级审查后再决定是否推进。")
    if len(evidence_gaps) >= 5:
        stoppers.append("核心材料缺口较大，当前证据基础不足以形成有效审查意见。")
    return dedupe(stoppers)


def build_key_review_points(payload: Dict[str, Any]) -> List[str]:
    points: List[str] = []
    application = payload.get("application", {})
    financials = payload.get("financials", {})
    external = payload.get("external_risks", {})
    credit = payload.get("credit_exposure", {})

    points.extend([
        f"重点核验本次{application.get('product_type', '授信')}金额与用途“{application.get('purpose', '待补充')}”是否匹配企业真实周转需求。",
        f"重点核验第一还款来源“{application.get('repayment_source', '待补充')}”是否可通过订单、回款和流水证据支撑。",
        "重点核验客户经理提交材料中合同、发票、纳税和流水是否能形成业务闭环。",
    ])
    if financials.get("accounts_receivable_mn"):
        points.append("重点核验应收账款质量、账龄结构和主要客户回款稳定性。")
    if financials.get("inventory_mn"):
        points.append("重点核验存货规模、库龄和与订单执行的匹配关系。")
    if credit.get("other_bank_borrowings_mn") or credit.get("existing_loans_mn"):
        points.append("重点核验存量授信、他行借款和短期集中到期压力。")
    if external.get("cross_guarantee_risk"):
        points.append("重点核验关联企业担保链和资金往来，防止风险穿透至申请主体。")
    return dedupe(points)


def build_general_watch_items(payload: Dict[str, Any]) -> List[str]:
    items: List[str] = []
    company = payload.get("company", {})
    collateral = payload.get("collateral", {})
    external = payload.get("external_risks", {})

    if company.get("years_in_operation") and company.get("years_in_operation") < 3:
        items.append("企业经营年限较短，需要持续关注经营稳定性。")
    if collateral.get("liquidity_comment"):
        items.append(f"押品处置方面需关注：{collateral.get('liquidity_comment')}。")
    if external.get("credit_report_flags"):
        items.append(f"征信或授信记录提示：{external.get('credit_report_flags')}。")
    if not items:
        items.append("暂未发现明显一般关注项，可随补件情况动态调整。")
    return dedupe(items)


def build_supplement_requests(payload: Dict[str, Any], evidence_gaps: List[str]) -> List[str]:
    requests: List[str] = []
    financials = payload.get("financials", {})
    collateral = payload.get("collateral", {})
    external = payload.get("external_risks", {})

    requests.extend(evidence_gaps)
    if financials.get("accounts_receivable_mn"):
        requests.append("补充应收账款账龄、前十大客户应收明细及对应回款记录。")
    if financials.get("inventory_mn"):
        requests.append("补充存货明细、库龄和主要库存对应订单说明。")
    if collateral.get("collateral_type"):
        requests.append("补充抵押物权属、评估、查封状态及处置说明。")
    if collateral.get("guarantor_strength"):
        requests.append("补充保证人财力证明和可执行资产说明。")
    if external.get("litigation_cases", 0):
        requests.append("补充涉诉事项清单、涉案金额、进展和影响说明。")
    return dedupe(requests)


def build_review_questions(payload: Dict[str, Any]) -> List[str]:
    questions: List[str] = []
    application = payload.get("application", {})
    credit = payload.get("credit_exposure", {})
    external = payload.get("external_risks", {})

    questions.extend([
        f"本次申请{application.get('amount_mn', '待确认')}百万元的测算依据是什么，是否能拆解到采购、订单或项目节点？",
        "客户经理是否已经取得可以证明交易闭环的核心合同、发票、回款和流水样本？",
        f"第一还款来源“{application.get('repayment_source', '待补充')}”若出现延迟，备用还款安排是什么？",
    ])
    if credit.get("overdue_history"):
        questions.append(f"历史逾期或续作情况“{credit.get('overdue_history')}”的具体背景和当前改善情况是什么？")
    if external.get("cross_guarantee_risk"):
        questions.append("关联公司担保和资金往来是否已经穿透核实，是否存在潜在代偿压力？")
    if external.get("litigation_cases", 0):
        questions.append("涉诉事项对主要客户合作、回款和押品处置是否存在实际影响？")
    return dedupe(questions)


def build_risk_mitigants(payload: Dict[str, Any]) -> List[str]:
    mitigants: List[str] = []
    collateral = payload.get("collateral", {})
    application = payload.get("application", {})
    external = payload.get("external_risks", {})

    if collateral.get("collateral_type"):
        mitigants.append("若继续推进，可要求落实押品权属核验、价值折扣和处置预案。")
    if application.get("guarantee_mode"):
        mitigants.append("若继续推进，可补强保证人财力证明并明确担保责任边界。")
    mitigants.append("可考虑增加回款归集、监管账户或关键客户回款监控等控制措施。")
    if external.get("cross_guarantee_risk"):
        mitigants.append("对关联企业风险较高的，可要求限制新增对外担保并穿透核查关联往来。")
    return dedupe(mitigants)


def build_initial_recommendation(hard_stoppers: List[str], inconsistencies: List[str], payload: Dict[str, Any]) -> str:
    external = payload.get("external_risks", {})
    if hard_stoppers:
        return "暂不建议直接推进"
    if external.get("litigation_cases", 0) or external.get("cross_guarantee_risk") or len(inconsistencies) >= 3:
        return "审慎推进"
    if inconsistencies:
        return "补强证据后推进"
    return "可进入下一环节"


def build_next_steps(payload: Dict[str, Any], hard_stoppers: List[str]) -> List[str]:
    steps: List[str] = []
    if hard_stoppers:
        steps.append("先解决阻断项和核心证据缺口，再决定是否恢复常规审查流程。")
    else:
        steps.append("先按补件清单补强证据链，再形成完整审查底稿。")
    steps.append("与客户经理核对用途测算、回款来源和存量债务压力。")
    steps.append("对涉诉、关联担保、流水异常等问题做专项核验或升级审查。")
    steps.append("整理上会前提示或内部审查摘要，明确需附加的缓释条件。")
    return dedupe(steps)


def build_summary(payload: Dict[str, Any], hard_stoppers: List[str], inconsistencies: List[str], evidence_gaps: List[str], recommendation: str) -> str:
    company = payload.get("company", {})
    application = payload.get("application", {})
    goals = payload.get("review_goals", {})
    parts = [
        f"{company.get('name', '该企业')}当前处于{goals.get('review_stage', '审查复核')}阶段，目标是{goals.get('task_type', '生成审查要点')}。",
        f"本次申请为{application.get('product_type', '授信')}，金额约{application.get('amount_mn', '待确认')}百万元。",
        f"当前初步建议为“{recommendation}”。",
    ]
    if hard_stoppers:
        parts.append(f"已识别{len(hard_stoppers)}项阻断因素，应优先处理。")
    if evidence_gaps:
        parts.append(f"现有材料仍有{len(evidence_gaps)}项关键证据缺口。")
    if inconsistencies:
        parts.append(f"另有{len(inconsistencies)}项资料或数据不一致点待解释。")
    parts.append("该结果仅用于审查要点整理和后续动作安排，不替代最终审批结论。")
    return "".join(parts)


def build_packet(payload: Dict[str, Any]) -> Dict[str, Any]:
    missing_top = [key for key in REQUIRED_TOP_LEVEL if key not in payload]
    if missing_top:
        raise ValueError(f"输入缺少顶层字段: {', '.join(missing_top)}")

    evidence_gaps = build_evidence_gaps(payload)
    inconsistencies = build_inconsistencies(payload)
    hard_stoppers = build_hard_stoppers(payload, evidence_gaps)
    recommendation = build_initial_recommendation(hard_stoppers, inconsistencies, payload)

    return {
        "skill_name": "bank-t123-corporate-finance-creditdue-diligence-review-assistant",
        "company_name": payload.get("company", {}).get("name", "未命名企业"),
        "review_stage": payload.get("review_goals", {}).get("review_stage", "审查复核"),
        "hard_stoppers": hard_stoppers,
        "key_review_points": build_key_review_points(payload),
        "general_watch_items": build_general_watch_items(payload),
        "evidence_gaps": evidence_gaps,
        "inconsistencies": inconsistencies,
        "supplement_requests": build_supplement_requests(payload, evidence_gaps),
        "review_questions": build_review_questions(payload),
        "risk_mitigants": build_risk_mitigants(payload),
        "initial_recommendation": recommendation,
        "next_steps": build_next_steps(payload, hard_stoppers),
        "summary": build_summary(payload, hard_stoppers, inconsistencies, evidence_gaps, recommendation),
    }


def render_markdown(packet: Dict[str, Any]) -> str:
    sections = [
        f"# {packet['company_name']} 授信审查要点包",
        "",
        f"- Skill: `{packet['skill_name']}`",
        f"- 阶段: {packet['review_stage']}",
        f"- 初步建议: {packet['initial_recommendation']}",
        "",
        "## 摘要",
        packet["summary"],
        "",
    ]
    mapping = [
        ("hard_stoppers", "硬性阻断项"),
        ("key_review_points", "重点审查要点"),
        ("general_watch_items", "一般关注项"),
        ("evidence_gaps", "证据缺口"),
        ("inconsistencies", "材料不一致点"),
        ("supplement_requests", "补充核验要求"),
        ("review_questions", "审查提问单"),
        ("risk_mitigants", "风险缓释建议"),
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
    parser = argparse.ArgumentParser(description="Generate corporate credit review points.")
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
