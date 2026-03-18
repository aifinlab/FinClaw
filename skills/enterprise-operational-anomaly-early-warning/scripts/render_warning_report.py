#!/usr/bin/env python3
"""渲染企业贷后预警报告示例脚本。"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


def render_report(payload: Dict[str, Any]) -> str:
    company = payload.get("company", {})
    level = payload.get("level", {})
    signals: List[Dict[str, Any]] = payload.get("signals", [])
    pending = payload.get("pending_checks", [])
    actions = payload.get("actions", [])

    lines = []
    lines.append("# 企业贷后经营异常预警报告")
    lines.append("")
    lines.append("## 一、企业基本情况")
    lines.append("")
    lines.append(f"- 企业名称：{company.get('name', '')}")
    lines.append(f"- 所属行业：{company.get('industry', '')}")
    lines.append(f"- 授信余额：{company.get('credit_balance', '')}")
    lines.append(f"- 监测期间：{company.get('monitoring_period', '')}")
    lines.append("")
    lines.append("## 二、预警等级结论")
    lines.append("")
    lines.append(f"**预警等级：** {level.get('预警等级', '')}")
    lines.append("")
    lines.append(f"**评分说明：** {level.get('说明', '')}")
    lines.append("")
    lines.append("## 三、核心异常信号")
    lines.append("")
    if not signals:
        lines.append("当前未识别到明显异常信号。")
    else:
        for idx, sig in enumerate(signals, 1):
            lines.append(f"### {idx}. {sig.get('信号', '')}")
            lines.append("")
            lines.append(f"- 维度：{sig.get('维度', '')}")
            lines.append(f"- 描述：{sig.get('描述', '')}")
            lines.append(f"- 严重程度：{sig.get('严重程度', '')}")
            lines.append(f"- 是否已核验：{'是' if sig.get('已核验') else '否'}")
            lines.append("")
    lines.append("## 四、待核验事项")
    lines.append("")
    if pending:
        for item in pending:
            lines.append(f"- {item}")
    else:
        lines.append("- 暂无")
    lines.append("")
    lines.append("## 五、建议动作")
    lines.append("")
    if actions:
        for item in actions:
            lines.append(f"- {item}")
    else:
        lines.append("- 建议持续监测并定期复核。")
    lines.append("")
    lines.append("## 六、结论边界")
    lines.append("")
    lines.append("当前结论基于已获取资料形成，仍需结合补充材料、现场核查与人工复核进一步确认。")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="渲染企业贷后预警报告")
    parser.add_argument("input", help="输入 JSON 文件路径")
    parser.add_argument("-o", "--output", help="输出 Markdown 文件路径")
    args = parser.parse_args()

    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    report = render_report(payload)
    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
    else:
        print(report)


if __name__ == "__main__":
    main()
