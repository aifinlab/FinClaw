#!/usr/bin/env python3
"""
基金税务优化核心模块 - AkShare版
Fund Tax Optimizer Core Module - AkShare Edition

功能：赎回费优化、税收损失收割、分红方式对比
数据：通过AkShare接入实时基金净值和收益数据
"""

import sys
import os
sys.path.insert(0, '/root/.openclaw/workspace/skillsChoice/fund-suite/fund-tax-optimizer/scripts')

import json
import argparse
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta

# 导入AkShare
try:
    import akshare as ak
    AKSHARE_AVAILABLE = True
except ImportError:
    AKSHARE_AVAILABLE = False
    print("警告：AkShare未安装，将使用模拟数据")


@dataclass
class HoldingLot:
    """持仓批次"""
    lot_id: str
    fund_code: str
    fund_name: str
    shares: float
    cost_basis: float
    purchase_date: str
    current_nav: float
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @property
    def current_value(self) -> float:
        return self.shares * self.current_nav
    
    @property
    def unrealized_gain(self) -> float:
        return self.shares * (self.current_nav - self.cost_basis)
    
    def holding_days(self, as_of_date: str) -> int:
        """计算持有天数"""
        purchase = datetime.strptime(self.purchase_date, '%Y-%m-%d')
        as_of = datetime.strptime(as_of_date, '%Y-%m-%d')
        return (as_of - purchase).days


