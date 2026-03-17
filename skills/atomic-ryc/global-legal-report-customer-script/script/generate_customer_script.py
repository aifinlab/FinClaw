from __future__ import annotations

import argparse
from pathlib import Path

from fetch_public_content import fetch_document
from text_tools import find_lines, pick_highlights, truncate_text

AUDIENCE_MAP = {
    "investor": "投资者/股东",
    "customer": "普通客户",
    "internal": "内部同事/一线坐席",
}


def build_script(audience: str, tone: str, source_type: str, url: str, title: str, text: str) -> str:
    short_text = truncate_text(text)
    summary = pick_highlights(short_text, 5)
    risk_lines = find_lines(short_text, [r"风险", r"处罚", r"违规", r"责任", r"不确定"], 5)
    timing = find_lines(short_text, [r"\d{4}年\d{1,2}月\d{1,2}日", r"生效", r"实施", r"截止"], 4)

    one_liner = summary[0] if summary else "该事项涉及公开文件内容，建议以原始公告/法规原文为准。"
    standard_answer = "；".join(summary[:3]) if summary else one_liner
    concise_answer = one_liner
    escalation = "该问题涉及具体法律适用、投资判断或个案差异，建议升级至法务/合规/投关专员进一步确认。"
    forbidden = [
        "不得承诺收益、保证结果或替代正式法律意见。",
        "不得脱离原文擅自扩大解释。",
        "不得隐瞒已公开披露的关键风险与限制。",
    ]

    def fmt(items):
        return "\n".join(f"- {i}" for i in items) if items else "- 无"

    return f"""# 客服话术生成结果

## 场景信息
- 受众：{AUDIENCE_MAP.get(audience, audience)}
- 语气：{tone}
- 来源类型：{source_type}
- 文件标题：{title}
- 来源地址：{url}

## 标准答复
您好，关于您咨询的事项，我们根据公开文件初步整理如下：{standard_answer}。如需正式口径，请以披露原文或正式法规文本为准。

## 简版答复
您好，目前公开信息显示：{concise_answer}

## 风险提示语
{fmt(risk_lines or ['该答复仅基于公开可查文本自动整理，不构成法律意见或投资建议。'])}

## 时间节点提醒
{fmt(timing or ['未自动识别到明确时间节点，请人工复核原文。'])}

## 升级转接语
- {escalation}

## 禁说清单
{fmt(forbidden)}
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="生成法律条文或公司报告客服话术")
    parser.add_argument("--url", required=True)
    parser.add_argument("--audience", choices=["investor", "customer", "internal"], default="investor")
    parser.add_argument("--tone", default="professional")
    parser.add_argument("--title", default="")
    parser.add_argument("--source-type", choices=["law", "report", "other"], default="other")
    parser.add_argument("--max-chars", type=int, default=12000)
    parser.add_argument("--output", default="customer_script.md")
    args = parser.parse_args()

    doc = fetch_document(args.url)
    text = truncate_text(doc.text, args.max_chars)
    title = args.title or doc.title
    out = build_script(args.audience, args.tone, args.source_type, args.url, title, text)
    Path(args.output).write_text(out, encoding="utf-8")
    print(f"Saved: {args.output}")


if __name__ == "__main__":
    main()
