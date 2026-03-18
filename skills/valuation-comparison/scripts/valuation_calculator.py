#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
估值计算工具
用于计算 PE/PB/PS 等估值指标、历史分位、同业对比
"""

import json
from datetime import datetime
from typing import Dict, List, Optional


class ValuationCalculator:
    """估值计算器"""
    
    # 估值判断标准
    VALUATION_THRESHOLDS = {
        'low': 0.2,      # <20% 分位：低估
        'low_mid': 0.4,  # 20%-40%：偏低
        'mid': 0.6,      # 40%-60%：合理
        'mid_high': 0.8, # 60%-80%：偏高
        'high': 1.0      # >80%：高估
    }
    
    # 估值等级对应建议
    VALUATION_ADVICE = {
        'low': '买入',
        'low_mid': '增持',
        'mid': '持有',
        'mid_high': '减持',
        'high': '卖出'
    }
    
    @staticmethod
    def calculate_percentile(current_value: float, historical_values: List[float]) -> float:
        """
        计算历史分位
        
        Args:
            current_value: 当前值
            historical_values: 历史值列表
            
        Returns:
            分位值 (0-1)
        """
        if not historical_values:
            return 0.5
        
        sorted_values = sorted(historical_values)
        count_below = sum(1 for v in sorted_values if v < current_value)
        percentile = count_below / len(sorted_values)
        
        return round(percentile, 2)
    
    @staticmethod
    def get_valuation_level(percentile: float) -> str:
        """
        根据分位获取估值等级
        
        Args:
            percentile: 分位值 (0-1)
            
        Returns:
            估值等级描述
        """
        if percentile < ValuationCalculator.VALUATION_THRESHOLDS['low']:
            return '低估'
        elif percentile < ValuationCalculator.VALUATION_THRESHOLDS['low_mid']:
            return '偏低'
        elif percentile < ValuationCalculator.VALUATION_THRESHOLDS['mid']:
            return '合理'
        elif percentile < ValuationCalculator.VALUATION_THRESHOLDS['mid_high']:
            return '偏高'
        else:
            return '高估'
    
    @staticmethod
    def get_investment_advice(percentile: float) -> str:
        """
        根据分位获取投资建议
        
        Args:
            percentile: 分位值 (0-1)
            
        Returns:
            投资建议
        """
        level = ValuationCalculator.get_valuation_level(percentile)
        return ValuationCalculator.VALUATION_ADVICE.get(level, '持有')
    
    @staticmethod
    def calculate_pe(pe_ttm: float, historical_pe: List[float]) -> Dict:
        """
        计算 PE 估值分析
        
        Args:
            pe_ttm: 当前 PE-TTM
            historical_pe: 历史 PE 列表
            
        Returns:
            PE 分析结果字典
        """
        percentile = ValuationCalculator.calculate_percentile(pe_ttm, historical_pe)
        level = ValuationCalculator.get_valuation_level(percentile)
        advice = ValuationCalculator.get_investment_advice(percentile)
        
        # 计算历史统计
        pe_min = min(historical_pe) if historical_pe else 0
        pe_max = max(historical_pe) if historical_pe else 0
        pe_avg = sum(historical_pe) / len(historical_pe) if historical_pe else 0
        
        return {
            'current_pe': pe_ttm,
            'percentile': percentile,
            'percentile_str': f"{percentile * 100:.0f}%",
            'level': level,
            'advice': advice,
            'historical': {
                'min': round(pe_min, 2),
                'max': round(pe_max, 2),
                'avg': round(pe_avg, 2)
            }
        }
    
    @staticmethod
    def compare_with_peers(target_pe: float, peer_pe_list: List[float]) -> Dict:
        """
        与同业对比估值
        
        Args:
            target_pe: 目标公司 PE
            peer_pe_list: 同业 PE 列表
            
        Returns:
            对比结果字典
        """
        if not peer_pe_list:
            return {'premium': 0, 'level': '无数据'}
        
        peer_avg = sum(peer_pe_list) / len(peer_pe_list)
        premium = (target_pe - peer_avg) / peer_avg * 100
        
        if premium > 20:
            level = '显著溢价'
        elif premium > 5:
            level = '溢价'
        elif premium > -5:
            level = '持平'
        elif premium > -20:
            level = '折价'
        else:
            level = '显著折价'
        
        return {
            'target_pe': target_pe,
            'peer_avg': round(peer_avg, 2),
            'premium': round(premium, 2),
            'premium_str': f"{premium:+.1f}%",
            'level': level
        }
    
    @staticmethod
    def calculate_peg(pe: float, growth_rate: float) -> Dict:
        """
        计算 PEG 指标
        
        Args:
            pe: 市盈率
            growth_rate: 净利润增长率 (%)
            
        Returns:
            PEG 分析结果
        """
        if growth_rate <= 0:
            return {'peg': None, 'level': '不适用', 'advice': '增长为负'}
        
        peg = pe / growth_rate
        
        if peg < 0.5:
            level = '显著低估'
            advice = '买入'
        elif peg < 1:
            level = '低估'
            advice = '增持'
        elif peg < 1.5:
            level = '合理'
            advice = '持有'
        elif peg < 2:
            level = '高估'
            advice = '减持'
        else:
            level = '显著高估'
            advice = '卖出'
        
        return {
            'peg': round(peg, 2),
            'pe': pe,
            'growth_rate': growth_rate,
            'level': level,
            'advice': advice
        }
    
    @staticmethod
    def generate_valuation_table(data: List[Dict]) -> str:
        """
        生成估值对比表格（Markdown 格式）
        
        Args:
            data: 估值数据列表，每项包含 name, pe, pb, ps, roe 等
            
        Returns:
            Markdown 表格字符串
        """
        if not data:
            return "无数据"
        
        # 表头
        header = "| 公司 | PE-TTM | PB | PS-TTM | 股息率 | ROE |\n"
        separator = "|------|--------|-----|--------|--------|-----|\n"
        
        # 数据行
        rows = []
        for item in data:
            row = f"| {item.get('name', '')} | {item.get('pe', '-')} | {item.get('pb', '-')} | {item.get('ps', '-')} | {item.get('dividend', '-')} | {item.get('roe', '-')} |\n"
            rows.append(row)
        
        return header + separator + "".join(rows)


def main():
    """测试函数"""
    # 测试 PE 分析
    pe_result = ValuationCalculator.calculate_pe(15.0, [10, 12, 14, 16, 18, 20, 22, 24, 26, 28])
    print("PE 分析结果:")
    print(json.dumps(pe_result, ensure_ascii=False, indent=2))
    
    # 测试同业对比
    peer_result = ValuationCalculator.compare_with_peers(15.0, [12, 14, 16, 18, 20])
    print("\n同业对比结果:")
    print(json.dumps(peer_result, ensure_ascii=False, indent=2))
    
    # 测试 PEG
    peg_result = ValuationCalculator.calculate_peg(15.0, 20.0)
    print("\nPEG 分析结果:")
    print(json.dumps(peg_result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