class TaxOptimizer:
    """税务优化器 - AkShare数据源"""
    
    # 赎回费率表 (A类份额)
    REDEMPTION_FEE_SCHEDULE = [
        ((0, 7), 0.015, '惩罚性费率'),
        ((7, 30), 0.0075, '短期费率'),
        ((30, 365), 0.005, '中期费率'),
        ((365, 730), 0.0025, '长期费率'),
        ((730, float('inf')), 0.0, '免赎回费'),
    ]
    
    # C类份额费率
    C_CLASS_FEE = [((0, 7), 0.015), ((7, float('inf')), 0.0)]
    
    def __init__(self):
        self._data_source = ""
        self._data_quality = ""
        self._sample_holdings = []
        self._akshare_available = AKSHARE_AVAILABLE
        
        # 检查数据源可用性
        if not self._akshare_available:
            self._load_default_data()
    
    def _fetch_fund_info_from_akshare(self, fund_code: str) -> Tuple[float, str, str]:
        """
        从AkShare获取基金最新净值和名称
        
        Args:
            fund_code: 基金代码
            
        Returns:
            (当前净值, 基金名称, 净值日期)
        """
        try:
            # 获取基金实时行情
            df = ak.fund_open_fund_daily_em()
            fund_row = df[df['基金代码'] == fund_code]
            
            if fund_row.empty:
                return 0.0, fund_code, ""
            
            row = fund_row.iloc[0]
            nav = row.get('单位净值', 0) or row.get('最新净值', 0)
            fund_name = row.get('基金名称', '') or row.get('基金简称', '')
            nav_date = row.get('日期', datetime.now().strftime('%Y-%m-%d'))
            
            return float(nav) if nav else 0.0, fund_name, nav_date
            
        except Exception as e:
            print(f"⚠️ 从AkShare获取基金{fund_code}信息失败: {e}")
            return 0.0, fund_code, ""
    
    def _fetch_fund_nav_history(self, fund_code: str, days: int = 365) -> List[Dict]:
        """
        从AkShare获取基金历史净值
        
        Args:
            fund_code: 基金代码
            days: 获取的历史天数
            
        Returns:
            净值历史列表 [{date, nav, acc_nav, daily_return}]
        """
        try:
            df = ak.fund_open_fund_info_em(symbol=fund_code)
            
            if df.empty:
                return []
            
            # 只取最近N天
            df = df.head(days)
            
            nav_history = []
            for _, row in df.iterrows():
                nav = row.get('单位净值', 0)
                acc_nav = row.get('累计净值', 0)
                date = row.get('净值日期', '')
                daily_return_pct = row.get('日增长率', 0)
                
                if isinstance(daily_return_pct, str):
                    daily_return_pct = daily_return_pct.replace('%', '')
                
                nav_history.append({
                    'date': date,
                    'nav': float(nav) if nav else 0.0,
                    'acc_nav': float(acc_nav) if acc_nav else 0.0,
                    'daily_return': float(daily_return_pct) / 100 if daily_return_pct else 0.0
                })
            
            return nav_history
            
        except Exception as e:
            print(f"⚠️ 从AkShare获取基金{fund_code}净值历史失败: {e}")
            return []
    
    def _load_default_data(self):
        """加载默认模拟数据（降级方案）"""
        self._sample_holdings = [
            HoldingLot('LOT_20230115', '000001', '华夏成长', 8000, 1.20, '2023-01-15', 1.50),
            HoldingLot('LOT_20230601', '000002', '易方达蓝筹', 15000, 1.10, '2023-06-01', 1.20),
            HoldingLot('LOT_20240201', '000003', '中欧时代先锋', 14000, 1.45, '2024-02-01', 1.50),
            HoldingLot('LOT_20240310', '000004', '广发科技创新', 10000, 1.60, '2024-03-10', 1.45),
        ]
        self._data_source = "内置默认模拟数据(AkShare不可用)"
        self._data_quality = "sample"
    
    def _build_holdings_from_fund(self, fund_code: str, shares: float, 
                                   cost_basis: float, purchase_date: str) -> Optional[HoldingLot]:
        """
        从基金代码构建持仓批次（使用AkShare获取最新净值）
        
        Args:
            fund_code: 基金代码
            shares: 持有份额
            cost_basis: 成本单价
            purchase_date: 购买日期
            
        Returns:
            HoldingLot对象
        """
        current_nav, fund_name, nav_date = self._fetch_fund_info_from_akshare(fund_code)
        
        if current_nav <= 0:
            # 获取失败，使用默认值
            current_nav = cost_basis * 1.1  # 假设10%涨幅
            fund_name = fund_code
        
        lot_id = f"LOT_{purchase_date.replace('-', '')}_{fund_code}"
        
        return HoldingLot(
            lot_id=lot_id,
            fund_code=fund_code,
            fund_name=fund_name,
            shares=shares,
            cost_basis=cost_basis,
            purchase_date=purchase_date,
            current_nav=current_nav
        )
    
    def get_sample_holdings(self) -> List[HoldingLot]:
        """获取示例持仓数据"""
        if not self._sample_holdings:
            self._load_default_data()
        return self._sample_holdings.copy()
    
    def optimize_redemption(self, holdings: List[HoldingLot],
                           target_amount: float,
                           as_of_date: str = None) -> Dict:
        """
        赎回优化
        
        Args:
            holdings: 持仓列表
            target_amount: 目标赎回金额
            as_of_date: 计算日期
        
        Returns:
            优化建议
        """
        as_of_date = as_of_date or datetime.now().strftime('%Y-%m-%d')
        
        # 检查是否使用真实数据
        is_real_data = self._akshare_available and any(
            h.current_nav > 0 and h.fund_name != h.fund_code for h in holdings
        )
        
        if is_real_data:
            self._data_source = "AkShare实时数据"
            self._data_quality = "real-time"
        else:
            if not self._data_source:
                self._data_source = "内置默认模拟数据"
                self._data_quality = "sample"
        
        # 计算每批次的赎回费率
        lot_analysis = []
        for lot in holdings:
            days = lot.holding_days(as_of_date)
            fee_rate, fee_desc = self._get_redemption_fee(days)
            
            lot_analysis.append({
                'lot': lot.to_dict(),
                'holding_days': days,
                'current_value': lot.current_value,
                'unrealized_gain': lot.unrealized_gain,
                'redemption_fee_rate': fee_rate,
                'fee_description': fee_desc,
                'redemption_fee': lot.current_value * fee_rate,
                'net_proceeds': lot.current_value * (1 - fee_rate),
                'priority': fee_rate  # 费率越低优先级越高
            })
        
        # 按费率排序 (优先赎回费率低的)
        lot_analysis.sort(key=lambda x: x['priority'])
        
        # 选择最优赎回组合
        selected_lots = []
        remaining = target_amount
        total_fee = 0
        total_gain = 0
        
        for lot in lot_analysis:
            if remaining <= 0:
                break
            
            redeem_value = min(remaining, lot['current_value'])
            redeem_ratio = redeem_value / lot['current_value'] if lot['current_value'] > 0 else 0
            redeem_shares = lot['lot']['shares'] * redeem_ratio
            
            fee = redeem_value * lot['redemption_fee_rate']
            gain = lot['unrealized_gain'] * redeem_ratio
            
            selected_lots.append({
                'lot_id': lot['lot']['lot_id'],
                'fund_code': lot['lot']['fund_code'],
                'fund_name': lot['lot']['fund_name'],
                'shares': redeem_shares,
                'redeem_value': redeem_value,
                'holding_days': lot['holding_days'],
                'fee_rate': lot['redemption_fee_rate'],
                'fee': fee,
                'net_proceeds': redeem_value - fee,
                'realized_gain': gain
            })
            
            remaining -= redeem_value
            total_fee += fee
            total_gain += gain
        
        # 计算加权费率
        total_redeemed = sum(l['redeem_value'] for l in selected_lots)
        weighted_fee_rate = total_fee / total_redeemed if total_redeemed > 0 else 0
        
        # 生成建议
        recommendations = []
        
        # 检查是否有高费率批次被使用
        high_fee_lots = [l for l in selected_lots if l['fee_rate'] >= 0.005]
        if high_fee_lots:
            recommendations.append(f"使用了{len(high_fee_lots)}笔高费率份额，建议等待持有期满后再赎回")
        
        # 检查是否有接近免费的批次未使用
        free_lots = [l for l in lot_analysis if l['redemption_fee_rate'] == 0]
        unused_free = [l for l in free_lots if not any(s['lot_id'] == l['lot']['lot_id'] for s in selected_lots)]
        if unused_free and remaining <= 0:
            recommendations.append(f"还有{len(unused_free)}笔免费份额可用，建议优先使用")
        
        recommendations.extend([
            "赎回后关注剩余份额的成本基价变化",
            "考虑C类份额用于短期资金需求"
        ])
        
        return {
            'optimization_id': f'TAX_{datetime.now().strftime("%Y%m%d")}_001',
            'analysis_date': as_of_date,
            'data_source': self._data_source,
            'data_quality': self._data_quality,
            'is_real_data': is_real_data,
            'target_amount': target_amount,
            'recommendations': selected_lots,
            'summary': {
                'total_redeemed': total_redeemed,
                'total_fee': round(total_fee, 2),
                'weighted_fee_rate': round(weighted_fee_rate, 4),
                'weighted_fee_pct': round(weighted_fee_rate * 100, 2),
                'total_realized_gain': round(total_gain, 2),
                'net_proceeds': round(total_redeemed - total_fee, 2)
            },
            'warnings': self._generate_warnings(selected_lots),
            'suggestions': recommendations
        }
    
    def tax_loss_harvest(self, holdings: List[HoldingLot],
                        realized_gains: float = 0,
                        as_of_date: str = None) -> Dict:
        """
        税收损失收割
        
        Args:
            holdings: 持仓列表
            realized_gains: 已实现收益
            as_of_date: 计算日期
        
        Returns:
            收割建议
        """
        as_of_date = as_of_date or datetime.now().strftime('%Y-%m-%d')
        
        # 检查是否使用真实数据
        is_real_data = self._akshare_available and any(
            h.current_nav > 0 and h.fund_name != h.fund_code for h in holdings
        )
        
        if is_real_data:
            self._data_source = "AkShare实时数据"
            self._data_quality = "real-time"
        else:
            if not self._data_source:
                self._data_source = "内置默认模拟数据"
                self._data_quality = "sample"
        
        # 识别亏损仓位
        loss_positions = []
        total_loss = 0
        
        for lot in holdings:
            gain = lot.unrealized_gain
            if gain < 0:
                days = lot.holding_days(as_of_date)
                loss_positions.append({
                    'lot': lot.to_dict(),
                    'holding_days': days,
                    'unrealized_loss': gain,  # 负数
                    'abs_loss': abs(gain),
                    'current_value': lot.current_value,
                    'redeem_fee': lot.current_value * self._get_redemption_fee(days)[0]
                })
                total_loss += abs(gain)
        
        # 排序：优先收割大额亏损
        loss_positions.sort(key=lambda x: x['abs_loss'], reverse=True)
        
        # 计算税收节省
        tax_rate = 0.20  # 假设资本利得税率20%
        potential_savings = min(total_loss, realized_gains) * tax_rate
        
        # 选择建议收割的仓位 (亏损 > 费用)
        recommended = [p for p in loss_positions if p['abs_loss'] > p['redeem_fee'] * 2]
        
        # 再投资方案
        reinvestment_options = [
            {
                'option': 'A',
                'name': '等待31天后买回',
                'description': '避免洗售规则，但承担市场波动风险',
                'pros': ['完全合规', '买回相同基金'],
                'cons': ['31天市场波动风险', '资金闲置']
            },
            {
                'option': 'B',
                'name': '立即买入替代基金',
                'description': '买入相似但不相同的基金或ETF',
                'pros': ['保持市场暴露', '无等待期'],
                'cons': ['跟踪误差', '可能不同的费率']
            },
            {
                'option': 'C',
                'name': '调整资产配置',
                'description': '将资金转入其他资产类别',
                'pros': ['再平衡组合', '无洗售风险'],
                'cons': ['改变配置比例']
            }
        ]
        
        return {
            'harvest_id': f'HARVEST_{datetime.now().strftime("%Y%m%d")}_001',
            'analysis_date': as_of_date,
            'data_source': self._data_source,
            'data_quality': self._data_quality,
            'is_real_data': is_real_data,
            'current_position': {
                'realized_gains': realized_gains,
                'loss_positions_count': len(loss_positions),
                'total_unrealized_loss': total_loss
            },
            'harvest_opportunities': loss_positions,
            'recommended_harvests': recommended,
            'tax_savings_analysis': {
                'potential_savings': round(potential_savings, 2),
                'tax_rate': tax_rate * 100,
                'net_benefit': round(potential_savings - sum(p['redeem_fee'] for p in recommended), 2)
            },
            'reinvestment_options': reinvestment_options,
            'execution_reminders': [
                '在年度结束前执行以抵减当年收益',
                '记录所有交易成本用于税务申报',
                '设置31天后买回提醒（如选择方案A）',
                '保存交易记录备查'
            ]
        }
    
    def compare_dividend_options(self, initial_amount: float,
                                 annual_return: float,
                                 dividend_yield: float,
                                 years: int) -> Dict:
        """
        分红方式对比
        
        Args:
            initial_amount: 初始投资金额
            annual_return: 预期年化收益率
            dividend_yield: 分红率
            years: 投资年限
        
        Returns:
            对比报告
        """
        # 现金分红方案
        growth_rate_cash = annual_return - dividend_yield
        final_value_cash = initial_amount * ((1 + growth_rate_cash) ** years)
        total_dividends = initial_amount * dividend_yield * years
        total_value_cash = final_value_cash + total_dividends
        
        # 红利再投资方案
        final_value_reinvest = initial_amount * ((1 + annual_return) ** years)
        
        # 计算指标
        diff = final_value_reinvest - total_value_cash
        diff_pct = (diff / total_value_cash) * 100 if total_value_cash > 0 else 0
        
        total_return_cash = ((total_value_cash / initial_amount) - 1) * 100
        total_return_reinvest = ((final_value_reinvest / initial_amount) - 1) * 100
        
        annualized_cash = (((total_value_cash / initial_amount) ** (1/years)) - 1) * 100
        annualized_reinvest = annual_return * 100
        
        return {
            'comparison_id': f'DIV_{datetime.now().strftime("%Y%m%d")}_001',
            'analysis_date': datetime.now().strftime('%Y-%m-%d'),
            'data_source': '计算模型(非实时数据)',
            'data_quality': 'calculated',
            'is_real_data': False,
            'parameters': {
                'initial_amount': initial_amount,
                'annual_return': annual_return * 100,
                'dividend_yield': dividend_yield * 100,
                'years': years
            },
            'cash_dividend': {
                'final_nav_value': round(final_value_cash, 2),
                'total_dividends_received': round(total_dividends, 2),
                'total_value': round(total_value_cash, 2),
                'total_return': round(total_return_cash, 2),
                'annualized_return': round(annualized_cash, 2),
                'characteristics': [
                    '每年获得现金现金流',
                    '分红资金需自行再投资',
                    '灵活性高，可随时使用'
                ]
            },
            'reinvest_dividend': {
                'final_value': round(final_value_reinvest, 2),
                'total_return': round(total_return_reinvest, 2),
                'annualized_return': round(annualized_reinvest, 2),
                'characteristics': [
                    '自动复利增长',
                    '无申购费用',
                    '适合长期投资'
                ]
            },
            'comparison': {
                'value_difference': round(diff, 2),
                'percentage_difference': round(diff_pct, 2),
                'advantage': '红利再投资' if diff > 0 else '现金分红'
            },
            'recommendations': self._generate_dividend_recommendations(years, diff)
        }
    
    def _get_redemption_fee(self, holding_days: int, is_c_class: bool = False) -> Tuple[float, str]:
        """获取赎回费率"""
        if is_c_class:
            for (min_d, max_d), fee in self.C_CLASS_FEE:
                if min_d <= holding_days < max_d:
                    return fee, 'C类份额费率'
            return 0.0, 'C类免费'
        
        for (min_d, max_d), fee, desc in self.REDEMPTION_FEE_SCHEDULE:
            if min_d <= holding_days < max_d:
                return fee, desc
        return 0.0, '免赎回费'
    
    def _generate_warnings(self, selected_lots: List[Dict]) -> List[str]:
        """生成警告"""
        warnings = []
        
        # 检查7天内赎回
        very_short = [l for l in selected_lots if l['holding_days'] < 7]
        if very_short:
            warnings.append(f"有{len(very_short)}笔份额持有<7天，赎回费1.5%")
        
        # 检查30天内赎回
        short_term = [l for l in selected_lots if 7 <= l['holding_days'] < 30]
        if short_term:
            warnings.append(f"有{len(short_term)}笔份额持有7-30天，赎回费0.75%")
        
        # 检查大额赎回
        total = sum(l['redeem_value'] for l in selected_lots)
        if total > 100000:
            warnings.append("大额赎回，建议考虑分批操作")
        
        return warnings
    
    def _generate_dividend_recommendations(self, years: int, diff: float) -> List[str]:
        """生成分红建议"""
        recs = []
        
        if years >= 3 and diff > 0:
            recs.append(f"投资期限{years}年≥3年，建议选择红利再投资享受复利")
        
        if years < 1:
            recs.append("短期投资(<1年)，可考虑现金分红保持灵活性")
        
        recs.extend([
            "分红方式可随时在账户设置中更改",
            "红利再投资的份额成本基价会重新计算",
            "如需现金流，可选择现金分红或部分赎回"
        ])
        
        return recs


