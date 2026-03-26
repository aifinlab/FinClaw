#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
行业市场数据工具
用于获取和分析行业市场规模、增速、集中度等数据
"""

from datetime import datetime
from typing import Dict, List, Optional
import json


class IndustryMarketData:
    """行业市场数据管理器"""

    @staticmethod
    def calculate_market_size(historical_data: List[Dict]) -> Dict:
        """
        测算市场规模和增速

        Args:
            historical_data: 历史数据列表，每项包含 year 和 size

        Returns:
            市场规模分析结果
        """
        if not historical_data:
            return {'level': '无数据'}

        # 按年份排序
        sorted_data = sorted(historical_data, key=lambda x: x.get('year', 0))

        # 最新数据
        latest = sorted_data[-1]
        previous = sorted_data[-2] if len(sorted_data) > 1 else None

        # 同比增速
        if previous:
            yoy = (latest['size'] - previous['size']) / previous['size'] * 100
        else:
            yoy = 0

        # CAGR
        n_years = len(sorted_data) - 1
        if n_years > 0 and sorted_data[0]['size'] > 0:
            cagr = ((latest['size'] / sorted_data[0]['size']) ** (1 / n_years) - 1) * 100
        else:
            cagr = 0

        # 增速判断
        if cagr > 30:
            growth_level = '高速增长'
        elif cagr > 15:
            growth_level = '较快增长'
        elif cagr > 5:
            growth_level = '稳定增长'
        else:
            growth_level = '低速增长'

        return {
            'latest_year': latest.get('year'),
            'latest_size': latest.get('size'),
            'yoy': round(yoy, 2),
            'yoy_str': f"{yoy:+.1f}%",
            'cagr': round(cagr, 2),
            'cagr_str': f"{cagr:+.1f}%",
            'n_years': n_years,
            'growth_level': growth_level,
            'historical': sorted_data
        }

    @staticmethod
    def calculate_concentration(market_shares: List[Dict]) -> Dict:
        """
        计算市场集中度（CR3/CR5/CR10）

        Args:
            market_shares: 市场份额列表，每项包含 company 和 share

        Returns:
            集中度分析结果
        """
        if not market_shares:
            return {'level': '无数据'}

        # 按份额排序
        sorted_shares = sorted(market_shares, key=lambda x: x.get('share', 0), reverse=True)
        shares = [s.get('share', 0) for s in sorted_shares]

        # 计算 CR3/CR5/CR10
        cr3 = sum(shares[:3]) if len(shares) >= 3 else sum(shares)
        cr5 = sum(shares[:5]) if len(shares) >= 5 else sum(shares)
        cr10 = sum(shares[:10]) if len(shares) >= 10 else sum(shares)

        # 集中度判断
        if cr3 > 70:
            concentration_level = '高度集中'
        elif cr3 > 50:
            concentration_level = '中度集中'
        elif cr3 > 30:
            concentration_level = '低度集中'
        else:
            concentration_level = '分散竞争'

        return {
            'cr3': round(cr3, 2),
            'cr3_str': f"{cr3:.1f}%",
            'cr5': round(cr5, 2),
            'cr5_str': f"{cr5:.1f}%",
            'cr10': round(cr10, 2),
            'cr10_str': f"{cr10:.1f}%",
            'concentration_level': concentration_level,
            'top_companies': sorted_shares[:10]
        }

    @staticmethod
    def analyze_competitive_landscape(companies: List[Dict]) -> str:
        """
        分析竞争格局

        Args:
            companies: 公司列表，每项包含 name, share, growth 等

        Returns:
            竞争格局分析文本
        """
        if not companies:
            return "无数据"

        # 按份额排序
        sorted_companies = sorted(companies, key=lambda x: x.get('share', 0), reverse=True)

        output = "## 竞争格局分析\n\n"

        # 第一梯队
        leaders = [c for c in sorted_companies if c.get('share', 0) > 20]
        if leaders:
            output += "### 第一梯队（份额>20%）\n"
            for c in leaders:
                output += f"- **{c['name']}**: 份额 {c.get('share', 0):.1f}%, 增速 {c.get('growth', 0):+.1f}%\n"
            output += "\n"

        # 第二梯队
        followers = [c for c in sorted_companies if 5 < c.get('share', 0) <= 20]
        if followers:
            output += "### 第二梯队（份额 5%-20%）\n"
            for c in followers:
                output += f"- {c['name']}: 份额 {c.get('share', 0):.1f}%, 增速 {c.get('growth', 0):+.1f}%\n"
            output += "\n"

        # 其他
        others = [c for c in sorted_companies if c.get('share', 0) <= 5]
        if others:
            output += "### 其他参与者（份额≤5%）\n"
            for c in others[:5]:  # 最多显示 5 家
                output += f"- {c['name']}: 份额 {c.get('share', 0):.1f}%\n"
            if len(others) > 5:
                output += f"- ... 等{len(others) - 5}家公司\n"

        return output

    @staticmethod
    def generate_market_table(data: List[Dict]) -> str:
        """
        生成市场数据表格（Markdown 格式）

        Args:
            data: 市场数据列表

        Returns:
            Markdown 表格字符串
        """
        if not data:
            return "无数据"

        header = "| 年份 | 市场规模 (亿元) | 同比增速 | CR3 | 竞争格局 |\n"
        separator = "|------|---------------|----------|-----|----------|\n"

        rows = []
        for d in data:
            row = f"| {d.get('year', '-')} | {d.get('size', '-')} | {d.get('yoy', '-')} | {d.get('cr3', '-')} | {d.get('landscape', '-')} |\n"
            rows.append(row)

        return header + separator + "".join(rows)

    @staticmethod
    def estimate_tam(potential_customers: int, penetration: float,
                     avg_price: float) -> Dict:
        """
        测算 TAM（总可触达市场）

        Args:
            potential_customers: 潜在客户数量
            penetration: 渗透率 (0-1)
            avg_price: 平均客单价

        Returns:
            TAM 测算结果
        """
        tam = potential_customers * penetration * avg_price

        # 市场阶段判断
        if penetration < 0.1:
            stage = '导入期'
        elif penetration < 0.3:
            stage = '成长期'
        elif penetration < 0.7:
            stage = '成熟期'
        else:
            stage = '饱和期'

        return {
            'potential_customers': potential_customers,
            'penetration': penetration,
            'penetration_str': f"{penetration * 100:.1f}%",
            'avg_price': avg_price,
            'tam': round(tam, 2),
            'tam_str': f"{tam/10000:.2f}亿元" if tam > 10000 else f"{tam:.2f}亿元",
            'stage': stage
        }


def main():
    """测试函数"""
    # 测试市场规模计算
    market_data = [
        {'year': 2019, 'size': 1000},
        {'year': 2020, 'size': 1100},
        {'year': 2021, 'size': 1300},
        {'year': 2022, 'size': 1500},
        {'year': 2023, 'size': 1800}
    ]
    market_result = IndustryMarketData.calculate_market_size(market_data)
    print("市场规模分析结果:")
    print(json.dumps(market_result, ensure_ascii=False, indent=2))

    # 测试集中度计算
    shares = [
        {'company': '公司 A', 'share': 30},
        {'company': '公司 B', 'share': 25},
        {'company': '公司 C', 'share': 20},
        {'company': '公司 D', 'share': 10},
        {'company': '公司 E', 'share': 5}
    ]
    cr_result = IndustryMarketData.calculate_concentration(shares)
    print("\n市场集中度分析结果:")
    print(json.dumps(cr_result, ensure_ascii=False, indent=2))

    # 测试 TAM 测算
    tam_result = IndustryMarketData.estimate_tam(10000000, 0.15, 500)
    print("\nTAM 测算结果:")
    print(json.dumps(tam_result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
