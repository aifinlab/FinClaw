#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""把结构化审核结果渲染为中文 Markdown 审核意见。"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import json
import sys


def bullet_lines(items: List[str]) -> str:
    if not items:
        return "- 无\n"
    return "".join(f"- {item}\n" for item in items)


def render_report(data: Dict[str, Any]) -> str:
    obj = data.get("审核对象", {})
    register = data.get("材料台账", [])
    missing = data.get("缺件清单", [])
    issues = data.get("问题清单", [])
    pending = data.get("待核验事项", [])
    suggestions = data.get("补件建议", [])
    conclusion = data.get("审核结论", "未提供")

    lines = []
    lines.append("# 授信材料完整性审核意见\n")
    lines.append("## 一、审核对象概况\n")
    lines.append(f"- 企业名称：{obj.get('企业名称', '')}\n")
    lines.append(f"- 统一社会信用代码：{obj.get('统一社会信用代码', '')}\n")
    lines.append(f"- 授信品种：{obj.get('授信品种', '')}\n")
    lines.append(f"- 申请金额：{obj.get('申请金额', '')}\n")
    lines.append(f"- 担保方式：{obj.get('担保方式', '')}\n")
    lines.append(f"- 审核阶段：{obj.get('审核阶段', '')}\n\n")

    lines.append("## 二、材料收件概况\n")
    lines.append(f"- 当前纳入核验的材料数量：{len(register)} 份\n")
    provided = sum(1 for row in register if str(row.get("是否已提供", "")) == "是")
    lines.append(f"- 已标记为已提供的材料数量：{provided} 份\n\n")

    lines.append("## 三、缺件清单\n")
    lines.append(bullet_lines(missing) + "\n")

    lines.append("## 四、问题清单\n")
    lines.append(bullet_lines(issues) + "\n")

    lines.append("## 五、待核验事项\n")
    lines.append(bullet_lines(pending) + "\n")

    lines.append("## 六、补件建议\n")
    lines.append(bullet_lines(suggestions) + "\n")

    lines.append("## 七、审核结论\n")
    lines.append(f"{conclusion}\n")

    return "".join(lines)


def main() -> None:
    if len(sys.argv) < 3:
        print("用法: python review_report_renderer.py 输入.json 输出.md")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    data = json.loads(input_path.read_text(encoding="utf-8"))
    report = render_report(data)
    output_path.write_text(report, encoding="utf-8")
    print(f"已输出审核意见: {output_path}")


if __name__ == "__main__":
    main()
