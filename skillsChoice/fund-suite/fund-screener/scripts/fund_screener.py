#!/usr/bin/env python3
"""
基金筛选器核心模块
Fund Screener Core Module

功能：基金筛选、评级、对比
"""

import sys
import os
sys.path.insert(0, '/root/.openclaw/workspace/finclaw/skills/fund-suite/fund-screener/scripts')

import json
import argparse
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import statistics

# 尝试导入pandas，如果没有则使用内置数据结构
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    print("警告：pandas未安装，使用基础数据结构")


@dataclass
class FundInfo:
    """基金信息数据类"""
    fund_code: str
    fund_name: str
    fund_type: str
    nav: float = 0.0
    nav_date: str = ""
    return_1y: float = 0.0
    return_3y: float = 0.0
    return_5y: float = 0.0
    volatility: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    scale: float = 0.0  # 规模（亿元）
    manager: str = ""
    manager_exp: int = 0  # 从业年限
    expense_ratio: float = 0.0
    establish_date: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class FundRating:
    """基金评级"""
    fund_code: str
    overall: int = 0  # 1-5星
    return_rating: int = 0
    risk_rating: int = 0
    scale_rating: int = 0
    manager_rating: int = 0
    fee_rating: int = 0
    
    def to_dict(self) -> Dict:
        return asdict(self)


