#!/usr/bin/env python3
"""
基金持仓穿透分析核心模块
Fund Holding Analyzer Core Module

功能：持仓集中度、重仓股分析、行业分布、FOF穿透
"""

import sys
sys.path.insert(0, '/root/.openclaw/workspace/finclaw/skills/fund-suite/fund-holding-analyzer/scripts')

import json
import argparse
import math
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class Holding:
    """持仓数据"""
    code: str
    name: str
    weight: float
    sector: str
    change: float = 0.0
    market_cap: float = 0.0  # 亿元
    pe: float = 0.0
    
    def to_dict(self) -> Dict:
        return asdict(self)


class HoldingAnalyzer:
    """持仓分析器"""
    
    def __init__(self):
        pass
    
    def _get_sector_from_code(self, code: str) -> str:
        """根据股票代码获取行业 - 尝试使用AkShare"""
        try:
            import akshare as ak
            # 尝试获取股票行业信息
            df = ak.stock_individual_info_em(symbol=code)
            if df is not None and not df.empty:
                # 查找行业信息
                for _, row in df.iterrows():
                    if '行业' in str(row.get('item', '')):
                        return row.get('value', '未知行业')
        except Exception:
            pass
        
        # 如果无法获取，返回未知
        return '未知行业'
    
    def analyze_holdings(self, fund_code: str, quarter: str,
                        holdings_data: Optional[List[Dict]] = None) -> Dict:
        """
        持仓综合分析
        
        Args:
            fund_code: 基金代码
            quarter: 报告期 (如 2024Q4)
            holdings_data: 持仓数据 (如不提供使用模拟数据)
        
        Returns:
            持仓分析报告
        """
        # 使用模拟数据或传入数据
        holdings = holdings_data or self._get_sample_holdings()
        
        # 计算集中度
        concentration = self.calculate_concentration(holdings)
        
        # 行业分布
        sector_dist = self._analyze_sector_distribution(holdings)
        
        # 风格分析
        style = self._analyze_style(holdings)
        
        # 重仓股分析
        top_holdings = sorted(holdings, key=lambda x: x['weight'], reverse=True)[:10]
        
        return {
            'analysis_id': f'HOLD_{datetime.now().strftime("%Y%m%d")}_{fund_code}',
            'fund_code': fund_code,
            'fund_name': fund_code,  # 实际使用时应从API获取基金名称
            'quarter': quarter,
            'analysis_date': datetime.now().strftime('%Y-%m-%d'),
            'concentration': concentration,
            'top_holdings': [h if isinstance(h, dict) else h.to_dict() for h in top_holdings],
            'sector_distribution': sector_dist,
            'style_exposure': style,
            'turnover_analysis': self._analyze_turnover(holdings),
            'recommendations': self._generate_recommendations(concentration, sector_dist),
            'data_source': '用户传入' if holdings_data else '示例数据(需替换)'
        }
    
    def calculate_concentration(self, holdings: List[Dict]) -> Dict:
        """
        计算集中度指标
        
        Args:
            holdings: 持仓列表
        
        Returns:
            集中度指标
        """
        # 排序
        sorted_holdings = sorted(holdings, key=lambda x: x['weight'], reverse=True)
        weights = [h['weight'] for h in sorted_holdings]
        
        # CR5, CR10
        cr5 = sum(weights[:5]) if len(weights) >= 5 else sum(weights)
        cr10 = sum(weights[:10]) if len(weights) >= 10 else sum(weights)
        
        # HHI (赫芬达尔指数)
        hhi = sum(w ** 2 for w in weights)
        
        # 有效持仓数
        effective_holdings = 1 / hhi if hhi > 0 else len(weights)
        
        # 基尼系数 (简化计算)
        sorted_weights = sorted(weights)
        n = len(sorted_weights)
        cumsum = 0
        gini_numerator = 0
        for i, w in enumerate(sorted_weights, 1):
            cumsum += w
            gini_numerator += (2 * i - n - 1) * w
        gini = gini_numerator / (n * cumsum) if cumsum > 0 else 0
        
        # 集中度评级
        if hhi < 0.05:
            rating = '🟢 非常分散'
        elif hhi < 0.10:
            rating = '🟢 分散'
        elif hhi < 0.15:
            rating = '🟡 适中'
        elif hhi < 0.25:
            rating = '🟠 集中'
        else:
            rating = '🔴 非常集中'
        
        return {
            'cr5': round(cr5, 4),
            'cr5_pct': round(cr5 * 100, 2),
            'cr10': round(cr10, 4),
            'cr10_pct': round(cr10 * 100, 2),
            'hhi': round(hhi, 4),
            'effective_holdings': round(effective_holdings, 1),
            'gini': round(abs(gini), 4),
            'rating': rating,
            'interpretation': self._interpret_concentration(hhi, cr10)
        }
    
    def fof_lookthrough(self, fof_code: str, holdings: List[Dict],
                       max_depth: int = 2) -> Dict:
        """
        FOF穿透分析
        
        Args:
            fof_code: FOF基金代码
            holdings: FOF持仓的子基金列表
            max_depth: 最大穿透层级
        
        Returns:
            穿透分析报告
        """
        # 穿透结果初始化
        lookthrough_result = {
            'fof_code': fof_code,
            'analysis_date': datetime.now().strftime('%Y-%m-%d'),
            'max_depth': max_depth,
            'level_1_holdings': holdings,
            'lookthrough_summary': {
                'stock_ratio': 0.0,
                'bond_ratio': 0.0,
                'cash_ratio': 0.0,
                'other_ratio': 0.0,
                'data_note': '请传入底层资产数据或连接API获取'
            },
            'stock_holdings': [],
            'sector_distribution': {},
            'style_analysis': {},
            'related_party_check': [],
            'data_source': '需传入底层数据'
        }
        
        # 如果未提供底层数据，返回提示
        if not holdings:
            lookthrough_result['error'] = '未提供子基金底层持仓数据'
            return lookthrough_result
        
        # 累加各子基金的资产配置（假设holdings中包含底层数据）
        total_stock = 0
        stock_details = {}
        
        for fund in holdings:
            fund_weight = fund.get('weight', 0)
            
            # 从传入的数据中获取底层资产比例
            underlying = fund.get('underlying_assets', {})
            stock_ratio = underlying.get('stock_ratio', 0)
            bond_ratio = underlying.get('bond_ratio', 0)
            cash_ratio = underlying.get('cash_ratio', 0)
            
            lookthrough_result['lookthrough_summary']['stock_ratio'] += stock_ratio * fund_weight
            lookthrough_result['lookthrough_summary']['bond_ratio'] += bond_ratio * fund_weight
            lookthrough_result['lookthrough_summary']['cash_ratio'] += cash_ratio * fund_weight
            
            # 汇总股票持仓
            for stock in underlying.get('stocks', []):
                effective_weight = stock.get('weight', 0) * fund_weight
                total_stock += effective_weight
                code = stock.get('code')
                if code:
                    if code in stock_details:
                        stock_details[code]['weight'] += effective_weight
                        stock_details[code]['sources'].append(fund.get('name', 'Unknown'))
                    else:
                        stock_details[code] = {
                            'code': code,
                            'name': stock.get('name', 'Unknown'),
                            'weight': effective_weight,
                            'sources': [fund.get('name', 'Unknown')]
                        }
        
        # 整理股票持仓
        sorted_stocks = sorted(stock_details.values(), key=lambda x: x['weight'], reverse=True)
        lookthrough_result['stock_holdings'] = sorted_stocks[:10]
        
        # 关联交易检测
        for code, detail in stock_details.items():
            if len(detail['sources']) > 1:
                lookthrough_result['related_party_check'].append({
                    'code': code,
                    'name': detail['name'],
                    'total_weight': detail['weight'],
                    'sources': detail['sources'],
                    'note': '在多个子基金中均有配置'
                })
        
        # 行业分布
        sector_dist = {}
        for stock in sorted_stocks:
            sector = stock.get('sector') or self._get_sector_from_code(stock['code']) or '其他'
            sector_dist[sector] = sector_dist.get(sector, 0) + stock['weight']
        
        lookthrough_result['sector_distribution'] = sector_dist
        
        return lookthrough_result
    
    def _analyze_sector_distribution(self, holdings: List[Dict]) -> Dict:
        """分析行业分布"""
        sector_weights = {}
        
        for h in holdings:
            sector = h.get('sector', '其他')
            sector_weights[sector] = sector_weights.get(sector, 0) + h['weight']
        
        # 排序
        sorted_sectors = sorted(sector_weights.items(), key=lambda x: x[1], reverse=True)
        
        # 计算HHI
        hhi = sum(w ** 2 for _, w in sector_weights.items())
        
        return {
            'distribution': dict(sorted_sectors),
            'top3': dict(sorted_sectors[:3]),
            'top3_ratio': sum(w for _, w in sorted_sectors[:3]),
            'hhi': round(hhi, 4),
            'concentration': '集中' if hhi > 0.15 else '适中' if hhi > 0.10 else '分散'
        }
    
    def _analyze_style(self, holdings: List[Dict]) -> Dict:
        """分析风格暴露"""
        # 市值分布
        cap_dist = {'large': 0, 'mid': 0, 'small': 0, 'micro': 0}
        
        for h in holdings:
            cap = h.get('market_cap', 0)
            weight = h.get('weight', 0)
            
            if cap > 500:
                cap_dist['large'] += weight
            elif cap > 100:
                cap_dist['mid'] += weight
            elif cap > 50:
                cap_dist['small'] += weight
            else:
                cap_dist['micro'] += weight
        
        # 估值分布
        val_dist = {'value': 0, 'blend': 0, 'growth': 0}
        
        for h in holdings:
            pe = h.get('pe', 0)
            weight = h.get('weight', 0)
            
            if 0 < pe < 15:
                val_dist['value'] += weight
            elif pe < 30:
                val_dist['blend'] += weight
            else:
                val_dist['growth'] += weight
        
        # 判断主导风格
        dominant_cap = max(cap_dist, key=cap_dist.get)
        dominant_val = max(val_dist, key=val_dist.get)
        
        style_tags = []
        if dominant_cap == 'large':
            style_tags.append('大盘')
        elif dominant_cap == 'small':
            style_tags.append('小盘')
        
        if dominant_val == 'value':
            style_tags.append('价值')
        elif dominant_val == 'growth':
            style_tags.append('成长')
        
        return {
            'market_cap': cap_dist,
            'valuation': val_dist,
            'dominant_style': ''.join(style_tags) if style_tags else '均衡',
            'style_tags': style_tags
        }
    
    def _analyze_turnover(self, holdings: List[Dict]) -> Dict:
        """分析换手率"""
        changes = [abs(h.get('change', 0)) for h in holdings]
        total_change = sum(changes) / 2  # 双边换手率
        
        new_entries = [h for h in holdings if h.get('change', 0) == h.get('weight', 0)]
        exits = [h for h in holdings if h.get('change', 0) < 0 and h.get('weight', 0) == 0]
        
        return {
            'turnover_ratio': round(total_change, 4),
            'turnover_pct': round(total_change * 100, 2),
            'new_entries': len(new_entries),
            'exits': len(exits),
            'rating': '高' if total_change > 0.5 else '中' if total_change > 0.3 else '低'
        }
    
    def _interpret_concentration(self, hhi: float, cr10: float) -> str:
        """解读集中度"""
        if hhi < 0.05:
            return "持仓非常分散，风险分散但可能错失集中收益机会"
        elif hhi < 0.10:
            return "持仓分散，适度集中"
        elif hhi < 0.15:
            return "持仓适中，前10大占比" + f"{cr10*100:.0f}%，风险收益相对均衡"
        elif hhi < 0.25:
            return "持仓较为集中，对重仓股依赖较大"
        else:
            return "持仓高度集中，波动可能较大"
    
    def _generate_recommendations(self, concentration: Dict, sector: Dict) -> List[str]:
        """生成建议"""
        recs = []
        
        if concentration['hhi'] > 0.20:
            recs.append('持仓高度集中，建议适当分散降低单一标的风险')
        
        if sector.get('hhi', 0) > 0.20:
            recs.append('行业集中度较高，需关注行业政策风险')
        
        recs.extend([
            '关注重仓股的基本面变化',
            '注意季报披露后的持仓变化',
            '结合市场环境判断风格暴露的合理性'
        ])
        
        return recs
    
    def _get_sample_holdings(self) -> List[Dict]:
        """获取示例持仓数据 - 仅用于演示"""
        import warnings
        warnings.warn("使用示例数据，生产环境请传入真实持仓数据", UserWarning)
        return [
            {'code': 'INPUT_CODE', 'name': '示例股票-请传入真实数据', 'weight': 0.085, 'sector': '示例', 'change': 0.015, 'market_cap': 0, 'pe': 0},
        ]


