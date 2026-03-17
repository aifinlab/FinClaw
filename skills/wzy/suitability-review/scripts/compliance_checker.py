#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合规审核工具
用于研报合规检查、风险披露验证、适当性匹配
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple


class ComplianceChecker:
    """合规审核器"""
    
    # 禁止词汇
    PROHIBITED_WORDS = [
        '暴涨', '暴跌', '翻倍', '必涨', '稳赚', '一定', '肯定',
        '最佳', '第一', '最强', '唯一', '绝对', '保证'
    ]
    
    # 评级选项
    VALID_RATINGS = ['买入', '增持', '中性', '减持', '卖出', '未评级']
    
    # 风险等级
    RISK_LEVELS = ['R1', 'R2', 'R3', 'R4', 'R5']
    
    @staticmethod
    def check_title(title: str) -> Dict:
        """
        检查标题合规性
        
        Args:
            title: 标题
            
        Returns:
            检查结果
        """
        issues = []
        
        # 检查禁止词汇
        for word in ComplianceChecker.PROHIBITED_WORDS:
            if word in title:
                issues.append(f'标题包含禁止词汇：{word}')
        
        # 检查是否包含公司名
        if len(title) < 5:
            issues.append('标题过短，建议包含公司/行业名称')
        
        # 检查是否有实质内容
        if '分析' in title and len(title) < 10:
            issues.append('标题过于空泛，建议体现核心观点')
        
        return {
            'title': title,
            'valid': len(issues) == 0,
            'issues': issues
        }
    
    @staticmethod
    def check_rating(rating: str, has_target_price: bool, has_logic: bool) -> Dict:
        """
        检查评级合规性
        
        Args:
            rating: 评级
            has_target_price: 是否有目标价
            has_logic: 是否有逻辑支撑
            
        Returns:
            检查结果
        """
        issues = []
        
        # 检查评级有效性
        if rating not in ComplianceChecker.VALID_RATINGS:
            issues.append(f'无效评级：{rating}，应为{ComplianceChecker.VALID_RATINGS}')
        
        # 检查是否有目标价
        if rating in ['买入', '增持'] and not has_target_price:
            issues.append('买入/增持评级应有目标价支撑')
        
        # 检查是否有逻辑
        if not has_logic:
            issues.append('评级应有逻辑支撑')
        
        return {
            'rating': rating,
            'valid': len(issues) == 0,
            'issues': issues
        }
    
    @staticmethod
    def check_data_sources(text: str) -> Dict:
        """
        检查数据来源标注
        
        Args:
            text: 报告文本
            
        Returns:
            检查结果
        """
        issues = []
        
        # 检查是否有数据来源
        source_patterns = [
            r'来源 [：:]\s*\w+',
            r'数据来自 [：:]\s*\w+',
            r'根据\s*\w+',
            r'Wind', '同花顺', 'iFinD', '公司公告', '年报'
        ]
        
        has_source = any(re.search(p, text) for p in source_patterns)
        
        if not has_source:
            issues.append('未标注数据来源')
        
        # 检查是否有时点
        time_patterns = [
            r'\d{4}年 \d{1,2}月 \d{1,2}日',
            r'\d{4}-\d{2}-\d{2}',
            r'截至 \d{4}年',
            r'20\d{2}年'
        ]
        
        has_time = any(re.search(p, text) for p in time_patterns)
        
        if not has_time:
            issues.append('未标注数据时点')
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'has_source': has_source,
            'has_time': has_time
        }
    
    @staticmethod
    def check_risk_disclosure(text: str) -> Dict:
        """
        检查风险披露
        
        Args:
            text: 报告文本
            
        Returns:
            检查结果
        """
        issues = []
        
        # 检查是否有风险提示章节
        has_risk_section = bool(re.search(r'风险 [提示 | 因素 | 警告]', text))
        
        if not has_risk_section:
            issues.append('缺少风险提示章节')
        else:
            # 检查风险数量
            risk_items = re.findall(r'[-•*]\s*[^-\n]+风险 [^-\n]*', text)
            if len(risk_items) < 2:
                issues.append('风险提示不足（建议至少 2 条）')
        
        # 检查风险是否具体
        vague_risks = ['市场风险', '投资风险', '其他风险']
        for vague in vague_risks:
            if vague in text and len(text.split(vague)[0]) < 100:
                issues.append(f'风险提示过于空泛：{vague}')
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'has_risk_section': has_risk_section
        }
    
    @staticmethod
    def check_disclaimer(text: str) -> Dict:
        """
        检查免责声明
        
        Args:
            text: 报告文本
            
        Returns:
            检查结果
        """
        issues = []
        
        # 检查必要声明
        required_phrases = [
            '仅供参考', '不构成投资建议', '投资有风险', '据此操作'
        ]
        
        has_disclaimer = any(phrase in text for phrase in required_phrases)
        
        if not has_disclaimer:
            issues.append('缺少免责声明')
        
        # 检查分析师声明
        has_analyst_statement = bool(re.search(r'分析师 (声明 | 承诺)', text))
        
        if not has_analyst_statement:
            issues.append('缺少分析师声明')
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'has_disclaimer': has_disclaimer,
            'has_analyst_statement': has_analyst_statement
        }
    
    @staticmethod
    def check_suitability(risk_level: str, product_risk: str) -> Dict:
        """
        检查适当性匹配
        
        Args:
            risk_level: 客户风险等级 (C1-C5)
            product_risk: 产品风险等级 (R1-R5)
            
        Returns:
            检查结果
        """
        issues = []
        
        # 等级映射
        level_map = {'C1': 1, 'C2': 2, 'C3': 3, 'C4': 4, 'C5': 5,
                     'R1': 1, 'R2': 2, 'R3': 3, 'R4': 4, 'R5': 5}
        
        customer_level = level_map.get(risk_level, 0)
        product_level = level_map.get(product_risk, 0)
        
        if customer_level == 0:
            issues.append(f'无效客户风险等级：{risk_level}')
        if product_level == 0:
            issues.append(f'无效产品风险等级：{product_risk}')
        
        if customer_level > 0 and product_level > 0:
            if product_level > customer_level:
                issues.append(f'产品风险 ({product_risk}) 高于客户风险承受能力 ({risk_level})，需超配警示')
        
        return {
            'customer_risk': risk_level,
            'product_risk': product_risk,
            'matched': product_level <= customer_level,
            'valid': len(issues) == 0,
            'issues': issues
        }
    
    @staticmethod
    def generate_compliance_report(report_data: Dict) -> Dict:
        """
        生成合规审核报告
        
        Args:
            report_data: 报告数据
            
        Returns:
            合规报告
        """
        results = {}
        all_issues = []
        
        # 标题检查
        if 'title' in report_data:
            results['title'] = ComplianceChecker.check_title(report_data['title'])
            all_issues.extend(results['title'].get('issues', []))
        
        # 评级检查
        if 'rating' in report_data:
            results['rating'] = ComplianceChecker.check_rating(
                report_data['rating'],
                report_data.get('has_target_price', False),
                report_data.get('has_logic', False)
            )
            all_issues.extend(results['rating'].get('issues', []))
        
        # 数据来源检查
        if 'text' in report_data:
            results['data_sources'] = ComplianceChecker.check_data_sources(report_data['text'])
            all_issues.extend(results['data_sources'].get('issues', []))
            
            results['risk_disclosure'] = ComplianceChecker.check_risk_disclosure(report_data['text'])
            all_issues.extend(results['risk_disclosure'].get('issues', []))
            
            results['disclaimer'] = ComplianceChecker.check_disclaimer(report_data['text'])
            all_issues.extend(results['disclaimer'].get('issues', []))
        
        # 适当性检查
        if 'risk_level' in report_data and 'product_risk' in report_data:
            results['suitability'] = ComplianceChecker.check_suitability(
                report_data['risk_level'],
                report_data['product_risk']
            )
            all_issues.extend(results['suitability'].get('issues', []))
        
        # 综合结论
        if len(all_issues) == 0:
            conclusion = '通过，可发布'
        elif len(all_issues) <= 2:
            conclusion = '修改后通过'
        else:
            conclusion = '不通过，需重大修改'
        
        return {
            'results': results,
            'all_issues': all_issues,
            'issue_count': len(all_issues),
            'conclusion': conclusion,
            'checked_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }


def main():
    """测试函数"""
    # 测试数据
    test_report = {
        'title': 'XX 公司：业绩高速增长，建议买入',
        'rating': '买入',
        'has_target_price': True,
        'has_logic': True,
        'text': """
        来源：Wind，截至 2024 年 3 月
        公司 2023 年营收增长 50%...
        
        风险提示：
        - 行业竞争加剧风险
        - 原材料价格波动风险
        
        免责声明：本报告仅供参考，不构成投资建议。投资有风险，据此操作风险自担。
        分析师声明：本人承诺独立、客观地出具本报告。
        """,
        'risk_level': 'C4',
        'product_risk': 'R3'
    }
    
    # 生成合规报告
    report = ComplianceChecker.generate_compliance_report(test_report)
    
    print("合规审核报告:")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
