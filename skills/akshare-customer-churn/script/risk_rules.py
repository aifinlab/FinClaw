from __future__ import annotations

import json
import re
from dataclasses import dataclass, asdict
from typing import Any, Dict, Iterable, List, Optional, Tuple

import pandas as pd


RISK_KEYWORDS = {
    "客户流失": 20,
    "大客户流失": 28,
    "客户减少": 15,
    "订单下滑": 16,
    "订单减少": 16,
    "续费下降": 18,
    "退订": 20,
    "退货": 10,
    "投诉": 8,
    "客诉": 10,
    "渠道退出": 18,
    "经销商退出": 18,
    "合作终止": 24,
    "终止合作": 24,
    "需求疲软": 15,
    "销量下滑": 14,
    "销量下降": 14,
    "价格战": 10,
    "应收账款": 6,
    "坏账": 12,
}

MDA_KEYWORDS = {
    "客户集中": 12,
    "大客户": 8,
    "订单": 6,
    "渠道": 6,
    "续费": 10,
    "流失": 18,
    "需求": 6,
    "竞争加剧": 10,
    "降价": 8,
    "回款": 8,
}


@dataclass
class RiskItem:
    name: str
    score: float
    level: str
    evidence: str
    category: str



def _to_number(value: Any) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(",", "")
    if not text or text in {"--", "nan", "None"}:
        return None
    text = text.replace("%", "")
    m = re.search(r"-?\d+(?:\.\d+)?", text)
    return float(m.group()) if m else None



def _detect_period_columns(df: pd.DataFrame) -> List[str]:
    cols = []
    for c in df.columns:
        s = str(c)
        if re.search(r"20\d{2}", s) or re.search(r"\d{4}-\d{2}-\d{2}", s):
            cols.append(c)
    return cols or list(df.columns[1:5])



def _label_column(df: pd.DataFrame) -> str:
    return str(df.columns[0])



def _find_metric_values(df: pd.DataFrame, patterns: Iterable[str], top_n: int = 2) -> List[float]:
    if df.empty:
        return []
    label_col = _label_column(df)
    period_cols = _detect_period_columns(df)
    for _, row in df.iterrows():
        label = str(row.get(label_col, ""))
        if any(p in label for p in patterns):
            values = [_to_number(row.get(c)) for c in period_cols]
            values = [v for v in values if v is not None]
            if values:
                return values[:top_n]
    return []



def _score_level(score: float) -> str:
    if score >= 70:
        return "high"
    if score >= 40:
        return "medium"
    return "low"



def _calc_change_risk(current: Optional[float], previous: Optional[float], good_when_higher: bool,
                      mild: float, severe: float, label: str, category: str) -> Optional[RiskItem]:
    if current is None or previous is None:
        return None
    delta = current - previous
    adverse = -delta if good_when_higher else delta
    if adverse <= mild:
        return None
    if adverse >= severe:
        score = 24
        level = "high"
    else:
        score = 12
        level = "medium"
    evidence = f"{label}: 最近值 {current:.2f}, 上期 {previous:.2f}, 不利变化 {adverse:.2f}"
    return RiskItem(name=label, score=score, level=level, evidence=evidence, category=category)



def analyze_financial_churn_risk(financial_abstract: pd.DataFrame, financial_indicator: pd.DataFrame) -> List[RiskItem]:
    items: List[RiskItem] = []

    revenue_yoy = _find_metric_values(financial_abstract, ["营业总收入同比", "营业收入同比"])
    gross_margin = _find_metric_values(financial_indicator, ["销售毛利率", "毛利率"])
    ar_turnover = _find_metric_values(financial_indicator, ["应收账款周转率"])
    inventory_turnover = _find_metric_values(financial_indicator, ["存货周转率"])
    ocf_ratio = _find_metric_values(financial_indicator, ["经营现金净流量/营业收入", "经营现金流/营业收入"])

    if revenue_yoy:
        cur = revenue_yoy[0]
        if cur < 0:
            items.append(RiskItem(
                name="收入同比转负",
                score=26,
                level="high",
                evidence=f"最近一期收入同比为 {cur:.2f}%",
                category="financial",
            ))
        elif cur < 5:
            items.append(RiskItem(
                name="收入增速偏弱",
                score=12,
                level="medium",
                evidence=f"最近一期收入同比为 {cur:.2f}%",
                category="financial",
            ))
        if len(revenue_yoy) >= 2 and revenue_yoy[0] < revenue_yoy[1] - 10:
            items.append(RiskItem(
                name="收入增速明显放缓",
                score=14,
                level="medium",
                evidence=f"最近一期 {revenue_yoy[0]:.2f}%, 上一期 {revenue_yoy[1]:.2f}%",
                category="financial",
            ))

    for item in [
        _calc_change_risk(gross_margin[0] if len(gross_margin) > 0 else None,
                          gross_margin[1] if len(gross_margin) > 1 else None,
                          good_when_higher=True, mild=2, severe=5,
                          label="销售毛利率下滑", category="financial"),
        _calc_change_risk(ar_turnover[0] if len(ar_turnover) > 0 else None,
                          ar_turnover[1] if len(ar_turnover) > 1 else None,
                          good_when_higher=True, mild=0.2, severe=0.8,
                          label="应收账款周转率恶化", category="financial"),
        _calc_change_risk(inventory_turnover[0] if len(inventory_turnover) > 0 else None,
                          inventory_turnover[1] if len(inventory_turnover) > 1 else None,
                          good_when_higher=True, mild=0.2, severe=0.8,
                          label="存货周转率恶化", category="financial"),
        _calc_change_risk(ocf_ratio[0] if len(ocf_ratio) > 0 else None,
                          ocf_ratio[1] if len(ocf_ratio) > 1 else None,
                          good_when_higher=True, mild=3, severe=8,
                          label="经营现金流质量下降", category="financial"),
    ]:
        if item:
            items.append(item)

    return items