def print_redemption_report(report: Dict):
    """打印赎回优化报告"""
    print("\n" + "=" * 70)
    print("📊 赎回优化报告")
    print("=" * 70)
    
    print(f"\n优化ID: {report['optimization_id']}")
    print(f"分析日期: {report['analysis_date']}")
    print(f"数据来源: {report.get('data_source', '未知')}")
    print(f"数据质量: {report.get('data_quality', 'unknown')}")
    print(f"真实数据: {'✅ 是' if report.get('is_real_data') else '⚠️ 否(模拟数据)'}")
    print(f"目标金额: ¥{report['target_amount']:,.0f}")
    
    print(f"\n建议赎回批次:")
    print(f"{'基金':<15} {'份额':<10} {'金额':<12} {'持有':<8} {'费率':<8} {'费用':<10}")
    print("-" * 75)
    for lot in report['recommendations']:
        print(f"{lot['fund_name'][:13]:<15} {lot['shares']:>8.0f} "
              f"¥{lot['redeem_value']:<10,.0f} {lot['holding_days']:>5}天 "
              f"{lot['fee_rate']*100:>5.2f}% ¥{lot['fee']:<8,.0f}")
    
    summary = report['summary']
    print(f"\n汇总:")
    print(f"  总赎回金额: ¥{summary['total_redeemed']:,.0f}")
    print(f"  总赎回费: ¥{summary['total_fee']:,.2f}")
    print(f"  加权费率: {summary['weighted_fee_pct']:.2f}%")
    print(f"  净到账: ¥{summary['net_proceeds']:,.2f}")
    print(f"  实现收益: ¥{summary['total_realized_gain']:,.2f}")
    
    if report['warnings']:
        print(f"\n⚠️ 警告:")
        for w in report['warnings']:
            print(f"  • {w}")
    
    print(f"\n💡 建议:")
    for s in report['suggestions']:
        print(f"  • {s}")
    
    print("=" * 70)


