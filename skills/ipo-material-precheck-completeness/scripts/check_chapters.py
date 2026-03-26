#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
招股书章节完整性检查脚本
"""

from datetime import datetime
from pathlib import Path
import argparse
import json
import re

# 标准章节结构
STANDARD_CHAPTERS = [
    {"id": "01", "name": "封面、书脊、目录、释义", "required": True,
     "subsections": ["封面", "书脊", "目录", "释义"]},
    {"id": "02", "name": "概览", "required": True,
     "subsections": ["发行人简介", "控股股东及实际控制人简介", "主要财务数据", "本次发行情况", "募集资金用途"]},
    {"id": "03", "name": "本次发行概况", "required": True,
     "subsections": ["股票种类", "发行股数", "每股面值", "发行价格", "发行方式", "发行对象"]},
    {"id": "04", "name": "风险因素", "required": True,
     "subsections": ["市场风险", "经营风险", "财务风险", "管理风险", "技术风险", "募集资金投资项目风险"]},
    {"id": "05", "name": "发行人基本情况", "required": True,
     "subsections": ["发行人基本信息", "历史沿革", "股权结构", "控股股东及实际控制人", "子公司及参股公司", "员工情况"]},
    {"id": "06", "name": "业务与技术", "required": True,
     "subsections": ["主营业务概况", "行业基本情况", "竞争地位", "主要产品/服务", "业务模式",
                    "主要原材料及采购", "主要客户及销售", "主要固定资产", "主要无形资产", "核心技术及研发"]},
    {"id": "07", "name": "同业竞争与关联交易", "required": True,
     "subsections": ["同业竞争情况", "关联方及关联关系", "关联交易情况", "规范关联交易的措施"]},
    {"id": "08", "name": "董事、监事、高级管理人员与核心技术人员", "required": True,
     "subsections": ["董事、监事、高管简历", "核心技术人员简历", "薪酬情况", "兼职情况", "持股情况"]},
    {"id": "09", "name": "公司治理", "required": True,
     "subsections": ["股东大会制度", "董事会制度", "监事会制度", "独立董事制度", "董事会秘书制度", "内部控制制度"]},
    {"id": "10", "name": "财务会计信息", "required": True,
     "subsections": ["财务报表", "主要会计政策", "会计估计变更", "合并报表范围", "非经常性损益", "主要财务指标"]},
    {"id": "11", "name": "管理层讨论与分析", "required": True,
     "subsections": ["财务状况分析", "盈利能力分析", "现金流量分析", "资本性支出分析"]},
    {"id": "12", "name": "业务发展目标", "required": True,
     "subsections": ["发展战略", "经营目标", "发展计划", "假设条件"]},
    {"id": "13", "name": "募集资金运用", "required": True,
     "subsections": ["募集资金总额", "投资项目概况", "项目可行性分析", "项目实施计划", "项目效益分析"]},
    {"id": "14", "name": "股利分配政策", "required": True,
     "subsections": ["现行股利分配政策", "最近三年分红情况", "发行后股利分配政策", "分红回报规划"]},
    {"id": "15", "name": "其他重要事项", "required": True,
     "subsections": ["重大合同", "对外担保", "诉讼仲裁", "行政处罚"]},
    {"id": "16", "name": "有关声明", "required": True,
     "subsections": ["发行人声明", "保荐机构声明", "会计师事务所声明", "律师事务所声明"]},
    {"id": "17", "name": "备查文件", "required": True,
     "subsections": ["备查文件清单", "查阅时间", "查阅地点"]},
]


def load_prospectus_text(input_path):
    """加载招股书文本"""
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return content


def analyze_chapters(content):
    """分析章节结构"""
    results = {
        'found_chapters': [],
        'missing_chapters': [],
        'incomplete_chapters': [],
        'summary': {}
    }

    # 检测章节
    chapter_pattern = r'第 [零一二三四五六七八九十百\d]+节\s*[：:]\s*(.+?)(?:\n|$)'
    found_chapters = re.findall(chapter_pattern, content)

    found_chapter_names = [name.strip() for _, name in found_chapters]

    # 检查每个标准章节
    for std_chapter in STANDARD_CHAPTERS:
        chapter_name = std_chapter['name']
        is_required = std_chapter['required']

        # 查找匹配的章节
        found = False
        for found_name in found_chapter_names:
            if chapter_name.split()[0] in found_name or chapter_name in found_name:
                found = True
                results['found_chapters'].append({
                    **std_chapter,
                    'found_as': found_name
                })
                break

        if not found:
            if is_required:
                results['missing_chapters'].append(std_chapter)
            else:
                results['incomplete_chapters'].append(std_chapter)

    # 计算完整率
    required_count = sum(1 for c in STANDARD_CHAPTERS if c['required'])
    found_required = len([c for c in results['found_chapters'] if c['required']])

    if required_count > 0:
        completeness_rate = (found_required / required_count) * 100
    else:
        completeness_rate = 0

    results['summary'] = {
        'check_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_chapters': len(STANDARD_CHAPTERS),
        'required_chapters': required_count,
        'found_chapters': len(results['found_chapters']),
        'missing_chapters': len(results['missing_chapters']),
        'completeness_rate': f"{completeness_rate:.1f}%"
    }

    return results


def generate_report(results, output_path):
    """生成检查报告"""
    report_lines = []

    report_lines.append("# 招股书章节完整性检查报告\n")
    report_lines.append(f"生成时间：{results['summary']['check_date']}\n")
    report_lines.append("---\n")

    # 检查概况
    report_lines.append("## 检查概况\n")
    summary = results['summary']
    report_lines.append(f"- 检查标准：《公开发行证券的公司信息披露内容与格式准则第 1 号》")
    report_lines.append(f"- 应包含章节：{summary['total_chapters']} 节")
    report_lines.append(f"- 已包含章节：{summary['found_chapters']} 节")
    report_lines.append(f"- 缺失章节：{summary['missing_chapters']} 节")
    report_lines.append(f"- **完整率：{summary['completeness_rate']}**\n")

    # 已包含章节
    if results['found_chapters']:
        report_lines.append("## ✅ 已包含章节\n")
        report_lines.append("| 序号 | 章节编号 | 章节名称 |")
        report_lines.append("|------|----------|----------|")
        for idx, chapter in enumerate(results['found_chapters'], 1):
            report_lines.append(f"| {idx} | 第{chapter['id']}节 | {chapter['name']} |")
        report_lines.append("")

    # 缺失章节
    if results['missing_chapters']:
        report_lines.append("## ❌ 缺失章节\n")
        report_lines.append("| 序号 | 章节编号 | 章节名称 |")
        report_lines.append("|------|----------|----------|")
        for idx, chapter in enumerate(results['missing_chapters'], 1):
            report_lines.append(f"| {idx} | 第{chapter['id']}节 | {chapter['name']} |")
        report_lines.append("")

        report_lines.append("### 补正建议\n")
        report_lines.append("请尽快补充以下章节：\n")
        for idx, chapter in enumerate(results['missing_chapters'], 1):
            report_lines.append(f"{idx}. **第{chapter['id']}节 {chapter['name']}**")
            if chapter.get('subsections'):
                report_lines.append(f"   应包含内容：{', '.join(chapter['subsections'][:5])}...")
        report_lines.append("")

    # 输出报告
    report_content = "\n".join(report_lines)

    output_file = Path(output_path) / f"章节完整性检查报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report_content)

    print(f"检查报告已生成：{output_file}")

    return report_content


def main():
    parser = argparse.ArgumentParser(description='招股书章节完整性检查工具')
    parser.add_argument('--input', '-i', required=True, help='招股书文本文件路径')
    parser.add_argument('--output', '-o', required=True, help='输出报告目录')

    args = parser.parse_args()

    print("=" * 60)
    print("招股书章节完整性检查工具")
    print("=" * 60)

    print(f"\n[1/3] 加载招股书：{args.input}")
    content = load_prospectus_text(args.input)
    print(f"      文件大小：{len(content)} 字符")

    print(f"\n[2/3] 分析章节结构...")
    results = analyze_chapters(content)

    print(f"\n[3/3] 生成检查报告...")
    generate_report(results, args.output)

    print("\n" + "=" * 60)
    print("检查摘要")
    print("=" * 60)
    summary = results['summary']
    print(f"完整率：{summary['completeness_rate']}")
    print(f"缺失章节：{summary['missing_chapters']} 节")
    print("=" * 60)


if __name__ == '__main__':
    main()
