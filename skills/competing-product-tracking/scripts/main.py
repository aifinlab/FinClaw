#!/usr/bin/env python3
from pathlib import Path
import argparse
import json
import re

SKILL_META = {
  "display_name": "竞品产品追踪助手",
  "domain": "产品管理",
  "scene": "竞品追踪",
  "description": "竞品产品追踪助手 - 产品管理/竞品追踪"
}
CATEGORIES = ["analysis", "product"]

POSITIVE_WORDS = ["领先", "稳定", "改善", "提升", "超额", "回撤控制", "规模提升", "费率优势", "风格一致"]
NEGATIVE_WORDS = ["下滑", "恶化", "回撤扩大", "偏离", "集中", "赎回", "波动", "争议", "违规"]


def load_text(path: str, raw_text: str) -> str:
    if raw_text:
        return raw_text
    if not path:
        return ""
    return Path(path).read_text(encoding="utf-8", errors="ignore")


def extract_basic(text: str, fund_code: str, fund_name: str) -> dict:
    if not fund_code:
        match = re.search(r"\d{6}", text)
        fund_code = match.group(0) if match else ""
    if not fund_name:
        name_match = re.search(r"([一-鿿A-Za-z0-9]+(基金|FOF|ETF|REITs))", text)
        fund_name = name_match.group(0) if name_match else ""
    return {
        "fund_code": fund_code,
        "fund_name": fund_name,
        "text_length": len(text),
    }


def keyword_hits(text: str, words: list) -> list:
    return [w for w in words if w in text]


def build_output(text: str, fund_code: str, fund_name: str) -> dict:
    base = {
        "skill": SKILL_META["display_name"],
        "domain": SKILL_META["domain"],
        "scene": SKILL_META["scene"],
        "input_summary": extract_basic(text, fund_code, fund_name),
        "key_findings": [],
        "data_quality": {
            "has_text": bool(text.strip()),
            "text_length": len(text),
        },
        "limitations": ["仅基于输入文本进行初步结构化输出。"],
    }

    pos_hits = keyword_hits(text, POSITIVE_WORDS)
    neg_hits = keyword_hits(text, NEGATIVE_WORDS)
    score = 60 + 5 * len(pos_hits) - 8 * len(neg_hits)
    score = max(0, min(100, score))

    if "analysis" in CATEGORIES:
        base["analysis"] = {
            "metrics": {"summary_score": score, "positive_hits": pos_hits, "negative_hits": neg_hits},
            "diagnosis": [],
            "risks": neg_hits,
            "recommendations": [],
        }
    if "monitoring" in CATEGORIES:
        level = "low" if score >= 70 else "medium" if score >= 45 else "high"
        base["monitoring"] = {
            "alert_level": level,
            "trigger_indicators": neg_hits,
            "actions": [],
        }
    if "content" in CATEGORIES:
        base["content"] = {
            "draft": "",
            "key_points": [],
            "compliance_notes": [],
        }
    if "qa" in CATEGORIES:
        base["qa"] = {
            "questions": [],
            "answers": [],
            "citations": [],
        }
    if "compliance" in CATEGORIES:
        base["compliance"] = {
            "flags": neg_hits,
            "revision_suggestions": [],
            "risk_level": "high" if neg_hits else "low",
        }
    if "service" in CATEGORIES:
        base["customer_strategy"] = {
            "segments": [],
            "touchpoints": [],
            "tone": "稳健、可解释",
        }
    if "product" in CATEGORIES:
        base["product"] = {
            "positioning": "",
            "target_audience": "",
            "differentiators": [],
        }

    return base


def render_markdown(result: dict) -> str:
    lines = [
        f"# {result['skill']} 输出摘要",
        f"- 领域: {result['domain']}",
        f"- 场景: {result['scene']}",
        "",
        "## 关键结论",
    ]
    for item in result.get("key_findings", [])[:5]:
        lines.append(f"- {item}")
    if not result.get("key_findings"):
        lines.append("- (暂无关键结论，请补充输入文本)")

    if "analysis" in result:
        metrics = result["analysis"].get("metrics", {})
        lines.append("## 核心指标")
        lines.append(f"- summary_score: {metrics.get('summary_score')}")

    if "monitoring" in result:
        lines.append("## 监测预警")
        lines.append(f"- alert_level: {result['monitoring'].get('alert_level')}")

    lines.append("## 数据质量")
    lines.append(f"- text_length: {result['data_quality'].get('text_length')}")

    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=SKILL_META["description"])
    parser.add_argument("--input", help="Input text file path")
    parser.add_argument("--text", help="Raw input text")
    parser.add_argument("--fund-code", help="Fund code override", default="")
    parser.add_argument("--fund-name", help="Fund name override", default="")
    parser.add_argument("--output-json", default="result.json")
    parser.add_argument("--output-md", default="report.md")
    args = parser.parse_args()

    text = load_text(args.input, args.text)
    result = build_output(text, args.fund_code, args.fund_name)

    Path(args.output_json).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    Path(args.output_md).write_text(render_markdown(result), encoding="utf-8")

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
