#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
募投项目检查脚本
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import argparse
import json

# 募投项目检查标准
CHECK_STANDARDS = {
    'max_projects': 5,  # 最多项目数量
    'max_investment_ratio': 3.0,  # 投资总额/净资产上限
    'min_irr': 0.10,  # 最低内部收益率
    'max_payback_years': 7,  # 最长投资回收期
}


def load_project_data(input_path: str) -> Dict[str, Any]:
    """加载项目数据"""
    with open(input_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def check_compliance(projects: List[Dict]) -> Dict[str, Any]:
    """检查合规性"""
    results = {
        'policy_compliance': True,
        'approval_status': [],
        'land_compliance': True,
        'issues': []
    }

    for project in projects:
        project_name = project.get('name', '')

        # 检查审批状态
        approvals = project.get('approvals', {})
        required_approvals = ['project_filing', 'environmental_approval']

        for approval in required_approvals:
            status = approvals.get(approval, 'unknown')
            results['approval_status'].append({
                'project': project_name,
                'approval': approval,
                'status': status
            })
            if status != 'approved':
                results['issues'].append(f"{project_name} 的{approval}审批未完成")

    return results


def check_feasibility(projects: List[Dict]) -> Dict[str, Any]:
    """检查可行性"""
    results = {
        'market_feasibility': [],
        'technical_feasibility': [],
        'financial_feasibility': [],
        'issues': []
    }

    for project in projects:
        project_name = project.get('name', '')

        # 财务可行性
        financial = project.get('financial_analysis', {})
        irr = financial.get('irr', 0)
        payback_years = financial.get('payback_years', 999)

        financial_ok = irr >= CHECK_STANDARDS['min_irr'] and payback_years <= CHECK_STANDARDS['max_payback_years']

        results['financial_feasibility'].append({
            'project': project_name,
            'irr': irr,
            'payback_years': payback_years,
            'feasible': financial_ok
        })

        if not financial_ok:
            results['issues'].append(
                f"{project_name} 财务可行性不足（IRR={irr:.1%}, 回收期={payback_years:.1f}年）"
            )

    return results


def check_disclosure(projects: List[Dict]) -> Dict[str, Any]:
    """检查信息披露"""
    required_sections = [
        'project_overview',
        'investment_budget',
        'construction_schedule',
        'benefit_analysis',
        'risk_analysis'
    ]

    results = {
        'complete_sections': [],
        'missing_sections': [],
        'issues': []
    }

    for project in projects:
        project_name = project.get('name', '')
        disclosure = project.get('disclosure', {})

        for section in required_sections:
            if section in disclosure and disclosure[section]:
                results['complete_sections'].append({
                    'project': project_name,
                    'section': section
                })
            else:
                results['missing_sections'].append({
                    'project': project_name,
                    'section': section
                })
                results['issues'].append(f"{project_name} 缺少{section}披露")

    return results


def generate_report(results: Dict[str, Any], output_path: str) -> str:
    """生成检查报告"""
    lines = []

    lines.append("# 募投项目检查报告\n")
    lines.append(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    lines.append("---\n")

    # 合规性检查
    lines.append("## 一、合规性检查\n")
    compliance = results.get('compliance', {})

    if compliance.get('issues'):
        lines.append("### ⚠️ 合规性问题\n")
        for issue in compliance['issues']:
            lines.append(f"- {issue}")
    else:
        lines.append("### ✅ 合规性检查通过\n")
    lines.append("")

    # 审批状态
    if compliance.get('approval_status'):
        lines.append("### 审批状态\n")
        lines.append("| 项目 | 审批类型 | 状态 |")
        lines.append("|------|----------|------|")
        for status in compliance['approval_status']:
            status_icon = "✅" if status['status'] == 'approved' else "⏳"
            lines.append(f"| {status['project']} | {status['approval']} | {status_icon} {status['status']} |")
        lines.append("")

    # 可行性分析
    lines.append("## 二、可行性分析\n")
    feasibility = results.get('feasibility', {})

    if feasibility.get('financial_feasibility'):
        lines.append("### 财务可行性\n")
        lines.append("| 项目 | IRR | 投资回收期 | 可行性 |")
        lines.append("|------|-----|------------|--------|")
        for item in feasibility['financial_feasibility']:
            icon = "✅" if item['feasible'] else "❌"
            lines.append(f"| {item['project']} | {item['irr']:.1%} | {item['payback_years']:.1f}年 | {icon} |")
        lines.append("")

    # 信息披露
    lines.append("## 三、信息披露检查\n")
    disclosure = results.get('disclosure', {})

    if disclosure.get('missing_sections'):
        lines.append("### ⚠️ 缺失披露内容\n")
        for item in disclosure['missing_sections']:
            lines.append(f"- {item['project']}：缺少{item['section']}")
    else:
        lines.append("### ✅ 信息披露完整\n")
    lines.append("")

    # 总体结论
    lines.append("## 四、总体结论\n")
    all_issues = (
        compliance.get('issues', []) +
        feasibility.get('issues', []) +
        disclosure.get('issues', [])
    )

    if all_issues:
        lines.append(f"### 发现 {len(all_issues)} 项问题，需整改后申报\n")
        for idx, issue in enumerate(all_issues, 1):
            lines.append(f"{idx}. {issue}")
    else:
        lines.append("### ✅ 募投项目检查通过，可以申报\n")

    # 输出报告
    report_content = "\n".join(lines)

    output_file = Path(output_path) / f"募投项目检查报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report_content)

    print(f"检查报告已生成：{output_file}")
    return report_content


def main():
    parser = argparse.ArgumentParser(description='募投项目检查工具')
    parser.add_argument('--input', '-i', required=True, help='项目数据文件路径（JSON）')
    parser.add_argument('--output', '-o', required=True, help='输出报告目录')

    args = parser.parse_args()

    print("=" * 60)
    print("募投项目检查工具")
    print("=" * 60)

    print(f"\n[1/3] 加载项目数据：{args.input}")
    data = load_project_data(args.input)
    projects = data.get('projects', [])
    print(f"      项目数量：{len(projects)}")

    print(f"\n[2/3] 执行检查...")
    results = {
        'compliance': check_compliance(projects),
        'feasibility': check_feasibility(projects),
        'disclosure': check_disclosure(projects)
    }

    print(f"\n[3/3] 生成检查报告...")
    generate_report(results, args.output)

    print("\n" + "=" * 60)
    print("检查完成")
    print("=" * 60)


if __name__ == '__main__':
    main()
