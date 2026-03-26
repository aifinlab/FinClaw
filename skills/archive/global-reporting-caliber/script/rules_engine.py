"""Rules engine for reporting caliber validation."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from rule_catalog import RULES, RuleItem
from typing import Dict, List

import re
# ===== AkShare开源数据支持（新增） =====
from skillsChoice.common.unified_data_api import (
    get_data_api,
    get_financial_report,
    get_index_quote,
    get_futures_quote,
)
# ====================================


@dataclass
class Finding:
    rule_id: str
    topic: str
    severity: str
    score: float
    status: str
    matched_keywords: List[str]
    missing_keywords: List[str]
    explanation: str


class ReportingCaliberEngine:
    def __init__(self, rules: List[RuleItem] | None = None):
        self.rules = rules or RULES

    @staticmethod
    def normalize_text(text: str) -> str:
        text = text or ""
        text = re.sub(r"\s+", " ", text)
        return text

    def evaluate_text(self, text: str) -> Dict[str, object]:
        normalized = self.normalize_text(text)
        findings: List[Finding] = []
        for rule in self.rules:
            matched = [kw for kw in rule.expected_keywords if kw in normalized]
            missing = [kw for kw in rule.expected_keywords if kw not in normalized]
            ratio = len(matched) / max(len(rule.expected_keywords), 1)
            status = "pass" if ratio >= 0.7 else "review" if ratio >= 0.4 else "alert"
            findings.append(
                Finding(
                    rule_id=rule.rule_id,
                    topic=rule.topic,
                    severity=rule.severity,
                    score=round(ratio, 4),
                    status=status,
                    matched_keywords=matched,
                    missing_keywords=missing,
                    explanation=f"命中 {len(matched)} 个预期字段，缺失 {len(missing)} 个字段。",
                )
            )
        risk_score = round(sum((1 - f.score) for f in findings) / max(len(findings), 1), 4)
        return {
            "risk_score": risk_score,
            "summary": self._build_summary(findings, risk_score),
            "findings": [asdict(f) for f in findings],
        }

    @staticmethod
    def _build_summary(findings: List[Finding], risk_score: float) -> str:
        alerts = [f for f in findings if f.status == "alert"]
        reviews = [f for f in findings if f.status == "review"]
        return (
            f"总体口径风险分数为 {risk_score:.2f}。"
            f"其中 alert {len(alerts)} 条，review {len(reviews)} 条。"
            "结果为启发式校验，需结合法务、董办或信披专员复核。"
        )
