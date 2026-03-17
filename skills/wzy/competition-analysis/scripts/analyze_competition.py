#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
同业竞争分析脚本
"""

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any


def load_competition_data(input_path: str) -> Dict[str, Any]:
    """加载同业竞争数据"""
    with open(input_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def analyze_competition(data: Dict[str, Any]) -> Dict[str, Any]:
    """分析同业竞争"""
    results = {
        'related_parties': [],
        'competition_analysis': [],
        'solutions': [],
        'summary': {}
    }
    
    related_parties = data.get('related_parties', [])
    issuer_business = data.get('issuer_business', {})
    
    # 分析每个关联方
    for party in related_parties:
        analysis = compare_business(party, issuer_business)
        results['competition_analysis'].append(analysis)
    
    # 识别同业竞争
    competition_cases = [
        a for a in results['competition_analysis'] 
        if a['is_competition'] or a['is_similar']
    ]
    
    # 生成解决方案建议
    for case in competition_cases:
        solution = suggest_solution(case)
        results['solutions'].append({
            'party': case['party_name'],
            'issue': case['issue_type'],
            'solution': solution
        })
    
    # 摘要
    results['summary'] = {
        'analyze_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_parties': len(related_parties),
        'competition_count': len([c for c in results['competition_analysis'] if c['is_competition']]),
        'similar_count': len([c for c in results['competition_analysis'] if c['is_similar'] and not c['is_competition']]),
        'no_competition_count': len([c for c in results['competition_analysis'] if not c['is_competition'] and not c['is_similar']])
    }
    
    return results


def compare_business(party: Dict[str, Any], issuer: Dict[str, Any]) -> Dict[str, Any]:
    """比对业务"""
    result = {
        'party_name': party.get('name', ''),
        'party_business': party.get('business', ''),
        'is_competition': False,
        'is_similar': False,
        'issue_type': '',
        'similarity_score': 0
    }
    
    party_products = set(party.get('products', []))
    issuer_products = set(issuer.get('products', []))
    
    # 计算产品相似度
    if issuer_products:
        overlap = party_products & issuer_products
        similarity = len(overlap) / len(issuer_products)
        result['similarity_score'] = similarity
        
        if similarity > 0.5:
            result['is_competition'] = True
            result['issue_type'] = '同业竞争'
        elif similarity > 0.2:
            result['is_similar'] = True
            result['issue_type'] = '业务相似'
    
    # 检查客户重叠
    party_customers = set(party.get('customers', []))
    issuer_customers = set(issuer.get('customers', []))
    
    if party_customers & issuer_customers:
        result['customer_overlap'] = True
        if result['is_similar']:
            result['is_competition'] = True
            result['issue_type'] = '同业竞争（客户重叠）'
    
    return result


def suggest_solution(analysis: Dict[str, Any]) -> str:
    """建议解决方案"""
    issue_type = analysis.get('issue_type', '')
    
    if '同业竞争' in issue_type:
        return "建议：1. 收购竞争方股权；2. 竞争方停止竞争业务；3. 竞争方转让给无关联第三方"
    elif '业务相似' in issue_type:
        return "建议：1. 划分业务区域/客户；2. 竞争方变更经营范围；3. 出具避免竞争承诺"
    else:
        return "无需特别处理"


def generate_report(results: Dict[str, Any], output_path: str) -> str:
    """生成分析报告"""
    lines = []
    
    lines.append("# 同业竞争分析报告\n")
    lines.append(f"生成时间：{results['summary']['analyze_date']}\n")
    lines.append("---\n")
    
    # 分析概况
    lines.append("## 分析概况\n")
    summary = results['summary']
    lines.append(f"- 关联方总数：{summary['total_parties']} 家")
    lines.append(f"- 存在同业竞争：{summary['competition_count']} 家")
    lines.append(f"- 业务相似：{summary['similar_count']} 家")
    lines.append(f"- 无竞争关系：{summary['no_competition_count']} 家\n")
    
    # 同业竞争情况
    competition_cases = [c for c in results['competition_analysis'] if c['is_competition']]
    if competition_cases:
        lines.append("## ⚠️ 同业竞争情况\n")
        lines.append("| 竞争方 | 主营业务 | 相似度 | 问题类型 |")
        lines.append("|--------|----------|--------|----------|")
        for case in competition_cases:
            lines.append(f"| {case['party_name']} | {case['party_business']} | {case['similarity_score']*100:.0f}% | {case['issue_type']} |")
        lines.append("")
    
    # 解决方案
    if results['solutions']:
        lines.append("## 解决方案建议\n")
        for idx, sol in enumerate(results['solutions'], 1):
            lines.append(f"### {idx}. {sol['party']}")
            lines.append(f"**问题**：{sol['issue']}")
            lines.append(f"**建议**：{sol['solution']}\n")
    
    # 结论
    lines.append("## 分析结论\n")
    if summary['competition_count'] > 0:
        lines.append(f"存在{summary['competition_count']}家同业竞争方，需制定解决方案并实施整改。\n")
    elif summary['similar_count'] > 0:
        lines.append(f"存在{summary['similar_count']}家业务相似方，建议进一步核查并规范。\n")
    else:
        lines.append("不存在同业竞争，符合 IPO 要求。\n")
    
    # 输出报告
    report_content = "\n".join(lines)
    
    output_file = Path(output_path) / f"同业竞争分析报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"分析报告已生成：{output_file}")
    return report_content


def main():
    parser = argparse.ArgumentParser(description='同业竞争分析工具')
    parser.add_argument('--input', '-i', required=True, help='关联方数据文件路径（JSON）')
    parser.add_argument('--output', '-o', required=True, help='输出报告目录')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("同业竞争分析工具")
    print("=" * 60)
    
    print(f"\n[1/3] 加载关联方数据：{args.input}")
    data = load_competition_data(args.input)
    
    print(f"\n[2/3] 分析同业竞争...")
    results = analyze_competition(data)
    
    print(f"\n[3/3] 生成分析报告...")
    generate_report(results, args.output)
    
    print("\n" + "=" * 60)
    print("分析摘要")
    print("=" * 60)
    print(f"同业竞争：{results['summary']['competition_count']} 家")
    print(f"业务相似：{results['summary']['similar_count']} 家")
    print("=" * 60)


if __name__ == '__main__':
    main()
