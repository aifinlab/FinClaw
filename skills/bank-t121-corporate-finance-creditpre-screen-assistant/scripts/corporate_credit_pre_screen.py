#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""企业授信初筛脚本。"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Tuple
import argparse
import json

REQUIRED_MATERIALS = [
    "营业执照",
    "公司章程",
    "最近三年财务报表",
    "最近一期财务报表",
    "银行流水",
    "授信用途说明",
]


def load_payload(path: Path) -> Dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".jsonl":
        first = next((line for line in text.splitlines() if line.strip()), "{}")
        return json.loads(first)
    return json.loads(text)


def safe_float(value: Any) -> float | None:
    if value in (None, "", "NA", "N/A"):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def pct(value: float | None) -> str:
    if value is None:
        return "未提供"
    return f"{value * 100:.1f}%"


def ratio(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return numerator / denominator


def find_material(materials: List[Dict[str, Any]], keyword: str) -> Dict[str, Any] | None:
    for item in materials:
        name = str(item.get("name", ""))
        if keyword in name:
            return item
    return None


def collect_completeness(materials: List[Dict[str, Any]]) -> Dict[str, Any]:
    missing = []
    provided_count = 0
    for keyword in REQUIRED_MATERIALS:
        material = find_material(materials, keyword)
        if material and material.get("provided", False):
            provided_count += 1
        else:
            missing.append(keyword)
    return {
        "provided_count": provided_count,
        "required_count": len(REQUIRED_MATERIALS),
        "missing_items": missing,
    }


def build_key_metrics(payload: Dict[str, Any]) -> Dict[str, float | None]:
    financials = payload.get("financials", {})
    revenue = safe_float(financials.get("revenue_mn"))
    net_profit = safe_float(financials.get("net_profit_mn"))
    operating_cash_flow = safe_float(financials.get("operating_cash_flow_mn"))
    ebitda = safe_float(financials.get("ebitda_mn"))
    interest_expense = safe_float(financials.get("interest_expense_mn"))
    total_assets = safe_float(financials.get("total_assets_mn"))
    total_liabilities = safe_float(financials.get("total_liabilities_mn"))
    current_assets = safe_float(financials.get("current_assets_mn"))
    current_liabilities = safe_float(financials.get("current_liabilities_mn"))
    interest_bearing_debt = safe_float(financials.get("interest_bearing_debt_mn"))
    accounts_receivable = safe_float(financials.get("accounts_receivable_mn"))

    return {
        "资产负债率": ratio(total_liabilities, total_assets),
        "流动比率": ratio(current_assets, current_liabilities),
        "经营现金流/带息债务": ratio(operating_cash_flow, interest_bearing_debt),
        "利息保障倍数": ratio(ebitda, interest_expense),
        "应收/收入": ratio(accounts_receivable, revenue),
        "净利率": ratio(net_profit, revenue),
    }


def score_subject(payload: Dict[str, Any]) -> Tuple[int, List[str], List[str]]:
    company = payload.get("company", {})
    score = 78
    positives: List[str] = []
    watch_items: List[str] = []

    years = safe_float(company.get("years_in_operation"))
    if years is None:
        score -= 12
        watch_items.append("企业经营年限未提供，主体稳定性需补充核验。")
    elif years >= 5:
        positives.append(f"企业已持续经营 {int(years)} 年，主体连续性相对较好。")
    else:
        score -= 8
        watch_items.append("企业经营年限较短，需关注经营稳定性和客户沉淀。")

    if company.get("actual_controller"):
        positives.append("已提供实际控制人信息，股权穿透具备基础。")
    else:
        score -= 12
        watch_items.append("实际控制人信息未明确，治理和关联方风险需补核。")

    if not company.get("unified_credit_code"):
        score -= 15
        watch_items.append("统一社会信用代码缺失，主体基础信息不完整。")

    return max(score, 0), positives, watch_items


def score_business(payload: Dict[str, Any]) -> Tuple[int, List[str], List[str]]:
    operations = payload.get("operations", {})
    score = 74
    positives: List[str] = []
    watch_items: List[str] = []

    top_customer_ratio = safe_float(operations.get("top_customer_ratio_pct"))
    if top_customer_ratio is not None and top_customer_ratio > 55:
        score -= 18
        watch_items.append("前五大客户集中度偏高，需关注单一客户依赖和订单波动风险。")
    elif top_customer_ratio is not None:
        positives.append("客户集中度暂未见极端偏高。")

    contract_coverage = safe_float(operations.get("contract_coverage_months"))
    if contract_coverage is not None and contract_coverage >= 6:
        positives.append("在手合同对未来回款有一定覆盖。")
    else:
        score -= 8
        watch_items.append("在手合同覆盖期偏短或未提供，需关注收入持续性。")

    if str(operations.get("bank_flow_match_status", "")).strip() not in ("", "基本匹配"):
        score -= 10
        watch_items.append("流水与交易背景存在待解释事项，需优先核对主要大额往来。")

    return max(score, 0), positives, watch_items


def score_financials(payload: Dict[str, Any]) -> Tuple[int, List[str], List[str], List[str]]:
    metrics = build_key_metrics(payload)
    financials = payload.get("financials", {})
    score = 72
    positives: List[str] = []
    watch_items: List[str] = []
    hard_flags: List[str] = []

    liability_ratio = metrics["资产负债率"]
    current_ratio = metrics["流动比率"]
    ocf_debt = metrics["经营现金流/带息债务"]
    interest_cover = metrics["利息保障倍数"]
    ar_revenue = metrics["应收/收入"]
    net_profit = safe_float(financials.get("net_profit_mn"))
    ocf = safe_float(financials.get("operating_cash_flow_mn"))

    if liability_ratio is not None and liability_ratio > 0.8:
        score -= 18
        watch_items.append("资产负债率偏高，债务承压较重。")
    elif liability_ratio is not None:
        positives.append(f"资产负债率约为 {pct(liability_ratio)}。")

    if current_ratio is not None and current_ratio < 1:
        score -= 15
        watch_items.append("流动比率低于 1，短期偿债能力偏弱。")
    elif current_ratio is not None:
        positives.append(f"流动比率约为 {current_ratio:.2f}。")

    if ocf_debt is not None and ocf_debt < 0.05:
        score -= 12
        watch_items.append("经营现金流对带息债务覆盖偏弱。")

    if interest_cover is not None and interest_cover < 2:
        score -= 15
        watch_items.append("利息保障倍数偏低，财务安全边际较薄。")

    if ar_revenue is not None and ar_revenue > 0.35:
        score -= 8
        watch_items.append("应收账款占收入比例偏高，需关注回款质量和账龄。")

    if net_profit is not None and ocf is not None and net_profit > 0 and ocf < 0:
        score -= 15
        hard_flags.append("净利润为正但经营现金流为负，利润质量需重点核验。")

    return max(score, 0), positives, watch_items, hard_flags


def score_application(payload: Dict[str, Any]) -> Tuple[int, List[str], List[str], List[str]]:
    application = payload.get("application", {})
    score = 76
    positives: List[str] = []
    watch_items: List[str] = []
    hard_flags: List[str] = []

    purpose = str(application.get("purpose", "")).strip()
    repayment_source = str(application.get("repayment_source", "")).strip()
    amount = safe_float(application.get("amount_mn"))
    term = safe_float(application.get("term_months"))

    if not purpose:
        score -= 20
        hard_flags.append("授信用途未明确，当前无法判断融资用途真实性。")
    else:
        positives.append("授信用途已有明确表述。")

    if not repayment_source:
        score -= 20
        hard_flags.append("第一还款来源未明确，项目基础逻辑不足。")
    else:
        positives.append("已提供第一还款来源说明。")

    if amount is None or term is None:
        score -= 10
        watch_items.append("申请金额或期限信息不完整，难以判断与经营周转是否匹配。")

    return max(score, 0), positives, watch_items, hard_flags


def score_external(payload: Dict[str, Any]) -> Tuple[int, List[str], List[str], List[str]]:
    risks = payload.get("external_risks", {})
    support = payload.get("credit_support", {})
    score = 70
    positives: List[str] = []
    watch_items: List[str] = []
    hard_flags: List[str] = []

    if risks.get("dishonest_status"):
        score -= 30
        hard_flags.append("存在失信或被执行红旗，需显著下调推进意愿。")

    litigation_cases = safe_float(risks.get("litigation_cases"))
    litigation_amount = safe_float(risks.get("litigation_amount_mn"))
    if litigation_cases is not None and litigation_cases >= 3:
        score -= 12
        watch_items.append("涉诉数量偏多，需关注案件性质和对经营、现金流的影响。")
    if litigation_amount is not None and litigation_amount >= 10:
        score -= 12
        watch_items.append("涉诉金额较大，需核对是否可能形成实质影响。")

    if risks.get("major_negative_news"):
        score -= 15
        watch_items.append("存在重大负面舆情，需补充事件进展和处理结果。")

    if risks.get("cross_guarantee_risk"):
        score -= 10
        watch_items.append("存在交叉担保或担保链风险，需穿透核查风险传导。")

    collateral_value = safe_float(support.get("collateral_value_mn"))
    if collateral_value is not None and collateral_value > 0:
        positives.append("已提供抵押或保证等增信安排，可作为后续缓释方向。")
    else:
        watch_items.append("增信措施信息有限，需核对实际缓释能力。")

    return max(score, 0), positives, watch_items, hard_flags


def build_interview_questions(payload: Dict[str, Any], watch_items: List[str]) -> List[str]:
    questions = [
        "请说明本次授信对应的具体采购、生产或销售场景，以及资金使用路径。",
        "最近 12 个月经营现金流和利润出现差异的主要原因是什么？",
        "主要客户回款周期、账龄结构和信用质量如何？",
    ]

    if any("交叉担保" in item or "担保链" in item for item in watch_items):
        questions.append("请补充说明现有对外担保和互保安排，是否存在潜在代偿压力。")
    if any("流水" in item for item in watch_items):
        questions.append("请对流水中待解释的大额往来逐笔说明交易背景和对手方。")
    if any("涉诉" in item for item in watch_items):
        questions.append("请说明涉诉事项的成因、当前进展以及预计现金流影响。")

    return questions


def summarize_recommendation(
    completeness: Dict[str, Any],
    hard_flags: List[str],
    watch_items: List[str],
    scores: Dict[str, int],
) -> Tuple[str, str]:
    avg_score = sum(scores.values()) / max(len(scores), 1)
    if hard_flags:
        return "不建议直接推进", "中"
    if completeness["provided_count"] <= 2:
        return "审慎推进", "低"
    if avg_score >= 75 and len(watch_items) <= 3:
        return "可进入下一环节", "中高"
    if avg_score >= 60:
        return "有条件推进", "中"
    return "审慎推进", "中"


def build_result(payload: Dict[str, Any]) -> Dict[str, Any]:
    company = payload.get("company", {})
    materials = payload.get("materials", [])

    completeness = collect_completeness(materials)
    subject_score, subject_pos, subject_watch = score_subject(payload)
    business_score, business_pos, business_watch = score_business(payload)
    financial_score, financial_pos, financial_watch, financial_hard = score_financials(payload)
    app_score, app_pos, app_watch, app_hard = score_application(payload)
    external_score, external_pos, external_watch, external_hard = score_external(payload)

    hard_flags = financial_hard + app_hard + external_hard
    watch_items = subject_watch + business_watch + financial_watch + app_watch + external_watch
    positives = subject_pos + business_pos + financial_pos + app_pos + external_pos

    if completeness["missing_items"]:
        watch_items.append("核心授信材料尚未齐全，当前判断需保留明显边界。")

    supplement_requests = completeness["missing_items"] + [
        "请补充近 12 个月主要银行流水明细及大额往来解释。",
        "请补充主要客户合同、发票及回款闭环材料。",
    ]
    supplement_requests = list(dict.fromkeys(supplement_requests))

    scores = {
        "主体与治理": subject_score,
        "业务与行业逻辑": business_score,
        "财务与现金流": financial_score,
        "授信用途与还款来源": app_score,
        "外部风险与增信措施": external_score,
    }
    recommendation, confidence = summarize_recommendation(completeness, hard_flags, watch_items, scores)
    key_metrics = build_key_metrics(payload)

    next_steps = [
        "先补齐缺失材料，再决定是否进入正式尽调。",
        "对重点风险项安排客户访谈或管理层说明。",
        "如涉及担保链、涉诉或流水异常，建议升级做专项核验。",
    ]
    if recommendation == "可进入下一环节":
        next_steps[0] = "可进入正式尽调或审查准备阶段，同时同步补齐一般性缺口材料。"
    if recommendation == "不建议直接推进":
        next_steps[0] = "在关键红旗解释清楚前，不建议继续推进授信流程。"

    summary = (
        f"{company.get('name', '该企业')} 当前初筛结论为“{recommendation}”。"
        f"资料完整性为 {completeness['provided_count']}/{completeness['required_count']}，"
        f"主体、业务、财务和外部风险层面已识别 {len(hard_flags)} 项硬性红旗、"
        f"{len(watch_items)} 项重点关注事项。"
    )

    return {
        "skill_name": "bank-t121-corporate-finance-creditpre-screen-assistant",
        "company_name": company.get("name", ""),
        "recommendation": recommendation,
        "confidence": confidence,
        "completeness": completeness,
        "dimension_scores": scores,
        "hard_stop_flags": hard_flags,
        "major_watch_items": watch_items,
        "positive_signals": positives,
        "supplement_requests": supplement_requests,
        "interview_questions": build_interview_questions(payload, watch_items),
        "next_steps": next_steps,
        "key_metrics": key_metrics,
        "narrative_summary": summary,
    }


def render_markdown(result: Dict[str, Any]) -> str:
    completeness = result["completeness"]
    metrics = result["key_metrics"]
    current_ratio_text = "未提供" if metrics["流动比率"] is None else f"{metrics['流动比率']:.2f}"
    interest_cover_text = (
        "未提供" if metrics["利息保障倍数"] is None else f"{metrics['利息保障倍数']:.2f}"
    )

    def bullet_block(items: List[str]) -> List[str]:
        if not items:
            return ["- 暂无"]
        return [f"- {item}" for item in items]

    lines = [
        f"# 对公授信初筛结果 - {result['company_name'] or '未命名企业'}",
        "",
        "## 一、初筛结论",
        f"- 结论等级：{result['recommendation']}",
        f"- 结论把握度：{result['confidence']}",
        f"- 摘要：{result['narrative_summary']}",
        "",
        "## 二、资料完整性",
        f"- 已满足核心材料数：{completeness['provided_count']}/{completeness['required_count']}",
        "- 缺失材料：",
        *bullet_block(completeness["missing_items"]),
        "",
        "## 三、关键指标概览",
        f"- 资产负债率：{pct(metrics['资产负债率'])}",
        f"- 流动比率：{current_ratio_text}",
        f"- 经营现金流/带息债务：{pct(metrics['经营现金流/带息债务'])}",
        f"- 利息保障倍数：{interest_cover_text}",
        f"- 应收/收入：{pct(metrics['应收/收入'])}",
        "",
        "## 四、维度评分",
    ]

    for name, score in result["dimension_scores"].items():
        lines.append(f"- {name}：{score}")

    lines.extend(
        [
            "",
            "## 五、硬性阻断项",
            *bullet_block(result["hard_stop_flags"]),
            "",
            "## 六、重点关注事项",
            *bullet_block(result["major_watch_items"]),
            "",
            "## 七、正向信号",
            *bullet_block(result["positive_signals"]),
            "",
            "## 八、补件清单",
            *bullet_block(result["supplement_requests"]),
            "",
            "## 九、建议访谈问题",
            *bullet_block(result["interview_questions"]),
            "",
            "## 十、下一步建议",
            *bullet_block(result["next_steps"]),
            "",
            "## 十一、结论边界",
            "- 当前结果仅用于对公授信初筛，不替代正式尽调、审查和审批意见。",
            "- 未核验事项不得视为已确认事实，外部风险和增信有效性仍需后续核验。",
        ]
    )

    return "\n".join(lines)


def write_output(content: str, output_path: Path | None) -> None:
    if output_path is None:
        print(content)
        return
    output_path.write_text(content, encoding="utf-8")
    print(f"已输出结果: {output_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="企业授信初筛脚本")
    parser.add_argument("--input", required=True, help="输入 JSON/JSONL 文件路径")
    parser.add_argument("--output", help="输出文件路径")
    parser.add_argument(
        "--format",
        choices=("json", "markdown"),
        default="markdown",
        help="输出格式，默认 markdown",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = load_payload(Path(args.input))
    result = build_result(payload)

    if args.format == "json":
        content = json.dumps(result, ensure_ascii=False, indent=2)
    else:
        content = render_markdown(result)

    output_path = Path(args.output) if args.output else None
    write_output(content, output_path)


if __name__ == "__main__":
    main()
