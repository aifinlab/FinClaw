#!/usr/bin/env python3
"""
基金市场研究核心模块
Fund Market Research Core Module

功能：市场概览、资金流向、热门板块、发行日历
"""

import sys
sys.path.insert(0, '/root/.openclaw/workspace/finclaw/skills/fund-suite/fund-market-research/scripts')

import json
import argparse
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import random
import warnings

# 数据文件路径
SAMPLE_DATA_PATH = '/root/.openclaw/workspace/skillsChoice/fund-suite/sample_data.json'

def _load_sample_data_from_file() -> Dict:
    """从外部JSON文件加载示例数据"""
    try:
        with open(SAMPLE_DATA_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        warnings.warn(f"无法加载示例数据文件: {e}。将使用最小化默认数据。")
        return {}


@dataclass
class MarketOverview:
    """市场概览数据"""
    total_funds: int = 0
    total_scale: float = 0.0  # 万亿
    scale_change_mom: float = 0.0  # 环比变化
    scale_change_yoy: float = 0.0  # 同比变化
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class CategoryData:
    """分类数据"""
    name: str
    count: int = 0
    scale: float = 0.0  # 万亿
    avg_return_ytd: float = 0.0
    avg_return_1y: float = 0.0
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class FundFlow:
    """资金流向数据"""
    net_inflow: float = 0.0  # 亿元
    inflow_amount: float = 0.0
    outflow_amount: float = 0.0
    inflow_funds: int = 0
    outflow_funds: int = 0
    
    def to_dict(self) -> Dict:
        return asdict(self)


class FundMarketResearch:
    """基金市场研究主类"""
    
    def __init__(self):
        self._load_sample_data()
    
    def _load_sample_data(self):
        """加载示例数据（⚠️ 警告：此为示例数据，生产环境请接入真实数据源）"""
        warnings.warn(
            "⚠️ 正在使用示例数据（sample_data.json）！\n"
            "   生产环境请接入真实数据源，如：\n"
            "   - AkShare API\n"
            "   - 同花顺iFinD\n"
            "   -  Wind 金融终端",
            UserWarning,
            stacklevel=2
        )
        
        # 从外部文件加载数据，如果不存在则使用最小化默认数据
        sample_data = _load_sample_data_from_file()
        
        # 市场规模数据（示例数据）
        mo = sample_data.get('market_overview', {})
        self.market_overview = MarketOverview(
            total_funds=mo.get('total_funds', 1000),
            total_scale=mo.get('total_scale', 25.0),
            scale_change_mom=mo.get('scale_change_mom', 0.30),
            scale_change_yoy=mo.get('scale_change_yoy', 2.50)
        )
        
        # 分类数据（示例数据-需替换）
        cats = sample_data.get('categories', {})
        self.categories = {
            'equity': CategoryData('股票型', 500, 8.0, 5.0, 15.0),
            'hybrid': CategoryData('混合型', 400, 6.0, 4.0, 12.0),
            'bond': CategoryData('债券型', 300, 8.0, 1.5, 4.5),
            'money': CategoryData('货币型', 100, 3.0, 0.8, 2.0),
            'qdii': CategoryData('QDII', 50, 1.0, 6.0, 18.0),
            'index': CategoryData('指数型', 50, 1.0, 3.0, 10.0),
        }
        
        # 市场趋势（示例数据-需替换）
        self.market_trends = {
            'new_funds_30d': 30,
            'total_raising': 500.0,
            'net_inflow': -50.0,
            'sentiment_index': 50.0,
            'active_funds': 1000,
            '_note': '示例数据-需替换为真实数据'
        }
        
        # 分类资金流向（示例数据-需替换）
        self.category_flows = {
            'equity': FundFlow(-50.0, 200.0, 250.0, 500, 800),
            'hybrid': FundFlow(-20.0, 150.0, 170.0, 400, 600),
            'bond': FundFlow(30.0, 120.0, 90.0, 500, 400),
            'money': FundFlow(10.0, 80.0, 70.0, 200, 150),
            'qdii': FundFlow(-5.0, 15.0, 20.0, 80, 100),
        }
        
        # 热门板块（示例数据-需替换）
        self.hot_sectors = [
            {'name': '示例板块A', 'fund_count': 10, 'scale': 500, 'return_30d': 5.0, 'heat': 80, '_note': '示例数据'},
            {'name': '示例板块B', 'fund_count': 8, 'scale': 400, 'return_30d': 3.0, 'heat': 60, '_note': '示例数据'},
        ]
        
        # 热门流入基金（示例数据-需替换）
        funds = sample_data.get('funds', {})
        equity_funds = funds.get('equity', [])
        hybrid_funds = funds.get('hybrid', [])
        
        self.hot_inflows = [
            {'code': equity_funds[0]['code'] if equity_funds else '000003', 
             'name': equity_funds[0]['name'] if equity_funds else '示例股票基金A', 'inflow': 5.0, '_note': '示例数据'},
            {'code': hybrid_funds[0]['code'] if hybrid_funds else '000001', 
             'name': hybrid_funds[0]['name'] if hybrid_funds else '示例混合基金A', 'inflow': 3.0, '_note': '示例数据'},
        ]
        
        # 热门流出基金（示例数据-需替换）
        self.hot_outflows = [
            {'code': hybrid_funds[1]['code'] if len(hybrid_funds) > 1 else '000002', 
             'name': hybrid_funds[1]['name'] if len(hybrid_funds) > 1 else '示例混合基金B', 'outflow': 5.0, '_note': '示例数据'},
        ]
        
        # 发行日历（示例数据-需替换）
        self.upcoming_funds = [
            {
                'fund_code': '待公布',
                'fund_name': '示例新基金A',
                'fund_type': '混合型',
                'manager': '示例经理',
                'company': '示例公司',
                'start_date': '2026-04-01',
                'end_date': '2026-04-20',
                'target_scale': '10亿',
                'investment_theme': '示例主题',
                'status': '即将发行',
                '_note': '示例数据-需替换'
            },
        ]
    
    def get_overview(self) -> Dict:
        """获取市场概览"""
        return {
            'report_date': datetime.now().strftime('%Y-%m-%d'),
            'market_overview': self.market_overview.to_dict(),
            'categories': {k: v.to_dict() for k, v in self.categories.items()},
            'market_trends': self.market_trends,
        }
    
    def get_fund_flow(self, days: int = 30, category: Optional[str] = None) -> Dict:
        """
        获取资金流向
        
        Args:
            days: 统计天数
            category: 分类筛选（equity/hybrid/bond/money/qdii）
        
        Returns:
            资金流向数据
        """
        if category:
            if category in self.category_flows:
                flow = self.category_flows[category]
                return {
                    'period': f'{days}天',
                    'category': self.categories.get(category, CategoryData(category)).name,
                    'flow_data': flow.to_dict(),
                }
            else:
                return {'error': f'不存在的分类: {category}'}
        
        # 总体流向
        total_inflow = sum(f.inflow_amount for f in self.category_flows.values())
        total_outflow = sum(f.outflow_amount for f in self.category_flows.values())
        total_net = sum(f.net_inflow for f in self.category_flows.values())
        
        return {
            'period': f'{days}天',
            'overall': {
                'net_inflow': round(total_net, 2),
                'inflow_amount': round(total_inflow, 2),
                'outflow_amount': round(total_outflow, 2),
            },
            'by_category': {
                k: {
                    'name': self.categories.get(k, CategoryData(k)).name,
                    **v.to_dict()
                }
                for k, v in self.category_flows.items()
            },
            'hot_inflows': self.hot_inflows,
            'hot_outflows': self.hot_outflows,
        }
    
    def get_hot_sectors(self, top_n: int = 5) -> Dict:
        """
        获取热门板块
        
        Args:
            top_n: 返回前N个板块
        
        Returns:
            热门板块数据
        """
        # 排序并返回
        sorted_sectors = sorted(self.hot_sectors, key=lambda x: x['heat'], reverse=True)
        
        # 风格主题热度
        style_themes = [
            {'name': '成长风格', 'heat_index': 78.5, 'trend': 'up'},
            {'name': '价值风格', 'heat_index': 42.3, 'trend': 'down'},
            {'name': '红利策略', 'heat_index': 58.6, 'trend': 'up'},
            {'name': '量化策略', 'heat_index': 65.2, 'trend': 'up'},
        ]
        
        # 区域主题
        region_themes = [
            {'name': '港股', 'flow_30d': 25.3, 'heat': '🔥🔥'},
            {'name': '美股', 'flow_30d': -8.5, 'heat': '🔥'},
            {'name': '新兴市场', 'flow_30d': 3.2, 'heat': '🔥'},
            {'name': '欧洲市场', 'flow_30d': -2.1, 'heat': ''},
        ]
        
        return {
            'report_date': datetime.now().strftime('%Y-%m-%d'),
            'sector_ranking': sorted_sectors[:top_n],
            'all_sectors': sorted_sectors,
            'style_themes': style_themes,
            'region_themes': region_themes,
        }
    
    def get_returns_distribution(self, fund_type: Optional[str] = None) -> Dict:
        """
        获取收益分布
        
        Args:
            fund_type: 基金类型筛选
        
        Returns:
            收益分布数据
        """
        # 模拟收益分布
        distributions = {
            'ytd': {
                'avg': 3.2,
                'median': 2.8,
                'max': 35.2,
                'min': -15.5,
                'distribution': {
                    '>20%': 850,
                    '10-20%': 1850,
                    '0-10%': 4200,
                    '-10-0%': 2800,
                    '<-10%': 1880,
                }
            },
            '1y': {
                'avg': 8.5,
                'median': 7.2,
                'max': 68.5,
                'min': -25.3,
                'distribution': {
                    '>30%': 650,
                    '20-30%': 1200,
                    '10-20%': 2800,
                    '0-10%': 3200,
                    '<0%': 3530,
                }
            }
        }
        
        return {
            'report_date': datetime.now().strftime('%Y-%m-%d'),
            'fund_type': fund_type or '全部',
            'distributions': distributions,
        }
    
    def get_calendar(self, days: int = 30) -> Dict:
        """
        获取基金发行日历
        
        Args:
            days: 未来N天
        
        Returns:
            发行日历数据
        """
        today = datetime.now()
        end_date = today + timedelta(days=days)
        
        # 筛选日期范围内的基金
        upcoming = []
        for fund in self.upcoming_funds:
            start = datetime.strptime(fund['start_date'], '%Y-%m-%d')
            if today <= start <= end_date:
                upcoming.append(fund)
        
        # 统计信息
        status_count = {}
        for fund in self.upcoming_funds:
            status = fund['status']
            status_count[status] = status_count.get(status, 0) + 1
        
        return {
            'report_date': today.strftime('%Y-%m-%d'),
            'period': f'未来{days}天',
            'upcoming_funds': upcoming,
            'statistics': {
                'total_upcoming': len(upcoming),
                'by_status': status_count,
                'total_target_scale': sum(float(f['target_scale'].replace('亿', '')) 
                                         for f in upcoming if '亿' in f['target_scale']),
            }
        }
    
    def get_sentiment_index(self) -> Dict:
        """获取市场情绪指数"""
        # 基于多个因子计算
        factors = {
            'new_fund_issuance': 65,  # 新发基金数量
            'fund_flow': 45,          # 资金流向
            'market_return': 58,      # 市场收益
            'volatility': 52,         # 波动率
            'investor_attention': 60, # 投资者关注度
        }
        
        # 加权计算
        weights = {
            'new_fund_issuance': 0.25,
            'fund_flow': 0.30,
            'market_return': 0.20,
            'volatility': 0.15,
            'investor_attention': 0.10,
        }
        
        sentiment = sum(factors[k] * weights[k] for k in factors)
        
        if sentiment >= 70:
            level = '过热'
            emoji = '🔥🔥🔥'
        elif sentiment >= 60:
            level = '偏热'
            emoji = '🔥🔥'
        elif sentiment >= 50:
            level = '中性'
            emoji = '⚖️'
        elif sentiment >= 40:
            level = '偏冷'
            emoji = '❄️'
        else:
            level = '过冷'
            emoji = '❄️❄️'
        
        return {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'sentiment_index': round(sentiment, 1),
            'sentiment_level': level,
            'emoji': emoji,
            'factors': factors,
            'interpretation': self._interpret_sentiment(sentiment),
        }
    
    def _interpret_sentiment(self, sentiment: float) -> str:
        """解读情绪指数"""
        if sentiment >= 70:
            return '市场情绪高涨，新发基金活跃，需警惕追高风险'
        elif sentiment >= 60:
            return '市场情绪积极，资金流入明显，可适当参与'
        elif sentiment >= 50:
            return '市场情绪中性，建议均衡配置，关注结构性机会'
        elif sentiment >= 40:
            return '市场情绪偏谨慎，资金流向防御，关注低风险品种'
        else:
            return '市场情绪低迷，可能处于底部区域，可逢低布局'


def print_overview(overview: Dict):
    """打印市场概览"""
    print("\n" + "=" * 80)
    print(f"📊 {overview['report_date']} 基金市场概览")
    print("=" * 80)
    
    m = overview['market_overview']
    print(f"\n市场规模:")
    print(f"  基金总数: {m['total_funds']:,}只")
    print(f"  管理规模: {m['total_scale']:.2f}万亿")
    print(f"  较上月: {m['scale_change_mom']:+.2f}万亿 ({m['scale_change_mom']/m['total_scale']*100:+.1f}%)")
    print(f"  较上年: {m['scale_change_yoy']:+.2f}万亿 ({m['scale_change_yoy']/(m['total_scale']-m['scale_change_yoy'])*100:+.1f}%)")
    
    print(f"\n类别分布:")
    for key, cat in overview['categories'].items():
        print(f"  {cat['name']:<8}: {cat['count']:>4}只 | {cat['scale']:>5.2f}万亿 | 年内收益 {cat['avg_return_ytd']:>+5.1f}%")
    
    t = overview['market_trends']
    print(f"\n市场趋势:")
    print(f"  近30天新发基金: {t['new_funds_30d']}只")
    print(f"  募集资金: {t['total_raising']:.1f}亿")
    flow_emoji = "🟢" if t['net_inflow'] > 0 else "🔴"
    print(f"  资金净流入: {flow_emoji} {t['net_inflow']:+.1f}亿")
    print(f"  市场情绪指数: {t['sentiment_index']:.1f}")
    
    print("=" * 80)


def print_fund_flow(flow_data: Dict):
    """打印资金流向"""
    print("\n" + "=" * 80)
    print(f"💰 {flow_data['period']}资金流向分析")
    print("=" * 80)
    
    o = flow_data['overall']
    print(f"\n总体流向:")
    flow_emoji = "🟢流入" if o['net_inflow'] > 0 else "🔴流出"
    print(f"  资金净流向: {flow_emoji} {abs(o['net_inflow']):.1f}亿")
    print(f"  流入金额: {o['inflow_amount']:.1f}亿")
    print(f"  流出金额: {o['outflow_amount']:.1f}亿")
    
    print(f"\n分类流向:")
    print(f"{'类别':<10} {'净流入':<12} {'流入':<10} {'流出':<10} {'状态':<6}")
    print("-" * 60)
    for key, cat in flow_data['by_category'].items():
        emoji = "🟢" if cat['net_inflow'] > 0 else "🔴"
        status = "流入" if cat['net_inflow'] > 0 else "流出"
        print(f"{cat['name']:<10} {cat['net_inflow']:>+10.1f}亿 {cat['inflow_amount']:>8.1f}亿 {cat['outflow_amount']:>8.1f}亿 {emoji} {status}")
    
    print(f"\n热门流入 TOP5:")
    for i, fund in enumerate(flow_data['hot_inflows'], 1):
        print(f"  {i}. {fund['name']} ({fund['code']}): +{fund['inflow']:.1f}亿")
    
    print(f"\n热门流出 TOP5:")
    for i, fund in enumerate(flow_data['hot_outflows'], 1):
        print(f"  {i}. {fund['name']} ({fund['code']}): -{fund['outflow']:.1f}亿")
    
    print("=" * 80)


def print_hot_sectors(sectors_data: Dict):
    """打印热门板块"""
    print("\n" + "=" * 80)
    print(f"🔥 {sectors_data['report_date']} 热门板块追踪")
    print("=" * 80)
    
    print(f"\n行业主题热度:")
    print(f"{'排名':<4} {'板块':<12} {'基金数':<8} {'规模(亿)':<10} {'30天收益':<10} {'热度':<8}")
    print("-" * 70)
    for i, sector in enumerate(sectors_data['sector_ranking'], 1):
        heat_fire = "🔥" * (sector['heat'] // 30 + 1)
        print(f"{i:<4} {sector['name']:<12} {sector['fund_count']:<8} "
              f"{sector['scale']:<10} {sector['return_30d']:>+8.1f}% {heat_fire:<8}")
    
    print(f"\n风格主题热度:")
    for theme in sectors_data['style_themes']:
        trend_emoji = "📈" if theme['trend'] == 'up' else "📉"
        heat_fire = "🔥" * int(theme['heat_index'] // 30)
        print(f"  {theme['name']:<10} 热度指数: {theme['heat_index']:.1f} {heat_fire} {trend_emoji}")
    
    print(f"\n区域主题热度:")
    for region in sectors_data['region_themes']:
        flow_emoji = "🟢" if region['flow_30d'] > 0 else "🔴"
        print(f"  {region['name']:<10} 30天流向: {flow_emoji} {region['flow_30d']:>+6.1f}亿 {region['heat']}")
    
    print("=" * 80)


def print_calendar(calendar: Dict):
    """打印发行日历"""
    print("\n" + "=" * 80)
    print(f"📅 {calendar['period']}基金发行日历")
    print("=" * 80)
    
    s = calendar['statistics']
    print(f"\n统计信息:")
    print(f"  待发基金: {s['total_upcoming']}只")
    print(f"  目标规模: {s['total_target_scale']:.0f}亿")
    for status, count in s['by_status'].items():
        print(f"  {status}: {count}只")
    
    print(f"\n待发基金详情:")
    print(f"{'基金名称':<20} {'类型':<8} {'经理':<8} {'发行日期':<12} {'目标规模':<10} {'状态':<8}")
    print("-" * 80)
    for fund in calendar['upcoming_funds']:
        print(f"{fund['fund_name'][:18]:<20} {fund['fund_type']:<8} {fund['manager']:<8} "
              f"{fund['start_date']:<12} {fund['target_scale']:<10} {fund['status']:<8}")
    
    print("=" * 80)


def print_sentiment(sentiment: Dict):
    """打印市场情绪"""
    print("\n" + "=" * 80)
    print(f"💭 市场情绪指数")
    print("=" * 80)
    
    print(f"\n情绪指数: {sentiment['sentiment_index']:.1f} {sentiment['emoji']}")
    print(f"情绪状态: {sentiment['sentiment_level']}")
    print(f"\n解读: {sentiment['interpretation']}")
    
    print(f"\n因子分解:")
    for factor, value in sentiment['factors'].items():
        bar = "█" * int(value / 5)
        print(f"  {factor:<20} {value:>5.1f} {bar}")
    
    print("=" * 80)


def main():
    """主函数 - CLI入口"""
    parser = argparse.ArgumentParser(description='基金市场研究')
    parser.add_argument('--overview', action='store_true', help='市场概览')
    parser.add_argument('--flow', action='store_true', help='资金流向')
    parser.add_argument('--period', default='30d', help='统计周期')
    parser.add_argument('--category', help='分类筛选')
    parser.add_argument('--hot-sectors', action='store_true', help='热门板块')
    parser.add_argument('--returns-dist', action='store_true', help='收益分布')
    parser.add_argument('--fund-type', help='基金类型')
    parser.add_argument('--calendar', action='store_true', help='发行日历')
    parser.add_argument('--days', type=int, default=30, help='天数')
    parser.add_argument('--sentiment', action='store_true', help='市场情绪')
    parser.add_argument('--json', action='store_true', help='输出JSON格式')
    
    args = parser.parse_args()
    
    research = FundMarketResearch()
    
    # 解析周期
    period_days = 30
    if args.period.endswith('d'):
        period_days = int(args.period[:-1])
    
    # 市场概览
    if args.overview:
        data = research.get_overview()
        if args.json:
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            print_overview(data)
        return
    
    # 资金流向
    if args.flow:
        data = research.get_fund_flow(days=period_days, category=args.category)
        if args.json:
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            print_fund_flow(data)
        return
    
    # 热门板块
    if args.hot_sectors:
        data = research.get_hot_sectors()
        if args.json:
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            print_hot_sectors(data)
        return
    
    # 收益分布
    if args.returns_dist:
        data = research.get_returns_distribution(fund_type=args.fund_type)
        if args.json:
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            print(json.dumps(data, ensure_ascii=False, indent=2))
        return
    
    # 发行日历
    if args.calendar:
        data = research.get_calendar(days=args.days)
        if args.json:
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            print_calendar(data)
        return
    
    # 市场情绪
    if args.sentiment:
        data = research.get_sentiment_index()
        if args.json:
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            print_sentiment(data)
        return
    
    # 默认输出概览
    data = research.get_overview()
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print_overview(data)


if __name__ == '__main__':
    main()