def print_holding_report(report: Dict):
    """打印持仓分析报告"""
    print("\n" + "=" * 70)
    print("📊 持仓分析报告")
    print("=" * 70)
    
    print(f"\n分析ID: {report['analysis_id']}")
    print(f"基金代码: {report['fund_code']}")
    print(f"报告期: {report['quarter']}")
    
    conc = report['concentration']
    print(f"\n集中度分析:")
    print(f"  CR5:  {conc['cr5_pct']:.1f}% (前5大持仓)")
    print(f"  CR10: {conc['cr10_pct']:.1f}% (前10大持仓)")
    print(f"  HHI:  {conc['hhi']:.4f} (赫芬达尔指数)")
    print(f"  有效持仓数: {conc['effective_holdings']}")
    print(f"  评级: {conc['rating']}")
    print(f"  解读: {conc['interpretation']}")
    
    print(f"\n前十大重仓股:")
    print(f"{'排名':<4} {'代码':<10} {'名称':<12} {'权重':<8} {'变化':<8} {'行业':<10}")
    print("-" * 65)
    for i, h in enumerate(report['top_holdings'][:10], 1):
        change_str = f"{h['change']*100:+.1f}%"
        print(f"{i:<4} {h['code']:<10} {h['name']:<12} "
              f"{h['weight']*100:>6.1f}% {change_str:<8} {h['sector']:<10}")
    
    sector = report['sector_distribution']
    print(f"\n行业分布 (Top 5):")
    for sect, weight in list(sector['distribution'].items())[:5]:
        print(f"  {sect}: {weight*100:.1f}%")
    print(f"  行业HHI: {sector['hhi']:.4f} ({sector['concentration']})")
    
    style = report['style_exposure']
    print(f"\n风格分析:")
    print(f"  主导风格: {style['dominant_style']}")
    print(f"  市值分布: 大盘{style['market_cap']['large']*100:.0f}% / "
          f"中盘{style['market_cap']['mid']*100:.0f}% / "
          f"小盘{style['market_cap']['small']*100:.0f}%")
    print(f"  估值分布: 价值{style['valuation']['value']*100:.0f}% / "
          f"均衡{style['valuation']['blend']*100:.0f}% / "
          f"成长{style['valuation']['growth']*100:.0f}%")
    
    turnover = report['turnover_analysis']
    print(f"\n换手率分析:")
    print(f"  换手率: {turnover['turnover_pct']:.1f}% ({turnover['rating']})")
    print(f"  新进: {turnover['new_entries']}只 | 退出: {turnover['exits']}只")
    
    print("=" * 70)


