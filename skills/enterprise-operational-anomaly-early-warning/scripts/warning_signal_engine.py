#!/usr/bin/env python3
"""企业贷后预警信号识别示例脚本。"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


def _ratio_change(curr: float | None, prev: float | None) -> float | None:
    if curr is None or prev is None or prev == 0:
        return None
    return (curr - prev) / abs(prev)


def detect_warning_signals(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    signals: List[Dict[str, Any]] = []

    revenue = data.get("revenue", {})
    rev_change = _ratio_change(revenue.get("current"), revenue.get("previous"))
    if rev_change is not None and rev_change <= -0.2:
        signals.append({
            "维度": "经营异常",
            "信号": "营业收入明显下滑",
            "描述": f"本期收入较上期下降 {rev_change:.1%}",
            "严重程度": "中",
            "已核验": False,
        })

    ocf = data.get("operating_cash_flow", {})
    if ocf.get("current") is not None and ocf.get("current") < 0:
        signals.append({
            "维度": "财务异常",
            "信号": "经营性现金流为负",
            "描述": f"本期经营性现金流为 {ocf['current']}",
            "严重程度": "高" if ocf.get("continuous_negative") else "中",
            "已核验": False,
        })

    ar_days = data.get("ar_days", {})
    ar_days_change = _ratio_change(ar_days.get("current"), ar_days.get("previous"))
    if ar_days_change is not None and ar_days_change >= 0.2:
        signals.append({
            "维度": "经营异常",
            "信号": "回款周期拉长",
            "描述": f"应收周转天数较上期上升 {ar_days_change:.1%}",
            "严重程度": "中",
            "已核验": False,
        })

    account = data.get("account_flow", {})
    acc_change = _ratio_change(account.get("current"), account.get("previous"))
    if acc_change is not None and acc_change <= -0.3:
        signals.append({
            "维度": "账户与交易异常",
            "信号": "账户流水明显收缩",
            "描述": f"主要账户流水较上期下降 {acc_change:.1%}",
            "严重程度": "中",
            "已核验": False,
        })

    litigation = data.get("litigation", {})
    if litigation.get("new_cases", 0) > 0:
        signals.append({
            "维度": "外部风险异常",
            "信号": "新增涉诉事项",
            "描述": f"近期新增涉诉 {litigation['new_cases']} 起",
            "严重程度": "高" if litigation.get("material") else "中",
            "已核验": False,
        })

    mgmt = data.get("management_change", {})
    if mgmt.get("recent_change"):
        signals.append({
            "维度": "外部风险异常",
            "信号": "管理层或实控人发生变化",
            "描述": mgmt.get("description", "近期存在管理层或实控人变动"),
            "严重程度": "中",
            "已核验": False,
        })

    repayment = data.get("repayment", {})
    if repayment.get("interest_delay") or repayment.get("principal_delay"):
        signals.append({
            "维度": "履约与授信异常",
            "信号": "履约出现迟缓迹象",
            "描述": "存在付息或还本延迟情况",
            "严重程度": "高",
            "已核验": True,
        })

    return signals


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="识别企业贷后预警信号")
    parser.add_argument("input", help="输入 JSON 文件路径")
    parser.add_argument("-o", "--output", help="输出 JSON 文件路径")
    args = parser.parse_args()

    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    result = detect_warning_signals(data)
    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
    else:
        print(output)


if __name__ == "__main__":
    main()
