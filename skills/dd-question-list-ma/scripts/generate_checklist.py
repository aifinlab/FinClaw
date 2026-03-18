#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
并购尽调问题清单生成脚本
用于根据行业类型生成定制化的尽调问题清单
"""

import json
from datetime import datetime

# 行业特定问题库
INDUSTRY_QUESTIONS = {
    "TMT": [
        "请说明公司的核心技术来源及先进性",
        "请介绍研发投入占比及研发人员情况",
        "请说明用户/客户数据的获取方式及合规性",
        "请介绍核心技术的保护措施（专利、软著等）",
        "请说明技术迭代风险及应对措施",
        "请介绍获客成本及用户生命周期价值",
        "请说明平台/系统的稳定性和安全性"
    ],
    "医疗": [
        "请说明产品/服务的医疗器械注册证情况",
        "请介绍研发管线及临床进展",
        "请说明医保准入情况及影响",
        "请介绍带量采购政策对公司的影响",
        "请说明核心产品的专利保护情况",
        "请介绍医疗事故及纠纷情况",
        "请说明两票制等政策的影响"
    ],
    "制造": [
        "请说明产能利用率及扩产计划",
        "请介绍主要设备的成新率及折旧情况",
        "请说明原材料价格波动的影响及应对措施",
        "请介绍安全生产及环保合规情况",
        "请说明产品质量控制体系",
        "请介绍核心技术人员及稳定性",
        "请说明供应链稳定性及替代方案"
    ],
    "消费": [
        "请说明品牌定位及品牌价值",
        "请介绍销售渠道结构及变化趋势",
        "请说明经销商管理模式及返利政策",
        "请介绍产品质量及食品安全控制",
        "请说明消费者投诉及处理情况",
        "请介绍营销推广策略及效果",
        "请说明库存管理及周转情况"
    ]
}

def generate_checklist(industry: str, transaction_type: str = "控股收购") -> dict:
    """
    生成尽调问题清单
    
    Args:
        industry: 行业类型 (TMT/医疗/制造/消费)
        transaction_type: 交易类型 (控股收购/参股投资/资产收购)
    
    Returns:
        问题清单字典
    """
    # 基础问题模块
    base_modules = [
        "一、业务与商业尽调",
        "二、财务尽调",
        "三、法律尽调",
        "四、人力资源尽调",
        "五、并购整合专项"
    ]
    
    # 获取行业特定问题
    industry_questions = INDUSTRY_QUESTIONS.get(industry, [])
    
    checklist = {
        "project_name": "",
        "industry": industry,
        "transaction_type": transaction_type,
        "generated_date": datetime.now().strftime("%Y-%m-%d"),
        "modules": base_modules,
        "industry_specific_questions": industry_questions,
        "total_questions": len(industry_questions) + 20  # 基础问题 + 行业问题
    }
    
    return checklist

def export_to_json(checklist: dict, output_path: str):
    """导出为 JSON 文件"""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(checklist, f, ensure_ascii=False, indent=2)
    print(f"清单已导出至：{output_path}")

if __name__ == "__main__":
    # 示例：生成 TMT 行业尽调清单
    checklist = generate_checklist(industry="TMT", transaction_type="控股收购")
    export_to_json(checklist, "ma_dd_checklist.json")
    print(f"生成问题总数：{checklist['total_questions']}")
