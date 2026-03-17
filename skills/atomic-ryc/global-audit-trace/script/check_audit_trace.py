from typing import Dict, List
import argparse

from common import load_json, save_json


def regulation_ids(regulations: Dict, keyword: str) -> List[str]:
    ids = []
    for item in regulations.get("regulations", []):
        snippets = item.get("matched_snippets", [])
        if any(keyword in (hit.get("snippet", "") + hit.get("keyword", "")) for hit in snippets):
            ids.append(item.get("rule_id", "UNKNOWN"))
    return ids or ["MANUAL-REVIEW"]


def run(company_data: Dict, regulations: Dict) -> Dict:
    profile = company_data.get("profile", {})
    keyword_hits = company_data.get("annual_report_keyword_hits", [])
    keyword_text = " ".join([x.get("keyword", "") for x in keyword_hits])

    checks: List[Dict] = []

    has_internal_control = any("内部控制" in x.get("keyword", "") for x in keyword_hits)
    checks.append({
        "check_name": "内部控制相关披露存在性",
        "status": "pass" if has_internal_control else "warning",
        "risk_level": "LOW" if has_internal_control else "MEDIUM",
        "matched_rule_ids": regulation_ids(regulations, "内部控制"),
        "evidence": next((x.get("snippet") for x in keyword_hits if "内部控制" in x.get("keyword", "")), None),
    })

    has_audit_report = any("审计报告" in x.get("keyword", "") for x in keyword_hits)
    checks.append({
        "check_name": "审计报告线索存在性",
        "status": "pass" if has_audit_report else "warning",
        "risk_level": "LOW" if has_audit_report else "MEDIUM",
        "matched_rule_ids": regulation_ids(regulations, "审计"),
        "evidence": next((x.get("snippet") for x in keyword_hits if "审计报告" in x.get("keyword", "")), None),
    })

    audit_firm = profile.get("audit_firm")
    checks.append({
        "check_name": "审计机构字段可识别性",
        "status": "pass" if audit_firm else "warning",
        "risk_level": "LOW" if audit_firm else "MEDIUM",
        "matched_rule_ids": regulation_ids(regulations, "信息披露"),
        "evidence": audit_firm,
    })

    board_secretary = profile.get("board_secretary")
    office_address = profile.get("office_address")
    phone = profile.get("phone")
    contact_score = sum(bool(x) for x in [board_secretary, office_address, phone])
    checks.append({
        "check_name": "关键联系字段完整性",
        "status": "pass" if contact_score >= 2 else "warning",
        "risk_level": "LOW" if contact_score >= 2 else "MEDIUM",
        "matched_rule_ids": regulation_ids(regulations, "信息披露"),
        "evidence": {
            "board_secretary": board_secretary,
            "office_address": office_address,
            "phone": phone,
        },
    })

    has_trace = bool(company_data.get("trace"))
    checks.append({
        "check_name": "抓取留痕完整性",
        "status": "pass" if has_trace else "fail",
        "risk_level": "LOW" if has_trace else "HIGH",
        "matched_rule_ids": ["TRACE-001"],
        "evidence": company_data.get("trace", []),
    })

    website_info = company_data.get("website_info") or {}
    site_error = website_info.get("error") if isinstance(website_info, dict) else None
    checks.append({
        "check_name": "公司官网辅助核验可用性",
        "status": "warning" if site_error else "pass",
        "risk_level": "MEDIUM" if site_error else "LOW",
        "matched_rule_ids": ["MANUAL-REVIEW"],
        "evidence": site_error or website_info.get("url"),
    })

    high_count = sum(1 for x in checks if x["risk_level"] == "HIGH")
    med_count = sum(1 for x in checks if x["risk_level"] == "MEDIUM")
    overall = "HIGH" if high_count else ("MEDIUM" if med_count >= 2 else "LOW")

    return {
        "company": company_data.get("company_name"),
        "stock_code": company_data.get("stock_code"),
        "overall_risk": overall,
        "checks": checks,
        "trace": company_data.get("trace", []),
        "regulation_count": len(regulations.get("regulations", [])),
        "raw_keyword_summary": keyword_text,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="执行留痕与审计校验")
    parser.add_argument("--company-json", required=True)
    parser.add_argument("--regulations-json", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    company_data = load_json(args.company_json)
    regulations = load_json(args.regulations_json)
    result = run(company_data, regulations)
    save_json(result, args.output)
    print(f"saved: {args.output}")
