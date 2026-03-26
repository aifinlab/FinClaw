#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
IPO 尽调问题清单生成脚本
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import argparse

# 尽调问题模板
DD_QUESTIONS = {
    'company_basic': {
        'title': '一、公司基本情况',
        'questions': [
            '请说明公司设立背景及设立过程',
            '请提供公司历次股权变更的工商档案',
            '请说明是否存在重大资产重组情况',
            '请提供子公司及分支机构的营业执照及章程',
            '请说明公司现有股权结构',
            '请说明控股股东及实际控制人情况',
            '请说明是否存在股权代持情况',
        ]
    },
    'business': {
        'title': '二、业务与技术',
        'questions': [
            '请说明公司主营业务及产品/服务',
            '请说明公司业务模式及盈利模式',
            '请说明公司核心竞争力',
            '请说明行业发展状况及市场竞争格局',
            '请说明主要原材料及供应情况',
            '请提供前五大供应商名单及采购金额',
            '请说明生产模式及主要生产流程',
            '请说明主要客户情况及销售模式',
            '请提供前五大客户名单及销售金额',
            '请说明研发体系及核心技术',
            '请提供专利、商标等知识产权清单',
        ]
    },
    'finance': {
        'title': '三、财务会计',
        'questions': [
            '请提供最近三年及一期财务报表',
            '请说明主要会计政策及会计估计',
            '请说明收入确认政策及时点',
            '请说明成本构成及核算方法',
            '请说明期间费用构成及变动原因',
            '请说明应收账款账龄及坏账准备计提',
            '请说明存货构成及跌价准备计提',
            '请说明固定资产构成及折旧政策',
            '请说明税种、税率及税收优惠情况',
            '请提供最近三年纳税申报表',
        ]
    },
    'governance': {
        'title': '四、公司治理',
        'questions': [
            '请提供三会会议文件',
            '请说明内部控制制度及执行情况',
            '请提供内控评价报告',
            '请说明董监高任职资格及履职情况',
            '请提供董监高薪酬情况',
            '请说明董监高兼职情况',
        ]
    },
    'legal': {
        'title': '五、法律合规',
        'questions': [
            '请提供土地使用权证、房产证',
            '请提供主要知识产权证书',
            '请提供重大合同清单及合同文本',
            '请说明未决诉讼、仲裁情况',
            '请说明行政处罚情况',
            '请提供员工名册及社保、公积金缴纳证明',
            '请说明劳动纠纷情况',
        ]
    },
    'investment': {
        'title': '六、募投项目',
        'questions': [
            '请说明募投项目背景及必要性',
            '请提供募投项目可行性研究报告',
            '请说明投资估算及构成',
            '请说明建设周期及实施计划',
            '请提供项目备案/核准文件',
            '请提供环评批复文件',
            '请提供用地手续文件',
            '请说明项目效益测算及依据',
            '请说明项目风险及应对措施',
        ]
    }
}


def generate_questions(industry: str = 'general') -> Dict[str, Any]:
    """生成问题清单"""
    results = {
        'industry': industry,
        'categories': [],
        'total_questions': 0
    }

    question_num = 1
    for category_id, category_data in DD_QUESTIONS.items():
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

    lines.append("# IPO 尽职调查问题清单\n")
    lines.append(f"生成时间：{results['generate_date']}")
    lines.append(f"适用行业：{results['industry']}\n")
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

    output_file = Path(output_path) / f"IPO 尽调问题清单_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report_content)

    print(f"问题清单已生成：{output_file}")
    return report_content


def main():
    parser = argparse.ArgumentParser(description='IPO 尽调问题清单生成工具')
    parser.add_argument('--industry', '-i', default='general', help='行业类型')
    parser.add_argument('--output', '-o', required=True, help='输出报告目录')

    args = parser.parse_args()

    print("=" * 60)
    print("IPO 尽调问题清单生成工具")
    print("=" * 60)

    print(f"\n[1/2] 生成问题清单（行业：{args.industry}）...")
    results = generate_questions(args.industry)

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
