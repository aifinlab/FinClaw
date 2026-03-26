#!/usr/bin/env python3
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List
import argparse
import json
import re
import sys


DEFAULT_KB = {
    "urgent_keywords": ["今天", "立即", "马上", "24小时", "截止", "已违约", "被起诉", "冻结"],
    "high_risk_keywords": ["刑事", "监管处罚", "无效", "重大违约", "保全", "强制执行"],
    "categories": [
        {
            "id": "contract_effect",
            "name": "合同效力",
            "keywords": ["效力", "生效", "无效", "可撤销", "解除"],
            "base_priority": 3,
            "reply_template": "建议先核对合同成立与生效要件、授权链路和签署流程，明确是否存在效力瑕疵。",
        },
        {
            "id": "guarantee_security",
            "name": "担保与增信",
            "keywords": ["担保", "保证", "抵押", "质押", "反担保"],
            "base_priority": 3,
            "reply_template": "建议核查担保范围、担保期间、登记状态及担保物可处置性。",
        },
        {
            "id": "default_dispute",
            "name": "违约与争议",
            "keywords": ["违约", "仲裁", "诉讼", "管辖", "追偿", "保全"],
            "base_priority": 4,
            "reply_template": "建议先确认违约触发条款、证据链完整性及争议解决路径，再评估执行策略。",
        },
        {
            "id": "compliance_disclosure",
            "name": "合规与披露",
            "keywords": ["合规", "披露", "监管", "报送", "处罚", "整改"],
            "base_priority": 4,
            "reply_template": "建议核对监管口径、披露义务与时间节点，优先完成风险事项报备与整改计划。",
        },
        {
            "id": "data_privacy",
            "name": "数据与隐私",
            "keywords": ["个人信息", "数据", "隐私", "保密", "跨境"],
            "base_priority": 2,
            "reply_template": "建议明确数据处理目的、授权基础、传输范围与安全措施，评估合规边界。",
        },
    ],
    "fallback_reply": "建议先补齐事实与证据，再由法务对具体条款和适用法律进行逐项确认。",
}


def load_items(path: Path) -> List[Dict[str, Any]]:
    raw = path.read_text(encoding="utf-8").strip()
    if not raw:
        return []
    if raw.lstrip().startswith("["):
        arr = json.loads(raw)
        if not isinstance(arr, list):
            raise ValueError("JSON input must be an array.")
        return [x for x in arr if isinstance(x, dict)]

    items = []
    for idx, line in enumerate(raw.splitlines(), start=1):
        text = line.strip()
        if not text:
            continue
        obj = json.loads(text)
        if not isinstance(obj, dict):
            raise ValueError(f"JSONL line {idx} must be object.")
        items.append(obj)
    return items


def load_kb(path: Path | None) -> Dict[str, Any]:
    if path is None:
        return DEFAULT_KB
    data = json.loads(path.read_text(encoding="utf-8"))
    kb = {
        "urgent_keywords": [str(x) for x in data.get("urgent_keywords", DEFAULT_KB["urgent_keywords"])],
        "high_risk_keywords": [str(x) for x in data.get("high_risk_keywords", DEFAULT_KB["high_risk_keywords"])],
        "categories": data.get("categories", DEFAULT_KB["categories"]),
        "fallback_reply": str(data.get("fallback_reply", DEFAULT_KB["fallback_reply"])),
    }
    if not isinstance(kb["categories"], list):
        kb["categories"] = DEFAULT_KB["categories"]
    return kb


def count_hits(text: str, words: List[str]) -> int:
    total = 0
    for w in words:
        total += len(re.findall(re.escape(w), text, flags=re.IGNORECASE))
    return total


def priority_level(score: int) -> str:
    if score >= 9:
        return "P1"
    if score >= 5:
        return "P2"
    return "P3"


def role_weight(role: str) -> int:
    role = role.lower()
    if role in {"ic", "investment_committee", "management", "ceo", "总经理"}:
        return 2
    if role in {"compliance", "legal", "风控"}:
        return 1
    return 0


def detect_category(question_text: str, kb: Dict[str, Any]) -> Dict[str, Any]:
    best = None
    best_hits = -1
    for cat in kb["categories"]:
        if not isinstance(cat, dict):
            continue
        keywords = [str(x) for x in cat.get("keywords", [])]
        hits = count_hits(question_text, keywords)
        if hits > best_hits:
            best_hits = hits
            best = cat

    if best is None or best_hits <= 0:
        return {
            "id": "general",
            "name": "综合咨询",
            "base_priority": 2,
            "reply_template": kb["fallback_reply"],
            "hits": 0,
        }

    return {
        "id": str(best.get("id", "general")),
        "name": str(best.get("name", "综合咨询")),
        "base_priority": int(best.get("base_priority", 2)),
        "reply_template": str(best.get("reply_template", kb["fallback_reply"])),
        "hits": best_hits,
    }


