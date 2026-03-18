#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
将财务诊断结果渲染为 Markdown 报告。
"""

from __future__ import annotations
import json
import sys
from pathlib import Path


def render_table(flags):
    lines = ["| 序号 | 红旗事项 | 触发依据 | 影响判断 | 建议核验事项 |", "|---|---|---|---|---|"]
    for i, item in enumerate(flags, 1):
        lines.append(
            f"| {i} | {item.get('item','')} | {item.get('basis','')} | {item.get('impact','')} | {item.get('follow_up','')} |"
        )
    if len(flags) == 0:
        lines.append("| 1 | 暂未识别到明显红旗 | - | - | - |")
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("用法：python render_financial_health_report.py 输入.json [输出.md]")
        sys.exit(1)

    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else None

    data = json.loads(input_file.read_text(encoding="utf-8"))

    report = f"""# 企业财务健康诊断报告

## 一、诊断结论摘要
- 企业名称：{data.get("enterprise_name", "")}
- 报表期间：{data.get("reporting_period", "")}
- 报表口径：{data.get("scope", "")}
- 财务健康评级：{data.get("overall_rating", "")}
- 总体结论：{data.get("summary", "")}

## 二、主要优势
""" + "\n".join([f"- {x}" for x in data.get("strengths", [])]) + f"""

## 三、主要风险
""" + "\n".join([f"- {x}" for x in data.get("risks", [])]) + f"""

## 四、偿债能力分析
- 短期偿债判断：{data.get("solvency_analysis", {}).get("short_term", "")}
- 长期偿债判断：{data.get("solvency_analysis", {}).get("long_term", "")}

## 五、盈利能力与盈利质量分析
- 盈利趋势判断：{data.get("profitability_analysis", {}).get("trend", "")}
- 盈利质量判断：{data.get("profitability_analysis", {}).get("quality", "")}

## 六、营运能力分析
- 应收周转判断：{data.get("operating_analysis", {}).get("receivable_turnover", "")}
- 存货周转判断：{data.get("operating_analysis", {}).get("inventory_turnover", "")}
- 营运资本判断：{data.get("operating_analysis", {}).get("working_capital", "")}

## 七、现金流分析
- 经营现金流判断：{data.get("cashflow_analysis", {}).get("operating_cashflow", "")}
- 利润现金匹配判断：{data.get("cashflow_analysis", {}).get("profit_cash_match", "")}
- 融资依赖判断：{data.get("cashflow_analysis", {}).get("financing_dependency", "")}

## 八、资本结构分析
- 杠杆判断：{data.get("capital_structure_analysis", {}).get("leverage", "")}
- 权益缓冲判断：{data.get("capital_structure_analysis", {}).get("equity_buffer", "")}
- 债务结构判断：{data.get("capital_structure_analysis", {}).get("debt_structure", "")}

## 九、财务红旗清单
{render_table(data.get("red_flags", []))}

## 十、缺失信息
""" + "\n".join([f"- {x}" for x in data.get("data_gaps", [])]) + f"""

## 十一、后续建议
""" + "\n".join([f"- {x}" for x in data.get("follow_up_actions", [])]) + "\n"

    if output_file:
        output_file.write_text(report, encoding="utf-8")
    else:
        print(report)


if __name__ == "__main__":
    main()
