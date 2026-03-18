#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""将结构化 JSON 渲染为中文 Markdown 风格漂移报告。"""
from __future__ import annotations
import json
import sys
from pathlib import Path
from typing import Any, Dict, List


def load_payload(path: str) -> Dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def render_list(items: List[str]) -> str:
    if not items:
        return "- 暂无\n"
    return "".join(f"- {item}\n" for item in items)


def render(payload: Dict[str, Any]) -> str:
    basic = payload.get("basic_info", {})
    conclusion = payload.get("conclusion", {})
    target = payload.get("target_style", {})
    actual = payload.get("actual_changes", {})
    evidence = payload.get("evidence", [])
    risks = payload.get("risks", [])
    followups = payload.get("followups", [])
    missing = payload.get("missing_info", [])

    sections = []
    sections.append("# 风格漂移识别报告\n")
    sections.append("## 一、分析对象与范围\n")
    sections.append(f"- 产品名称：{basic.get('product_name', '未提供')}\n")
    sections.append(f"- 产品代码：{basic.get('product_code', '未提供')}\n")
    sections.append(f"- 分析日期：{basic.get('analysis_date', '未提供')}\n")
    sections.append(f"- 分析窗口：{basic.get('analysis_window', '未提供')}\n")
    sections.append(f"- 分析目的：{basic.get('purpose', '未提供')}\n\n")

    sections.append("## 二、结论摘要\n")
    sections.append(f"- 综合判断：{conclusion.get('judgement', '未提供')}\n")
    sections.append(f"- 漂移等级：{conclusion.get('level', '未提供')}\n")
    sections.append(f"- 当前可信度：{conclusion.get('confidence', '未提供')}\n")
    sections.append(f"- 一句话结论：{conclusion.get('summary', '未提供')}\n\n")

    sections.append("## 三、目标风格画像\n")
    sections.append(f"- 产品既定定位：{target.get('positioning', '未提供')}\n")
    sections.append(f"- 历史稳定风格特征：{target.get('historical_style', '未提供')}\n\n")

    sections.append("## 四、实际风格变化情况\n")
    for title, key in [
        ("市值风格变化", "size"),
        ("成长/价值风格变化", "growth_value"),
        ("行业配置变化", "industry"),
        ("因子暴露变化", "factor"),
        ("仓位与交易风格变化", "trading"),
    ]:
        sections.append(f"### {title}\n")
        sections.append(f"{actual.get(key, '未提供')}\n\n")

    sections.append("## 五、核心证据链\n")
    sections.append(render_list(evidence) + "\n")
    sections.append("## 六、风险提示\n")
    sections.append(render_list(risks) + "\n")
    sections.append("## 七、后续跟踪建议\n")
    sections.append(render_list(followups) + "\n")
    sections.append("## 八、待补充信息\n")
    sections.append(render_list(missing))
    return "".join(sections)


def main() -> None:
    if len(sys.argv) < 3:
        print("用法：python render_style_drift_report.py 输入.json 输出.md", file=sys.stderr)
        sys.exit(1)
    payload = load_payload(sys.argv[1])
    output = render(payload)
    Path(sys.argv[2]).write_text(output, encoding="utf-8")
    print(sys.argv[2])


if __name__ == "__main__":
    main()
