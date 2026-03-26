from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple
import json

import numpy as np
import pandas as pd


@dataclass
class MetricResult:
    name: str
    value: Optional[float]
    score: float
    direction: str
    evidence: str


def _to_number(value) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, (int, float, np.number)):
        if pd.isna(value):
            return None
        return float(value)
    text = str(value).strip().replace(',', '')
    if text in {'', 'None', 'nan', 'NaN', '--'}:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _pick_column(columns: Iterable[str], keywords: List[str]) -> Optional[str]:
    cols = [str(c) for c in columns]
    for kw in keywords:
        for col in cols:
            if kw in col:
                return col
    return None


def _latest_row(df: pd.DataFrame) -> pd.Series:
    if df.empty:
        raise ValueError('数据为空')
    date_col = _pick_column(df.columns, ['REPORT_DATE', 'REPORTDATE', '报告日期', '截止日期'])
    if date_col is not None:
        tmp = df.copy()
        tmp[date_col] = pd.to_datetime(tmp[date_col], errors='coerce')
        tmp = tmp.sort_values(date_col, ascending=False)
        return tmp.iloc[0]
    return df.iloc[0]


def _second_latest_row(df: pd.DataFrame) -> Optional[pd.Series]:
    if len(df) < 2:
        return None
    date_col = _pick_column(df.columns, ['REPORT_DATE', 'REPORTDATE', '报告日期', '截止日期'])
    if date_col is not None:
        tmp = df.copy()
        tmp[date_col] = pd.to_datetime(tmp[date_col], errors='coerce')
        tmp = tmp.sort_values(date_col, ascending=False)
        return tmp.iloc[1]
    return df.iloc[1]


def _safe_div(a: Optional[float], b: Optional[float]) -> Optional[float]:
    if a is None or b in (None, 0):
        return None
    return a / b


def _score_thresholds(value: Optional[float], good: float, mid: float, reverse: bool = False) -> float:
    if value is None:
        return 50.0
    if reverse:
        if value <= good:
            return 90.0
        if value <= mid:
            return 65.0
        return 25.0
    else:
        if value >= good:
            return 90.0
        if value >= mid:
            return 65.0
        return 25.0


def build_overdue_risk_report(balance_df: pd.DataFrame, profit_df: pd.DataFrame, cashflow_df: pd.DataFrame) -> Dict:
    balance = _latest_row(balance_df)
    profit = _latest_row(profit_df)
    cashflow = _latest_row(cashflow_df)
    prev_profit = _second_latest_row(profit_df)

    current_liab = _to_number(balance.get(_pick_column(balance.index, ['流动负债合计', 'TOTAL_CURRENT_LIAB', '流动负债'])) )
    monetary_funds = _to_number(balance.get(_pick_column(balance.index, ['货币资金', 'MONETARYFUNDS'])))
    short_borrow = _to_number(balance.get(_pick_column(balance.index, ['短期借款', 'SHORTTERMLOAN'])))
    notes_payable = _to_number(balance.get(_pick_column(balance.index, ['应付票据', 'NOTESPAYABLE'])))
    accounts_receivable = _to_number(balance.get(_pick_column(balance.index, ['应收账款', 'ACCOUNTS_RECE'])))

    revenue = _to_number(profit.get(_pick_column(profit.index, ['营业总收入', '营业收入', 'TOTAL_OPERATE_INCOME', 'OPERATE_INCOME'])))
    net_profit = _to_number(profit.get(_pick_column(profit.index, ['净利润', 'NETPROFIT'])))
    prev_revenue = _to_number(prev_profit.get(_pick_column(prev_profit.index, ['营业总收入', '营业收入', 'TOTAL_OPERATE_INCOME', 'OPERATE_INCOME']))) if prev_profit is not None else None

    cfo = _to_number(cashflow.get(_pick_column(cashflow.index, ['经营活动产生的现金流量净额', 'NETCASH_OPERATE'])))

    debt_pressure = _safe_div((short_borrow or 0) + (notes_payable or 0), monetary_funds)
    cash_cover = _safe_div(cfo, current_liab)
    receivable_burden = _safe_div(accounts_receivable, revenue)
    profit_quality = _safe_div(cfo, net_profit)
    revenue_growth = None
    if revenue is not None and prev_revenue not in (None, 0):
        revenue_growth = (revenue - prev_revenue) / prev_revenue

    metrics = [
        MetricResult(
            name='短债资金压力',
            value=debt_pressure,
            score=_score_thresholds(debt_pressure, good=0.8, mid=1.2, reverse=True),
            direction='lower_is_better',
            evidence='(短期借款 + 应付票据) / 货币资金'
        ),
        MetricResult(
            name='经营现金流覆盖流动负债',
            value=cash_cover,
            score=_score_thresholds(cash_cover, good=0.2, mid=0.08, reverse=False),
            direction='higher_is_better',
            evidence='经营活动现金流净额 / 流动负债合计'
        ),
        MetricResult(
            name='应收账款负担',
            value=receivable_burden,
            score=_score_thresholds(receivable_burden, good=0.2, mid=0.35, reverse=True),
            direction='lower_is_better',
            evidence='应收账款 / 营业总收入'
        ),
        MetricResult(
            name='利润现金含量',
            value=profit_quality,
            score=_score_thresholds(profit_quality, good=0.9, mid=0.5, reverse=False),
            direction='higher_is_better',
            evidence='经营活动现金流净额 / 净利润'
        ),
        MetricResult(
            name='收入变化率',
            value=revenue_growth,
            score=_score_thresholds(revenue_growth, good=0.05, mid=-0.05, reverse=False),
            direction='higher_is_better',
            evidence='(本期收入 - 上期收入) / 上期收入'
        ),
    ]

    weights = {
        '短债资金压力': 0.28,
        '经营现金流覆盖流动负债': 0.24,
        '应收账款负担': 0.18,
        '利润现金含量': 0.18,
        '收入变化率': 0.12,
    }
    total_score = float(sum(m.score * weights[m.name] for m in metrics))
    overdue_risk_score = round(100 - total_score, 2)

    if overdue_risk_score >= 70:
        level = '高风险'
    elif overdue_risk_score >= 45:
        level = '中风险'
    else:
        level = '低风险'

    warnings = []
    for m in metrics:
        if m.score <= 25:
            warnings.append(f'{m.name}偏弱: {m.evidence}')

    return {
        'overdue_risk_score': overdue_risk_score,
        'risk_level': level,
        'metrics': [
            {
                'name': m.name,
                'value': None if m.value is None else round(m.value, 4),
                'metric_score': round(m.score, 2),
                'direction': m.direction,
                'evidence': m.evidence,
            }
            for m in metrics
        ],
        'warnings': warnings,
        'model_note': '该模型基于公开财务数据进行规则评分，用于识别企业潜在逾期/偿债压力，不构成信用评级或投资建议。',
    }


if __name__ == '__main__':
    # minimal self-check example
    demo = {
        'sample': 'Run through run_demo.py to generate a full report.'
    }
    print(json.dumps(demo, ensure_ascii=False, indent=2))
