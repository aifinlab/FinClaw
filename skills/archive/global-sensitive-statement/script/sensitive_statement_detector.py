from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, asdict
from legal_rules import LEGAL_BASES, SENSITIVE_PATTERNS
from pathlib import Path
from typing import Iterable, List
import argparse
import json

import re

SENTENCE_SPLIT_RE = re.compile(r"(?<=[。！？；\n])")


@dataclass
class Finding:
    sentence: str
    category: str
    matched_terms: list[str]
    risk_level: str
    reason: str
    legal_basis: list[dict]


class SensitiveStatementDetector:
    def __init__(self) -> None:
        self.legal_base_map = {item["id"]: item for item in LEGAL_BASES}

    def split_sentences(self, text: str) -> list[str]:
        parts = [s.strip() for s in SENTENCE_SPLIT_RE.split(text) if s.strip()]
        return [p for p in parts if p]

    def detect(self, text: str) -> list[Finding]:
        sentences = self.split_sentences(text)
        findings: list[Finding] = []

        for sentence in sentences:
            for rule in SENSITIVE_PATTERNS:
                matched_terms: list[str] = []
                for pattern in rule["patterns"]:
                    for match in re.finditer(pattern, sentence):
                        matched_terms.append(match.group(0))
                if matched_terms:
                    findings.append(
                        Finding(
                            sentence=sentence,
                            category=rule["category"],
                            matched_terms=sorted(set(matched_terms)),
                            risk_level=rule["risk_level"],
                            reason=rule["why"],
                            legal_basis=[self.legal_base_map[x] for x in rule["legal_basis"]],
                        )
                    )

        findings.extend(self._detect_prediction_without_risk(sentences))
        return findings

    def _detect_prediction_without_risk(self, sentences: Iterable[str]) -> list[Finding]:
        findings: list[Finding] = []
        prediction_terms = ("预计", "有望", "预期", "可能", "将", "计划")
        risk_terms = ("风险", "不确定性", "谨慎决策", "注意投资风险", "以", "为准")

        for sentence in sentences:
            if any(term in sentence for term in prediction_terms) and not any(term in sentence for term in risk_terms):
                findings.append(
                    Finding(
                        sentence=sentence,
                        category="预测表述缺少同句风险限定",
                        matched_terms=[term for term in prediction_terms if term in sentence],
                        risk_level="medium",
                        reason="发现预测性或展望性表述，但同句未见明显风险限定、依据边界或提示语。建议复核上下文是否已有充分说明。",
                        legal_basis=[self.legal_base_map["LAW-SEC-INFO-01"], self.legal_base_map["RULE-CSRC-182-03"]],
                    )
                )
        return findings

    def summarize(self, findings: list[Finding]) -> dict:
        category_counter = Counter(item.category for item in findings)
        level_counter = Counter(item.risk_level for item in findings)
        risk_score = 0
        for level, count in level_counter.items():
            weight = {"high": 3, "medium": 2, "info": 1}.get(level, 1)
            risk_score += weight * count

        if risk_score >= 16:
            rating = "高"
        elif risk_score >= 8:
            rating = "中"
        else:
            rating = "低"

        return {
            "total_findings": len(findings),
            "risk_score": risk_score,
            "risk_rating": rating,
            "by_category": dict(category_counter),
            "by_level": dict(level_counter),
        }


def load_text(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def save_json(findings: list[Finding], summary: dict, output_path: str | Path) -> None:
    payload = {
        "summary": summary,
        "findings": [asdict(item) for item in findings],
    }
    Path(output_path).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def save_markdown(findings: list[Finding], summary: dict, output_path: str | Path) -> None:
    lines: List[str] = []
    lines.append("# 敏感表述识别报告")
    lines.append("")
    lines.append(f"- 总命中数：{summary['total_findings']}")
    lines.append(f"- 风险分值：{summary['risk_score']}")
    lines.append(f"- 风险等级：{summary['risk_rating']}")
    lines.append("")
    lines.append("## 分类汇总")
    lines.append("")
    for category, count in summary["by_category"].items():
        lines.append(f"- {category}: {count}")
    lines.append("")
    lines.append("## 明细")
    lines.append("")
    for idx, item in enumerate(findings, start=1):
        lines.append(f"### {idx}. {item.category} / {item.risk_level}")
        lines.append(f"- 句子：{item.sentence}")
        lines.append(f"- 命中词：{', '.join(item.matched_terms)}")
        lines.append(f"- 说明：{item.reason}")
        lines.append("- 法规依据：")
        for basis in item.legal_basis:
            lines.append(f"  - {basis['name']}：{basis['summary']}（{basis['url']}）")
        lines.append("")
    Path(output_path).write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="上市企业敏感表述识别")
    parser.add_argument("input", help="待分析的 UTF-8 文本文件")
    parser.add_argument("--json-out", default="report.json", help="JSON 输出路径")
    parser.add_argument("--md-out", default="report.md", help="Markdown 输出路径")
    args = parser.parse_args()

    text = load_text(args.input)
    detector = SensitiveStatementDetector()
    findings = detector.detect(text)
    summary = detector.summarize(findings)
    save_json(findings, summary, args.json_out)
    save_markdown(findings, summary, args.md_out)

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