class FundScreener:
    """基金筛选器主类"""
    
    def __init__(self):
        self.fund_data = []
        self.ratings_cache = {}
        self._load_sample_data()
    
    def _load_sample_data(self):
        """加载示例基金数据（实际环境从API获取）"""
        self.fund_data = [
            FundInfo("000001", "华夏成长混合", "混合型", 1.5234, "2026-03-20", 
                    25.3, 45.2, 68.5, 18.5, 1.45, -15.2, 156.8, "张三", 8, 1.2),
            FundInfo("000002", "易方达蓝筹精选", "混合型", 2.1234, "2026-03-20",
                    22.1, 55.2, 72.3, 16.2, 1.42, -12.8, 234.5, "李四", 12, 1.5),
            FundInfo("000003", "中欧时代先锋", "股票型", 1.8234, "2026-03-20",
                    21.7, 48.9, 58.2, 20.1, 1.15, -18.5, 89.3, "王五", 6, 1.2),
            FundInfo("000004", "富国天惠成长", "混合型", 3.2345, "2026-03-20",
                    28.5, 52.3, 75.1, 17.8, 1.52, -14.2, 189.5, "赵六", 10, 1.0),
            FundInfo("000005", "景顺长城新兴", "股票型", 2.5678, "2026-03-20",
                    19.8, 38.5, 52.3, 22.5, 0.95, -21.5, 67.8, "孙七", 5, 1.5),
            FundInfo("000006", "嘉实沪深300", "指数型", 1.3456, "2026-03-20",
                    15.2, 35.8, 48.2, 18.5, 0.85, -16.8, 456.2, "周八", 15, 0.8),
            FundInfo("000007", "招商中证白酒", "指数型", 2.7890, "2026-03-20",
                    32.5, 68.9, 85.2, 25.3, 1.35, -22.5, 523.8, "吴九", 7, 1.0),
            FundInfo("000008", "南方稳健成长", "混合型", 1.6789, "2026-03-20",
                    12.8, 28.5, 42.3, 12.5, 1.08, -10.2, 123.4, "郑十", 9, 1.2),
            FundInfo("000009", "广发科技创新", "股票型", 1.8901, "2026-03-20",
                    35.2, 42.8, 38.5, 28.5, 1.28, -25.8, 45.6, "钱十一", 4, 1.5),
            FundInfo("000010", "工银瑞信战略", "混合型", 2.0123, "2026-03-20",
                    17.5, 32.6, 48.9, 15.8, 1.18, -13.5, 78.9, "孙十二", 6, 1.2),
        ]
    
    def screen(self, 
               fund_type: Optional[str] = None,
               min_return_1y: Optional[float] = None,
               max_return_1y: Optional[float] = None,
               min_return_3y: Optional[float] = None,
               max_volatility: Optional[float] = None,
               min_scale: Optional[float] = None,
               max_scale: Optional[float] = None,
               max_fee: Optional[float] = None,
               min_sharpe: Optional[float] = None,
               manager_exp: Optional[int] = None,
               rating_min: Optional[int] = None,
               limit: int = 20) -> List[Dict]:
        """
        筛选基金
        
        Args:
            fund_type: 基金类型（股票型/混合型/债券型/指数型）
            min_return_1y: 近1年最小收益(%)
            max_return_1y: 近1年最大收益(%)
            min_return_3y: 近3年最小收益(%)
            max_volatility: 最大波动率(%)
            min_scale: 最小规模(亿元)
            max_scale: 最大规模(亿元)
            max_fee: 最大管理费率(%)
            min_sharpe: 最小夏普比率
            manager_exp: 基金经理最小从业年限
            rating_min: 最低星级(1-5)
            limit: 返回数量限制
        
        Returns:
            符合条件的基金列表
        """
        results = []
        
        for fund in self.fund_data:
            # 应用筛选条件
            if fund_type and fund.fund_type != fund_type:
                continue
            if min_return_1y is not None and fund.return_1y < min_return_1y:
                continue
            if max_return_1y is not None and fund.return_1y > max_return_1y:
                continue
            if min_return_3y is not None and fund.return_3y < min_return_3y:
                continue
            if max_volatility is not None and fund.volatility > max_volatility:
                continue
            if min_scale is not None and fund.scale < min_scale:
                continue
            if max_scale is not None and fund.scale > max_scale:
                continue
            if max_fee is not None and fund.expense_ratio > max_fee:
                continue
            if min_sharpe is not None and fund.sharpe_ratio < min_sharpe:
                continue
            if manager_exp is not None and fund.manager_exp < manager_exp:
                continue
            
            # 计算评级
            rating = self._calculate_rating(fund)
            
            if rating_min is not None and rating.overall < rating_min:
                continue
            
            # 添加到结果
            fund_dict = fund.to_dict()
            fund_dict['rating'] = rating.to_dict()
            fund_dict['peer_rank'] = self._get_peer_rank(fund)
            results.append(fund_dict)
        
        # 排序：综合评分降序
        results.sort(key=lambda x: x['rating']['overall'], reverse=True)
        
        # 添加排名
        for i, fund in enumerate(results[:limit], 1):
            fund['rank'] = i
        
        return results[:limit]
    
    def _calculate_rating(self, fund: FundInfo) -> FundRating:
        """计算基金评级"""
        rating = FundRating(fund_code=fund.fund_code)
        
        # 收益评级（近1年收益排名）
        all_returns = [f.return_1y for f in self.fund_data]
        return_pct = self._get_percentile(fund.return_1y, all_returns)
        rating.return_rating = self._pct_to_star(return_pct)
        
        # 风险评级（波动率越低越好）
        all_vols = [f.volatility for f in self.fund_data]
        vol_pct = 100 - self._get_percentile(fund.volatility, all_vols)  # 反转
        rating.risk_rating = self._pct_to_star(vol_pct)
        
        # 规模评级
        if fund.scale >= 100:
            rating.scale_rating = 5
        elif fund.scale >= 50:
            rating.scale_rating = 4
        elif fund.scale >= 20:
            rating.scale_rating = 3
        elif fund.scale >= 5:
            rating.scale_rating = 2
        else:
            rating.scale_rating = 1
        
        # 基金经理评级
        if fund.manager_exp >= 10:
            rating.manager_rating = 5
        elif fund.manager_exp >= 7:
            rating.manager_rating = 4
        elif fund.manager_exp >= 5:
            rating.manager_rating = 3
        elif fund.manager_exp >= 3:
            rating.manager_rating = 2
        else:
            rating.manager_rating = 1
        
        # 费用评级（费率越低越好）
        if fund.expense_ratio <= 1.0:
            rating.fee_rating = 5
        elif fund.expense_ratio <= 1.2:
            rating.fee_rating = 4
        elif fund.expense_ratio <= 1.5:
            rating.fee_rating = 3
        elif fund.expense_ratio <= 2.0:
            rating.fee_rating = 2
        else:
            rating.fee_rating = 1
        
        # 综合评级（加权平均）
        weights = {'return': 0.3, 'risk': 0.25, 'scale': 0.15, 'manager': 0.2, 'fee': 0.1}
        overall_score = (
            rating.return_rating * weights['return'] +
            rating.risk_rating * weights['risk'] +
            rating.scale_rating * weights['scale'] +
            rating.manager_rating * weights['manager'] +
            rating.fee_rating * weights['fee']
        )
        rating.overall = round(overall_score)
        
        return rating
    
    def _get_percentile(self, value: float, all_values: List[float]) -> float:
        """获取分位数（0-100）"""
        sorted_values = sorted(all_values)
        n = len(sorted_values)
        
        # 找到位置
        count = sum(1 for v in sorted_values if v <= value)
        return (count / n) * 100
    
    def _pct_to_star(self, pct: float) -> int:
        """分位数转星级"""
        if pct >= 90:
            return 5
        elif pct >= 70:
            return 4
        elif pct >= 50:
            return 3
        elif pct >= 30:
            return 2
        else:
            return 1
    
    def _get_peer_rank(self, fund: FundInfo) -> str:
        """获取同类排名"""
        peers = [f for f in self.fund_data if f.fund_type == fund.fund_type]
        peers.sort(key=lambda x: x.return_1y, reverse=True)
        
        rank = next((i for i, p in enumerate(peers, 1) if p.fund_code == fund.fund_code), 0)
        return f"{rank}/{len(peers)}"
    
    def compare_funds(self, fund_codes: List[str]) -> Dict:
        """对比多只基金"""
        funds = [f for f in self.fund_data if f.fund_code in fund_codes]
        
        comparison = {
            'funds': [],
            'metrics': {}
        }
        
        for fund in funds:
            rating = self._calculate_rating(fund)
            fund_dict = fund.to_dict()
            fund_dict['rating'] = rating.to_dict()
            fund_dict['peer_rank'] = self._get_peer_rank(fund)
            comparison['funds'].append(fund_dict)
        
        return comparison
    
    def get_fund_detail(self, fund_code: str) -> Optional[Dict]:
        """获取基金详情"""
        fund = next((f for f in self.fund_data if f.fund_code == fund_code), None)
        if not fund:
            return None
        
        rating = self._calculate_rating(fund)
        
        detail = fund.to_dict()
        detail['rating'] = rating.to_dict()
        detail['peer_rank'] = self._get_peer_rank(fund)
        
        # 添加分析建议
        detail['analysis'] = self._generate_analysis(fund, rating)
        
        return detail
    
    def _generate_analysis(self, fund: FundInfo, rating: FundRating) -> Dict:
        """生成基金分析建议"""
        analysis = {
            'strengths': [],
            'weaknesses': [],
            'suitable_for': []
        }
        
        # 优势
        if rating.return_rating >= 4:
            analysis['strengths'].append('收益表现优秀，同类排名前30%')
        if rating.risk_rating >= 4:
            analysis['strengths'].append('风险控制良好，波动率较低')
        if rating.scale_rating >= 4:
            analysis['strengths'].append('规模适中，流动性良好')
        if rating.manager_rating >= 4:
            analysis['strengths'].append('基金经理经验丰富')
        if rating.fee_rating >= 4:
            analysis['strengths'].append('管理费率较低')
        
        # 劣势
        if rating.return_rating <= 2:
            analysis['weaknesses'].append('近期收益表现一般')
        if rating.risk_rating <= 2:
            analysis['weaknesses'].append('波动较大，需关注风险')
        if rating.scale_rating <= 2:
            analysis['weaknesses'].append('规模较小，存在清盘风险')
        
        # 适合人群
        if fund.fund_type == '股票型':
            analysis['suitable_for'].append('风险承受能力较高的投资者')
        elif fund.fund_type == '混合型':
            analysis['suitable_for'].append('追求平衡配置的投资者')
        elif fund.fund_type == '债券型':
            analysis['suitable_for'].append('保守型投资者')
        
        return analysis


