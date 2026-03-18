from __future__ import annotations

import json
import sys
from pathlib import Path


def render(data: dict) -> str:
    lines = []
    lines.append("# 财富顾问合规话术审阅结果")
    lines.append("")
    lines.append(f"- 任务类型：{data.get('任务类型', '未知')}")
    lines.append(f"- 场景：{data.get('场景', '未知')}")
    lines.append(f"- 风险等级：{data.get('风险等级', '未知')}")
    lines.append("")
    lines.append("## 风险点列表")
    for item in data.get("风险点列表", []):
        lines.append(f"- [{item.get('category', '未分类')}] 命中模式：{item.get('pattern', '')}；片段：{item.get('snippet', '')}")
    if not data.get("风险点列表"):
        lines.append("- 未发现显著规则命中，但仍建议人工复核。")
    lines.append("")
    lines.append("## 改写后话术")
    lines.append(data.get("改写后话术", ""))
    lines.append("")
    lines.append("## 必须补充披露")
    for x in data.get("必须补充披露", []):
        lines.append(f"- {x}")
    if not data.get("必须补充披露"):
        lines.append("- 请补充收益不确定性、风险等级、期限与流动性等基础披露。")
    lines.append("")
    lines.append("## 客户经理提示")
    for x in data.get("客户经理提示", []):
        lines.append(f"- {x}")
    if not data.get("客户经理提示"):
        lines.append("- 话术落地前请结合本机构内部禁语清单复核。")
    return "\n".join(lines)


def main() -> None:
    if len(sys.argv) != 3:
        print("用法: python render_compliance_report.py 输入json路径 输出md路径")
        sys.exit(1)
    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    data = json.loads(input_path.read_text(encoding="utf-8"))
    output_path.write_text(render(data), encoding="utf-8")
    print(str(output_path))


if __name__ == "__main__":
    main()
