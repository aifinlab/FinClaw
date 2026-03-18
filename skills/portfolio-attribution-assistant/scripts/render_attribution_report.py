from __future__ import annotations

import json
import sys
from pathlib import Path


def format_pct(value):
    try:
        return f"{float(value) * 100:.2f}%"
    except Exception:
        return str(value)


def top_n(items, key, n=5, reverse=True):
    return sorted(items, key=lambda x: x.get(key, 0), reverse=reverse)[:n]


def render(report: dict) -> str:
    meta = report.get('基础信息', {})
    summary = report.get('汇总', {})
    industries = report.get('行业归因结果', [])
    stock_pos = report.get('正向个券', [])
    stock_neg = report.get('负向个券', [])
    data_gaps = report.get('数据缺口', [])

    pos_ind = top_n(industries, '总贡献', 5, True)
    neg_ind = top_n(industries, '总贡献', 5, False)

    lines = []
    lines.append('# 组合归因分析报告')
    lines.append('')
    lines.append('## 一、执行摘要')
    lines.append(f"- 分析对象：{meta.get('分析对象', '')}")
    lines.append(f"- 分析区间：{meta.get('分析区间', '')}")
    lines.append(f"- 组合收益：{format_pct(meta.get('组合收益', 0))}")
    lines.append(f"- 基准收益：{format_pct(meta.get('基准收益', 0))}")
    lines.append(f"- 超额收益：{format_pct(meta.get('超额收益', 0))}")
    lines.append('')
    lines.append('## 二、行业归因摘要')
    lines.append(f"- 配置贡献合计：{format_pct(summary.get('配置贡献合计', 0))}")
    lines.append(f"- 选股贡献合计：{format_pct(summary.get('选股贡献合计', 0))}")
    lines.append(f"- 交互贡献合计：{format_pct(summary.get('交互贡献合计', 0))}")
    lines.append('')
    lines.append('### 1. 正向贡献靠前行业')
    for item in pos_ind:
        lines.append(f"- {item.get('行业')}: 总贡献 {format_pct(item.get('总贡献', 0))}，配置 {format_pct(item.get('配置贡献', 0))}，选股 {format_pct(item.get('选股贡献', 0))}")
    lines.append('')
    lines.append('### 2. 负向拖累靠前行业')
    for item in neg_ind:
        lines.append(f"- {item.get('行业')}: 总贡献 {format_pct(item.get('总贡献', 0))}，配置 {format_pct(item.get('配置贡献', 0))}，选股 {format_pct(item.get('选股贡献', 0))}")
    lines.append('')
    lines.append('## 三、个券贡献摘要')
    lines.append('### 1. 正向贡献个券')
    for item in stock_pos[:5]:
        lines.append(f"- {item.get('名称', item.get('代码', ''))}: 贡献 {format_pct(item.get('贡献', 0))}")
    lines.append('')
    lines.append('### 2. 负向拖累个券')
    for item in stock_neg[:5]:
        lines.append(f"- {item.get('名称', item.get('代码', ''))}: 贡献 {format_pct(item.get('贡献', 0))}")
    lines.append('')
    lines.append('## 四、数据缺口与风险提示')
    if data_gaps:
        for gap in data_gaps:
            lines.append(f"- {gap}")
    else:
        lines.append('- 当前未显式记录数据缺口，但仍需复核行业分类、收益口径与权重口径的一致性。')
    lines.append('')
    lines.append('## 五、结论')
    lines.append('- 请结合行业权重偏离、行业收益差异、个券集中贡献与风格暴露共同解释本期业绩。')
    lines.append('- 如缺少高质量行业数据，行业配置与选股结论应视为解释性结论而非最终审定结论。')
    return '\n'.join(lines)


def main():
    if len(sys.argv) < 2:
        print('用法: python render_attribution_report.py 输入.json [输出.md]')
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    data = json.loads(input_path.read_text(encoding='utf-8'))
    text = render(data)
    if output_path:
        output_path.write_text(text, encoding='utf-8')
    else:
        print(text)


if __name__ == '__main__':
    main()
