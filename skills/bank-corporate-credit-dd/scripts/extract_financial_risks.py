#!/usr/bin/env python3
"""Simple rule-based financial red flag extractor for due diligence.

Usage:
    python extract_financial_risks.py financials.json > risks.json

Input example:
{
  "revenue_growth": 0.35,
  "profit_growth": 0.02,
  "accounts_receivable_growth": 0.70,
  "inventory_growth": 0.55,
  "operating_cashflow": -1200000,
  "net_profit": 800000,
  "current_ratio": 0.85,
  "debt_to_asset_ratio": 0.78
}
"""

from __future__ import annotations

from typing import Any, Dict, List
import json
import sys


def analyze(data: Dict[str, Any]) -> List[Dict[str, str]]:
    risks: List[Dict[str, str]] = []

    ar_growth = data.get("accounts_receivable_growth")
    inv_growth = data.get("inventory_growth")
    ocf = data.get("operating_cashflow")
    net_profit = data.get("net_profit")
    current_ratio = data.get("current_ratio")
    debt_ratio = data.get("debt_to_asset_ratio")
    revenue_growth = data.get("revenue_growth")
    profit_growth = data.get("profit_growth")

    if isinstance(ar_growth, (int, float)) and ar_growth > 0.4:
        risks.append({
            "risk_dimension": "财务质量",
            "risk_description": "应收账款增长过快，需关注收入确认质量与回款压力。",
            "recommended_check": "核验前五大客户回款、账龄结构与合同验收单据。"
        })

    if isinstance(inv_growth, (int, float)) and inv_growth > 0.4:
        risks.append({
            "risk_dimension": "运营周转",
            "risk_description": "存货增长较快，需关注库存积压与减值风险。",
            "recommended_check": "检查存货结构、库龄、跌价准备与出库销售匹配情况。"
        })

    if isinstance(ocf, (int, float)) and isinstance(net_profit, (int, float)) and ocf < 0 and net_profit > 0:
        risks.append({
            "risk_dimension": "现金流",
            "risk_description": "经营现金流为负但账面利润为正，存在利润与现金流背离。",
            "recommended_check": "结合流水、应收应付、预收预付明细核验盈利质量。"
        })

    if isinstance(current_ratio, (int, float)) and current_ratio < 1:
        risks.append({
            "risk_dimension": "短期偿债",
            "risk_description": "流动比率偏低，短期偿债压力较大。",
            "recommended_check": "梳理短期债务到期结构和备用流动性来源。"
        })

    if isinstance(debt_ratio, (int, float)) and debt_ratio > 0.75:
        risks.append({
            "risk_dimension": "杠杆水平",
            "risk_description": "资产负债率较高，杠杆压力偏大。",
            "recommended_check": "补充融资结构、担保负担与债务续作安排。"
        })

    if isinstance(revenue_growth, (int, float)) and isinstance(profit_growth, (int, float)):
        if revenue_growth > 0.3 and profit_growth < 0.05:
            risks.append({
                "risk_dimension": "盈利能力",
                "risk_description": "收入增长较快但利润未同步增长，需关注毛利率与成本确认。",
                "recommended_check": "分析毛利率变动、费用率变化及异常交易。"
            })

    return risks


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python extract_financial_risks.py financials.json", file=sys.stderr)
        return 1

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        print("Input JSON must be an object.", file=sys.stderr)
        return 1

    risks = analyze(data)
    json.dump(risks, sys.stdout, ensure_ascii=False, indent=2)
    return 0



def main():


        raise SystemExit(main())


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n操作被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)