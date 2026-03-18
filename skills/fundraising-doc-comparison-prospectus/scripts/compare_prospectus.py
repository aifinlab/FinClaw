#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
招股书募资文件对比脚本
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


def compare_documents(data: Dict[str, Any]) -> Dict[str, Any]:
    """对比文件"""
    results = {
        'projects': [],
        'discrepancies': [],
        'summary': {}
    }
    
    projects = data.get('projects', [])
    tolerance = data.get('tolerance', 0.05)  # 5% 容忍度
    
    for project in projects:
        project_name = project.get('name', '')
        
        # 对比投资总额
        prospectus_amount = project.get('prospectus', {}).get('total_investment', 0)
        feasibility_amount = project.get('feasibility', {}).get('total_investment', 0)
        filing_amount = project.get('filing', {}).get('total_investment', 0)
        
        # 计算差异
        if feasibility_amount > 0:
            diff_rate = abs(prospectus_amount - feasibility_amount) / feasibility_amount
        else:
            diff_rate = 0
        
        is_consistent = diff_rate <= tolerance
        
        project_result = {
            'name': project_name,
            'prospectus_amount': prospectus_amount,
            'feasibility_amount': feasibility_amount,
            'filing_amount': filing_amount,
            'diff_rate': diff_rate,
            'is_consistent': is_consistent
        }
        
        results['projects'].append(project_result)
        
        if not is_consistent:
            results['discrepancies'].append({
                'project': project_name,
                'item': '投资总额',
                'prospectus': prospectus_amount,
                'feasibility': feasibility_amount,
                'difference': abs(prospectus_amount - feasibility_amount),
                'diff_rate': diff_rate
            })
    
    # 摘要
    results['summary'] = {
        'compare_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_projects': len(projects),
        'consistent_projects': len([p for p in results['projects'] if p['is_consistent']]),
        'discrepancy_projects': len(results['discrepancies'])
    }
    
    return results


def generate_report(results: Dict[str, Any], output_path: str) -> str:
    """生成对比报告"""
    lines = []
    
    lines.append("# 募资文件对比报告（招股书版）\n")
    lines.append(f"生成时间：{results['summary']['compare_date']}\n")
    lines.append("---\n")
    
    # 对比概况
    lines.append("## 对比概况\n")
    summary = results['summary']
    lines.append(f"- 对比项目：{summary['total_projects']} 个")
    lines.append(f"- 一致项目：{summary['consistent_projects']} 个")
    lines.append(f"- 差异项目：{summary['discrepancy_projects']} 个\n")
    
    # 项目对比
    lines.append("## 项目对比\n")
    lines.append("| 项目名称 | 招股书金额 | 可研金额 | 备案金额 | 差异率 | 一致性 |")
    lines.append("|----------|------------|----------|----------|--------|--------|")
    for proj in results['projects']:
        icon = "✅" if proj['is_consistent'] else "❌"
        lines.append(
            f"| {proj['name']} | {proj['prospectus_amount']:,.0f} | "
            f"{proj['feasibility_amount']:,.0f} | {proj['filing_amount']:,.0f} | "
            f"{proj['diff_rate']*100:.1f}% | {icon} |"
        )
    lines.append("")
    
    # 差异明细
    if results['discrepancies']:
        lines.append("## ⚠️ 差异明细\n")
        for disc in results['discrepancies']:
            lines.append(f"### {disc['project']}")
            lines.append(f"- 对比项：{disc['item']}")
            lines.append(f"- 招股书：{disc['prospectus']:,.0f}元")
            lines.append(f"- 可研报告：{disc['feasibility']:,.0f}元")
            lines.append(f"- 差异：{disc['difference']:,.0f}元 ({disc['diff_rate']*100:.1f}%)")
            lines.append("")
    
    # 结论
    lines.append("## 对比结论\n")
    if results['discrepancies']:
        lines.append(f"存在{len(results['discrepancies'])}项差异，需核实原因并修正。\n")
    else:
        lines.append("募投项目信息披露一致，符合 IPO 要求。\n")
    
    # 输出报告
    report_content = "\n".join(lines)
    
    output_file = Path(output_path) / f"募资文件对比报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"对比报告已生成：{output_file}")
    return report_content


def main():
    parser = argparse.ArgumentParser(description='募资文件对比工具')
    parser.add_argument('--input', '-i', required=True, help='对比数据文件路径（JSON）')
    parser.add_argument('--output', '-o', required=True, help='输出报告目录')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("募资文件对比工具（招股书版）")
    print("=" * 60)
    
    print(f"\n[1/3] 加载对比数据：{args.input}")
    data = load_comparison_data(args.input)
    
    print(f"\n[2/3] 对比文件...")
    results = compare_documents(data)
    
    print(f"\n[3/3] 生成对比报告...")
    generate_report(results, args.output)
    
    print("\n" + "=" * 60)
    print("对比摘要")
    print("=" * 60)
    print(f"差异项目：{results['summary']['discrepancy_projects']} 个")
    print("=" * 60)


if __name__ == '__main__':
    main()
