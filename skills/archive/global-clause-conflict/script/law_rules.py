from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import List, Dict
import re


@dataclass
class Finding:
    rule_id: str
    severity: str
    title: str
    evidence: str
    basis: str
    suggestion: str
    source: str

    def to_dict(self) -> Dict[str, str]:
        return asdict(self)


RULE_BASES = {
    "company_law": "《中华人民共和国公司法》（2023年修订，2024-07-01施行）",
    "charter_guideline": "《上市公司章程指引（2025年修订）》",
    "sse_norm": "《上海证券交易所上市公司自律监管指引第1号——规范运作（2025年5月修订）》",
    "szse_norm": "《深圳证券交易所上市公司自律监管指引第1号——主板上市公司规范运作（2025年修订）》",
}


def normalize_text(text: str) -> str:
    text = text.replace("\u3000", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def snippet(text: str, pattern: str, width: int = 60) -> str:
    match = re.search(pattern, text, flags=re.I)
    if not match:
        return "未截取到稳定证据片段"
    start = max(0, match.start() - width)
    end = min(len(text), match.end() + width)
    return text[start:end]


def apply_rules(materials: List[dict]) -> List[Finding]:
    findings: List[Finding] = []

    for material in materials:
        raw = material["text"]
        text = normalize_text(raw)
        source = material["source"]

        # 1. 旧式“监事会必设”单一路径表述
        if re.search(r"公司设监事会", text) and not re.search(r"审计委员会|内部监督机构", text):
            findings.append(Finding(
                rule_id="RULE_AUDIT_OR_SUPERVISOR",
                severity="high",
                title="监督机构条款可能未按现行规则更新",
                evidence=snippet(text, r"公司设监事会"),
                basis=RULE_BASES["charter_guideline"],
                suggestion="核对公司是否已依据现行章程指引更新内部监督机构安排与表述。",
                source=source,
            ))

        # 2. 法定代表人表述过于绝对
        if re.search(r"董事长为公司的法定代表人", text) and not re.search(r"依章程规定|由董事长或者经理担任|法定代表人.*产生", text):
            findings.append(Finding(
                rule_id="RULE_LEGAL_REPRESENTATIVE",
                severity="medium",
                title="法定代表人条款可能过旧或刚性过强",
                evidence=snippet(text, r"董事长为公司的法定代表人"),
                basis=RULE_BASES["company_law"] + "；" + RULE_BASES["charter_guideline"],
                suggestion="检查章程是否明确法定代表人的产生、变更与权限边界，并与现行法保持一致。",
                source=source,
            ))

        # 3. 对外担保权限过宽
        if re.search(r"董事长.*有权决定.*对外担保", text) or re.search(r"总经理.*有权决定.*对外担保", text):
            findings.append(Finding(
                rule_id="RULE_GUARANTEE_AUTHORITY",
                severity="high",
                title="对外担保授权可能过宽",
                evidence=snippet(text, r"对外担保"),
                basis=RULE_BASES["charter_guideline"] + "；" + RULE_BASES["sse_norm"] + " / " + RULE_BASES["szse_norm"],
                suggestion="核对担保审批权限、审议层级、关联方回避与信息披露安排，避免由单一管理层直接决定。",
                source=source,
            ))

        # 4. 关联交易未见回避
        if re.search(r"关联交易", text) and not re.search(r"回避", text):
            findings.append(Finding(
                rule_id="RULE_RELATED_PARTY_RECUSE",
                severity="medium",
                title="关联交易条款可能缺少回避机制",
                evidence=snippet(text, r"关联交易"),
                basis=RULE_BASES["sse_norm"] + " / " + RULE_BASES["szse_norm"],
                suggestion="补充关联董事、关联股东回避表决及审议程序条款。",
                source=source,
            ))

        # 5. 利润分配仅强调现金分红比例但未设程序
        if re.search(r"现金分红", text) and not re.search(r"股东会审议|董事会审议|独立意见|审议程序", text):
            findings.append(Finding(
                rule_id="RULE_DIVIDEND_PROCEDURE",
                severity="low",
                title="利润分配条款可能缺少程序性约束",
                evidence=snippet(text, r"现金分红"),
                basis=RULE_BASES["charter_guideline"],
                suggestion="补充分红政策制定、调整、审议和披露程序。",
                source=source,
            ))

        # 6. 股东会/董事会权限交叉
        if re.search(r"董事会决定公司经营方针", text):
            findings.append(Finding(
                rule_id="RULE_AUTHORITY_OVERLAP",
                severity="high",
                title="董事会与股东会权限表述可能交叉冲突",
                evidence=snippet(text, r"董事会决定公司经营方针"),
                basis=RULE_BASES["company_law"] + "；" + RULE_BASES["charter_guideline"],
                suggestion="核对经营方针、投资计划、预算决策等事项的法定权力分配，避免越权。",
                source=source,
            ))

        # 7. 信息披露责任主体缺失
        if re.search(r"信息披露", text) and not re.search(r"董事会秘书|信息披露事务", text):
            findings.append(Finding(
                rule_id="RULE_DISCLOSURE_RESPONSIBILITY",
                severity="medium",
                title="信息披露责任主体可能不完整",
                evidence=snippet(text, r"信息披露"),
                basis=RULE_BASES["sse_norm"] + " / " + RULE_BASES["szse_norm"],
                suggestion="检查信息披露事务管理、责任主体和内部报送机制是否明确。",
                source=source,
            ))

    findings.extend(compare_materials(materials))
    return findings


def compare_materials(materials: List[dict]) -> List[Finding]:
    findings: List[Finding] = []
    if len(materials) < 2:
        return findings

    texts = [(m["source"], normalize_text(m["text"])) for m in materials]

    board_limits = []
    for source, text in texts:
        match = re.search(r"董事会.{0,20}([一二三四五六七八九十0-9]+)日内.*召开", text)
        if match:
            board_limits.append((source, match.group(0)))

    if len(board_limits) >= 2:
        values = {v for _, v in board_limits}
        if len(values) > 1:
            evidence = "；".join([f"{s}: {v}" for s, v in board_limits[:3]])
            findings.append(Finding(
                rule_id="RULE_INTERNAL_INCONSISTENCY_BOARD_NOTICE",
                severity="medium",
                title="不同材料中的董事会通知期限表述不一致",
                evidence=evidence,
                basis="企业内部制度之间应保持一致，并与现行章程及规范运作规则协调。",
                suggestion="核对公司章程、董事会议事规则和最新修订公告，以最新有效文本为准统一条款。",
                source="multiple",
            ))

    return findings


def summarize_findings(findings: List[Finding]) -> str:
    high = sum(1 for f in findings if f.severity == "high")
    medium = sum(1 for f in findings if f.severity == "medium")
    low = sum(1 for f in findings if f.severity == "low")
    return f"发现 {high} 项高风险、{medium} 项中风险、{low} 项低风险问题。"


def risk_level(findings: List[Finding]) -> str:
    if any(f.severity == "high" for f in findings):
        return "high"
    if any(f.severity == "medium" for f in findings):
        return "medium"
    if findings:
        return "low"
    return "none"