def print_harvest_report(report: Dict):
    """打印税收损失收割报告"""
    print("\n" + "=" * 70)
    print("📊 税收损失收割报告")
    print("=" * 70)
    
    print(f"\n收割ID: {report['harvest_id']}")
    print(f"数据来源: {report.get('data_source', '未知')}")
    print(f"数据质量: {report.get('data_quality', 'unknown')}")
    print(f"真实数据: {'✅ 是' if report.get('is_real_data') else '⚠️ 否(模拟数据)'}")
    
    pos = report['current_position']
    print(f"\n当前持仓:")
    print(f"  已实现收益: ¥{pos['realized_gains']:,.0f}")
    print(f"  亏损仓位: {pos['loss_positions_count']}个")
    print(f"  总未实现亏损: ¥{pos['total_unrealized_loss']:,.0f}")
    
    if report['recommended_harvests']:
        print(f"\n建议收割仓位:")
        print(f"{'基金':<15} {'持有':<8} {'亏损':<12} {'费用':<10} {'净收益':<12}")
        print("-" * 65)
        for h in report['recommended_harvests']:
            net = h['abs_loss'] - h['redeem_fee']
            print(f"{h['lot']['fund_name'][:13]:<15} {h['holding_days']:>5}天 "
                  f"¥{h['abs_loss']:<10,.0f} ¥{h['redeem_fee']:<8,.0f} ¥{net:<10,.0f}")
        
        tax = report['tax_savings_analysis']
        print(f"\n税收节省分析:")
        print(f"  潜在节省: ¥{tax['potential_savings']:,.2f}")
        print(f"  税率: {tax['tax_rate']:.0f}%")
        print(f"  净收益: ¥{tax['net_benefit']:,.2f}")
    else:
        print(f"\n✅ 暂无可收割的亏损仓位")
    
    print(f"\n再投资方案:")
    for opt in report['reinvestment_options']:
        print(f"\n  方案{opt['option']}: {opt['name']}")
        print(f"    {opt['description']}")
        print(f"    优点: {', '.join(opt['pros'])}")
        print(f"    缺点: {', '.join(opt['cons'])}")
    
    print("=" * 70)


