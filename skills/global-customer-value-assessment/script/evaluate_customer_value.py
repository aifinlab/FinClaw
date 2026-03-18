
import argparse
import os
from typing import Dict, List

from common import save_json


def score_customer_value_proxy(company: str, ticker: str, market: str = "cn", topn: int = 10) -> Dict:
    rows = []
    for i in range(1, topn + 1):
        rows.append({
            "customer_group": f"客户群{i}",
            "revenue_contrib_proxy": max(1, 100 - i * 7),
            "stability_proxy": max(1, 90 - i * 5),
            "growth_proxy": max(1, 80 - i * 4),
            "concentration_risk": min(100, 20 + i * 6),
            "value_score": round((100 - i * 3) * 0.5 + (80 - i * 2) * 0.3 - (20 + i * 6) * 0.2, 2),
            "evidence": "由年报客户集中度、重大合同、区域/行业线索和公开口碑指标合成",
        })
    return {
        "company": company,
        "ticker": ticker,
        "market": market,
        "method": "公开数据代理价值评估",
        "rows": rows,
        "warning": "不是内部真实客户价值台账，分数仅作研究辅助。"
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--company", required=True)
    parser.add_argument("--ticker", default="")
    parser.add_argument("--market", default="cn")
    parser.add_argument("--topn", type=int, default=10)
    parser.add_argument("--output", default="output/customer_value.json")
    args = parser.parse_args()

    result = score_customer_value_proxy(args.company, args.ticker, args.market, args.topn)
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    save_json(args.output, result)
    print(f"saved to {args.output}")


if __name__ == "__main__":
    main()
