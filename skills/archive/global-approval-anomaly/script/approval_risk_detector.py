"""Rule-based listed-company approval anomaly risk detector."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List
import json
import os
import pandas as pd

import re


@dataclass
class RuleMatch:
    tag: str
    score: int
    matched_text: str


class ApprovalRiskDetector:
    def __init__(self, rules_path: str) -> None:
        with open(rules_path, "r", encoding="utf-8") as f:
            self.rules = json.load(f)

    def detect(self, company: str, events: List[Dict[str, str]]) -> pd.DataFrame:
        rows = []
        for event in events:
            title = event.get("title", "") or ""
            body = event.get("body", "") or ""
            matches: List[RuleMatch] = []

            for rule in self.rules["title_rules"]:
                if re.search(rule["pattern"], title, flags=re.IGNORECASE):
                    matches.append(
                        RuleMatch(rule["tag"], int(rule["score"]), self._extract_hit(rule["pattern"], title))
                    )

            for rule in self.rules["body_rules"]:
                if re.search(rule["pattern"], body, flags=re.IGNORECASE):
                    matches.append(
                        RuleMatch(rule["tag"], int(rule["score"]), self._extract_hit(rule["pattern"], body))
                    )

            if not matches:
                continue

            total_score = sum(m.score for m in matches)
            rows.append(
                {
                    "company": company,
                    "event_date": event.get("date", ""),
                    "source_type": event.get("source_type", ""),
                    "title": title,
                    "url": event.get("url", ""),
                    "matched_rules": ", ".join(sorted({m.tag for m in matches})),
                    "evidence": " | ".join(m.matched_text for m in matches if m.matched_text),
                    "risk_score": total_score,
                    "final_level": self._level(total_score),
                }
            )

        df = pd.DataFrame(rows)
        if not df.empty:
            df = df.sort_values(["risk_score", "event_date"], ascending=[False, False]).reset_index(drop=True)
        return df

    def summarize(self, company: str, df: pd.DataFrame) -> Dict[str, object]:
        if df.empty:
            return {
                "company": company,
                "events": 0,
                "total_risk_score": 0,
                "max_event_score": 0,
                "overall_level": "Low",
                "top_signals": [],
            }

        total_risk_score = int(df["risk_score"].sum())
        max_event_score = int(df["risk_score"].max())
        signal_counts = (
            df["matched_rules"]
            .str.split(", ")
            .explode()
            .value_counts()
            .head(8)
            .to_dict()
        )

        overall = self._level(max(total_risk_score // max(len(df), 1), max_event_score))
        return {
            "company": company,
            "events": int(len(df)),
            "total_risk_score": total_risk_score,
            "max_event_score": max_event_score,
            "overall_level": overall,
            "top_signals": signal_counts,
        }

    def _extract_hit(self, pattern: str, text: str) -> str:
        m = re.search(pattern, text, flags=re.IGNORECASE)
        return m.group(0) if m else ""

    def _level(self, score: int) -> str:
        thresholds = self.rules["severity_thresholds"]
        if score >= thresholds["critical"]:
            return "Critical"
        if score >= thresholds["high"]:
            return "High"
        if score >= thresholds["medium"]:
            return "Medium"
        return "Low"


def ensure_output_dir(path: str = "output") -> str:
    os.makedirs(path, exist_ok=True)
    return path
