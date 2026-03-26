#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
财务数据一致性检查脚本
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import argparse
import json

# 允许的误差范围
TOLERANCE = {
    'absolute': 100,  # 绝对误差（元）
    'ratio': 0.005,   # 相对误差（0.5%）
}


def load_financial_data(input_path: str) -> Dict[str, Any]:
    """加载财务数据"""
    with open(input_path, 'r', encoding='utf-8') as f:
        if input_path.endswith('.json'):
            return json.load(f)
        else:
            # 简化处理，假设是 JSON 格式
            raise ValueError("目前仅支持 JSON 格式输入")


def compare_values(val1: float, val2: float, item_name: str) -> Dict[str, Any]:
    """比较两个数值"""
    if val1 is None or val2 is None:
        return {'consistent': False, 'reason': '数据缺失'}

    diff = abs(val1 - val2)
    if val1 != 0:
        ratio = diff / abs(val1)
    else:
        ratio = 0 if diff == 0 else float('inf')

    is_consistent = (diff <= TOLERANCE['absolute']) or (ratio <= TOLERANCE['ratio'])

    return {
        'consistent': is_consistent,
        'value1': val1,
        'value2': val2,
        'difference': diff,
        'ratio': ratio,
        'reason': '超出允许误差范围' if not is_consistent else '在允许误差范围内'
    }


def check_consistency(data: Dict[str, Any]) -> Dict[str, Any]:
    """检查财务数据一致性"""
    results = {
        'consistent_items': [],
        'inconsistent_items': [],
        'missing_items': [],
        'summary': {}
    }

    # 检查各文件间的数据一致性
    documents = data.get('documents', {})
    items = data.get('items', [])

    total_checks = 0
    consistent_count = 0

    for item in items:
        item_name = item.get('name', '')
        period = item.get('period', '')

        # 获取各文件中的数据
        values = {}
        for doc_name, doc_data in documents.items():
            value = doc_data.get(item_name, {}).get(period)
            values[doc_name] = value

        # 两两比较
        doc_names = list(values.keys())
        for i in range(len(doc_names)):
            for j in range(i + 1, len(doc_names)):
                doc1, doc2 = doc_names[i], doc_names[j]
                val1, val2 = values[doc1], values[doc2]

                total_checks += 1
                comparison = compare_values(val1, val2, item_name)

                check_result = {
                    'item': item_name,
                    'period': period,
                    'document1': doc1,
                    'document2': doc2,
                    **comparison
                }

                if comparison['consistent']:
                    consistent_count += 1
                    results['consistent_items'].append(check_result)
                else:
                    results['inconsistent_items'].append(check_result)

    # 计算一致率
    consistency_rate = (consistent_count / total_checks * 100) if total_checks > 0 else 0

    results['summary'] = {
        'check_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_checks': total_checks,
        'consistent_count': consistent_count,
        'inconsistent_count': len(results['inconsistent_items']),
        'consistency_rate': f"{consistency_rate:.1f}%"
    }

    return results


def generate_report(results: Dict[str, Any], output_path: str) -> str:
    """生成检查报告"""
    lines = []

    lines.append("# 财务数据一致性检查报告\n")
    lines.append(f"生成时间：{results['summary']['check_date']}\n")
    lines.append("---\n")

    # 检查概况
    lines.append("## 检查概况\n")
    summary = results['summary']
    lines.append(f"- 检查数据项：{summary['total_checks']} 项次")
    lines.append(f"- 一致数据项：{summary['consistent_count']} 项次")
    lines.append(f"- 不一致数据项：{summary['inconsistent_count']} 项次")
    lines.append(f"- **一致率：{summary['consistency_rate']}**\n")

    # 不一致项目
    if results['inconsistent_items']:
        lines.append("## ⚠️ 不一致项目\n")
        lines.append("| 数据项 | 期间 | 文件 1 | 文件 2 | 数值 1 | 数值 2 | 差异 | 差异率 |")
        lines.append("|--------|------|--------|--------|--------|--------|------|--------|")

        for item in results['inconsistent_items']:
            lines.append(
                f"| {item['item']} | {item['period']} | {item['document1']} | {item['document2']} | "
                f"{item['value1']:,.2f} | {item['value2']:,.2f} | {item['difference']:,.2f} | "
                f"{item['ratio']*100:.2f}% |"
            )
        lines.append("")

        # 处理建议
        lines.append("### 处理建议\n")
        for idx, item in enumerate(results['inconsistent_items'], 1):
            lines.append(f"{idx}. **{item['item']}（{item['period']}）**")
            lines.append(f"   - 差异金额：{item['difference']:,.2f}")
            lines.append(f"   - 差异率：{item['ratio']*100:.2f}%")
            lines.append(f"   - 建议：核实{item['document1']}与{item['document2']}的数据来源及计算口径\n")

    # 输出报告
    report_content = "\n".join(lines)

    output_file = Path(output_path) / f"财务一致性检查报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report_content)

    print(f"检查报告已生成：{output_file}")
    return report_content


def main():
    parser = argparse.ArgumentParser(description='财务数据一致性检查工具')
    parser.add_argument('--input', '-i', required=True, help='财务数据文件路径（JSON）')
    parser.add_argument('--output', '-o', required=True, help='输出报告目录')

    args = parser.parse_args()

    print("=" * 60)
    print("财务数据一致性检查工具")
    print("=" * 60)

    print(f"\n[1/3] 加载财务数据：{args.input}")
    data = load_financial_data(args.input)

    print(f"\n[2/3] 检查数据一致性...")
    results = check_consistency(data)

    print(f"\n[3/3] 生成检查报告...")
    generate_report(results, args.output)

    print("\n" + "=" * 60)
    print("检查摘要")
    print("=" * 60)
    print(f"一致率：{results['summary']['consistency_rate']}")
    print(f"不一致项：{results['summary']['inconsistent_count']} 项")
    print("=" * 60)


if __name__ == '__main__':
    main()
