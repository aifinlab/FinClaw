"""
材料完整性校验规则。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from fetch_public_data import Announcement, normalize_title, search_official_rule_sources

from typing import Dict, List


@dataclass
class MaterialRule:
    key: str
    display_name: str
    required: bool
    keywords_any: List[str]
    evidence_hint: str
    legal_basis: List[str] = field(default_factory=list)


def get_rules(report_type: str) -> List[MaterialRule]:
    rule_sources = search_official_rule_sources()

    if report_type == "annual_report":
        return [
            MaterialRule(
                key="annual_report_full",
                display_name="年度报告全文",
                required=True,
                keywords_any=["年度报告", "年报全文"],
                evidence_hint="应存在年度报告全文披露记录。",
                legal_basis=[
                    rule_sources["csrc_disclosure_measures_2025"]["name"],
                    rule_sources["annual_report_format_2021"]["name"],
                ],
            ),
            MaterialRule(
                key="annual_report_summary",
                display_name="年度报告摘要或提示性公告",
                required=True,
                keywords_any=["年度报告摘要", "年报摘要", "年度报告披露提示性公告"],
                evidence_hint="常见年报配套公告。",
                legal_basis=[
                    rule_sources["annual_report_format_2021"]["name"],
                ],
            ),
            MaterialRule(
                key="board_resolution",
                display_name="审议定期报告的董事会决议公告",
                required=True,
                keywords_any=["董事会决议公告", "董事会会议决议公告"],
                evidence_hint="年报通常需经董事会审议并披露相关决议公告。",
                legal_basis=[
                    rule_sources["csrc_disclosure_measures_2025"]["name"],
                    rule_sources["sse_announcement_guide_2025"]["name"],
                    rule_sources["szse_announcement_guide_2025"]["name"],
                ],
            ),
            MaterialRule(
                key="supervisory_resolution",
                display_name="审议定期报告的监事会决议公告",
                required=True,
                keywords_any=["监事会决议公告", "监事会会议决议公告"],
                evidence_hint="年报通常需经监事会审核并披露相关决议公告。",
                legal_basis=[
                    rule_sources["csrc_disclosure_measures_2025"]["name"],
                    rule_sources["sse_announcement_guide_2025"]["name"],
                    rule_sources["szse_announcement_guide_2025"]["name"],
                ],
            ),
            MaterialRule(
                key="audit_report",
                display_name="审计报告或审计意见附件",
                required=True,
                keywords_any=["审计报告", "标准无保留意见审计报告", "审计意见"],
                evidence_hint="年度财务报告通常附审计报告。",
                legal_basis=[
                    rule_sources["annual_report_format_2021"]["name"],
                ],
            ),
            MaterialRule(
                key="internal_control_report",
                display_name="内部控制评价报告 / 内控审计相关文件",
                required=False,
                keywords_any=["内部控制评价报告", "内部控制审计报告", "内控评价报告", "内控审计报告"],
                evidence_hint="部分公司会同步披露内部控制相关文件，应人工结合公司情况复核。",
                legal_basis=[
                    rule_sources["sse_announcement_guide_2025"]["name"],
                    rule_sources["szse_announcement_guide_2025"]["name"],
                ],
            ),
            MaterialRule(
                key="profit_distribution",
                display_name="利润分配或资本公积转增预案相关公告",
                required=False,
                keywords_any=["利润分配预案", "利润分配方案", "资本公积转增", "现金分红"],
                evidence_hint="如公司董事会提出分配方案，通常会出现相关公告。",
                legal_basis=[
                    rule_sources["sse_announcement_guide_2025"]["name"],
                    rule_sources["szse_announcement_guide_2025"]["name"],
                ],
            ),
        ]

    if report_type == "semiannual_report":
        return [
            MaterialRule(
                key="semiannual_report_full",
                display_name="半年度报告全文",
                required=True,
                keywords_any=["半年度报告", "半年报全文"],
                evidence_hint="应存在半年度报告全文披露记录。",
                legal_basis=[
                    rule_sources["csrc_disclosure_measures_2025"]["name"],
                    rule_sources["semiannual_report_format_2021"]["name"],
                ],
            ),
            MaterialRule(
                key="semiannual_report_summary",
                display_name="半年度报告摘要",
                required=True,
                keywords_any=["半年度报告摘要", "半年报摘要"],
                evidence_hint="半年度报告常见配套摘要。",
                legal_basis=[
                    rule_sources["semiannual_report_format_2021"]["name"],
                ],
            ),
            MaterialRule(
                key="board_resolution",
                display_name="审议定期报告的董事会决议公告",
                required=True,
                keywords_any=["董事会决议公告", "董事会会议决议公告"],
                evidence_hint="半年度报告通常需经董事会审议。",
                legal_basis=[
                    rule_sources["csrc_disclosure_measures_2025"]["name"],
                ],
            ),
            MaterialRule(
                key="supervisory_resolution",
                display_name="审议定期报告的监事会决议公告",
                required=True,
                keywords_any=["监事会决议公告", "监事会会议决议公告"],
                evidence_hint="半年度报告通常需经监事会审核。",
                legal_basis=[
                    rule_sources["csrc_disclosure_measures_2025"]["name"],
                ],
            ),
        ]

    raise ValueError(f"Unsupported report_type: {report_type}")


def match_rules(announcements: List[Announcement], report_type: str) -> Dict[str, dict]:
    rules = get_rules(report_type)
    results: Dict[str, dict] = {}
    normalized = [
        {
            "title": ann.title,
            "publish_time": ann.publish_time,
            "adjunct_url": ann.adjunct_url,
            "norm_title": normalize_title(ann.title),
        }
        for ann in announcements
    ]

    for rule in rules:
        evidence = []
        keywords = [normalize_title(k) for k in rule.keywords_any]
        for ann in normalized:
            if any(k in ann["norm_title"] for k in keywords):
                evidence.append(
                    {
                        "title": ann["title"],
                        "publish_time": ann["publish_time"],
                        "url": ann["adjunct_url"],
                    }
                )

        status = "PASS" if evidence else ("FAIL" if rule.required else "WARN")
        results[rule.key] = {
            "display_name": rule.display_name,
            "required": rule.required,
            "status": status,
            "evidence_hint": rule.evidence_hint,
            "legal_basis": rule.legal_basis,
            "evidence": evidence,
        }
    return results


def summarize_overall(rule_results: Dict[str, dict]) -> str:
    required_fail = any(v["required"] and v["status"] == "FAIL" for v in rule_results.values())
    any_warn = any(v["status"] == "WARN" for v in rule_results.values())
    if required_fail:
        return "FAIL"
    if any_warn:
        return "WARN"
    return "PASS"
