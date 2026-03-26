from __future__ import annotations

from rule_definitions import RULE_CATALOG
from typing import Any, Dict, List

import datetime as dt


class RuleEngine:
    def __init__(self, rules: List[Dict[str, Any]] | None = None):
        self.rules = rules or RULE_CATALOG

    @staticmethod
    def _parse_date(value: Any):
        if not value:
            return None
        if isinstance(value, dt.date):
            return value
        for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y%m%d"):
            try:
                return dt.datetime.strptime(str(value), fmt).date()
            except ValueError:
                continue
        return None

    def _match_when(self, facts: Dict[str, Any], when: Dict[str, Any]) -> bool:
        for key, expected in when.items():
            if key.endswith("_gte"):
                real_key = key[:-4]
                if float(facts.get(real_key, 0) or 0) < float(expected):
                    return False
            else:
                value = facts.get(key)
                if isinstance(expected, list):
                    if value not in expected:
                        return False
                elif value != expected:
                    return False
        return True

    def _run_rule(self, rule: Dict[str, Any], facts: Dict[str, Any]) -> Dict[str, Any]:
        logic = rule["logic"]
        rule_type = logic["type"]
        passed = True
        detail = ""

        if rule_type == "date_diff_lte":
            when = logic.get("when", {})
            if self._match_when(facts, when):
                left = self._parse_date(facts.get(logic["left"]))
                right = self._parse_date(facts.get(logic["right"]))
                if not left or not right:
                    passed = False
                    detail = "缺少事件日期或披露日期。"
                else:
                    delta = (right - left).days
                    passed = delta <= logic["days"]
                    detail = f"事件到披露间隔 {delta} 天，阈值 {logic['days']} 天。"
            else:
                detail = "未命中适用场景，跳过。"

        elif rule_type == "all_required_if":
            when = logic.get("when", {})
            if self._match_when(facts, when):
                missing = [f for f in logic["required"] if f not in facts]
                falsey = [f for f in logic["truthy"] if not bool(facts.get(f))]
                passed = not missing and not falsey
                detail = f"缺失字段={missing}; 未满足字段={falsey}"
            else:
                detail = "未命中适用场景，跳过。"

        elif rule_type == "must_be_false_and_true":
            when = logic.get("when", {})
            if self._match_when(facts, when):
                must_true = [f for f in logic.get("must_be_true", []) if not bool(facts.get(f))]
                must_false = [f for f in logic.get("must_be_false", []) if bool(facts.get(f))]
                passed = not must_true and not must_false
                detail = f"应为真但不为真={must_true}; 应为假但不为假={must_false}"
            else:
                detail = "未命中适用场景，跳过。"

        elif rule_type == "number_lte":
            value = float(facts.get(logic["field"], 0) or 0)
            threshold = float(logic["threshold"])
            passed = value <= threshold
            detail = f"数值={value}, 阈值={threshold}"

        elif rule_type == "keyword_absence":
            haystack = str(facts.get(logic["field"], "") or "")
            hit = [kw for kw in logic["keywords"] if kw in haystack]
            passed = len(hit) == 0
            detail = f"命中关键词={hit}"

        else:
            passed = False
            detail = f"未知规则类型: {rule_type}"

        return {
            "rule_id": rule["rule_id"],
            "rule_name": rule["name"],
            "passed": passed,
            "severity": "low" if passed else rule.get("severity_on_fail", "medium"),
            "detail": detail,
            "description": rule.get("description", ""),
            "legal_basis_keywords": rule.get("legal_basis_keywords", []),
            "explanation": rule.get("explanation", ""),
        }

    def evaluate(self, facts: Dict[str, Any]) -> Dict[str, Any]:
        results = [self._run_rule(rule, facts) for rule in self.rules]
        failed = [r for r in results if not r["passed"]]
        risk_level = "low"
        if any(r["severity"] == "high" for r in failed):
            risk_level = "high"
        elif any(r["severity"] == "medium" for r in failed):
            risk_level = "medium"
        return {
            "summary": {
                "total_rules": len(results),
                "failed_rules": len(failed),
                "risk_level": risk_level,
            },
            "results": results,
        }