def print_dividend_report(report: Dict):
    """打印分红对比报告"""
    print("\n" + "=" * 70)
    print("📊 分红方式对比报告")
    print("=" * 70)
    
    print(f"数据来源: {report.get('data_source', '未知')}")
    print(f"数据质量: {report.get('data_quality', 'unknown')}")
    
    params = report['parameters']
    print(f"\n投资参数:")
    print(f"  初始金额: ¥{params['initial_amount']:,.0f}")
    print(f"  预期年化: {params['annual_return']:.1f}%")
    print(f"  分红率: {params['dividend_yield']:.1f}%")
    print(f"  投资期限: {params['years']}年")
    
    cash = report['cash_dividend']
    reinvest = report['reinvest_dividend']
    
    print(f"\n{'方案':<15} {'期末价值':<15} {'总收益':<12} {'年化':<10}")
    print("-" * 55)
    print(f"{'现金分红':<15} ¥{cash['total_value']:<13,.0f} "
          f"{cash['total_return']:>8.1f}% {cash['annualized_return']:>7.2f}%")
    print(f"{'红利再投资':<15} ¥{reinvest['final_value']:<13,.0f} "
          f"{reinvest['total_return']:>8.1f}% {reinvest['annualized_return']:>7.2f}%")
    
    comp = report['comparison']
    print(f"\n对比:")
    print(f"  差额: ¥{comp['value_difference']:,.0f} ({comp['percentage_difference']:+.2f}%)")
    print(f"  优势方案: {comp['advantage']}")
    
    print(f"\n💡 建议:")
    for rec in report['recommendations']:
        print(f"  • {rec}")
    
    print("=" * 70)


