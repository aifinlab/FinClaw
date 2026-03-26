#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
财务数据分析工具
用于分析财报数据、计算增长率、判断超预期情况
"""

from datetime import datetime
from typing import Dict, List, Optional
import json


class FinancialAnalyzer:
    """财务数据分析器"""

    # 超预期判断标准
    BEAT_THRESHOLDS = {
        'big_beat': 0.2,    # >20%：大超预期
        'beat': 0.1,        # 10%-20%：超预期
        'inline': 0.1,      # ±10%：符合预期
        'miss': -0.1,       # -10% 至 -20%：低于预期
        'big_miss': -0.2    # <-20%：大低于预期
    }

    @staticmethod
    def calculate_growth(current: float, previous: float) -> Dict:
        """
        计算增长率

        Args:
            current: 当期值
            previous: 上期值

        Returns:
            增长率分析结果
        """
        if previous == 0:
            return {
                'growth_rate': None,
                'growth_str': 'N/A',
                'direction': '平'
            }

        growth_rate = (current - previous) / previous * 100

        if growth_rate > 50:
            direction = '高速增长'
        elif growth_rate > 20:
            direction = '较快增长'
        elif growth_rate > 0:
            direction = '增长'
        elif growth_rate > -20:
            direction = '下滑'
        elif growth_rate > -50:
            direction = '较大下滑'
        else:
            direction = '大幅下滑'

        return {
            'current': current,
            'previous': previous,
            'growth_rate': round(growth_rate, 2),
            'growth_str': f"{growth_rate:+.1f}%",
            'direction': direction
        }

    @staticmethod
    def check_beat_expectation(actual: float, expected: float) -> Dict:
        """
        检查是否超预期

        Args:
            actual: 实际值
            expected: 预期值（一致预期）

        Returns:
            超预期分析结果
        """
        if expected == 0:
            return {
                'surprise': None,
                'surprise_str': 'N/A',
                'level': '无预期'
            }

        surprise = (actual - expected) / expected

        if surprise > FinancialAnalyzer.BEAT_THRESHOLDS['big_beat']:
            level = '大超预期'
        elif surprise > FinancialAnalyzer.BEAT_THRESHOLDS['beat']:
            level = '超预期'
        elif surprise > FinancialAnalyzer.BEAT_THRESHOLDS['miss']:
            level = '符合预期'
        elif surprise > FinancialAnalyzer.BEAT_THRESHOLDS['big_miss']:
            level = '低于预期'
        else:
            level = '大低于预期'

        return {
            'actual': actual,
            'expected': expected,
            'surprise': round(surprise, 4),
            'surprise_str': f"{surprise * 100:+.1f}%",
            'level': level
        }

    @staticmethod
    def analyze_profit_margin(gross_profit: float, revenue: float,
                              operating_profit: float, net_profit: float) -> Dict:
        """
        分析利润率指标

        Args:
            gross_profit: 毛利润
            revenue: 营业收入
            operating_profit: 营业利润
            net_profit: 净利润

        Returns:
            利润率分析结果
        """
        if revenue == 0:
            return {'level': '无数据'}

        gross_margin = gross_profit / revenue * 100
        operating_margin = operating_profit / revenue * 100
        net_margin = net_profit / revenue * 100

        # 利润率健康度判断
        if gross_margin > 50 and net_margin > 20:
            health = '优秀'
        elif gross_margin > 30 and net_margin > 10:
            health = '良好'
        elif gross_margin > 20 and net_margin > 5:
            health = '一般'
        else:
            health = '较差'

        return {
            'gross_margin': round(gross_margin, 2),
            'gross_margin_str': f"{gross_margin:.1f}%",
            'operating_margin': round(operating_margin, 2),
            'operating_margin_str': f"{operating_margin:.1f}%",
            'net_margin': round(net_margin, 2),
            'net_margin_str': f"{net_margin:.1f}%",
            'health': health
        }

    @staticmethod
    def analyze_expense_ratio(selling_expense: float, admin_expense: float,
                              rd_expense: float, revenue: float) -> Dict:
        """
        分析费用率指标

        Args:
            selling_expense: 销售费用
            admin_expense: 管理费用
            rd_expense: 研发费用
            revenue: 营业收入

        Returns:
            费用率分析结果
        """
        if revenue == 0:
            return {'level': '无数据'}

        selling_ratio = selling_expense / revenue * 100
        admin_ratio = admin_expense / revenue * 100
        rd_ratio = rd_expense / revenue * 100
        total_ratio = (selling_expense + admin_expense + rd_expense) / revenue * 100

        return {
            'selling_ratio': round(selling_ratio, 2),
            'selling_ratio_str': f"{selling_ratio:.1f}%",
            'admin_ratio': round(admin_ratio, 2),
            'admin_ratio_str': f"{admin_ratio:.1f}%",
            'rd_ratio': round(rd_ratio, 2),
            'rd_ratio_str': f"{rd_ratio:.1f}%",
            'total_ratio': round(total_ratio, 2),
            'total_ratio_str': f"{total_ratio:.1f}%"
        }

    @staticmethod
    def generate_earnings_table(data: List[Dict]) -> str:
        """
        生成财报数据表格（Markdown 格式）

        Args:
            data: 财报数据列表，每项包含 period, revenue, profit, growth 等

        Returns:
            Markdown 表格字符串
        """
        if not data:
            return "无数据"

        # 表头
        header = "| 指标 | 本期 | 上期 | 同比 | 预期 | 超预期 |\n"
        separator = "|------|------|------|------|------|----------|\n"

        # 数据行
        rows = []
        for item in data:
            surprise_str = item.get('surprise_str', '-')
            row = f"| {item.get('metric', '')} | {item.get('current', '-')} | {item.get('previous', '-')} | {item.get('growth_str', '-')} | {item.get('expected', '-')} | {surprise_str} |\n"
            rows.append(row)

        return header + separator + "".join(rows)

    @staticmethod
    def get_earnings_comment(level: str, actual: float, expected: float) -> str:
        """
        生成财报点评短语

        Args:
            level: 超预期等级
            actual: 实际值
            expected: 预期值

        Returns:
            点评短语
        """
        comments = {
            '大超预期': f"业绩大超预期，实际值{actual}较预期{expected}高出{(actual-expected)/expected*100:.1f}%",
            '超预期': f"业绩超预期，实际值{actual}较预期{expected}高出{(actual-expected)/expected*100:.1f}%",
            '符合预期': f"业绩符合预期，实际值{actual}与预期{expected}基本一致",
            '低于预期': f"业绩低于预期，实际值{actual}较预期{expected}低{(expected-actual)/expected*100:.1f}%",
            '大低于预期': f"业绩大低于预期，实际值{actual}较预期{expected}低{(expected-actual)/expected*100:.1f}%"
        }

        return comments.get(level, f"业绩数据：实际{actual}，预期{expected}")


def main():
    """测试函数"""
    # 测试增长率计算
    growth_result = FinancialAnalyzer.calculate_growth(120.0, 100.0)
    print("增长率计算结果:")
    print(json.dumps(growth_result, ensure_ascii=False, indent=2))

    # 测试超预期判断
    beat_result = FinancialAnalyzer.check_beat_expectation(1.25, 1.15)
    print("\n超预期判断结果:")
    print(json.dumps(beat_result, ensure_ascii=False, indent=2))

    # 测试利润率分析
    margin_result = FinancialAnalyzer.analyze_profit_margin(50, 100, 25, 20)
    print("\n利润率分析结果:")
    print(json.dumps(margin_result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