def print_fof_report(report: Dict):
    """打印FOF穿透报告"""
    print("\n" + "=" * 70)
    print("📊 FOF穿透分析报告")
    print("=" * 70)
    
    print(f"\nFOF代码: {report['fof_code']}")
    print(f"穿透层级: {report['max_depth']}")
    
    summary = report['lookthrough_summary']
    print(f"\n穿透后资产分布:")
    print(f"  股票: {summary['stock_ratio']*100:.1f}%")
    print(f"  债券: {summary['bond_ratio']*100:.1f}%")
    print(f"  现金: {summary['cash_ratio']*100:.1f}%")
    print(f"  其他: {summary['other_ratio']*100:.1f}%")
    
    print(f"\n穿透后股票持仓 (Top 10):")
    print(f"{'代码':<10} {'名称':<12} {'等效权重':<10} {'来源基金数':<12}")
    print("-" * 50)
    for stock in report['stock_holdings'][:10]:
        sources = len(stock.get('sources', []))
        print(f"{stock['code']:<10} {stock['name']:<12} "
              f"{stock['weight']*100:>7.2f}% {sources:<12}")
    
    if report['related_party_check']:
        print(f"\n⚠️ 关联交易检测:")
        for item in report['related_party_check']:
            print(f"  {item['name']}({item['code']}): {item['total_weight']*100:.2f}%")
            print(f"    来源: {', '.join(item['sources'])}")
    else:
        print(f"\n✅ 未发现明显关联交易")
    
    print("=" * 70)


