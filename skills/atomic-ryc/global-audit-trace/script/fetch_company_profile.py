import argparse
from typing import Dict, List, Optional

from common import clean_text, extract_first, fetch_pdf_text, fetch_text, keyword_hits, parse_args_common, save_json


FIELD_PATTERNS = {
    "company_name": [r"公司名称[:：]?\s*([^\n]{2,80})", r"中文名称[:：]?\s*([^\n]{2,80})"],
    "stock_code": [r"股票代码[:：]?\s*([0-9]{6})", r"证券代码[:：]?\s*([0-9]{6})"],
    "stock_short_name": [r"股票简称[:：]?\s*([^\n ]{2,30})", r"证券简称[:：]?\s*([^\n ]{2,30})"],
    "board_secretary": [r"董事会秘书[\s\S]{0,40}?姓名\s*([^\n]{2,30})", r"董事会秘书[:：]?\s*([^\n]{2,30})"],
    "office_address": [r"办公地址\s*([^\n]{5,120})"],
    "phone": [r"电话\s*([0-9\-]{6,30})"],
    "email": [r"电子信箱\s*([A-Za-z0-9_.\-]+@[A-Za-z0-9_.\-]+)"],
    "audit_firm": [r"会计师事务所[:：]?\s*([^\n]{4,80})", r"审计机构[:：]?\s*([^\n]{4,80})"],
    "audit_opinion": [r"审计意见[:：]?\s*([^\n]{2,40})", r"非标准审计意见提示\s*([^\n]{1,20})"],
}


AUDIT_KEYWORDS = [
    "审计报告",
    "内部控制自我评价报告",
    "内部控制评价报告",
    "内部控制审计报告",
    "信息披露管理制度",
    "内部审计制度",
    "审计委员会",
    "董事会",
    "监事会",
]


def parse_fields(text: str) -> Dict:
    result = {}
    for field, patterns in FIELD_PATTERNS.items():
        result[field] = extract_first(patterns, text)
    return result


def run(company_name: str, stock_code: str, annual_report_url: str, company_site: Optional[str]) -> Dict:
    annual_payload = fetch_pdf_text(annual_report_url)
    annual_text = clean_text(annual_payload["text"])
    profile = parse_fields(annual_text)
    profile["input_company_name"] = company_name
    profile["input_stock_code"] = stock_code
    profile["annual_report_url"] = annual_report_url

    traces: List[Dict] = [annual_payload["trace"]]
    website_info = None
    if company_site:
        try:
            site_payload = fetch_text(company_site)
            site_text = clean_text(site_payload["text"])
            website_info = {
                "url": company_site,
                "keywords": keyword_hits(site_text, [company_name, stock_code, "投资者关系", "公司治理", "审计", "内控", "信息披露"]),
            }
            traces.append(site_payload["trace"])
        except Exception as exc:
            website_info = {"url": company_site, "error": str(exc)}

    return {
        "company_name": company_name,
        "stock_code": stock_code,
        "profile": profile,
        "annual_report_keyword_hits": keyword_hits(annual_text, AUDIT_KEYWORDS),
        "website_info": website_info,
        "trace": traces,
    }


if __name__ == "__main__":
    parser = parse_args_common("抓取上市公司公开资料")
    parser.add_argument("--company-name", required=True)
    parser.add_argument("--stock-code", required=True)
    parser.add_argument("--annual-report-url", required=True)
    parser.add_argument("--company-site", default=None)
    args = parser.parse_args()

    result = run(
        company_name=args.company_name,
        stock_code=args.stock_code,
        annual_report_url=args.annual_report_url,
        company_site=args.company_site,
    )
    save_json(result, args.output)
    print(f"saved: {args.output}")
