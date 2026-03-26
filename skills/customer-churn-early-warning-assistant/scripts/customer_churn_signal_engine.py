from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, List
import json


@dataclass
class Signal:
    dimension: str
    signal: str
    severity: str
    evidence: str
    score: int


def _safe_num(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def detect_signals(record: Dict[str, Any]) -> Dict[str, Any]:
    signals: List[Signal] = []

    aum_change = _safe_num(record.get("aum_change_pct_90d"))
    txn_change = _safe_num(record.get("txn_freq_change_pct_90d"))
    app_change = _safe_num(record.get("app_active_days_change_pct_90d"))
    salary_active = bool(record.get("salary_inflow_active", True))
    product_exit_count = int(_safe_num(record.get("product_exit_count_180d")))
    external_transfer_ratio = _safe_num(record.get("external_transfer_ratio_90d"))
    touch_no_response = int(_safe_num(record.get("touch_no_response_count_60d")))
    complaint_count = int(_safe_num(record.get("complaint_count_180d")))

    if aum_change <= -30:
        signals.append(Signal("资产", "近 90 天资产显著下降", "高", f"AUM 变动 {aum_change:.1f}%", 25))
    elif aum_change <= -15:
        signals.append(Signal("资产", "近 90 天资产下降", "中", f"AUM 变动 {aum_change:.1f}%", 12))

    if txn_change <= -40:
        signals.append(Signal("交易", "交易频率明显下降", "高", f"交易频率变动 {txn_change:.1f}%", 18))
    elif txn_change <= -20:
        signals.append(Signal("交易", "交易频率下降", "中", f"交易频率变动 {txn_change:.1f}%", 9))

    if app_change <= -50:
        signals.append(Signal("渠道", "移动渠道活跃明显下降", "中", f"活跃天数变动 {app_change:.1f}%", 10))

    if not salary_active:
        signals.append(Signal("交易", "工资代发中断", "高", "近一期未识别工资代发入账", 20))

    if product_exit_count >= 2:
        signals.append(Signal("产品", "近期出现多项产品退出", "高", f"180 天退出产品数 {product_exit_count}", 20))
    elif product_exit_count == 1:
        signals.append(Signal("产品", "近期出现产品退出", "中", "180 天内至少 1 项产品退出", 10))

    if external_transfer_ratio >= 0.6:
        signals.append(Signal("竞品", "外部转移比例较高", "高", f"外部转移比例 {external_transfer_ratio:.2f}", 22))
    elif external_transfer_ratio >= 0.35:
        signals.append(Signal("竞品", "外部转移比例上升", "中", f"外部转移比例 {external_transfer_ratio:.2f}", 11))

    if touch_no_response >= 3:
        signals.append(Signal("关系", "多次触达未响应", "中", f"60 天未响应次数 {touch_no_response}", 10))

    if complaint_count >= 1:
        severity = "高" if complaint_count >= 2 else "中"
        score = 15 if complaint_count >= 2 else 8
        signals.append(Signal("服务", "近期存在投诉或负反馈", severity, f"180 天投诉数 {complaint_count}", score))

    total_score = sum(item.score for item in signals)
    if total_score >= 70:
        level = "紧急"
    elif total_score >= 45:
        level = "高"
    elif total_score >= 20:
        level = "中"
    else:
        level = "低"

    return {
        "customer_id": record.get("customer_id", ""),
        "warning_level": level,
        "overall_score": total_score,
        "signals": [asdict(s) for s in signals],
    }


if __name__ == "__main__":
    sample = {
        "customer_id": "C001",
        "aum_change_pct_90d": -26,
        "txn_freq_change_pct_90d": -33,
        "app_active_days_change_pct_90d": -52,
        "salary_inflow_active": False,
        "product_exit_count_180d": 1,
        "external_transfer_ratio_90d": 0.42,
        "touch_no_response_count_60d": 4,
        "complaint_count_180d": 1,
    }
    print(json.dumps(detect_signals(sample), ensure_ascii=False, indent=2))