def print_screening_results(results: List[Dict]):
    """打印筛选结果"""
    print("\n" + "=" * 80)
    print(f"📊 基金筛选结果")
    print("=" * 80)
    print(f"共找到 {len(results)} 只符合条件的基金\n")
    
    print(f"{'排名':<4} {'代码':<8} {'名称':<20} {'类型':<8} {'近1年':<8} {'规模':<8} {'评级':<8}")
    print("-" * 80)
    
    for fund in results:
        stars = "⭐" * fund['rating']['overall']
        print(f"{fund['rank']:<4} {fund['fund_code']:<8} {fund['fund_name'][:18]:<20} "
              f"{fund['fund_type']:<8} {fund['return_1y']:>6.1f}% {fund['scale']:>6.1f}亿 {stars:<8}")
    
    print("=" * 80)


def print_fund_detail(detail: Dict):
    """打印基金详情"""
    print("\n" + "=" * 80)
    print(f"📋 {detail['fund_name']} ({detail['fund_code']})")
    print("=" * 80)
    
    print(f"\n基本信息:")
    print(f"  基金类型: {detail['fund_type']}")
    print(f"  最新净值: ¥{detail['nav']:.4f} ({detail['nav_date']})")
    print(f"  基金规模: {detail['scale']:.2f}亿元")
    print(f"  管理费率: {detail['expense_ratio']:.2f}%")
    print(f"  基金经理: {detail['manager']} ({detail['manager_exp']}年经验)")
    
    print(f"\n业绩表现:")
    print(f"  近1年收益: {detail['return_1y']:+.2f}%")
    print(f"  近3年收益: {detail['return_3y']:+.2f}%")
    print(f"  近5年收益: {detail['return_5y']:+.2f}%")
    print(f"  波动率: {detail['volatility']:.2f}%")
    print(f"  夏普比率: {detail['sharpe_ratio']:.2f}")
    print(f"  最大回撤: {detail['max_drawdown']:.2f}%")
    print(f"  同类排名: {detail['peer_rank']}")
    
    print(f"\n五星评级:")
    r = detail['rating']
    print(f"  综合评级: {'⭐' * r['overall']} ({r['overall']}星)")
    print(f"  收益评分: {'⭐' * r['return_rating']}")
    print(f"  风险评分: {'⭐' * r['risk_rating']}")
    print(f"  规模评分: {'⭐' * r['scale_rating']}")
    print(f"  经理评分: {'⭐' * r['manager_rating']}")
    print(f"  费用评分: {'⭐' * r['fee_rating']}")
    
    if 'analysis' in detail:
        print(f"\n分析建议:")
        if detail['analysis']['strengths']:
            print("  ✅ 优势:")
            for s in detail['analysis']['strengths']:
                print(f"     • {s}")
        if detail['analysis']['weaknesses']:
            print("  ⚠️  注意:")
            for w in detail['analysis']['weaknesses']:
                print(f"     • {w}")
        if detail['analysis']['suitable_for']:
            print("  👤 适合人群:")
            for p in detail['analysis']['suitable_for']:
                print(f"     • {p}")
    
    print("=" * 80)


