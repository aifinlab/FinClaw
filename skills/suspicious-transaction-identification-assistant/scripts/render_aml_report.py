from __future__ import annotations
import json

from pathlib import Path
from typing import Any
import argparse


def render_report(result: dict[str, Any]) -> str:
    summary = result.get("summary", {})
    signals = result.get("signals", [])

    lines: list[str] = []
    lines.append("  # 可疑交易识别分析结果")
    lines.append("")
    lines.append("  # 1. 总体结论")
    lines.append(f"- 交易笔数：{summary.get('transaction_count', '未知')}")
    lines.append(
        f"- 风险等级：{summary.get('risk_level_after_calibration', summary.get('risk_level', '未知'))}")
    lines.append(f"- 基础分值：{summary.get('total_score', '未知')}")
    if "calibrated_score" in summary:
        lines.append(f"- 校准后分值：{summary.get('calibrated_score')}")
    lines.append(f"- 说明：{summary.get('note', '无')}")
    lines.append("")

    lines.append("  # 2. 异常信号")
    if signals:
        for idx, s in enumerate(signals, start=1):
            lines.append(f"  # {idx}. {s.get('signal_name', '未知信号')}")
            lines.append(f"- 信号编码：{s.get('signal_code', '')}")
            lines.append(f"- 风险级别：{s.get('level', '')}")
            lines.append(f"- 分值：{s.get('score', '')}")
            lines.append(f"- 证据摘要：{s.get('evidence', '')}")
            lines.append("")
    else:
        lines.append("当前未识别出明确异常信号。")
        lines.append("")

    lines.append("  # 3. 校准说明")
    notes = summary.get("calibration_notes", [])
    if notes:
        for n in notes:
            lines.append(f"- {n}")
    else:
        lines.append("- 未进行行业或外部名单校准。")
    lines.append("")

    lines.append("  # 4. 待核验事项")
    lines.append("- 核验客户身份、职业或经营范围与交易行为是否匹配。")
    lines.append("- 核验高风险地区交易的业务背景与合理性。")
    lines.append("- 核验主要对手方关系、资金用途及往来真实性。")
    lines.append("- 若需高置信度判断，补充行业数据、外部名单和客户尽调资料。")
    lines.append("")

    lines.append("  # 5. 结论边界")
    lines.append("- 本结果仅作为可疑交易识别与人工复核辅助，不直接构成法律或监管结论。")
    lines.append("- 当缺少行业数据或外部名单时，应谨慎解释，不宜上升为高置信度 AML 判断。")
    lines.append("- 涉及监管报送的动作，应由反洗钱或合规专业团队进一步判断。")
    lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":

   parser = argparse.ArgumentParser(description="渲染 AML 分析报告")
   parser.add_argument("input", help="输入 JSON 文件")
   parser.add_argument(
       "-o",
       "--output",
       default="aml_report.md",
       help="输出 Markdown 文件")
   args = parser.parse_args()

   result = json.loads(Path(args.input).read_text(encoding="utf-8"))
   report = render_report(result)
   Path(args.output).write_text(report, encoding="utf-8")
   print(f"已输出到 {args.output}")
