#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
招股书章节检查脚本
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import argparse
import re

# 章节检查要点
CHAPTER_CHECKPOINTS = {
    '01': {'name': '封面目录释义', 'required_elements': ['发行人名称', '股票类型', '发行股数', '目录', '释义']},
    '02': {'name': '概览', 'required_elements': ['发行人简介', '控股股东', '财务数据', '发行情况', '募集资金']},
    '03': {'name': '本次发行概况', 'required_elements': ['股票种类', '发行股数', '发行价格', '发行方式']},
    '04': {'name': '风险因素', 'required_elements': ['市场风险', '经营风险', '财务风险', '管理风险']},
    '05': {'name': '发行人基本情况', 'required_elements': ['基本信息', '历史沿革', '股权结构', '子公司']},
    '06': {'name': '业务与技术', 'required_elements': ['主营业务', '行业情况', '竞争地位', '业务模式', '核心技术']},
    '07': {'name': '同业竞争与关联交易', 'required_elements': ['同业竞争', '关联方', '关联交易']},
    '08': {'name': '董监高与核心技术人员', 'required_elements': ['简历', '薪酬', '兼职', '持股']},
    '09': {'name': '公司治理', 'required_elements': ['股东大会', '董事会', '监事会', '独立董事', '内部控制']},
    '10': {'name': '财务会计信息', 'required_elements': ['财务报表', '会计政策', '财务指标']},
    '11': {'name': '管理层讨论与分析', 'required_elements': ['财务状况', '盈利能力', '现金流量']},
    '12': {'name': '业务发展目标', 'required_elements': ['发展战略', '经营目标', '发展计划']},
    '13': {'name': '募集资金运用', 'required_elements': ['投资总额', '项目概况', '可行性', '效益分析']},
    '14': {'name': '股利分配政策', 'required_elements': ['现行政策', '分红情况', '发行后政策']},
    '15': {'name': '其他重要事项', 'required_elements': ['重大合同', '对外担保', '诉讼仲裁']},
    '16': {'name': '有关声明', 'required_elements': ['发行人声明', '保荐机构声明', '会计师声明', '律师声明']},
    '17': {'name': '备查文件', 'required_elements': ['备查文件清单', '查阅时间', '查阅地点']},
}


def load_prospectus_text(input_path: str) -> str:
    """加载招股书文本"""
    with open(input_path, 'r', encoding='utf-8') as f:
        return f.read()


def check_chapter_content(text: str, chapter_id: str, chapter_info: Dict) -> Dict[str, Any]:
    """检查章节内容"""
    result = {
        'chapter_id': chapter_id,
        'chapter_name': chapter_info['name'],
        'found_elements': [],
        'missing_elements': [],
        'status': 'pass'
    }

    # 简单检查：查找关键元素是否在文本中
    for element in chapter_info['required_elements']:
        if element in text:
            result['found_elements'].append(element)
        else:
            result['missing_elements'].append(element)

    # 判断状态
    missing_ratio = len(result['missing_elements']) / len(chapter_info['required_elements'])
    if missing_ratio == 0:
        result['status'] = 'pass'
    elif missing_ratio < 0.5:
        result['status'] = 'warning'
    else:
        result['status'] = 'fail'

    return result


def analyze_prospectus(text: str) -> Dict[str, Any]:
    """分析招股书"""
    results = {
        'chapter_results': [],
        'summary': {}
    }

    # 提取各章节内容（简化处理）
    chapter_pattern = r'第 ([零一二三四五六七八九十\d]+) 节'
    chapters_found = re.findall(chapter_pattern, text)

    # 检查每个章节
    for chapter_id, chapter_info in CHAPTER_CHECKPOINTS.items():
        result = check_chapter_content(text, chapter_id, chapter_info)
        results['chapter_results'].append(result)

    # 计算摘要
    total_chapters = len(CHAPTER_CHECKPOINTS)
    passed = sum(1 for r in results['chapter_results'] if r['status'] == 'pass')
    warnings = sum(1 for r in results['chapter_results'] if r['status'] == 'warning')
    failed = sum(1 for r in results['chapter_results'] if r['status'] == 'fail')

    results['summary'] = {
        'check_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_chapters': total_chapters,
        'passed': passed,
        'warnings': warnings,
        'failed': failed,
        'pass_rate': f"{(passed/total_chapters*100):.1f}%"
    }

    return results


def generate_report(results: Dict[str, Any], output_path: str) -> str:
    """生成检查报告"""
    lines = []

    lines.append("# 招股书章节检查报告\n")
    lines.append(f"生成时间：{results['summary']['check_date']}\n")
    lines.append("---\n")

    # 检查概况
    lines.append("## 检查概况\n")
    summary = results['summary']
    lines.append(f"- 检查章节：{summary['total_chapters']} 节")
    lines.append(f"- 通过：{summary['passed']} 节")
    lines.append(f"- 待完善：{summary['warnings']} 节")
    lines.append(f"- 缺失：{summary['failed']} 节")
    lines.append(f"- 通过率：{summary['pass_rate']}\n")

    # 待完善章节
    warning_results = [r for r in results['chapter_results'] if r['status'] in ['warning', 'fail']]
    if warning_results:
        lines.append("## ⚠️ 待完善章节\n")
        for result in warning_results:
            lines.append(f"### {result['chapter_id']}. {result['chapter_name']}")
            lines.append(f"状态：{'❌ 缺失' if result['status'] == 'fail' else '⚠️ 待完善'}")
            if result['missing_elements']:
                lines.append(f"缺失要素：{', '.join(result['missing_elements'])}")
            lines.append("")

    # 通过章节
    passed_results = [r for r in results['chapter_results'] if r['status'] == 'pass']
    if passed_results:
        lines.append("## ✅ 通过章节\n")
        for result in passed_results:
            lines.append(f"- {result['chapter_id']}. {result['chapter_name']}")
        lines.append("")

    # 输出报告
    report_content = "\n".join(lines)

    output_file = Path(output_path) / f"招股书章节检查报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report_content)

    print(f"检查报告已生成：{output_file}")
    return report_content


def main():
    parser = argparse.ArgumentParser(description='招股书章节检查工具')
    parser.add_argument('--input', '-i', required=True, help='招股书文本文件路径')
    parser.add_argument('--output', '-o', required=True, help='输出报告目录')

    args = parser.parse_args()

    print("=" * 60)
    print("招股书章节检查工具")
    print("=" * 60)

    print(f"\n[1/3] 加载招股书：{args.input}")
    text = load_prospectus_text(args.input)
    print(f"      文件大小：{len(text)} 字符")

    print(f"\n[2/3] 检查章节内容...")
    results = analyze_prospectus(text)

    print(f"\n[3/3] 生成检查报告...")
    generate_report(results, args.output)

    print("\n" + "=" * 60)
    print("检查摘要")
    print("=" * 60)
    print(f"通过率：{results['summary']['pass_rate']}")
    print(f"待完善：{results['summary']['warnings']} 节")
    print("=" * 60)


if __name__ == '__main__':
    main()
