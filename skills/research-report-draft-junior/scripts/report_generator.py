#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
研报生成工具
用于生成研报框架、填充模板、格式化输出
"""

import json
from datetime import datetime
from typing import Dict, List, Optional


class ReportGenerator:
    """研报生成器"""
    
    # 研报类型
    REPORT_TYPES = {
        'company': '公司研报',
        'industry': '行业研报',
        'strategy': '策略研报',
        'comment': '点评研报'
    }
    
    # 评级选项
    RATINGS = ['买入', '增持', '中性', '减持', '卖出']
    
    @staticmethod
    def generate_report_framework(report_type: str, company_name: str = '') -> Dict:
        """
        生成研报框架
        
        Args:
            report_type: 研报类型
            company_name: 公司名称
            
        Returns:
            研报框架字典
        """
        frameworks = {
            'company': {
                'title': f'{company_name} 研究报告',
                'sections': [
                    '核心观点',
                    '公司概况',
                    '行业分析',
                    '公司分析',
                    '财务分析',
                    '盈利预测',
                    '估值与评级',
                    '风险提示'
                ]
            },
            'industry': {
                'title': '行业研究报告',
                'sections': [
                    '核心观点',
                    '行业定义与分类',
                    '市场规模与增长',
                    '产业链分析',
                    '竞争格局',
                    '发展趋势',
                    '投资建议',
                    '风险提示'
                ]
            },
            'strategy': {
                'title': '投资策略报告',
                'sections': [
                    '核心观点',
                    '市场环境分析',
                    '配置策略',
                    '重点推荐',
                    '风险提示'
                ]
            },
            'comment': {
                'title': f'{company_name} 点评报告',
                'sections': [
                    '事件概述',
                    '核心观点',
                    '详细分析',
                    '投资建议',
                    '风险提示'
                ]
            }
        }
        
        framework = frameworks.get(report_type, frameworks['company'])
        
        return {
            'type': report_type,
            'type_cn': ReportGenerator.REPORT_TYPES.get(report_type, '公司研报'),
            'title': framework['title'],
            'sections': framework['sections'],
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    @staticmethod
    def generate_title(company: str, core_view: str, suffix: str = '') -> str:
        """
        生成研报标题
        
        Args:
            company: 公司名称
            core_view: 核心观点
            suffix: 后缀（如"首次覆盖"）
            
        Returns:
            研报标题
        """
        if suffix:
            return f'{company}：{core_view}——{suffix}'
        return f'{company}：{core_view}'
    
    @staticmethod
    def format_rating(rating: str, target_price: float = None, current_price: float = None) -> Dict:
        """
        格式化投资评级
        
        Args:
            rating: 评级
            target_price: 目标价
            current_price: 当前价
            
        Returns:
            评级信息字典
        """
        if rating not in ReportGenerator.RATINGS:
            rating = '中性'
        
        result = {
            'rating': rating,
            'rating_date': datetime.now().strftime('%Y-%m-%d')
        }
        
        if target_price and current_price:
            upside = (target_price - current_price) / current_price * 100
            result['target_price'] = round(target_price, 2)
            result['current_price'] = round(current_price, 2)
            result['upside'] = round(upside, 2)
            result['upside_str'] = f"{upside:+.1f}%"
        
        return result
    
    @staticmethod
    def generate_risk_warnings(risk_type: str = 'common') -> List[str]:
        """
        生成风险提示模板
        
        Args:
            risk_type: 风险类型
            
        Returns:
            风险提示列表
        """
        templates = {
            'common': [
                '宏观经济下行风险',
                '行业竞争加剧风险',
                '原材料价格波动风险',
                '政策变化风险'
            ],
            'growth': [
                '成长不及预期风险',
                '技术迭代风险',
                '市场竞争加剧风险',
                '估值过高风险'
            ],
            'cyclical': [
                '周期下行风险',
                '产品价格波动风险',
                '产能过剩风险',
                '需求下滑风险'
            ],
            'financial': [
                '资产质量恶化风险',
                '利率变化风险',
                '监管政策变化风险',
                '市场波动风险'
            ]
        }
        
        return templates.get(risk_type, templates['common'])
    
    @staticmethod
    def generate_financial_forecast_table(years: List[str], 
                                           revenue: List[float],
                                           profit: List[float],
                                           pe: List[float]) -> str:
        """
        生成盈利预测表格（Markdown 格式）
        
        Args:
            years: 年份列表
            revenue: 营收列表（亿元）
            profit: 利润列表（亿元）
            pe: PE 列表
            
        Returns:
            Markdown 表格字符串
        """
        if len(years) != len(revenue) or len(years) != len(profit):
            return "数据不完整"
        
        header = "| 指标 | " + " | ".join(years) + " |\n"
        separator = "|------|" + "|".join(["------"] * len(years)) + "|\n"
        
        rows = []
        
        # 营收行
        revenue_row = "| 营收 (亿元) | " + " | ".join([f"{r:.1f}" for r in revenue]) + " |\n"
        rows.append(revenue_row)
        
        # 利润行
        profit_row = "| 归母净利 (亿元) | " + " | ".join([f"{p:.1f}" for p in profit]) + " |\n"
        rows.append(profit_row)
        
        # PE 行
        pe_row = "| PE | " + " | ".join([f"{p:.1f}x" for p in pe]) + " |\n"
        rows.append(pe_row)
        
        return header + separator + "".join(rows)
    
    @staticmethod
    def export_report_to_markdown(report_data: Dict) -> str:
        """
        导出研报为 Markdown 格式
        
        Args:
            report_data: 研报数据字典
            
        Returns:
            Markdown 字符串
        """
        output = f"# {report_data.get('title', '研报')}\n\n"
        
        # 评级信息
        if 'rating' in report_data:
            rating_info = report_data['rating']
            output += f"## 投资评级：{rating_info.get('rating', '')}\n"
            if 'target_price' in rating_info:
                output += f"目标价：{rating_info['target_price']}元 ({rating_info.get('upside_str', '')})\n"
            output += "\n"
        
        # 各章节
        for section in report_data.get('sections', []):
            output += f"## {section}\n\n"
            section_key = section.replace(' ', '_').lower()
            content = report_data.get(section_key, '[待填写]')
            output += f"{content}\n\n"
        
        # 风险提示
        if 'risks' in report_data:
            output += "## 风险提示\n\n"
            for risk in report_data['risks']:
                output += f"- {risk}\n"
        
        return output


def main():
    """测试函数"""
    # 测试框架生成
    framework = ReportGenerator.generate_report_framework('company', '贵州茅台')
    print("研报框架:")
    print(json.dumps(framework, ensure_ascii=False, indent=2))
    
    # 测试标题生成
    title = ReportGenerator.generate_title('贵州茅台', '高端酒需求稳定', '首次覆盖')
    print(f"\n研报标题：{title}")
    
    # 测试评级格式化
    rating = ReportGenerator.format_rating('买入', 2000.0, 1700.0)
    print("\n评级信息:")
    print(json.dumps(rating, ensure_ascii=False, indent=2))
    
    # 测试风险提示
    risks = ReportGenerator.generate_risk_warnings('common')
    print("\n风险提示:")
    for risk in risks:
        print(f"- {risk}")
    
    # 测试盈利预测表格
    forecast = ReportGenerator.generate_financial_forecast_table(
        ['2023A', '2024E', '2025E'],
        [1000, 1180, 1380],
        [500, 600, 720],
        [30, 25, 21]
    )
    print("\n盈利预测表格:")
    print(forecast)


if __name__ == "__main__":
    main()
