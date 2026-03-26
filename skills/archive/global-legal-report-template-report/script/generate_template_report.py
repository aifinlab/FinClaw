from __future__ import annotations

from fetch_public_content import fetch_document
from pathlib import Path

from text_tools import find_lines, keyword_scores, pick_highlights, truncate_text
import argparse
import sys


def build_template_report(company: str, template: str, source_type: str, url: str, title: str, text: str) -> str:
    short_text = truncate_text(text)
    facts = pick_highlights(short_text, 8)
    rules = find_lines(short_text, [r"根据", r"依照", r"应当", r"不得", r"披露", r"公告"], 8)
    risks = find_lines(short_text, [r"风险", r"处罚", r"违规", r"责任", r"问询", r"监管"], 8)
    timing = find_lines(short_text, [r"\d{4}年\d{1,2}月\d{1,2}日", r"董事会", r"股东大会", r"生效", r"实施"], 8)
    quote_lines = facts[:3] + rules[:2]
    kws = [k for k, _ in keyword_scores(short_text, 12)]

    def fmt(items):
        return "\n".join(f"- {i}" for i in items) if items else "- 未识别"

    impact = []
    if risks:
        impact.append("存在需要重点复核的监管/合规风险表述。")
    if timing:
        impact.append("存在明确时间节点，适合纳入日程或台账管理。")
    if rules:
        impact.append("文本中包含可提炼为规则清单的要求。")
    if not impact:
        impact.append("建议由人工进一步阅读全文并补充判断。")

    return f"""# {template} 模板化报告

## 一、文件概况
- 公司/主体：{company or '未指定'}
- 文件标题：{title}
- 来源类型：{source_type}
- 来源地址：{url}
- 关键词：{', '.join(kws)}

## 二、关键事实
{fmt(facts)}

## 三、监管/规则要点
{fmt(rules)}

## 四、重要时间点
{fmt(timing)}

## 五、影响判断
{fmt(impact)}

## 六、待核事项
{fmt([
'核对原文全文与截取文本是否一致',
'核对是否存在后续修订、补充公告或问询回复',
'将涉及义务、截止日、责任主体转为结构化台账',
])}

## 七、引用片段
{fmt(quote_lines)}

## 八、交易说明
- 本报告仅用于公开信息整理、合规初筛、研究支持或客服辅助。
- 不构成投资建议、法律意见或对证券价格走势的保证。
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="生成法律条文或公司报告模板化报告")
    parser.add_argument("--url", required=True)
    parser.add_argument("--company", default="")
    parser.add_argument("--template", default="compliance_brief")
    parser.add_argument("--title", default="")
    parser.add_argument("--source-type", choices=["law", "report", "other"], default="other")
    parser.add_argument("--max-chars", type=int, default=15000)
    parser.add_argument("--output", default="template_report.md")
    args = parser.parse_args()

    doc = fetch_document(args.url)
    text = truncate_text(doc.text, args.max_chars)
    title = args.title or doc.title
    out = build_template_report(args.company, args.template, args.source_type, args.url, title, text)
    Path(args.output).write_text(out, encoding="utf-8")
    print(f"Saved: {args.output}")



def main():


        main()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n操作被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)