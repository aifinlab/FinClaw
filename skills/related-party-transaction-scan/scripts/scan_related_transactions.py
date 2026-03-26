#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
关联交易扫描脚本
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import argparse
import json


def load_transaction_data(input_path: str) -> Dict[str, Any]:
    """加载关联交易数据"""
    with open(input_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def scan_transactions(data: Dict[str, Any]) -> Dict[str, Any]:
    """扫描关联交易"""
    results = {
        'related_parties': [],
        'transaction_summary': {},
        'fairness_analysis': [],
        'risk_flags': []
    }

    # 关联方清单
    results['related_parties'] = data.get('related_parties', [])

    # 交易汇总
    transactions = data.get('transactions', [])
    summary = {}

    for tx in transactions:
        tx_type = tx.get('type', 'other')
        year = tx.get('year', 'unknown')
        amount = tx.get('amount', 0)

        if tx_type not in summary:
            summary[tx_type] = {}
        if year not in summary[tx_type]:
            summary[tx_type][year] = 0
        summary[tx_type][year] += amount

    results['transaction_summary'] = summary

    # 公允性分析
    for tx in transactions:
        fairness = analyze_fairness(tx)
        if fairness:
            results['fairness_analysis'].append(fairness)

    # 风险识别
    results['risk_flags'] = identify_risks(data, summary)

    return results


def analyze_fairness(transaction: Dict[str, Any]) -> Dict[str, Any]:
    """分析交易公允性"""
    related_price = transaction.get('related_price', 0)
    market_price = transaction.get('market_price', 0)

    if market_price > 0:
        diff_rate = abs(related_price - market_price) / market_price
        return {
            'transaction': transaction.get('description', ''),
            'related_price': related_price,
            'market_price': market_price,
            'diff_rate': f"{diff_rate*100:.1f}%",
            'fair': diff_rate < 0.10  # 差异率<10% 视为公允
        }
    return None


def identify_risks(data: Dict[str, Any], summary: Dict) -> List[Dict[str, Any]]:
    """识别风险"""
    risks = []

    # 检查关联交易占比
    total_revenue = data.get('total_revenue', 0)
    total_purchase = data.get('total_purchase', 0)

    related_sales = sum(summary.get('销售商品', {}).values())
    related_purchase = sum(summary.get('采购商品', {}).values())

    if total_revenue > 0:
        sales_ratio = related_sales / total_revenue
        if sales_ratio > 0.30:
            risks.append({
                'type': '关联销售占比过高',
                'value': f"{sales_ratio*100:.1f}%",
                'level': 'high'
            })

    if total_purchase > 0:
        purchase_ratio = related_purchase / total_purchase
        if purchase_ratio > 0.30:
            risks.append({
                'type': '关联采购占比过高',
                'value': f"{purchase_ratio*100:.1f}%",
                'level': 'high'
            })

    # 检查资金占用
    fund_occupation = data.get('fund_occupation', 0)
    if fund_occupation > 0:
        risks.append({
            'type': '关联资金占用',
            'value': f"{fund_occupation:,.0f}元",
            'level': 'high'
        })

    return risks


def generate_report(results: Dict[str, Any], output_path: str) -> str:
    """生成扫描报告"""
    lines = []

    lines.append("# 关联交易扫描报告\n")
    lines.append(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    lines.append("---\n")

    # 关联方概况
    lines.append("## 关联方概况\n")
    parties = results.get('related_parties', [])
    lines.append(f"- 关联法人：{sum(1 for p in parties if p.get('type') == 'corporate')} 家")
    lines.append(f"- 关联自然人：{sum(1 for p in parties if p.get('type') == 'individual')} 名")
    lines.append(f"- 关联方总数：{len(parties)}\n")

    # 交易汇总
    lines.append("## 关联交易汇总\n")
    summary = results.get('transaction_summary', {})
    lines.append("| 交易类型 | 金额（万元） |")
    lines.append("|----------|--------------|")
    for tx_type, amounts in summary.items():
        total = sum(amounts.values())
        lines.append(f"| {tx_type} | {total/10000:.1f} |")
    lines.append("")

    # 公允性分析
    fairness = results.get('fairness_analysis', [])
    if fairness:
        lines.append("## 公允性分析\n")
        lines.append("| 交易 | 关联价格 | 市场均价 | 差异率 | 是否公允 |")
        lines.append("|------|----------|----------|--------|----------|")
        for item in fairness:
            icon = "✅" if item['fair'] else "⚠️"
            lines.append(f"| {item['transaction']} | {item['related_price']} | {item['market_price']} | {item['diff_rate']} | {icon} |")
        lines.append("")

    # 风险提示
    risks = results.get('risk_flags', [])
    if risks:
        lines.append("## ⚠️ 风险提示\n")
        for risk in risks:
            level_icon = "🔴" if risk['level'] == 'high' else "🟡"
            lines.append(f"{level_icon} **{risk['type']}**：{risk['value']}")
        lines.append("")
    else:
        lines.append("## ✅ 未发现重大风险\n")

    # 结论
    lines.append("## 扫描结论\n")
    if risks:
        lines.append("关联交易存在需关注事项，建议进一步规范。\n")
    else:
        lines.append("关联交易必要、定价公允，符合 IPO 要求。\n")

    # 输出报告
    report_content = "\n".join(lines)

    output_file = Path(output_path) / f"关联交易扫描报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report_content)

    print(f"扫描报告已生成：{output_file}")
    return report_content


def main():
    parser = argparse.ArgumentParser(description='关联交易扫描工具')
    parser.add_argument('--input', '-i', required=True, help='关联交易数据文件路径（JSON）')
    parser.add_argument('--output', '-o', required=True, help='输出报告目录')

    args = parser.parse_args()

    print("=" * 60)
    print("关联交易扫描工具")
    print("=" * 60)

    print(f"\n[1/3] 加载关联交易数据：{args.input}")
    data = load_transaction_data(args.input)

    print(f"\n[2/3] 扫描关联交易...")
    results = scan_transactions(data)

    print(f"\n[3/3] 生成扫描报告...")
    generate_report(results, args.output)

    print("\n" + "=" * 60)
    print("扫描摘要")
    print("=" * 60)
    print(f"关联方数量：{len(results['related_parties'])}")
    print(f"风险提示：{len(results['risk_flags'])} 项")
    print("=" * 60)


if __name__ == '__main__':
    main()
