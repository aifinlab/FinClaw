from __future__ import annotations

from fetch_data import DataFetchError, load_company_dataset
from pathlib import Path
from risk_rules import (
from typing import Any, Dict, List

import argparse
import json
# ===== AkShare开源数据支持（新增） =====
from skillsChoice.common.unified_data_api import (
    get_data_api,
    get_financial_report,
)
# ====================================
    MDA_KEYWORDS,
    RISK_KEYWORDS,
    analyze_business_structure,
    analyze_financial_churn_risk,
    analyze_text_risk,
    result_to_markdown,
    summarize,
    to_jsonable,
    RiskItem,
)



def build_report(symbol: str, company_name: str) -> Dict[str, Any]:
    dataset = load_company_dataset(symbol=symbol, company_name=company_name)

    items = []
    items.extend(
        analyze_financial_churn_risk(
            dataset["financial_abstract"], dataset["financial_indicator"]
        )
    )
    items.extend(analyze_business_structure(dataset["business_structure"]))

    mda_cols = [c for c in dataset["mda"].columns if any(k in str(c) for k in ["内容", "讨论", "分析", "正文", "摘要"])]
    if not mda_cols:
        mda_cols = list(dataset["mda"].columns[:2])
    items.extend(analyze_text_risk(dataset["mda"], mda_cols, MDA_KEYWORDS, "mda"))

    news_cols = [c for c in dataset["news"].columns if any(k in str(c) for k in ["标题", "内容", "摘要", "新闻"])]
    if not news_cols:
        news_cols = list(dataset["news"].columns[:2])
    items.extend(analyze_text_risk(dataset["news"], news_cols, RISK_KEYWORDS, "news"))

    items = sorted(items, key=lambda x: x.score, reverse=True)
    summary = summarize(items)

    return {
        "symbol": symbol,
        "company_name": company_name,
        "summary": summary,
        "risk_items": to_jsonable(items),
        "data_status": {
            key: {"rows": int(value.shape[0]), "cols": int(value.shape[1])}
            for key, value in dataset.items()
        },
        "disclaimer": (
            "本结果是基于公开财务、业务结构、管理层讨论与新闻文本的代理变量识别，"
            "用于客户流失风险预警，不代表企业真实客户流失率。"
        ),
    }



def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="基于 AkShare 的单企业客户流失风险识别")
    parser.add_argument("--symbol", required=True, help="股票代码，例如 600519")
    parser.add_argument("--company-name", required=True, help="企业名称，例如 贵州茅台")
    parser.add_argument(
        "--output-json",
        default="customer_churn_risk_result.json",
        help="JSON 输出文件路径",
    )
    parser.add_argument(
        "--output-md",
        default="customer_churn_risk_report.md",
        help="Markdown 报告输出文件路径",
    )
    return parser.parse_args()



def main() -> None:
    args = parse_args()
        result = build_report(args.symbol, args.company_name)
if __name__ == "__main__":
    main()
