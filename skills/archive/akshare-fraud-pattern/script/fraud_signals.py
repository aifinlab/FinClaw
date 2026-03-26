"""财务欺诈模式识别模块。"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
import math

import numpy as np
import pandas as pd


@dataclass
class SignalResult:
    signal_name: str
    value: float
    threshold: str
    risk_level: str
    interpretation: str


def _find_first_matching_column(columns: Iterable[str], keywords: list[str]) -> str | None:
    normalized = {str(col).strip(): str(col).strip().lower() for col in columns}
    for original, lower_name in normalized.items():
        if all(keyword.lower() in lower_name for keyword in keywords):
            return original
    return None


def _to_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series.astype(str).str.replace(",", "", regex=False), errors="coerce")


def _prepare_statement(df: pd.DataFrame) -> pd.DataFrame:
    data = df.copy()
    date_col = _find_first_matching_column(data.columns, ["日期"]) or _find_first_matching_column(data.columns, ["report"])
    if date_col is None:
        for candidate in ["REPORT_DATE", "报告日期", "日期", "截止日期"]:
            if candidate in data.columns:
                date_col = candidate
                break
    if date_col is not None:
        data = data.rename(columns={date_col: "report_date"})
        data["report_date"] = pd.to_datetime(data["report_date"], errors="coerce")
        data = data.sort_values("report_date").reset_index(drop=True)
    return data


def _extract_series(df: pd.DataFrame, candidates: list[list[str]]) -> pd.Series:
    for keywords in candidates:
        col = _find_first_matching_column(df.columns, keywords)
        if col is not None:
            return _to_numeric(df[col])
    return pd.Series(np.nan, index=df.index)


def build_feature_frame(
    indicators: pd.DataFrame,
    balance_sheet: pd.DataFrame,
    income_statement: pd.DataFrame,
    cashflow_statement: pd.DataFrame,
) -> pd.DataFrame:
    bs = _prepare_statement(balance_sheet)
    inc = _prepare_statement(income_statement)
    cfs = _prepare_statement(cashflow_statement)

    feature = pd.DataFrame()

    for frame in [bs, inc, cfs]:
        if "report_date" in frame.columns:
            feature["report_date"] = frame["report_date"]
            break

    if feature.empty:
        raise ValueError("无法识别财报日期字段，请检查原始数据字段")

    feature["revenue"] = _extract_series(inc, [["营业总收入"], ["营业收入"], ["revenue"]])
    feature["cogs"] = _extract_series(inc, [["营业总成本"], ["营业成本"], ["cost"]])
    feature["net_income"] = _extract_series(inc, [["净利润"], ["归母净利润"], ["net", "profit"]])
    feature["selling_expense"] = _extract_series(inc, [["销售费用"], ["selling"]])
    feature["admin_expense"] = _extract_series(inc, [["管理费用"], ["admin"]])
    feature["finance_expense"] = _extract_series(inc, [["财务费用"], ["finance"]])

    feature["accounts_receivable"] = _extract_series(bs, [["应收账款"], ["应收票据", "应收账款"], ["receivable"]])
    feature["inventory"] = _extract_series(bs, [["存货"], ["inventory"]])
    feature["cash"] = _extract_series(bs, [["货币资金"], ["cash"]])
    feature["current_assets"] = _extract_series(bs, [["流动资产合计"], ["流动资产"], ["current", "asset"]])
    feature["ppe"] = _extract_series(bs, [["固定资产"], ["property"]])
    feature["total_assets"] = _extract_series(bs, [["资产总计"], ["总资产"], ["total", "asset"]])
    feature["total_debt"] = _extract_series(bs, [["负债合计"], ["总负债"], ["total", "liabil"]])

    feature["operating_cf"] = _extract_series(cfs, [["经营活动产生的现金流量净额"], ["经营活动现金流量净额"], ["operating", "cash"]])

    feature = feature.sort_values("report_date").reset_index(drop=True)

    feature["gross_margin"] = (feature["revenue"] - feature["cogs"]) / feature["revenue"].replace(0, np.nan)
    feature["cash_to_profit"] = feature["operating_cf"] / feature["net_income"].replace(0, np.nan)
    feature["ar_to_revenue"] = feature["accounts_receivable"] / feature["revenue"].replace(0, np.nan)
    feature["inventory_to_revenue"] = feature["inventory"] / feature["revenue"].replace(0, np.nan)
    feature["debt_ratio"] = feature["total_debt"] / feature["total_assets"].replace(0, np.nan)
    feature["asset_quality_proxy"] = 1 - (
        feature["current_assets"].fillna(0) + feature["ppe"].fillna(0)
    ) / feature["total_assets"].replace(0, np.nan)

    # 近似 Beneish 风格因子
    prev = feature.shift(1)
    feature["dsri"] = (feature["ar_to_revenue"]) / prev["ar_to_revenue"].replace(0, np.nan)
    feature["gmi"] = prev["gross_margin"] / feature["gross_margin"].replace(0, np.nan)
    feature["aqi"] = feature["asset_quality_proxy"] / prev["asset_quality_proxy"].replace(0, np.nan)
    feature["sgi"] = feature["revenue"] / prev["revenue"].replace(0, np.nan)
    feature["depi"] = ((prev["ppe"] / (prev["ppe"] + prev["cogs"].abs().replace(0, np.nan)))) / (
        (feature["ppe"] / (feature["ppe"] + feature["cogs"].abs().replace(0, np.nan))).replace(0, np.nan)
    )
    feature["sgai"] = (
        (feature["selling_expense"].fillna(0) + feature["admin_expense"].fillna(0))
        / feature["revenue"].replace(0, np.nan)
    ) / (
        (prev["selling_expense"].fillna(0) + prev["admin_expense"].fillna(0))
        / prev["revenue"].replace(0, np.nan)
    )
    feature["lvgi"] = feature["debt_ratio"] / prev["debt_ratio"].replace(0, np.nan)
    feature["tata"] = (feature["net_income"] - feature["operating_cf"]) / feature["total_assets"].replace(0, np.nan)

    if not indicators.empty and "report_date" not in indicators.columns:
        indicators = _prepare_statement(indicators)

    return feature


def compute_beneish_like_score(feature: pd.DataFrame) -> pd.Series:
    """使用近似 Beneish M-Score 权重构造启发式分数。"""
    score = (
        -4.84
        + 0.92 * feature["dsri"].fillna(1)
        + 0.528 * feature["gmi"].fillna(1)
        + 0.404 * feature["aqi"].fillna(1)
        + 0.892 * feature["sgi"].fillna(1)
        + 0.115 * feature["depi"].fillna(1)
        - 0.172 * feature["sgai"].fillna(1)
        + 4.679 * feature["tata"].fillna(0)
        - 0.327 * feature["lvgi"].fillna(1)
    )
    return score


def evaluate_signals(feature: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    latest = feature.dropna(how="all").iloc[-1]
    prev = feature.dropna(how="all").iloc[-2] if len(feature.dropna(how="all")) >= 2 else latest

    signals: list[SignalResult] = []

    revenue_growth = (latest["revenue"] - prev["revenue"]) / abs(prev["revenue"]) if pd.notna(prev["revenue"]) and prev["revenue"] else np.nan
    ar_growth = (latest["accounts_receivable"] - prev["accounts_receivable"]) / abs(prev["accounts_receivable"]) if pd.notna(prev["accounts_receivable"]) and prev["accounts_receivable"] else np.nan
    inventory_growth = (latest["inventory"] - prev["inventory"]) / abs(prev["inventory"]) if pd.notna(prev["inventory"]) and prev["inventory"] else np.nan
    beneish_score = compute_beneish_like_score(feature).iloc[-1]

    signals.append(
        SignalResult(
            "现金流/利润背离",
            float(latest["cash_to_profit"]) if pd.notna(latest["cash_to_profit"]) else math.nan,
            "< 0.8",
            "高" if pd.notna(latest["cash_to_profit"]) and latest["cash_to_profit"] < 0.8 else "中/低",
            "经营现金流长期弱于净利润，可能存在利润质量偏弱或收入确认过快。",
        )
    )
    signals.append(
        SignalResult(
            "应收账款扩张快于营收",
            float(ar_growth - revenue_growth) if pd.notna(ar_growth) and pd.notna(revenue_growth) else math.nan,
            "> 0.2",
            "高" if pd.notna(ar_growth) and pd.notna(revenue_growth) and (ar_growth - revenue_growth) > 0.2 else "中/低",
            "应收账款增速明显高于营收增速，提示收入确认可能偏激进。",
        )
    )
    signals.append(
        SignalResult(
            "存货扩张快于营收",
            float(inventory_growth - revenue_growth) if pd.notna(inventory_growth) and pd.notna(revenue_growth) else math.nan,
            "> 0.2",
            "高" if pd.notna(inventory_growth) and pd.notna(revenue_growth) and (inventory_growth - revenue_growth) > 0.2 else "中/低",
            "存货累积明显快于营收增长，提示压货、减值滞后或资产虚胖风险。",
        )
    )
    signals.append(
        SignalResult(
            "TATA 应计项目压力",
            float(latest["tata"]) if pd.notna(latest["tata"]) else math.nan,
            "> 0.05",
            "高" if pd.notna(latest["tata"]) and latest["tata"] > 0.05 else "中/低",
            "净利润与经营现金流差距较大，应计项目占比偏高。",
        )
    )
    signals.append(
        SignalResult(
            "Beneish 风格分数",
            float(beneish_score) if pd.notna(beneish_score) else math.nan,
            "> -1.78",
            "高" if pd.notna(beneish_score) and beneish_score > -1.78 else "中/低",
            "分数越高越接近经典盈余操纵风险区间；该值为近似构造，仅作研究参考。",
        )
    )

    signal_df = pd.DataFrame([signal.__dict__ for signal in signals])
    high_count = int((signal_df["risk_level"] == "高").sum())
    raw_score = min(100, round(high_count * 18 + max(0, beneish_score + 2.5) * 20)) if pd.notna(beneish_score) else high_count * 18
    raw_score = int(min(100, max(0, raw_score)))

    summary = (
        f"最新报告期: {latest['report_date'].date() if pd.notna(latest['report_date']) else '未知'}\n"
        f"综合风险评分: {raw_score}/100\n"
        f"高风险信号数量: {high_count}\n"
        "结论: "
        + (
            "该样本出现多项高风险财务异常，建议结合审计意见、监管问询和年报附注做进一步核查。"
            if raw_score >= 60
            else "当前样本存在一定异常，但尚需结合更多非财务证据交叉验证。"
        )
    )
    return signal_df, summary


def save_analysis(feature: pd.DataFrame, signal_df: pd.DataFrame, summary: str, output_dir: Path = Path("output")) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    feature.to_csv(output_dir / "feature_frame.csv", index=False, encoding="utf-8-sig")
    signal_df.to_csv(output_dir / "fraud_risk_signals.csv", index=False, encoding="utf-8-sig")
    (output_dir / "fraud_risk_summary.txt").write_text(summary, encoding="utf-8")
