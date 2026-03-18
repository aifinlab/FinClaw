from __future__ import annotations

from typing import Any, Dict, List


def evaluate_pre_screen(data: Dict[str, Any]) -> Dict[str, Any]:
    risks: List[str] = []
    missing: List[str] = []
    checks: Dict[str, str] = {}

    basic = data.get("申请人基础信息", {})
    app = data.get("申请信息", {})
    job = data.get("职业收入信息", {})
    debt = data.get("资产负债信息", {})
    credit = data.get("征信信息", {})

    required_pairs = [
        (basic.get("姓名"), "申请人姓名"),
        (app.get("产品类型"), "产品类型"),
        (app.get("申请金额"), "申请金额"),
        (app.get("申请用途"), "申请用途"),
        (job.get("月收入"), "月收入"),
        (credit.get("查询次数"), "征信查询次数"),
    ]
    for value, label in required_pairs:
        if value in (None, "", []):
            missing.append(label)

    age = basic.get("年龄")
    if isinstance(age, (int, float)):
        if age < 18:
            risks.append("申请人年龄低于常规贷款准入下限")
        elif age > 65:
            risks.append("申请人年龄高于部分零售贷款常规准入上限，需结合产品规则复核")
    else:
        missing.append("年龄")

    income = job.get("月收入")
    if isinstance(income, (int, float)):
        if income < 3000:
            risks.append("月收入偏低，偿付能力需重点核验")
    else:
        missing.append("可量化收入信息")

    query_count = credit.get("查询次数")
    if isinstance(query_count, (int, float)):
        if query_count >= 10:
            risks.append("近期征信查询次数较多，存在多头申请风险")
        elif query_count >= 6:
            risks.append("近期征信查询偏多，建议结合借贷行为进一步核验")

    overdue = str(credit.get("逾期情况") or "")
    if overdue and any(token in overdue for token in ["当前逾期", "连续", "严重", "呆账", "代偿"]):
        risks.append("征信存在较强负面信号，需审慎处理")

    purpose = str(app.get("申请用途") or "")
    if not purpose:
        missing.append("贷款用途说明")
    elif len(purpose) <= 2:
        risks.append("贷款用途描述过于模糊，需进一步核验")

    existing_loans = debt.get("现有贷款") or []
    if isinstance(existing_loans, list) and len(existing_loans) >= 4:
        risks.append("现有贷款笔数较多，需关注负债累积与还款压力")

    if missing:
        checks["资料完整性"] = "存在关键缺口"
    else:
        checks["资料完整性"] = "基础判断所需信息基本具备"

    if any("年龄低于" in r or "较强负面信号" in r for r in risks):
        level = "不建议推进"
    elif len(risks) >= 3:
        level = "审慎介入"
    elif risks or missing:
        level = "有条件通过"
    else:
        level = "通过初筛"

    return {
        "检查结果": checks,
        "风险信号": risks,
        "缺失信息": sorted(set(missing)),
        "预审结论": level,
    }


if __name__ == "__main__":
    sample = {
        "申请人基础信息": {"姓名": "张三", "年龄": 33},
        "申请信息": {"产品类型": "个人消费贷", "申请金额": 300000, "申请用途": "家装"},
        "职业收入信息": {"月收入": 28000},
        "资产负债信息": {"现有贷款": ["房贷", "车贷"]},
        "征信信息": {"查询次数": 7, "逾期情况": "近两年无严重逾期"},
    }
    from pprint import pprint
    pprint(evaluate_pre_screen(sample))