def analyze_text_risk(df: pd.DataFrame, text_columns: Iterable[str], keyword_map: Dict[str, int], category: str) -> List[RiskItem]:
    if df.empty:
        return []
    results: List[RiskItem] = []
    for _, row in df.head(30).iterrows():
        text_parts = [str(row.get(c, "")) for c in text_columns if c in df.columns]
        text = " ".join(text_parts)
        if not text.strip():
            continue
        hit_keywords = [kw for kw in keyword_map if kw in text]
        if not hit_keywords:
            continue
        raw_score = min(sum(keyword_map[kw] for kw in hit_keywords), 30)
        snippet = text[:120].replace("\n", " ")
        results.append(RiskItem(
            name=f"文本风险命中: {'/'.join(hit_keywords[:4])}",
            score=float(raw_score),
            level=_score_level(raw_score * 2),
            evidence=snippet,
            category=category,
        ))
    return results



def analyze_business_structure(df: pd.DataFrame) -> List[RiskItem]:
    if df.empty:
        return []
    items: List[RiskItem] = []
    candidate_cols = [c for c in df.columns if "主营" in str(c) or "营业收入比重" in str(c) or "收入比例" in str(c)]
    ratio_cols = [c for c in df.columns if "比重" in str(c) or "比例" in str(c)]
    if not ratio_cols:
        return items
    ratio_col = ratio_cols[0]
    ratios = pd.to_numeric(df[ratio_col], errors="coerce").dropna().sort_values(ascending=False)
    if not ratios.empty and ratios.iloc[0] >= 60:
        items.append(RiskItem(
            name="收入结构集中度较高",
            score=14,
            level="medium",
            evidence=f"单一业务/区域收入占比约 {ratios.iloc[0]:.2f}%",
            category="business_structure",
        ))
    return items



def summarize(items: List[RiskItem]) -> Dict[str, Any]:
    total = min(sum(i.score for i in items), 100.0)
    level = _score_level(total)
    counts = {
        "high": sum(1 for i in items if i.level == "high"),
        "medium": sum(1 for i in items if i.level == "medium"),
        "low": sum(1 for i in items if i.level == "low"),
    }
    return {
        "overall_risk_score": round(total, 2),
        "overall_risk_level": level,
        "high_risk_count": counts["high"],
        "medium_risk_count": counts["medium"],
        "low_risk_count": counts["low"],
        "rule_hit_count": len(items),
    }



def to_jsonable(items: List[RiskItem]) -> List[Dict[str, Any]]:
    return [asdict(i) for i in items]



def result_to_markdown(symbol: str, company_name: str, summary: Dict[str, Any], items: List[RiskItem]) -> str:
    lines = [
        f"# {company_name}（{symbol}）客户流失风险识别报告",
        "",
        "## 总体结论",
        f"- 综合风险分数：{summary['overall_risk_score']}",
        f"- 综合风险等级：{summary['overall_risk_level']}",
        f"- 命中规则数：{summary['rule_hit_count']}",
        f"- 高风险条目：{summary['high_risk_count']}",
        "",
        "## 风险明细",
    ]
    if not items:
        lines.append("- 未识别到明显风险信号；这不代表企业不存在真实客户流失风险。")
    else:
        for item in items:
            lines.extend([
                f"### {item.name}",
                f"- 分值：{item.score}",
                f"- 等级：{item.level}",
                f"- 类别：{item.category}",
                f"- 证据：{item.evidence}",
                "",
            ])
    lines.extend([
        "## 说明",
        "- 本结果基于 AkShare 可获取的公开数据做规则识别，核心是客户流失风险的代理变量，不是客户级真实流失率。",
        "- 建议结合企业 CRM、订单、复购、续费、客诉等内部数据做二次验证。",
    ])
    return "\n".join(lines)