def main():
    """主函数 - CLI入口"""
    parser = argparse.ArgumentParser(description='基金筛选器')
    parser.add_argument('--type', help='基金类型')
    parser.add_argument('--min-return', type=float, help='近1年最小收益(%)')
    parser.add_argument('--max-volatility', type=float, help='最大波动率(%)')
    parser.add_argument('--min-scale', type=float, help='最小规模(亿元)')
    parser.add_argument('--max-fee', type=float, help='最大管理费率(%)')
    parser.add_argument('--min-sharpe', type=float, help='最小夏普比率')
    parser.add_argument('--manager-exp', type=int, help='基金经理最小从业年限')
    parser.add_argument('--rating-min', type=int, help='最低星级(1-5)')
    parser.add_argument('--code', help='查看基金详情')
    parser.add_argument('--compare', help='对比多只基金，逗号分隔')
    parser.add_argument('--limit', type=int, default=20, help='返回数量限制')
    parser.add_argument('--json', action='store_true', help='输出JSON格式')
    
    args = parser.parse_args()
    
    screener = FundScreener()
    
    # 查看详情
    if args.code:
        detail = screener.get_fund_detail(args.code)
        if detail:
            if args.json:
                print(json.dumps(detail, ensure_ascii=False, indent=2))
            else:
                print_fund_detail(detail)
        else:
            print(f"未找到基金: {args.code}")
        return
    
    # 对比基金
    if args.compare:
        codes = args.compare.split(',')
        comparison = screener.compare_funds(codes)
        print("\n基金对比:")
        print(json.dumps(comparison, ensure_ascii=False, indent=2))
        return
    
    # 筛选基金
    results = screener.screen(
        fund_type=args.type,
        min_return_1y=args.min_return,
        max_volatility=args.max_volatility,
        min_scale=args.min_scale,
        max_fee=args.max_fee,
        min_sharpe=args.min_sharpe,
        manager_exp=args.manager_exp,
        rating_min=args.rating_min,
        limit=args.limit
    )
    
    if args.json:
        print(json.dumps({
            'total_found': len(results),
            'funds': results
        }, ensure_ascii=False, indent=2))
    else:
        print_screening_results(results)


if __name__ == '__main__':
    main()
