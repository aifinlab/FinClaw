#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于公网可查数据的上市公司披露完整性校验脚本。

功能概述：
1. 查询官方法规/交易所规则元数据；
2. 通过巨潮资讯公开接口搜索上市公司公告；
3. 下载最新定期报告 PDF；
4. 解析文本并根据预置检查清单进行“披露完整性”关键词校验；
5. 输出 JSON 报告，给出命中项、疑似缺失项与风险提示。

说明：
- 本脚本做的是“规则驱动 + 关键词/正则”的研究型完整性校验；
- 不能替代律师、保荐机构、审计师或交易所正式审核；
- 巨潮资讯接口/页面结构可能调整，如失效需相应修改。
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import textwrap
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import requests

try:
    import pdfplumber
except Exception:
    pdfplumber = None


TIMEOUT = 30
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/123.0 Safari/537.36"
)

CNINFO_SEARCH_URL = "https://www.cninfo.com.cn/new/hisAnnouncement/query"
CNINFO_PDF_BASE = "https://static.cninfo.com.cn/"


LAW_SOURCES = [
    {
        "name": "上市公司信息披露管理办法（证监会令第226号）",
        "url": "https://www.csrc.gov.cn/csrc/c101953/c7547359/content.shtml",
        "issuer": "中国证监会",
        "effective_date": "2025-07-01",
        "category": "部门规章",
    },
    {
        "name": "公开发行证券的公司信息披露内容与格式准则第2号——年度报告的内容与格式",
        "url": "https://www.csrc.gov.cn/csrc/c101954/c7547588/content.shtml",
        "issuer": "中国证监会",
        "effective_date": "2025-07-01",
        "category": "内容与格式准则",
    },
    {
        "name": "公开发行证券的公司信息披露内容与格式准则第3号——半年度报告的内容与格式",
        "url": "https://www.csrc.gov.cn/csrc/c101954/c7547590/content.shtml",
        "issuer": "中国证监会",
        "effective_date": "2025-07-01",
        "category": "内容与格式准则",
    },
    {
        "name": "上海证券交易所股票上市规则（2025年4月修订）",
        "url": "https://www.sse.com.cn/services/listingwithsse/home/policy/supervise/c/c_20250515_10779023.shtml",
        "issuer": "上海证券交易所",
        "effective_date": "2025-04-25",
        "category": "交易所规则",
    },
    {
        "name": "深圳证券交易所股票上市规则（2025年修订）",
        "url": "https://www.szse.cn/lawrules/rule/stock/listing/t20250425_614980.html",
        "issuer": "深圳证券交易所",
        "effective_date": "2025-04-25",
        "category": "交易所规则",
    },
    {
        "name": "巨潮资讯（上市公司公告公开查询）",
        "url": "https://www.cninfo.com.cn/",
        "issuer": "巨潮资讯",
        "effective_date": "N/A",
        "category": "公告披露平台",
    },
]


CHECKLISTS: Dict[str, List[Dict[str, object]]] = {
    "annual": [
        {
            "id": "basic_company_info",
            "title": "公司简介和主要财务指标",
            "patterns": [r"公司简介", r"主要会计数据", r"主要财务指标"],
            "level": "high",
            "desc": "年度报告通常应披露公司简介、主要会计数据和财务指标。",
        },
        {
            "id": "management_discussion",
            "title": "管理层讨论与分析",
            "patterns": [r"管理层讨论与分析", r"经营情况讨论与分析"],
            "level": "high",
            "desc": "年度报告通常应包含管理层讨论与分析（MD&A）章节。",
        },
        {
            "id": "major_risks",
            "title": "风险因素/可能面对的风险",
            "patterns": [r"风险因素", r"可能面对的风险", r"风险提示"],
            "level": "high",
            "desc": "年度报告通常应披露主要风险及应对措施。",
        },
        {
            "id": "governance",
            "title": "公司治理",
            "patterns": [r"公司治理", r"董事会", r"独立董事"],
            "level": "medium",
            "desc": "年度报告通常包含治理结构、董事会及专门委员会相关内容。",
        },
        {
            "id": "control_shareholder",
            "title": "控股股东及实际控制人",
            "patterns": [r"控股股东", r"实际控制人"],
            "level": "medium",
            "desc": "年度报告通常应说明控股股东和实际控制人情况。",
        },
        {
            "id": "related_party",
            "title": "关联交易",
            "patterns": [r"关联交易", r"日常关联交易"],
            "level": "medium",
            "desc": "存在相关事项时，年度报告一般应披露关联交易情况。",
        },
        {
            "id": "cash_dividend",
            "title": "利润分配/现金分红",
            "patterns": [r"利润分配", r"现金分红", r"分红"],
            "level": "medium",
            "desc": "年度报告通常会披露利润分配方案或分红政策执行情况。",
        },
        {
            "id": "auditor_opinion",
            "title": "审计报告/审计意见",
            "patterns": [r"审计报告", r"审计意见"],
            "level": "high",
            "desc": "年度报告通常包含审计报告或审计意见章节。",
        },
        {
            "id": "financial_statements",
            "title": "财务报表",
            "patterns": [r"资产负债表", r"利润表", r"现金流量表"],
            "level": "high",
            "desc": "年度报告通常应包含主要财务报表。",
        },
        {
            "id": "important_events",
            "title": "重大事项",
            "patterns": [r"重大事项", r"重大诉讼", r"重大合同"],
            "level": "medium",
            "desc": "年度报告通常会汇总报告期重大事项。",
        },
    ],
    "semiannual": [
        {
            "id": "basic_company_info",
            "title": "公司简介和主要财务指标",
            "patterns": [r"公司简介", r"主要会计数据", r"主要财务指标"],
            "level": "high",
            "desc": "半年度报告通常应披露公司简介、主要会计数据和财务指标。",
        },
        {
            "id": "management_discussion",
            "title": "管理层讨论与分析",
            "patterns": [r"管理层讨论与分析", r"经营情况讨论与分析"],
            "level": "high",
            "desc": "半年度报告通常应包含经营情况讨论。",
        },
        {
            "id": "major_risks",
            "title": "风险因素/风险提示",
            "patterns": [r"风险因素", r"风险提示", r"可能存在的风险"],
            "level": "medium",
            "desc": "半年度报告通常会披露当期主要风险。",
        },
        {
            "id": "important_events",
            "title": "重要事项",
            "patterns": [r"重要事项", r"重大事项"],
            "level": "medium",
            "desc": "半年度报告通常披露报告期重要事项。",
        },
        {
            "id": "financial_statements",
            "title": "财务报表",
            "patterns": [r"资产负债表", r"利润表", r"现金流量表"],
            "level": "high",
            "desc": "半年度报告通常应包含主要财务报表。",
        },
    ],
}


