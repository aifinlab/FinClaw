#!/usr/bin/env python3
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List
import argparse, json, re, sys

def load_items(path: Path) -> List[Dict[str, Any]]:
    raw = path.read_text(encoding="utf-8").strip()
    if not raw:
        return []
    if raw.lstrip().startswith("["):
        data = json.loads(raw)
        if not isinstance(data, list):
            raise ValueError("JSON input must be an array.")
        return [x for x in data if isinstance(x, dict)]
    items = []
    for idx, line in enumerate(raw.splitlines(), start=1):
        t = line.strip()
        if not t:
            continue
        obj = json.loads(t)
        if not isinstance(obj, dict):
            raise ValueError(f"JSONL line {idx} must be object.")
        items.append(obj)
    return items

def score_text(text: str, pos: List[str], neg: List[str]) -> Dict[str, int]:
    def hits(words):
        c = 0
        for w in words:
            c += len(re.findall(re.escape(w), text, flags=re.IGNORECASE))
        return c
    p = hits(pos)
    n = hits(neg)
    score = max(0, min(100, 60 + p * 4 - n * 6))
    return {"score": score, "pos": p, "neg": n}

def render(name: str, items: List[Dict[str, Any]], results: List[Dict[str, Any]], top: int) -> str:
    cnt = Counter([r["level"] for r in results])
    lines = [f"# {name}（自动报告）", "", "## 一、概览", f"- 样本数: {len(results)}", f"- low: {cnt.get('low',0)}", f"- medium: {cnt.get('medium',0)}", f"- high: {cnt.get('high',0)}", "", "## 二、重点条目"]
    ranked = sorted(results, key=lambda x: x["score"], reverse=True)[:top]
    if not ranked:
        lines.append("- 无")
    for r in ranked:
        lines.append(f"- {r['id']} | score={r['score']} | level={r['level']} | pos_hits={r['pos']} | neg_hits={r['neg']}")
    lines += ["", "## 三、免责声明", "- 本报告由系统自动生成，仅用于业务初筛。", "- 结论需由业务、风控、法务人工复核后使用。", "- 本报告不构成投资建议、授信决策或法律意见。"]
    return "\n".join(lines)

def main():
    p = argparse.ArgumentParser(description="Skill analyzer")
    p.add_argument("--input", required=True)
    p.add_argument("--output")
    p.add_argument("--top", type=int, default=15)
    p.add_argument("--positive", default="支持,改善,增信,完成,稳定")
    p.add_argument("--negative", default="违约,处罚,下滑,逾期,风险")
    p.add_argument("--title", default="Skill")
    a = p.parse_args()
    items = load_items(Path(a.input))
    pos = [x.strip() for x in a.positive.split(',') if x.strip()]
    neg = [x.strip() for x in a.negative.split(',') if x.strip()]
    results = []
    for i, item in enumerate(items, start=1):
      text = " ".join(str(v) for v in item.values())
      s = score_text(text, pos, neg)
      level = "high" if s["score"] < 45 else "medium" if s["score"] < 70 else "low"
      results.append({"id": item.get("id", f"R{i:03d}"), **s, "level": level})
    rep = render(a.title, items, results, a.top)
    if a.output:
      Path(a.output).write_text(rep, encoding="utf-8")
    else:
      sys.stdout.write(rep + "\n")

if __name__ == "__main__":
    main()
