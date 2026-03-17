
import argparse
import os
from collections import Counter
from typing import Dict, List

from common import save_json


def segment_customers_proxy(company: str, ticker: str, market: str = "cn") -> Dict:
    # 示例：实际项目可替换为从年报、招股书、客户案例、评论数据中抽取的标签
    proxies = [
        {"segment": "大客户/高集中度", "evidence": "前五大客户与重大合同公告线索", "size_proxy": 5},
        {"segment": "区域型客户", "evidence": "年报分地区收入与项目分布", "size_proxy": 8},
        {"segment": "行业型客户", "evidence": "行业解决方案/客户案例页面", "size_proxy": 6},
        {"segment": "长尾客户", "evidence": "公开评论、渠道页面、服务覆盖线索", "size_proxy": 20},
    ]
    return {
        "company": company,
        "ticker": ticker,
        "market": market,
        "method": "公开数据代理分群（规则+聚类占位）",
        "segments": proxies,
        "warning": "结果不等同企业内部 CRM 客户主数据，仅用于研究与演示。"
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--company", required=True)
    parser.add_argument("--ticker", default="")
    parser.add_argument("--market", default="cn")
    parser.add_argument("--output", default="output/customer_segments.json")
    args = parser.parse_args()

    result = segment_customers_proxy(args.company, args.ticker, args.market)
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    save_json(args.output, result)
    print(f"saved to {args.output}")


if __name__ == "__main__":
    main()
