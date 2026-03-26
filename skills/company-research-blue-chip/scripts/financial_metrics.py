#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
财务指标计算工具
用于计算 ROE、毛利率、净利率等核心财务指标
"""

from typing import Dict, List, Optional
import json


class FinancialMetricsCalculator:
    """财务指标计算器"""

    @staticmethod
    def calculate_roe(net_profit: float, avg_equity: float) -> Dict:
        """
        计算 ROE（净资产收益率）

        Args:
            net_profit: 净利润
            avg_equity: 平均净资产

        Returns:
            ROE 分析结果
        """
        if avg_equity == 0:
            return {'roe': None, 'level': '无数据'}

        roe = net_profit / avg_equity * 100

        if roe > 20:
            level = '优秀'
        elif roe > 15:
            level = '良好'
        elif roe > 10:
            level = '一般'
        elif roe > 5:
            level = '较差'
        else:
            level = '差'

        return {
            'roe': round(roe, 2),
            'roe_str': f"{roe:.1f}%",
            'net_profit': net_profit,
            'avg_equity': avg_equity,
            'level': level
        }

    @staticmethod
    def calculate_dupont_analysis(net_profit: float, revenue: float,
                                   avg_assets: float, avg_equity: float) -> Dict:
        """
        杜邦分析（ROE 拆解）

        Args:
            net_profit: 净利润
            revenue: 营业收入
            avg_assets: 平均总资产
            avg_equity: 平均净资产

        Returns:
            杜邦分析结果
        """
        # 净利率
        net_margin = net_profit / revenue * 100 if revenue > 0 else 0

        # 总资产周转率
        asset_turnover = revenue / avg_assets if avg_assets > 0 else 0

        # 权益乘数
        equity_multiplier = avg_assets / avg_equity if avg_equity > 0 else 0

        # ROE = 净利率 × 周转率 × 权益乘数
        roe = net_margin / 100 * asset_turnover * equity_multiplier * 100

        return {
            'roe': round(roe, 2),
            'roe_str': f"{roe:.1f}%",
            'net_margin': round(net_margin, 2),
            'net_margin_str': f"{net_margin:.1f}%",
            'asset_turnover': round(asset_turnover, 2),
            'equity_multiplier': round(equity_multiplier, 2),
            'breakdown': f"ROE = 净利率 ({net_margin:.1f}%) × 周转率 ({asset_turnover:.2f}) × 权益乘数 ({equity_multiplier:.2f})"
        }

    @staticmethod
    def calculate_growth_rates(data: List[Dict], metric: str) -> Dict:
        """
        计算增长率（CAGR、同比、环比）

        Args:
            data: 历史数据列表，每项包含 period 和 metric 值
            metric: 指标名称

        Returns:
            增长率分析结果
        """
        if len(data) < 2:
            return {'level': '数据不足'}

        # 按期间排序
        sorted_data = sorted(data, key=lambda x: x.get('period', ''))
        values = [d.get(metric, 0) for d in sorted_data]

        # 最新值和上期值
        latest = values[-1]
        previous = values[-2]

        # 同比
        yoy = (latest - previous) / previous * 100 if previous > 0 else 0

        # CAGR（如果有多年数据）
        n_years = len(values) - 1
        if n_years > 0 and values[0] > 0:
            cagr = ((latest / values[0]) ** (1 / n_years) - 1) * 100
        else:
            cagr = 0

        # 增长趋势判断
        if cagr > 30:
            trend = '高速增长'
        elif cagr > 15:
            trend = '较快增长'
        elif cagr > 5:
            trend = '稳定增长'
        elif cagr > 0:
            trend = '低速增长'
        else:
            trend = '下滑'

        return {
            'metric': metric,
            'latest': latest,
            'previous': previous,
            'yoy': round(yoy, 2),
            'yoy_str': f"{yoy:+.1f}%",
            'cagr': round(cagr, 2),
            'cagr_str': f"{cagr:+.1f}%",
            'n_years': n_years,
            'trend': trend
        }

    @staticmethod
    def calculate_cash_flow_ratio(operating_cf: float, current_liabilities: float,
                                   capex: float, net_profit: float) -> Dict:
        """
        现金流指标分析

        Args:
            operating_cf: 经营现金流
            current_liabilities: 流动负债
            capex: 资本开支
            net_profit: 净利润

        Returns:
            现金流分析结果
        """
        # 流动负债保障倍数
        cf_to_liability = operating_cf / current_liabilities if current_liabilities > 0 else 0

        # 自由现金流
        free_cf = operating_cf - capex

        # 净现比（经营现金流/净利润）
        cf_to_profit = operating_cf / net_profit if net_profit > 0 else 0

        # 现金流健康度
        if cf_to_profit > 1.2 and free_cf > 0:
            health = '优秀'
        elif cf_to_profit > 1.0 and free_cf > 0:
            health = '良好'
        elif cf_to_profit > 0.8:
            health = '一般'
        else:
            health = '较差'

        return {
            'operating_cf': operating_cf,
            'free_cf': round(free_cf, 2),
            'cf_to_liability': round(cf_to_liability, 2),
            'cf_to_profit': round(cf_to_profit, 2),
            'cf_to_profit_str': f"{cf_to_profit:.1f}x",
            'health': health
        }

    @staticmethod
    def generate_metrics_table(metrics_list: List[Dict]) -> str:
        """
        生成财务指标表格（Markdown 格式）

        Args:
            metrics_list: 指标列表

        Returns:
            Markdown 表格字符串
        """
        if not metrics_list:
            return "无数据"

        header = "| 指标 | 最新值 | 上期值 | 同比 | 趋势 |\n"
        separator = "|------|--------|--------|------|------|\n"

        rows = []
        for m in metrics_list:
            row = f"| {m.get('name', '')} | {m.get('latest', '-')} | {m.get('previous', '-')} | {m.get('yoy_str', '-')} | {m.get('trend', '-')} |\n"
            rows.append(row)

        return header + separator + "".join(rows)


def main():
    """测试函数"""
    # 测试 ROE 计算
    roe_result = FinancialMetricsCalculator.calculate_roe(100, 500)
    print("ROE 计算结果:")
    print(json.dumps(roe_result, ensure_ascii=False, indent=2))

    # 测试杜邦分析
    dupont_result = FinancialMetricsCalculator.calculate_dupont_analysis(100, 1000, 800, 500)
    print("\n杜邦分析结果:")
    print(json.dumps(dupont_result, ensure_ascii=False, indent=2))

    # 测试增长率计算
    growth_data = [
        {'period': '2020', 'revenue': 100},
        {'period': '2021', 'revenue': 120},
        {'period': '2022', 'revenue': 150},
        {'period': '2023', 'revenue': 180}
    ]
    growth_result = FinancialMetricsCalculator.calculate_growth_rates(growth_data, 'revenue')
    print("\n增长率计算结果:")
    print(json.dumps(growth_result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