@dataclass
class CheckResult:
    item_id: str
    title: str
    level: str
    status: str
    matched_patterns: List[str]
    desc: str


class DisclosureCompletenessChecker:
    def __init__(self, cache_dir: str = ".cache") -> None:
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": USER_AGENT,
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Origin": "https://www.cninfo.com.cn",
                "Referer": "https://www.cninfo.com.cn/",
            }
        )
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def query_laws(self, keyword: Optional[str] = None) -> List[Dict[str, str]]:
        if not keyword:
            return LAW_SOURCES
        keyword_lower = keyword.lower()
        out = []
        for item in LAW_SOURCES:
            blob = " ".join(str(v) for v in item.values()).lower()
            if keyword_lower in blob:
                out.append(item)
        return out

    def search_announcements(
        self,
        stock: str,
        category: str = "category_ndbg_szsh;category_bndbg_szsh",
        page_num: int = 1,
        page_size: int = 30,
    ) -> List[Dict[str, object]]:
        payload = {
            "stock": stock,
            "tabName": "fulltext",
            "pageSize": page_size,
            "pageNum": page_num,
            "plate": "",
            "category": category,
            "trade": "",
            "column": "szse",
            "searchkey": "",
            "secid": "",
            "sortName": "",
            "sortType": "",
            "isHLtitle": "true",
        }
        r = self.session.post(CNINFO_SEARCH_URL, data=payload, timeout=TIMEOUT)
        r.raise_for_status()
        data = r.json()
        return data.get("announcements", [])

    def pick_latest_report(self, stock: str, report_type: str) -> Dict[str, object]:
        anns = self.search_announcements(stock=stock)
        normalized = report_type.lower()
        title_patterns = {
            "annual": [r"年度报告(?!摘要)", r"年报全文", r"年度报告全文"],
            "semiannual": [r"半年度报告(?!摘要)", r"半年报全文", r"半年度报告全文"],
        }
        candidates = []
        for ann in anns:
            title = str(ann.get("announcementTitle", ""))
            if any(re.search(p, title) for p in title_patterns.get(normalized, [])):
                candidates.append(ann)
        if not candidates:
            raise RuntimeError(f"未找到 {stock} 的 {report_type} 报告公告。")
        candidates.sort(key=lambda x: str(x.get("announcementTime", "")), reverse=True)
        return candidates[0]

    def download_pdf(self, adjunct_url: str, filename: Optional[str] = None) -> Path:
        pdf_url = adjunct_url if adjunct_url.startswith("http") else CNINFO_PDF_BASE + adjunct_url.lstrip("/")
        filename = filename or Path(adjunct_url).name or "report.pdf"
        out_path = self.cache_dir / filename
        with self.session.get(pdf_url, timeout=TIMEOUT, stream=True) as r:
            r.raise_for_status()
            with open(out_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 64):
                    if chunk:
                        f.write(chunk)
        return out_path

    def extract_pdf_text(self, pdf_path: Path, max_pages: Optional[int] = None) -> str:
        if pdfplumber is None:
            raise RuntimeError("缺少 pdfplumber，请先安装：pip install pdfplumber")
        pages_text: List[str] = []
        with pdfplumber.open(str(pdf_path)) as pdf:
            for i, page in enumerate(pdf.pages):
                if max_pages is not None and i >= max_pages:
                    break
                txt = page.extract_text() or ""
                pages_text.append(txt)
        return "\n".join(pages_text)

    @staticmethod
    def normalize_text(text: str) -> str:
        text = text.replace("\u3000", " ")
        text = re.sub(r"\s+", " ", text)
        return text

    def run_check(self, text: str, report_type: str) -> List[CheckResult]:
        normalized_text = self.normalize_text(text)
        results: List[CheckResult] = []
        for item in CHECKLISTS[report_type]:
            matched = []
            for pat in item["patterns"]:
                if re.search(str(pat), normalized_text, flags=re.IGNORECASE):
                    matched.append(str(pat))
            status = "present" if matched else "suspected_missing"
            results.append(
                CheckResult(
                    item_id=str(item["id"]),
                    title=str(item["title"]),
                    level=str(item["level"]),
                    status=status,
                    matched_patterns=matched,
                    desc=str(item["desc"]),
                )
            )
        return results

    @staticmethod
    def summarize(results: List[CheckResult]) -> Dict[str, object]:
        total = len(results)
        present = sum(1 for r in results if r.status == "present")
        missing = total - present
        high_missing = [asdict(r) for r in results if r.status != "present" and r.level == "high"]
        score = round((present / total) * 100, 2) if total else 0.0
        if high_missing:
            risk = "high"
        elif missing >= max(2, total // 3):
            risk = "medium"
        else:
            risk = "low"
        return {
            "total_items": total,
            "present_items": present,
            "suspected_missing_items": missing,
            "completeness_score": score,
            "risk_level": risk,
            "high_priority_gaps": high_missing,
        }


def build_output(
    stock: str,
    report_type: str,
    ann: Dict[str, object],
    pdf_path: Path,
    text_len: int,
    results: List[CheckResult],
) -> Dict[str, object]:
    summary = DisclosureCompletenessChecker.summarize(results)
    return {
        "stock": stock,
        "report_type": report_type,
        "announcement": {
            "title": ann.get("announcementTitle"),
            "date": ann.get("announcementTime"),
            "adjunct_url": ann.get("adjunctUrl"),
            "sec_code": ann.get("secCode"),
            "sec_name": ann.get("secName"),
        },
        "local_pdf": str(pdf_path),
        "text_length": text_len,
        "rules": LAW_SOURCES,
        "summary": summary,
        "details": [asdict(r) for r in results],
        "disclaimer": [
            "本结果为基于公开数据与关键词/正则的研究型校验，不构成法律意见。",
            "若 PDF 为扫描件、目录命名差异较大、章节表述不标准，可能出现误报或漏报。",
            "如需更高准确度，建议结合 OCR、表格抽取、LLM 审阅及人工复核。",
        ],
    }


def cli() -> int:
    parser = argparse.ArgumentParser(
        description="使用公网可查数据，对上市公司定期报告做披露完整性校验。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """
            示例：
              python script/disclosure_completeness_check.py \
                --stock 000001,平安银行 \
                --report-type annual \
                --max-pages 80 \
                --output output/pab_annual_check.json

              python script/disclosure_completeness_check.py --query-laws 信息披露
            """
        ),
    )
    parser.add_argument("--stock", help="股票代码或“代码,简称”，例如 000001,平安银行")
    parser.add_argument(
        "--report-type",
        choices=["annual", "semiannual"],
        default="annual",
        help="要校验的定期报告类型。",
    )
    parser.add_argument("--max-pages", type=int, default=80, help="最多解析的 PDF 页数。")
    parser.add_argument("--cache-dir", default=".cache", help="缓存目录。")
    parser.add_argument("--output", default="disclosure_check_result.json", help="输出 JSON 文件路径。")
    parser.add_argument("--query-laws", nargs="?", const="", help="仅查询预置法规/规则信息，可附关键词。")
    args = parser.parse_args()

    checker = DisclosureCompletenessChecker(cache_dir=args.cache_dir)

    if args.query_laws is not None:
        print(json.dumps(checker.query_laws(args.query_laws), ensure_ascii=False, indent=2))
        return 0

    if not args.stock:
        print("错误：未提供 --stock", file=sys.stderr)
        return 2

    try:
        ann = checker.pick_latest_report(stock=args.stock, report_type=args.report_type)
        pdf_path = checker.download_pdf(
            adjunct_url=str(ann["adjunctUrl"]),
            filename=f"{ann.get('secCode', 'stock')}_{args.report_type}.pdf",
        )
        text = checker.extract_pdf_text(pdf_path, max_pages=args.max_pages)
        results = checker.run_check(text=text, report_type=args.report_type)
        output = build_output(
            stock=args.stock,
            report_type=args.report_type,
            ann=ann,
            pdf_path=pdf_path,
            text_len=len(text),
            results=results,
        )
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(output["summary"], ensure_ascii=False, indent=2))
        print(f"\n已输出到: {out_path}")
        return 0
    except Exception as exc:
        print(f"执行失败: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(cli())
