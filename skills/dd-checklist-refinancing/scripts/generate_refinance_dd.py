#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
再融资尽调问题清单生成脚本
"""

import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# 再融资尽调问题模板
REFINANCE_QUESTIONS = {
    'company_basic': {
        'title': '一、公司基本情况',
        'questions': [
            '请说明公司设立及上市情况',
            '请说明公司股权结构及控制关系',
            '请说明控股股东及实际控制人情况',
            '请提供子公司及参股公司清单',
            '请说明三会运作情况',
            '请说明内部控制制度及执行情况',
            '请说明信息披露情况',
            '请说明承诺履行情况',
        ]
    },
    'previous_fundraising': {
        'title': '二、前次募集资金使用',
        'questions': [
            '请说明前次募集资金的时间、方式、金额',
            '请说明前次募投项目情况',
            '请提供前次募资验资报告',
            '请说明前次募资使用进度',
            '请说明募投项目建设进度及达产情况',
            '请说明募投项目效益实现情况',
            '请说明是否存在募资用途变更情况',
            '请说明募资变更的决策程序',
            '请说明前次募资结余情况及原因',
            '请说明结余资金的后续安排',
        ]
    },
    'necessity': {
        'title': '三、本次募集资金必要性',
        'questions': [
            '请说明本次融资背景及目的',
            '请说明融资规模的合理性',
            '请说明融资时机的选择',
            '请说明公司业务发展规划',
            '请说明资金需求分析',
            '请说明融资渠道比较',
            '请说明股权融资的优势',
        ]
    },
    'investment_project': {
        'title': '四、本次募投项目',
        'questions': [
            '请说明募投项目背景及必要性',
            '请说明募投项目具体内容',
            '请提供投资估算及构成',
            '请说明建设周期及实施计划',
            '请说明市场可行性分析',
            '请说明技术可行性分析',
            '请说明财务可行性分析',
            '请提供项目备案/核准文件',
            '请提供环评批复文件',
            '请提供用地手续文件',
            '请说明项目效益测算及依据',
            '请说明项目风险及应对措施',
        ]
    },
    'finance': {
        'title': '五、财务情况',
        'questions': [
            '请提供最近三年及一期财务报表',
            '请说明资产负债情况',
            '请说明盈利能力及变动趋势',
            '请说明现金流量情况',
            '请说明偿债能力指标',
            '请说明主要会计政策',
            '请说明收入确认政策',
            '请说明资产减值计提情况',
        ]
    },
    'legal': {
        'title': '六、法律合规',
        'questions': [
            '请说明最近三年行政处罚情况',
            '请说明未决诉讼、仲裁情况',
            '请说明被监管措施情况',
            '请说明诚信记录',
            '请说明对外担保情况',
            '请说明关联担保情况',
            '请说明担保合规性',
        ]
    },
    'issuance_plan': {
        'title': '七、发行方案',
        'questions': [
            '请说明发行对象范围',
            '请说明发行对象资格',
            '请说明认购意向情况',
            '请说明锁定期安排',
            '请说明定价基准日',
            '请说明定价方式',
            '请说明发行底价',
            '请说明调价机制（如有）',
            '请说明发行数量上限',
            '请说明发行后股权结构变化',
            '请说明对控制权的影响',
        ]
    }
}


def generate_questions(financing_type: str = '定增') -> Dict[str, Any]:
    """生成问题清单"""
    results = {
        'financing_type': financing_type,
        'categories': [],
        'total_questions': 0
    }
    
    question_num = 1
    for category_id, category_data in REFINANCE_QUESTIONS.items():
        category = {
            'id': category_id,
            'title': category_data['title'],
            'questions': []
        }
        
        for q in category_data['questions']:
            category['questions'].append({
                'num': question_num,
                'question': q
            })
            question_num += 1
        
        results['categories'].append(category)
        results['total_questions'] += len(category_data['questions'])
    
    results['generate_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    return results


def generate_report(results: Dict[str, Any], output_path: str) -> str:
    """生成问题清单报告"""
    lines = []
    
    lines.append("# 再融资尽职调查问题清单\n")
    lines.append(f"生成时间：{results['generate_date']}")
    lines.append(f"融资类型：{results['financing_type']}\n")
    lines.append("---\n")
    
    lines.append(f"## 问题概况\n")
    lines.append(f"- 问题类别：{len(results['categories'])} 类")
    lines.append(f"- 问题总数：{results['total_questions']} 项\n")
    
    # 各类问题
    for category in results['categories']:
        lines.append(f"## {category['title']}\n")
        for q in category['questions']:
            lines.append(f"{q['num']}. {q['question']}")
        lines.append("")
    
    # 输出报告
    report_content = "\n".join(lines)
    
    output_file = Path(output_path) / f"再融资尽调问题清单_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"问题清单已生成：{output_file}")
    return report_content


def main():
    parser = argparse.ArgumentParser(description='再融资尽调问题清单生成工具')
    parser.add_argument('--type', '-t', default='定增', help='融资类型（定增/配股/可转债）')
    parser.add_argument('--output', '-o', required=True, help='输出报告目录')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("再融资尽调问题清单生成工具")
    print("=" * 60)
    
    print(f"\n[1/2] 生成问题清单（融资类型：{args.type}）...")
    results = generate_questions(args.type)
    
    print(f"\n[2/2] 生成问题清单报告...")
    generate_report(results, args.output)
    
    print("\n" + "=" * 60)
    print("生成摘要")
    print("=" * 60)
    print(f"问题类别：{len(results['categories'])} 类")
    print(f"问题总数：{results['total_questions']} 项")
    print("=" * 60)


if __name__ == '__main__':
    main()