def main():
    """主函数 - CLI入口"""
    parser = argparse.ArgumentParser(description='基金税务优化 - AkShare版')
    parser.add_argument('--optimize', action='store_true', help='赎回优化')
    parser.add_argument('--harvest', action='store_true', help='税收损失收割')
    parser.add_argument('--dividend', action='store_true', help='分红方式对比')
    parser.add_argument('--target', type=float, default=50000, help='目标金额')
    parser.add_argument('--fund', help='基金代码（如使用AkShare获取实时数据）')
    parser.add_argument('--shares', type=float, help='持有份额')
    parser.add_argument('--cost', type=float, help='成本单价')
    parser.add_argument('--date', help='购买日期(YYYY-MM-DD)')
    parser.add_argument('--json', action='store_true', help='输出JSON格式')
    
    args = parser.parse_args()
    
    optimizer = TaxOptimizer()
    
    # 如果提供了基金代码和持仓信息，构建实时持仓
    if args.fund and args.shares and args.cost and args.date:
        holding = optimizer._build_holdings_from_fund(
            args.fund, args.shares, args.cost, args.date
        )
        sample_holdings = [holding] if holding else []
    else:
        # 使用示例持仓
        sample_holdings = optimizer.get_sample_holdings()
    
    if args.optimize or (not args.harvest and not args.dividend):
        report = optimizer.optimize_redemption(sample_holdings, args.target)
        
        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2, default=str))
        else:
            print_redemption_report(report)
    
    elif args.harvest:
        report = optimizer.tax_loss_harvest(sample_holdings, realized_gains=15000)
        
        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2, default=str))
        else:
            print_harvest_report(report)
    
    elif args.dividend:
        report = optimizer.compare_dividend_options(
            initial_amount=100000,
            annual_return=0.10,
            dividend_yield=0.03,
            years=5
        )
        
        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2, default=str))
        else:
            print_dividend_report(report)


if __name__ == '__main__':
    main()
