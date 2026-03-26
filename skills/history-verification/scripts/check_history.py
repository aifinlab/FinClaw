#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
历史沿革核验脚本
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import argparse
import json

# 历史沿革事项类型
EVENT_TYPES = {
    'establishment': '设立',
    'capital_increase': '增资',
    'capital_decrease': '减资',
    'equity_transfer': '股权转让',
    'restructuring': '改制重组',
    'name_change': '名称变更',
    'address_change': '地址变更',
    'business_scope_change': '经营范围变更',
    'other': '其他变更'
}

# 必需文件清单
REQUIRED_DOCUMENTS = {
    'establishment': ['设立批复', '验资报告', '公司章程', '营业执照'],
    'capital_increase': ['增资协议', '股东会决议', '验资报告', '工商变更'],
    'capital_decrease': ['减资决议', '债权人公告', '验资报告', '工商变更'],
    'equity_transfer': ['股权转让协议', '股东会决议', '价款凭证', '完税证明', '工商变更'],
    'restructuring': ['改制方案', '审计评估', '批复文件', '工商变更'],
}


def load_history_data(input_path: str) -> Dict[str, Any]:
    """加载历史沿革数据"""
    with open(input_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def verify_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """核验单个事项"""
    result = {
        'event_id': event.get('id', ''),
        'event_type': event.get('type', ''),
        'event_date': event.get('date', ''),
        'description': event.get('description', ''),
        'status': 'pass',
        'issues': [],
        'missing_documents': []
    }

    event_type = event.get('type', '')
    documents = event.get('documents', [])

    # 检查必需文件
    required = REQUIRED_DOCUMENTS.get(event_type, [])
    doc_names = [d.get('name', '') for d in documents]

    for req_doc in required:
        if req_doc not in doc_names:
            result['missing_documents'].append(req_doc)
            result['issues'].append(f"缺少文件：{req_doc}")

    # 检查关键信息
    if not event.get('date'):
        result['issues'].append("缺少变更日期")
        result['status'] = 'warning'

    if not event.get('description'):
        result['issues'].append("缺少变更说明")
        result['status'] = 'warning'

    # 判断状态
    if result['missing_documents']:
        result['status'] = 'fail'
    elif result['issues']:
        result['status'] = 'warning'
    else:
        result['status'] = 'pass'

    return result


def verify_history(data: Dict[str, Any]) -> Dict[str, Any]:
    """核验历史沿革"""
    results = {
        'company_info': data.get('company_info', {}),
        'events': [],
        'summary': {}
    }

    events = data.get('events', [])

    for event in events:
        result = verify_event(event)
        results['events'].append(result)

    # 计算摘要
    total = len(results['events'])
    passed = sum(1 for e in results['events'] if e['status'] == 'pass')
    warnings = sum(1 for e in results['events'] if e['status'] == 'warning')
    failed = sum(1 for e in results['events'] if e['status'] == 'fail')

    results['summary'] = {
        'verify_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_events': total,
        'passed': passed,
        'warnings': warnings,
        'failed': failed,
        'pass_rate': f"{(passed/total*100):.1f}%" if total > 0 else 'N/A'
    }

    return results


def generate_report(results: Dict[str, Any], output_path: str) -> str:
    """生成核验报告"""
    lines = []

    lines.append("# 历史沿革核验报告\n")
    lines.append(f"生成时间：{results['summary']['verify_date']}\n")
    lines.append("---\n")

    # 公司基本信息
    company = results.get('company_info', {})
    lines.append("## 公司基本情况\n")
    lines.append(f"- 公司名称：{company.get('name', 'N/A')}")
    lines.append(f"- 设立时间：{company.get('establishment_date', 'N/A')}")
    lines.append(f"- 注册资本：{company.get('registered_capital', 'N/A')}")
    lines.append(f"- 变更次数：{results['summary']['total_events']} 次\n")

    # 核验概况
    lines.append("## 核验概况\n")
    summary = results['summary']
    lines.append(f"- 核验事项：{summary['total_events']} 项")
    lines.append(f"- 核验通过：{summary['passed']} 项")
    lines.append(f"- 存在瑕疵：{summary['warnings']} 项")
    lines.append(f"- 存在问题：{summary['failed']} 项")
    lines.append(f"- 通过率：{summary['pass_rate']}\n")

    # 存在问题事项
    failed_events = [e for e in results['events'] if e['status'] in ['warning', 'fail']]
    if failed_events:
        lines.append("## ⚠️ 存在问题事项\n")
        for idx, event in enumerate(failed_events, 1):
            event_type = EVENT_TYPES.get(event['event_type'], event['event_type'])
            lines.append(f"### {idx}. {event['event_date']} {event_type}")
            lines.append(f"状态：{'❌ 存在问题' if event['status'] == 'fail' else '⚠️ 存在瑕疵'}")
            if event['issues']:
                lines.append("问题：")
                for issue in event['issues']:
                    lines.append(f"- {issue}")
            if event['missing_documents']:
                lines.append(f"缺失文件：{', '.join(event['missing_documents'])}")
            lines.append("")

    # 核验结论
    lines.append("## 核验结论\n")
    if summary['failed'] > 0:
        lines.append(f"历史沿革存在{summary['failed']}项问题，需整改后申报。\n")
    elif summary['warnings'] > 0:
        lines.append(f"历史沿革基本清晰，存在{summary['warnings']}项瑕疵，建议补充完善。\n")
    else:
        lines.append("历史沿革清晰，历次变更合法有效，符合 IPO 要求。\n")

    # 输出报告
    report_content = "\n".join(lines)

    output_file = Path(output_path) / f"历史沿革核验报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report_content)

    print(f"核验报告已生成：{output_file}")
    return report_content


def main():
    parser = argparse.ArgumentParser(description='历史沿革核验工具')
    parser.add_argument('--input', '-i', required=True, help='历史沿革数据文件路径（JSON）')
    parser.add_argument('--output', '-o', required=True, help='输出报告目录')

    args = parser.parse_args()

    print("=" * 60)
    print("历史沿革核验工具")
    print("=" * 60)

    print(f"\n[1/3] 加载历史沿革数据：{args.input}")
    data = load_history_data(args.input)

    print(f"\n[2/3] 执行核验...")
    results = verify_history(data)

    print(f"\n[3/3] 生成核验报告...")
    generate_report(results, args.output)

    print("\n" + "=" * 60)
    print("核验摘要")
    print("=" * 60)
    print(f"通过率：{results['summary']['pass_rate']}")
    print(f"存在问题：{results['summary']['failed']} 项")
    print("=" * 60)


if __name__ == '__main__':
    main()
