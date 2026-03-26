#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
上市公司披露替代表述生成（公网可查数据版）
"""

from __future__ import annotations

from typing import Dict, List
import argparse
import datetime as dt
import json
import re

import requests

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/123.0 Safari/537.36"
)

REGULATION_BASELINES = [
    {
        "title": "上市公司信息披露管理办法（证监会令第182号）",
        "issuer": "中国证监会",
        "scope": "信息披露的一般真实性、准确性、完整性、及时性与公平披露要求",
        "url": "https://www.csrc.gov.cn/csrc/c101864/c2ee1a791fddc4f5ebeeb70aa8e2399cf/content.shtml",
    },
    {
        "title": "公开发行证券的公司信息披露内容与格式准则第2号——年度报告的内容与格式（2021年修订）",
        "issuer": "中国证监会",
        "scope": "年度报告章节、风险因素、重大事项、财务与治理披露口径",
        "url": "https://www.csrc.gov.cn/csrc/c101864/c6df1268b5b294448bdec7e010d880a01/content.shtml",
    },
    {
        "title": "上海证券交易所股票上市规则（2025年4月修订）",
        "issuer": "上海证券交易所",
        "scope": "上交所上市公司持续信息披露、自愿披露、重大事项等要求",
        "url": "https://www.sse.com.cn/lawandrules/sselawsrules2025/stocks/mainipo/c/c_20250515_10779023.shtml",
    },
    {
        "title": "深圳证券交易所上市公司自律监管指引第11号——信息披露工作评价（2025年修订）",
        "issuer": "深圳证券交易所",
        "scope": "深市信息披露质量评价、规范性与可读性参考",
        "url": "https://docs.static.szse.cn/www/lawrules/rule/stock/supervision/W020250314612975887908.pdf",
    },
]

CNINFO_QUERY_URL = "https://www.cninfo.com.cn/new/hisAnnouncement/query"

RISK_PATTERNS = [
    {
        "name": "弱化不利事实",
        "pattern": re.compile(r"(短期波动|阶段性承压|存在一定压力|有所下降|略有下滑|受到一定影响)"),
        "reason": "存在使用模糊词弱化不利事实的风险，建议补充量化影响与时间范围。",
    },
    {
        "name": "缺少时间边界",
        "pattern": re.compile(r"(近期|后续|未来|尽快|及时|适时)"),
        "reason": "存在时间表述模糊风险，建议明确期间、日期或触发条件。",
    },
    {
        "name": "缺少量化口径",
        "pattern": re.compile(r"(较大|明显|显著|一定程度|较快|持续)"),
        "reason": "存在定性多、定量少的问题，建议补充比例、金额、区间或同比环比口径。",
    },
    {
        "name": "预测性表述风险",
        "pattern": re.compile(r"(必将|一定会|确保|全面实现|不会产生重大影响)"),
        "reason": "可能构成过度确定性表述，建议改为审慎、条件化表达。",
    },
]

REWRITE_RULES = [
    (re.compile(r"不会产生重大影响"), "预计不会对公司经营业绩产生重大不利影响，但仍存在不确定性，公司将根据后续进展及时履行信息披露义务"),
    (re.compile(r"存在一定压力"), "对公司经营指标可能带来阶段性影响，具体影响程度以公司后续披露的定期报告或临时公告为准"),
    (re.compile(r"短期波动"), "在相关期间内出现波动，波动原因、影响范围及持续时间请结合本公告披露的业务、财务与市场因素综合判断"),
    (re.compile(r"及时推进"), "按照既定计划推进，并根据实际进展情况及时履行审议程序和信息披露义务"),
    (re.compile(r"后续"), "在后续具体实施期间"),
    (re.compile(r"近期"), "在最近一个报告期/最近三个月内"),
    (re.compile(r"显著"), "达到公司内部监测阈值或具有较为明显的变化特征"),
    (re.compile(r"确保"), "争取"),
]


def fetch_regulations() -> List[Dict[str, str]]:
    return REGULATION_BASELINES


def normalize_stock_code(code: str) -> str:
    code = re.sub(r"\D", "", code or "")
    if len(code) == 6:
        return code
    raise ValueError("股票代码应为6位数字，例如 600519 或 000001")


def query_cninfo_announcements(stock_code: str, start_date: str, end_date: str, page_size: int = 20) -> List[Dict]:
    headers = {
        "User-Agent": UA,
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://www.cninfo.com.cn/new/commonUrl/pageOfSearch?url=disclosure/list/search",
        "X-Requested-With": "XMLHttpRequest",
    }
    data = {
        "pageNum": 1,
        "pageSize": page_size,
        "column": "szse",
        "tabName": "fulltext",
        "plate": "",
        "stock": f"{stock_code},",
        "searchkey": "",
        "secid": "",
        "category": "",
        "trade": "",
        "seDate": f"{start_date}~{end_date}",
        "sortName": "",
        "sortType": "",
        "isHLtitle": "true",
    }
    resp = requests.post(CNINFO_QUERY_URL, headers=headers, data=data, timeout=20)
    resp.raise_for_status()
    payload = resp.json()
    results = []
    for item in payload.get("announcements", []) or []:
        results.append(
            {
                "title": item.get("announcementTitle"),
                "date": item.get("announcementTime"),
                "adjunctUrl": item.get("adjunctUrl"),
                "secName": item.get("secName"),
                "secCode": item.get("secCode"),
            }
        )
    return results


def convert_timestamp(ms):
    if ms is None:
        return None
    try:
        return dt.datetime.fromtimestamp(ms / 1000).strftime("%Y-%m-%d")
    except Exception:
        return str(ms)


def detect_risks(text: str) -> List[Dict[str, str]]:
    findings = []
    for item in RISK_PATTERNS:
        if item["pattern"].search(text):
            findings.append({"risk_tag": item["name"], "reason": item["reason"]})
    if not re.search(r"(元|万元|亿元|%|同比|环比|\d+)", text):
        findings.append({"risk_tag": "量化信息不足", "reason": "文本未明显包含金额、比例或同比环比数据，可考虑补充量化口径。"})
    if not re.search(r"(公司将|公司已|董事会|审议|披露义务|公告)", text):
        findings.append({"risk_tag": "治理或程序口径不足", "reason": "可考虑补充董事会/股东会审议、进展节点或持续披露安排。"})
    return findings


def rewrite_text(text: str) -> str:
    rewritten = text.strip()
    for pattern, repl in REWRITE_RULES:
        rewritten = pattern.sub(repl, rewritten)
    if "不确定性" not in rewritten:
        if rewritten.endswith("。"):
            rewritten = rewritten[:-1] + "，相关事项仍存在不确定性，公司将根据进展情况及时履行信息披露义务。"
        else:
            rewritten = rewritten + "，相关事项仍存在不确定性，公司将根据进展情况及时履行信息披露义务。"
    return rewritten


def build_result(company: str, stock_code: str, raw_text: str, start_date: str, end_date: str) -> Dict:
    regulations = fetch_regulations()
    risks = detect_risks(raw_text)
    rewritten = rewrite_text(raw_text)
    announcements = []
    announcement_error = None
    try:
        announcements = query_cninfo_announcements(stock_code, start_date, end_date)
        for item in announcements:
            item["date"] = convert_timestamp(item["date"])
    except Exception as e:
        announcement_error = str(e)

    return {
        "company": company,
        "stock_code": stock_code,
        "input_text": raw_text,
        "suggested_rewrite": rewritten,
        "risk_findings": risks,
        "regulation_baselines": regulations,
        "recent_announcements": announcements,
        "announcement_fetch_error": announcement_error,
        "compliance_notice": "本结果仅用于规范化表述和初步合规检查，不得用于隐瞒、淡化或替代依法应当披露的重大事实。",
    }


def main():
    parser = argparse.ArgumentParser(description="上市公司披露替代表述生成工具")
    parser.add_argument("--company", required=True, help="企业名称，例如 贵州茅台")
    parser.add_argument("--stock-code", required=True, help="6位股票代码，例如 600519")
    parser.add_argument("--text", required=True, help="待改写的原始披露文本")
    parser.add_argument("--start-date", default="2025-01-01", help="公告查询起始日期 YYYY-MM-DD")
    parser.add_argument("--end-date", default=dt.date.today().strftime("%Y-%m-%d"), help="公告查询结束日期 YYYY-MM-DD")
    parser.add_argument("--output", default="", help="输出 JSON 文件路径")
    args = parser.parse_args()

    stock_code = normalize_stock_code(args.stock_code)
    result = build_result(args.company, stock_code, args.text, args.start_date, args.end_date)
    result_json = json.dumps(result, ensure_ascii=False, indent=2)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(result_json)
        print(f"结果已写入: {args.output}")
    else:
        print(result_json)


if __name__ == "__main__":
    main()
