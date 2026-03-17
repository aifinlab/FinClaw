#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
风险因素披露检查脚本
"""

import argparse
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# 风险类别定义
RISK_CATEGORIES = {
    'market_risk': {
        'name': '市场风险',
        'keywords': ['市场', '宏观', '周期', '竞争', '价格', '需求', '贸易', '汇率'],
        'sub_risks': ['宏观经济波动', '行业周期', '市场竞争', '产品价格', '市场需求', '贸易政策', '汇率波动']
    },
    'operational_risk': {
        'name': '经营风险',
        'keywords': ['经营', '客户', '供应商', '原材料', '质量', '安全', '环保', '扩张', '境外'],
        'sub_risks': ['客户集中', '供应商集中', '原材料价格', '产品质量', '安全生产', '环保', '业务扩张', '境外经营']
    },
    'financial_risk': {
        'name': '财务风险',
        'keywords': ['财务', '应收', '存货', '毛利率', '税收', '补助', '偿债', '现金流', '担保'],
        'sub_risks': ['应收账款', '存货跌价', '毛利率波动', '税收优惠', '政府补助', '偿债', '现金流', '对外担保']
    },
    'management_risk': {
        'name': '管理风险',
        'keywords': ['管理', '实际控制', '人员', '内控', '规模', '并购'],
        'sub_risks': ['实际控制人控制', '核心人员流失', '内部控制', '规模扩张管理', '并购整合']
    },
    'technology_risk': {
        'name': '技术风险',
        'keywords': ['技术', '研发', '专利', '知识产权', '泄密', '迭代'],
        'sub_risks': ['技术迭代', '核心技术泄密', '核心技术人员流失', '研发失败', '知识产权纠纷', '技术许可到期']
    },
    'investment_risk': {
        'name': '募投项目风险',
        'keywords': ['募投', '项目', '产能', '效益', '折旧'],
        'sub_risks': ['项目实施', '产能消化', '效益不达预期', '折旧摊销增加']
    },
    'issuance_risk': {
        'name': '发行风险',
        'keywords': ['发行', '股价', '摊薄', '回报'],
        'sub_risks': ['发行失败', '股价波动', '摊薄即期回报']
    },
    'legal_risk': {
        'name': '法律风险',
        'keywords': ['法律', '诉讼', '仲裁', '处罚', '资质', '劳动'],
        'sub_risks': ['诉讼仲裁', '行政处罚', '资质许可', '劳动用工']
    },
    'other_risk': {
        'name': '其他风险',
        'keywords': ['其他', '不可抗力'],
        'sub_risks': ['不可抗力', '其他特定风险']
    }
}


def load_risk_text(input_path: str) -> str:
    """加载风险章节文本"""
    with open(input_path, 'r', encoding='utf-8') as f:
        return f.read()


def analyze_risk_disclosure(text: str) -> Dict[str, Any]:
    """分析风险披露情况"""
    results = {
        'covered_categories': [],
        'missing_categories': [],
        'risk_items': [],
        'quality_assessment': {}
    }
    
    # 检测已覆盖的风险类别
    for category_id, category_info in RISK_CATEGORIES.items():
        covered = False
        for keyword in category_info['keywords']:
            if keyword in text:
                covered = True
                break
        
        if covered:
            results['covered_categories'].append({
                'id': category_id,
                'name': category_info['name']
            })
        else:
            results['missing_categories'].append({
                'id': category_id,
                'name': category_info['name']
            })
    
    # 提取风险条目
    risk_pattern = r'[（(]\d+[）)]\s*([^\n]+)|^\d+[\.,]\s*([^\n]+)|^（[一二三四五六七八九十]+）\s*([^\n]+)'
    risk_matches = re.findall(risk_pattern, text, re.MULTILINE)
    
    for match in risk_matches:
        risk_text = next((m for m in match if m), '')
        if risk_text and len(risk_text) > 5:
            results['risk_items'].append(risk_text.strip())
    
    # 质量评估
    total_categories = len(RISK_CATEGORIES)
    covered_count = len(results['covered_categories'])
    coverage_rate = (covered_count / total_categories * 100) if total_categories > 0 else 0
    
    results['quality_assessment'] = {
        'coverage_rate': f"{coverage_rate:.1f}%",
        'risk_item_count': len(results['risk_items']),
        'rating': '优秀' if coverage_rate >= 90 else '良好' if coverage_rate >= 70 else '待改进'
    }
    
    return results


def generate_report(results: Dict[str, Any], output_path: str) -> str:
    """生成检查报告"""
    lines = []
    
    lines.append("# 风险因素披露检查报告\n")
    lines.append(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    lines.append("---\n")
    
    # 检查概况
    lines.append("## 检查概况\n")
    qa = results.get('quality_assessment', {})
    lines.append(f"- 应披露风险类别：{len(RISK_CATEGORIES)} 类")
    lines.append(f"- 已披露风险类别：{len(results['covered_categories'])} 类")
    lines.append(f"- 风险条目数量：{qa.get('risk_item_count', 0)} 条")
    lines.append(f"- 覆盖率：{qa.get('coverage_rate', '0%')}")
    lines.append(f"- 质量评级：**{qa.get('rating', '未知')}**\n")
    
    # 已覆盖类别
    if results['covered_categories']:
        lines.append("## ✅ 已披露风险类别\n")
        for cat in results['covered_categories']:
            lines.append(f"- {cat['name']}")
        lines.append("")
    
    # 缺失类别
    if results['missing_categories']:
        lines.append("## ⚠️ 缺失风险类别\n")
        for cat in results['missing_categories']:
            lines.append(f"- {cat['name']}")
        lines.append("")
    
    # 改进建议
    if results['missing_categories']:
        lines.append("## 📝 改进建议\n")
        lines.append("建议补充以下风险类别的披露：\n")
        for idx, cat in enumerate(results['missing_categories'], 1):
            category_info = RISK_CATEGORIES.get(cat['id'], {})
            sub_risks = category_info.get('sub_risks', [])
            lines.append(f"{idx}. **{cat['name']}**")
            if sub_risks:
                lines.append(f"   可披露：{', '.join(sub_risks[:3])}等")
        lines.append("")
    
    # 输出报告
    report_content = "\n".join(lines)
    
    output_file = Path(output_path) / f"风险披露检查报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"检查报告已生成：{output_file}")
    return report_content


def main():
    parser = argparse.ArgumentParser(description='风险因素披露检查工具')
    parser.add_argument('--input', '-i', required=True, help='风险章节文本文件路径')
    parser.add_argument('--output', '-o', required=True, help='输出报告目录')
    parser.add_argument('--industry', help='行业代码（可选）')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("风险因素披露检查工具")
    print("=" * 60)
    
    print(f"\n[1/3] 加载风险章节：{args.input}")
    text = load_risk_text(args.input)
    print(f"      文本长度：{len(text)} 字符")
    
    print(f"\n[2/3] 分析风险披露...")
    results = analyze_risk_disclosure(text)
    
    print(f"\n[3/3] 生成检查报告...")
    generate_report(results, args.output)
    
    print("\n" + "=" * 60)
    print("检查摘要")
    print("=" * 60)
    qa = results.get('quality_assessment', {})
    print(f"覆盖率：{qa.get('coverage_rate', 'N/A')}")
    print(f"质量评级：{qa.get('rating', 'N/A')}")
    print("=" * 60)


if __name__ == '__main__':
    main()
