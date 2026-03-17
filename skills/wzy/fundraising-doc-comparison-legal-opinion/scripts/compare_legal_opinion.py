#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
法律意见书募资文件对比脚本
"""

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any


def load_comparison_data(input_path: str) -> Dict[str, Any]:
    """加载对比数据"""
    with open(input_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def compare_legal(data: Dict[str, Any]) -> Dict[str, Any]:
    """对比法律意见书"""
    results = {
        'items': [],
        'discrepancies': [],
        'summary': {}
    }
    
    items = data.get('items', [])
    
    for item in items:
        item_name = item.get('name', '')
        
        prospectus_value = item.get('prospectus', '')
        legal_value = item.get('legal_opinion', '')
        
        # 文本对比
        is_consistent = str(prospectus_value).strip() == str(legal_value).strip()
        
        item_result = {
            'name': item_name,
            'prospectus': prospectus_value,
            'legal': legal_value,
            'is_consistent': is_consistent
        }
        
        results['items'].append(item_result)
        
        if not is_consistent:
            results['discrepancies'].append({
                'item': item_name,
                'prospectus': prospectus_value,
                'legal': legal_value
            })
    
    # 摘要
    results['summary'] = {
        'compare_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_items': len(items),
        'consistent_items': len([i for i in results['items'] if i['is_consistent']]),
        'discrepancy_items': len(results['discrepancies'])
    }
    
    return results


def generate_report(results: Dict[str, Any], output_path: str) -> str:
    """生成对比报告"""
    lines = []
    
    lines.append("# 募资文件对比报告（法律意见书版）\n")
    lines.append(f"生成时间：{results['summary']['compare_date']}\n")
    lines.append("---\n")
    
    # 对比概况
    lines.append("## 对比概况\n")
    summary = results['summary']
    lines.append(f"- 对比项目：{summary['total_items']} 项")
    lines.append(f"- 一致项目：{summary['consistent_items']} 项")
    lines.append(f"- 差异项目：{summary['discrepancy_items']} 项\n")
    
    # 对比明细
    lines.append("## 对比明细\n")
    lines.append("| 对比项 | 招股书 | 法律意见书 | 一致性 |")
    lines.append("|--------|--------|------------|--------|")
    for item in results['items']:
        icon = "✅" if item['is_consistent'] else "❌"
        lines.append(f"| {item['name']} | {item['prospectus']} | {item['legal']} | {icon} |")
    lines.append("")
    
    # 差异明细
    if results['discrepancies']:
        lines.append("## ⚠️ 差异明细\n")
        for idx, disc in enumerate(results['discrepancies'], 1):
            lines.append(f"### {idx}. {disc['item']}")
            lines.append(f"- 招股书：{disc['prospectus']}")
            lines.append(f"- 法律意见书：{disc['legal']}")
            lines.append(f"- 建议：核实差异原因，更新法律意见书\n")
    
    # 结论
    lines.append("## 对比结论\n")
    if results['discrepancies']:
        lines.append(f"存在{len(results['discrepancies'])}项差异，需核实并更新法律意见书。\n")
    else:
        lines.append("法律意见书与招股书信息披露一致。\n")
    
    # 输出报告
    report_content = "\n".join(lines)
    
    output_file = Path(output_path) / f"法律意见书对比报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"对比报告已生成：{output_file}")
    return report_content


def main():
    parser = argparse.ArgumentParser(description='法律意见书对比工具')
    parser.add_argument('--input', '-i', required=True, help='对比数据文件路径（JSON）')
    parser.add_argument('--output', '-o', required=True, help='输出报告目录')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("法律意见书对比工具")
    print("=" * 60)
    
    print(f"\n[1/3] 加载对比数据：{args.input}")
    data = load_comparison_data(args.input)
    
    print(f"\n[2/3] 对比文件...")
    results = compare_legal(data)
    
    print(f"\n[3/3] 生成对比报告...")
    generate_report(results, args.output)
    
    print("\n" + "=" * 60)
    print("对比摘要")
    print("=" * 60)
    print(f"差异项目：{results['summary']['discrepancy_items']} 项")
    print("=" * 60)


if __name__ == '__main__':
    main()