def triage(items: List[Dict[str, Any]], kb: Dict[str, Any]) -> Dict[str, Any]:
    records = []
    priority_counter = Counter()
    category_counter = Counter()

    for idx, item in enumerate(items, start=1):
        qid = str(item.get("question_id", f"Q{idx:03d}"))
        question = str(item.get("question", "") or "")
        context = str(item.get("context", "") or "")
        asker_role = str(item.get("asker_role", "") or "")
        deadline_text = str(item.get("deadline_text", "") or "")

        full = f"{question} {context} {deadline_text}".strip()
        category = detect_category(full, kb)

        urgent_hits = count_hits(full, kb["urgent_keywords"])
        high_risk_hits = count_hits(full, kb["high_risk_keywords"])

        score = category["base_priority"]
        score += min(urgent_hits * 2, 4)
        score += min(high_risk_hits * 2, 4)
        score += role_weight(asker_role)

        priority = priority_level(score)
        priority_counter[priority] += 1
        category_counter[category["name"]] += 1

        escalation = []
        if priority == "P1":
            escalation.append("建议2小时内由法务负责人复核")
        if high_risk_hits > 0:
            escalation.append("涉及高风险关键词，建议升级律师审阅")
        if "监管" in full or "处罚" in full:
            escalation.append("涉及监管事项，建议同步合规岗")

        draft = (
            f"【初步答复】{category['reply_template']} "
            "如需形成正式法律结论，请提供完整合同文本、事实证据及时间线，由律师终审。"
        )

        records.append(
            {
                "question_id": qid,
                "question": question,
                "category": category["name"],
                "priority": priority,
                "score": score,
                "reason": f"cat_hits={category['hits']}, urgent_hits={urgent_hits}, high_risk_hits={high_risk_hits}, role={asker_role or 'N/A'}",
                "draft": draft,
                "escalation": escalation,
            }
        )

    records.sort(key=lambda x: x["score"], reverse=True)
    return {
        "records": records,
        "priority_counter": priority_counter,
        "category_counter": category_counter,
    }


def render_report(result: Dict[str, Any], top_n: int) -> str:
    lines: List[str] = []
    lines.append("# 法务问答分流与答复草案报告")
    lines.append("")
    lines.append("## 一、问题概览")
    lines.append(f"- 问题总数: {len(result['records'])}")
    lines.append(f"- P1: {result['priority_counter'].get('P1', 0)}")
    lines.append(f"- P2: {result['priority_counter'].get('P2', 0)}")
    lines.append(f"- P3: {result['priority_counter'].get('P3', 0)}")
    lines.append("")

    lines.append("## 二、主题分布")
    if not result["category_counter"]:
        lines.append("- 无")
    else:
        for category, cnt in result["category_counter"].most_common():
            lines.append(f"- {category}: {cnt}")
    lines.append("")

    lines.append("## 三、高优先问题与答复草案")
    top_records = result["records"][:top_n]
    if not top_records:
        lines.append("- 无")
    else:
        for rec in top_records:
            lines.append(
                f"- {rec['question_id']} | priority={rec['priority']} | score={rec['score']} | category={rec['category']}"
            )
            lines.append(f"  - 问题: {rec['question']}")
            lines.append(f"  - 分流依据: {rec['reason']}")
            lines.append(f"  - 答复草案: {rec['draft']}")
            if rec["escalation"]:
                for e in rec["escalation"]:
                    lines.append(f"  - 升级建议: {e}")

    lines.append("")
    lines.append("## 四、方法与限制")
    lines.append("- 本报告用于法务问答分流和草案生成，不替代律师正式法律意见。")
    lines.append("- 对P1问题和高风险事项应优先升级处理。")
    lines.append("- 输出答复需结合完整事实与合同文本复核。")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Legal QA triage and draft response generator.")
    parser.add_argument("--input", required=True, help="Input JSON array or JSONL file.")
    parser.add_argument("--output", help="Output markdown path (default: stdout).")
    parser.add_argument("--kb", help="Custom knowledge-base JSON path.")
    parser.add_argument("--top", type=int, default=20, help="Top questions to display.")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    items = load_items(input_path)
    kb = load_kb(Path(args.kb)) if args.kb else load_kb(None)
    result = triage(items, kb)
    report = render_report(result, args.top)

    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
    else:
        sys.stdout.write(report + "\n")


if __name__ == "__main__":
    main()
