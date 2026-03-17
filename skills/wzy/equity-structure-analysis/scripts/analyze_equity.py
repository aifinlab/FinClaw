#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
股权结构分析脚本
"""

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any


def load_equity_data(input_path: str) -> Dict[str, Any]:
    """加载股权数据"""
    with open(input_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def analyze_shareholders(data: Dict[str, Any]) -> Dict[str, Any]:
    """分析股东情况"""
    results = {
        'shareholder_summary': {},
        '穿透分析': [],
        'risk_flags': [],
        'special_arrangements': []
    }
    
    shareholders = data.get('shareholders', [])
    
    # 股东分类统计
    individual_count = 0
    corporate_count = 0
    partnership_count = 0
    fund_count = 0
    
    for shareholder in shareholders:
        holder_type = shareholder.get('type', '')
        if holder_type == 'individual':
            individual_count += 1
        elif holder_type == 'corporate':
            corporate_count += 1
        elif holder_type == 'partnership':
            partnership_count += 1
        elif holder_type in ['fund', 'asset_management']:
            fund_count += 1
        
        # 检查风险信号
        risk_flags = check_risk_flags(shareholder)
        if risk_flags:
            results['risk_flags'].append({
                'shareholder': shareholder.get('name', ''),
                'flags': risk_flags
            })
        
        # 检查特殊权利安排
        special_rights = shareholder.get('special_rights', [])
        if special_rights:
            results['special_arrangements'].append({
                'shareholder': shareholder.get('name', ''),
                'rights': special_rights,
                'status': shareholder.get('rights_status', '未清理')
            })
    
    results['shareholder_summary'] = {
        'total': len(shareholders),
        'individual': individual_count,
        'corporate': corporate_count,
        'partnership': partnership_count,
        'fund': fund_count
    }
    
    return results


def check_risk_flags(shareholder: Dict[str, Any]) -> List[str]:
    """检查风险信号"""
    flags = []
    
    # 持股比例与出资能力不匹配
    if shareholder.get('holding_ratio', 0) > 10 and not shareholder.get('capital_source_verified', False):
        flags.append('出资来源未核实')
    
    # 不参与公司治理
    if shareholder.get('holding_ratio', 0) > 5 and shareholder.get('participate_governance', False) is False:
        flags.append('不参与公司治理')
    
    # 股权转让价格异常
    if shareholder.get('abnormal_transfer_price', False):
        flags.append('股权转让价格异常')
    
    # 股东背景与公司业务无关
    if shareholder.get('unrelated_background', False):
        flags.append('股东背景与公司业务无关')
    
    # 存在代持嫌疑
    if shareholder.get('suspected_nominee', False):
        flags.append('疑似代持')
    
    return flags


def generate_report(results: Dict[str, Any], output_path: str) -> str:
    """生成分析报告"""
    lines = []
    
    lines.append("# 股权结构分析报告\n")
    lines.append(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    lines.append("---\n")
    
    # 股东概况
    lines.append("## 股东概况\n")
    summary = results.get('shareholder_summary', {})
    lines.append(f"- 股东总数：{summary.get('total', 0)} 名")
    lines.append(f"- 自然人股东：{summary.get('individual', 0)} 名")
    lines.append(f"- 法人股东：{summary.get('corporate', 0)} 名")
    lines.append(f"- 合伙企业：{summary.get('partnership', 0)} 名")
    lines.append(f"- 资管产品/基金：{summary.get('fund', 0)} 名\n")
    
    # 风险信号
    if results['risk_flags']:
        lines.append("## ⚠️ 风险信号\n")
        for item in results['risk_flags']:
            lines.append(f"### {item['shareholder']}")
            lines.append("风险信号：")
            for flag in item['flags']:
                lines.append(f"- {flag}")
            lines.append("")
    else:
        lines.append("## ✅ 未发现明显风险信号\n")
    
    # 特殊权利安排
    if results['special_arrangements']:
        lines.append("## ⚠️ 特殊权利安排\n")
        for item in results['special_arrangements']:
            lines.append(f"### {item['shareholder']}")
            lines.append(f"权利条款：{', '.join(item['rights'])}")
            lines.append(f"清理状态：{item['status']}")
            lines.append("")
    else:
        lines.append("## ✅ 无特殊权利安排\n")
    
    # 结论
    lines.append("## 分析结论\n")
    has_issues = bool(results['risk_flags']) or bool(results['special_arrangements'])
    if has_issues:
        lines.append("股权结构存在需关注事项，建议进一步核查并规范。\n")
    else:
        lines.append("股权结构清晰，股东适格，符合 IPO 要求。\n")
    
    # 输出报告
    report_content = "\n".join(lines)
    
    output_file = Path(output_path) / f"股权结构分析报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"分析报告已生成：{output_file}")
    return report_content


def main():
    parser = argparse.ArgumentParser(description='股权结构分析工具')
    parser.add_argument('--input', '-i', required=True, help='股东数据文件路径（JSON）')
    parser.add_argument('--output', '-o', required=True, help='输出报告目录')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("股权结构分析工具")
    print("=" * 60)
    
    print(f"\n[1/3] 加载股东数据：{args.input}")
    data = load_equity_data(args.input)
    
    print(f"\n[2/3] 分析股权结构...")
    results = analyze_shareholders(data)
    
    print(f"\n[3/3] 生成分析报告...")
    generate_report(results, args.output)
    
    print("\n" + "=" * 60)
    print("分析摘要")
    print("=" * 60)
    summary = results.get('shareholder_summary', {})
    print(f"股东总数：{summary.get('total', 0)} 名")
    print(f"风险信号：{len(results['risk_flags'])} 项")
    print(f"特殊安排：{len(results['special_arrangements'])} 项")
    print("=" * 60)


if __name__ == '__main__':
    main()
