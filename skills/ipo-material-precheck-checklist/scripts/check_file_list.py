#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
IPO 材料文件清单检查脚本
用于系统检查 IPO 申报材料的文件完整性
"""

from datetime import datetime
from pathlib import Path
import argparse
import json

# 标准 IPO 文件清单（60 项）
STANDARD_FILE_LIST = [
    # 一、基础文件
    {"id": "A001", "name": "招股说明书（申报稿）", "category": "基础文件", "priority": "高", "required": True},
    {"id": "A002", "name": "发行保荐书", "category": "基础文件", "priority": "高", "required": True},
    {"id": "A003", "name": "审计报告（最近三年及一期）", "category": "基础文件", "priority": "高", "required": True},
    {"id": "A004", "name": "法律意见书", "category": "基础文件", "priority": "高", "required": True},
    {"id": "A005", "name": "律师工作报告", "category": "基础文件", "priority": "高", "required": True},

    # 二、主体资格文件
    {"id": "B001", "name": "发行人营业执照", "category": "主体资格", "priority": "高", "required": True},
    {"id": "B002", "name": "公司章程", "category": "主体资格", "priority": "高", "required": True},
    {"id": "B003", "name": "发起人协议", "category": "主体资格", "priority": "中", "required": True},
    {"id": "B004", "name": "工商登记档案", "category": "主体资格", "priority": "中", "required": True},
    {"id": "B005", "name": "税务登记证明", "category": "主体资格", "priority": "中", "required": False},

    # 三、历史沿革文件
    {"id": "C001", "name": "设立批准文件", "category": "历史沿革", "priority": "高", "required": True},
    {"id": "C002", "name": "历次验资报告", "category": "历史沿革", "priority": "高", "required": True},
    {"id": "C003", "name": "历次工商变更文件", "category": "历史沿革", "priority": "高", "required": True},
    {"id": "C004", "name": "股权转让协议", "category": "历史沿革", "priority": "中", "required": True},
    {"id": "C005", "name": "增资协议", "category": "历史沿革", "priority": "中", "required": True},
    {"id": "C006", "name": "国有资产批复（如适用）", "category": "历史沿革", "priority": "高", "required": False},
    {"id": "C007", "name": "外资审批文件（如适用）", "category": "历史沿革", "priority": "高", "required": False},

    # 四、业务资质文件
    {"id": "D001", "name": "业务经营许可证", "category": "业务资质", "priority": "高", "required": True},
    {"id": "D002", "name": "生产许可证", "category": "业务资质", "priority": "中", "required": False},
    {"id": "D003", "name": "产品认证证书", "category": "业务资质", "priority": "中", "required": False},
    {"id": "D004", "name": "质量管理体系认证", "category": "业务资质", "priority": "低", "required": False},
    {"id": "D005", "name": "环境评估批复", "category": "业务资质", "priority": "高", "required": True},
    {"id": "D006", "name": "安全生产许可证", "category": "业务资质", "priority": "中", "required": False},

    # 五、资产权属文件
    {"id": "E001", "name": "土地使用权证", "category": "资产权属", "priority": "高", "required": True},
    {"id": "E002", "name": "房屋所有权证", "category": "资产权属", "priority": "高", "required": True},
    {"id": "E003", "name": "专利证书", "category": "资产权属", "priority": "中", "required": True},
    {"id": "E004", "name": "商标注册证", "category": "资产权属", "priority": "中", "required": True},
    {"id": "E005", "name": "著作权登记证书", "category": "资产权属", "priority": "低", "required": False},

    # 六、重大合同文件
    {"id": "F001", "name": "重大销售合同", "category": "重大合同", "priority": "高", "required": True},
    {"id": "F002", "name": "重大采购合同", "category": "重大合同", "priority": "高", "required": True},
    {"id": "F003", "name": "借款合同及担保合同", "category": "重大合同", "priority": "高", "required": True},
    {"id": "F004", "name": "技术许可/转让合同", "category": "重大合同", "priority": "中", "required": False},
    {"id": "F005", "name": "关联交易协议", "category": "重大合同", "priority": "高", "required": True},

    # 七、财务税务文件
    {"id": "G001", "name": "最近三年纳税申报表", "category": "财务税务", "priority": "高", "required": True},
    {"id": "G002", "name": "税收优惠批复文件", "category": "财务税务", "priority": "中", "required": True},
    {"id": "G003", "name": "财政补贴文件", "category": "财务税务", "priority": "中", "required": True},
    {"id": "G004", "name": "社保缴纳证明", "category": "财务税务", "priority": "高", "required": True},
    {"id": "G005", "name": "住房公积金缴纳证明", "category": "财务税务", "priority": "高", "required": True},
    {"id": "G006", "name": "银行资信证明", "category": "财务税务", "priority": "低", "required": False},

    # 八、公司治理文件
    {"id": "H001", "name": "三会会议文件", "category": "公司治理", "priority": "高", "required": True},
    {"id": "H002", "name": "独立董事制度", "category": "公司治理", "priority": "中", "required": True},
    {"id": "H003", "name": "内部控制制度", "category": "公司治理", "priority": "高", "required": True},
    {"id": "H004", "name": "关联交易管理制度", "category": "公司治理", "priority": "高", "required": True},
    {"id": "H005", "name": "对外担保管理制度", "category": "公司治理", "priority": "高", "required": True},
    {"id": "H006", "name": "募集资金管理制度", "category": "公司治理", "priority": "高", "required": True},

    # 九、募投项目文件
    {"id": "I001", "name": "募投项目可行性研究报告", "category": "募投项目", "priority": "高", "required": True},
    {"id": "I002", "name": "项目备案/核准文件", "category": "募投项目", "priority": "高", "required": True},
    {"id": "I003", "name": "环评批复", "category": "募投项目", "priority": "高", "required": True},
    {"id": "I004", "name": "用地预审意见", "category": "募投项目", "priority": "中", "required": False},
    {"id": "I005", "name": "能评批复（如适用）", "category": "募投项目", "priority": "中", "required": False},

    # 十、其他重要文件
    {"id": "J001", "name": "控股股东/实际控制人承诺函", "category": "其他重要文件", "priority": "高", "required": True},
    {"id": "J002", "name": "董事、监事、高管承诺函", "category": "其他重要文件", "priority": "高", "required": True},
    {"id": "J003", "name": "避免同业竞争承诺", "category": "其他重要文件", "priority": "高", "required": True},
    {"id": "J004", "name": "规范关联交易承诺", "category": "其他重要文件", "priority": "高", "required": True},
    {"id": "J005", "name": "稳定股价预案", "category": "其他重要文件", "priority": "中", "required": True},
    {"id": "J006", "name": "分红政策承诺", "category": "其他重要文件", "priority": "中", "required": True},
    {"id": "J007", "name": "填补回报措施承诺", "category": "其他重要文件", "priority": "中", "required": True},
]


def load_submitted_files(input_path):
    """加载企业提交的文件清单"""
    submitted = {}

    if input_path.endswith('.json'):
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for item in data:
                submitted[item.get('name', '')] = {
                    'status': item.get('status', '已提供'),
                    'version': item.get('version', ''),
                    'date': item.get('date', ''),
                    'remarks': item.get('remarks', '')
                }
    elif input_path.endswith('.xlsx') or input_path.endswith('.xls'):
        try:
            import pandas as pd
            df = pd.read_excel(input_path)
            for _, row in df.iterrows():
                name = row.get('文件名称', row.get('name', ''))
                submitted[name] = {
                    'status': row.get('状态', row.get('status', '已提供')),
                    'version': row.get('版本', row.get('version', '')),
                    'date': row.get('日期', row.get('date', '')),
                    'remarks': row.get('备注', row.get('remarks', ''))
                }
        except ImportError:
            print("警告：pandas 未安装，无法读取 Excel 文件")
            print("请使用 JSON 格式的文件清单")
    else:
        print(f"不支持的文件格式：{input_path}")

    return submitted


def check_file_completeness(submitted_files):
    """检查文件完整性"""
    results = {
        'provided': [],
        'missing': [],
        'conditional': [],
        'summary': {}
    }

    total_required = 0
    total_provided = 0

    for file_item in STANDARD_FILE_LIST:
        file_name = file_item['name']
        is_required = file_item['required']

        if file_name in submitted_files:
            # 文件已提供
            results['provided'].append({
                **file_item,
                'submitted_info': submitted_files[file_name]
            })
            if is_required:
                total_required += 1
                total_provided += 1
        else:
            # 文件缺失
            if is_required:
                results['missing'].append(file_item)
                total_required += 1
            else:
                results['conditional'].append(file_item)

    # 计算完整率
    if total_required > 0:
        completeness_rate = (total_provided / total_required) * 100
    else:
        completeness_rate = 0

    results['summary'] = {
        'check_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_files': len(STANDARD_FILE_LIST),
        'required_files': total_required,
        'provided_files': total_provided,
        'missing_files': len(results['missing']),
        'conditional_files': len(results['conditional']),
        'completeness_rate': f"{completeness_rate:.1f}%"
    }

    return results


def generate_report(results, output_path):
    """生成检查报告"""
    report_lines = []

    # 报告标题
    report_lines.append("# IPO 材料文件清单检查报告\n")
    report_lines.append(f"生成时间：{results['summary']['check_date']}\n")
    report_lines.append("---\n")

    # 检查概况
    report_lines.append("## 检查概况\n")
    summary = results['summary']
    report_lines.append(f"- 检查标准：《公开发行证券的公司信息披露内容与格式准则》")
    report_lines.append(f"- 应提供文件：{summary['total_files']} 项")
    report_lines.append(f"- 必需文件：{summary['required_files']} 项")
    report_lines.append(f"- 已提供文件：{summary['provided_files']} 项")
    report_lines.append(f"- 缺失文件：{summary['missing_files']} 项")
    report_lines.append(f"- 条件性文件：{summary['conditional_files']} 项")
    report_lines.append(f"- **完整率：{summary['completeness_rate']}**\n")

    # 缺失文件清单
    if results['missing']:
        report_lines.append("## ❌ 缺失文件清单\n")
        report_lines.append("| 序号 | 文件 ID | 文件名称 | 类别 | 重要程度 |")
        report_lines.append("|------|---------|----------|------|----------|")
        for idx, item in enumerate(results['missing'], 1):
            report_lines.append(
                f"| {idx} | {item['id']} | {item['name']} | {item['category']} | {item['priority']} |"
            )
        report_lines.append("")

    # 条件性文件
    if results['conditional']:
        report_lines.append("## ⚠️ 条件性文件（视情况提供）\n")
        report_lines.append("| 序号 | 文件 ID | 文件名称 | 类别 | 适用条件 |")
        report_lines.append("|------|---------|----------|------|----------|")
        for idx, item in enumerate(results['conditional'], 1):
            condition = "如适用"
            if "国有" in item['name']:
                condition = "涉及国有资产"
            elif "外资" in item['name']:
                condition = "涉及外资"
            elif "能评" in item['name']:
                condition = "项目年综合能耗超过 1000 吨标准煤"
            elif "用地" in item['name']:
                condition = "涉及新增用地"

            report_lines.append(
                f"| {idx} | {item['id']} | {item['name']} | {item['category']} | {condition} |"
            )
        report_lines.append("")

    # 已提供文件
    report_lines.append("## ✅ 已提供文件\n")
    report_lines.append(f"共 {len(results['provided'])} 项文件已提供\n")

    # 补正建议
    if results['missing']:
        report_lines.append("## 📝 补正建议\n")
        for idx, item in enumerate(results['missing'], 1):
            report_lines.append(f"### {idx}. {item['name']}")

            suggestion = get_suggestion(item)
            report_lines.append(f"**建议**：{suggestion}\n")

    # 输出报告
    report_content = "\n".join(report_lines)

    output_file = Path(output_path) / f"IPO 文件清单检查报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report_content)

    print(f"检查报告已生成：{output_file}")

    # 同时输出 JSON 格式结果
    json_file = Path(output_path) / f"IPO 文件清单检查结果_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"检查结果 JSON 已生成：{json_file}")

    return report_content


def get_suggestion(file_item):
    """根据文件类型生成补正建议"""
    name = file_item['name']

    suggestions = {
        '纳税申报表': '联系主管税务机关，申请开具最近三年纳税证明或通过电子税务局导出',
        '社保缴纳证明': '向社保经办机构申请开具单位参保缴费证明（最近 12 个月）',
        '住房公积金缴纳证明': '向住房公积金管理中心申请开具缴存证明',
        '能评批复': '如募投项目年综合能耗超过 1000 吨标准煤，需编制节能报告并取得发改委批复',
        '环评批复': '委托有资质的环评机构编制环境影响报告，报生态环境部门审批',
        '用地预审意见': '向自然资源主管部门申请用地预审',
        '国有资产批复': '涉及国有股权变动的，需取得国资监管机构的批复文件',
        '外资审批文件': '涉及外资的，需取得商务主管部门的批准/备案文件',
    }

    for key, suggestion in suggestions.items():
        if key in name:
            return suggestion

    return f"请联系相关部门获取{ name }，确保文件在有效期内并加盖公章"


def main():
    parser = argparse.ArgumentParser(description='IPO 材料文件清单检查工具')
    parser.add_argument('--input', '-i', required=True, help='输入文件清单路径（JSON 或 Excel）')
    parser.add_argument('--output', '-o', required=True, help='输出报告目录')

    args = parser.parse_args()

    print("=" * 60)
    print("IPO 材料文件清单检查工具")
    print("=" * 60)

    # 加载提交的文件
    print(f"\n[1/3] 加载文件清单：{args.input}")
    submitted_files = load_submitted_files(args.input)
    print(f"      已加载 {len(submitted_files)} 项文件")

    # 检查完整性
    print(f"\n[2/3] 检查文件完整性...")
    results = check_file_completeness(submitted_files)

    # 生成报告
    print(f"\n[3/3] 生成检查报告...")
    generate_report(results, args.output)

    # 打印摘要
    print("\n" + "=" * 60)
    print("检查摘要")
    print("=" * 60)
    summary = results['summary']
    print(f"完整率：{summary['completeness_rate']}")
    print(f"缺失文件：{summary['missing_files']} 项")
    print(f"条件性文件：{summary['conditional_files']} 项")
    print("=" * 60)


if __name__ == '__main__':
    main()