def main():
    """主函数 - CLI入口"""
    parser = argparse.ArgumentParser(description='基金持仓分析')
    parser.add_argument('--fund', help='基金代码')
    parser.add_argument('--quarter', help='报告期(如: 2024Q4)')
    parser.add_argument('--concentration', action='store_true', help='集中度分析')
    parser.add_argument('--fof', action='store_true', help='FOF穿透分析')
    parser.add_argument('--json', action='store_true', help='输出JSON格式')
    parser.add_argument('--data-file', help='持仓数据文件(JSON格式)')
    
    args = parser.parse_args()
    
    analyzer = HoldingAnalyzer()
    
    # 从文件加载数据
    if args.data_file:
        try:
            with open(args.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"加载数据文件失败: {e}")
            return
    else:
        # 未提供数据文件时返回使用说明
        print("=" * 70)
        print("📊 基金持仓分析工具")
        print("=" * 70)
        print("\n使用方法:")
        print("  1. 准备持仓数据文件(JSON格式)")
        print("  2. 使用 --data-file 参数指定数据文件")
        print("\n数据文件格式示例:")
        print("""
{
  "fund_code": "000001",
  "quarter": "2024Q4",
  "holdings": [
    {"code": "600519", "name": "贵州茅台", "weight": 0.08, "sector": "食品饮料"},
    {"code": "300750", "name": "宁德时代", "weight": 0.06, "sector": "电力设备"}
  ]
}
        """)
        print("\n或使用 --fund 配合相关API获取真实数据")
        print("=" * 70)
        
        if args.fund:
            print(f"\n提示：分析基金 {args.fund} 需要提供持仓数据文件")
            print("请使用 --data-file 参数指定数据文件")
        return
    
    fund_code = args.fund or data.get('fund_code', 'UNKNOWN')
    quarter = args.quarter or data.get('quarter', datetime.now().strftime('%YQ') + str((datetime.now().month-1)//3 + 1))
    
    if args.fof:
        # FOF穿透分析
        fof_holdings = data.get('fof_holdings', [])
        if not fof_holdings:
            print("错误：FOF分析需要 fof_holdings 数据")
            return
        
        report = analyzer.fof_lookthrough(fund_code, fof_holdings, max_depth=2)
        
        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            print_fof_report(report)
    
    else:
        # 普通持仓分析
        holdings = data.get('holdings', [])
        if not holdings:
            print("错误：数据文件缺少 holdings 字段")
            return
        
        report = analyzer.analyze_holdings(fund_code, quarter, holdings)
        
        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            print_holding_report(report)


if __name__ == '__main__':
    main()
