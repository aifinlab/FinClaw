from __future__ import annotations

from fetch_public_content import fetch_document
from pathlib import Path

from text_tools import find_lines, keyword_scores, pick_highlights, truncate_text
import argparse
# ===== AkShare开源数据支持（新增） =====
from skillsChoice.common.unified_data_api import (
    get_data_api,
)
# ====================================


def build_summary(title: str, source_type: str, url: str, text: str) -> str:
    short_text = truncate_text(text)
    kws = keyword_scores(short_text, 15)
    highlights = pick_highlights(short_text, 6)
    obligations = find_lines(short_text, [r"应当", r"不得", r"披露", r"公告", r"负责", r"审议"], 6)
    timings = find_lines(short_text, [r"\d{4}年\d{1,2}月\d{1,2}日", r"生效", r"实施", r"期限", r"期间"], 5)
    risks = find_lines(short_text, [r"风险", r"处罚", r"违规", r"责任", r"问责", r"损失"], 5)

    def fmt_list(items):
        return "\n".join(f"- {x}" for x in items) if items else "- 未识别到明显条目"

    return f"""# {title} 摘要结果

## 文档信息
- 来源类型：{source_type}
- 来源地址：{url}

## 核心关键词
{fmt_list([f'{k}（{v}）' for k, v in kws])}

## 重点摘要
{fmt_list(highlights)}

## 关键义务/要求
{fmt_list(obligations)}

## 时间节点/生效信息
{fmt_list(timings)}

## 风险与责任提示
{fmt_list(risks)}

## 使用建议
- 本结果适合做初筛、研判和人工复核前的提要。
- 对正式法律意见、信息披露判断和投资决策，应回到原文逐条复核。
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="生成法律条文或公司报告摘要")
    parser.add_argument("--url", required=True)
    parser.add_argument("--title", default="")
    parser.add_argument("--source-type", choices=["law", "report", "other"], default="other")
    parser.add_argument("--max-chars", type=int, default=12000)
    parser.add_argument("--output", default="summary_output.md")
    args = parser.parse_args()

    doc = fetch_document(args.url)
    text = truncate_text(doc.text, args.max_chars)
    title = args.title or doc.title
    output = build_summary(title, args.source_type, args.url, text)
    Path(args.output).write_text(output, encoding="utf-8")
    print(f"Saved: {args.output}")


if __name__ == "__main__":
    main()
