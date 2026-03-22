#!/usr/bin/env python3
"""
基金定投规划核心模块（真实数据版）
Fund SIP Planner Core Module - Real Data Edition

功能：定投计划、智能定投、定投回测、止盈止损
数据源：AkShare / 同花顺iFinD
"""

import sys
sys.path.insert(0, '/root/.openclaw/workspace/finclaw/skills/fund-suite/fund-sip-planner/scripts')
sys.path.insert(0, '/root/.openclaw/workspace/finclaw/skills/fund-suite/data')

import json
import argparse
import math
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

# 导入数据适配器
try:
    from fund_data_adapter import get_fund_adapter
    DATA_ADAPTER_AVAILABLE = True
except ImportError as e:
    DATA_ADAPTER_AVAILABLE = False
    print(f"警告：数据适配器未加载: {e}")


@dataclass
class SIPPlan:
    """定投计划"""
    plan_id: str
    target_amount: float
    monthly_amount: float
    years: int
    strategy: str
    total_periods: int
    expected_return: float
    projected_value: float
    projected_profit: float
    data_source: str = "模拟"
    
    def to_dict(self) -> Dict:
        return asdict(self)


class SIPPlanner:
    """定投规划器（真实数据版）"""
    
    STRATEGY_PARAMS = {
        'fixed': {'name': '固定定投', 'description': '每期固定金额'},
        'ma': {'name': '均线定投', 'description': '基于均线偏离度调整'},
        'value': {'name': '估值定投', 'description': '基于估值百分位调整'},
        'pyramiding': {'name': '金字塔定投', 'description': '下跌加码策略'},
    }
    
    def __init__(self, use_real_data: bool = True):
        self.data_adapter = None
        self.data_source = "模拟数据"
        
        if use_real_data and DATA_ADAPTER_AVAILABLE:
            self._init_data_adapter()
    
    def _init_data_adapter(self):
        try:
            self.data_adapter = get_fund_adapter(prefer_ths=False)
            self.data_source = self.data_adapter.get_data_source()
            print(f"✅ 数据源: {self.data_source}")
        except Exception as e:
            print(f"⚠️ 数据适配器初始化失败: {e}")
    
    def calculate_sip(self, target_amount: float, years: int, 
                     expected_return: float = 0.08) -> Dict:
        """
        计算定投计划
        
        Args:
            target_amount: 目标金额
            years: 投资年限
            expected_return: 预期年化收益率
        
        Returns:
            定投计划详情
        """
        # 从真实数据获取预期收益率（如果可用）
        real_return = self._get_real_expected_return()
        if real_return:
            expected_return = real_return
            print(f"✅ 使用真实数据预期收益率: {expected_return:.1%}")
        
        months = years * 12
        monthly_return = (1 + expected_return) ** (1/12) - 1
        
        # 计算每月定投金额
        # FV = PMT * [(1+r)^n - 1] / r
        # PMT = FV * r / [(1+r)^n - 1]
        fv_factor = ((1 + monthly_return) ** months - 1) / monthly_return
        monthly_amount = target_amount / fv_factor
        
        # 总投资金额
        total_invested = monthly_amount * months
        total_profit = target_amount - total_invested
        
        plan = SIPPlan(
            plan_id=f"SIP_{datetime.now().strftime('%Y%m%d')}_{target_amount/10000:.0f}W",
            target_amount=target_amount,
            monthly_amount=monthly_amount,
            years=years,
            strategy='fixed',
            total_periods=months,
            expected_return=expected_return,
            projected_value=target_amount,
            projected_profit=total_profit,
            data_source=self.data_source
        )
        
        return {
            'plan': plan.to_dict(),
            'schedule': self._generate_schedule(monthly_amount, months),
            'projections': self._calculate_projections(monthly_amount, months, expected_return),
            'target_analysis': self._analyze_target(target_amount, monthly_amount, months, expected_return),
            'recommendations': self._generate_recommendations(years, expected_return)
        }
    
    def _get_real_expected_return(self) -> Optional[float]:
        """从真实数据获取预期收益率"""
        if not self.data_adapter:
            return None
        
        try:
            # 获取混合型基金平均收益作为参考
            import akshare as ak
            df = ak.fund_open_fund_rank_em()
            if not df.empty:
                # 取中位数收益作为预期
                returns = []
                for _, row in df.head(100).iterrows():
                    val = row.get('近1年', '0')
                    if isinstance(val, str) and '%' in val:
                        returns.append(float(val.replace('%', '')) / 100)
                
                if returns:
                    median_return = sorted(returns)[len(returns)//2]
                    # 保守估计，取中位数的80%
                    return max(0.04, min(0.12, median_return * 0.8))
        except Exception as e:
            print(f"获取真实预期收益失败: {e}")
        
        return None
    
    def _generate_schedule(self, monthly_amount: float, months: int) -> List[Dict]:
        """生成定投时间表"""
        schedule = []
        start_date = datetime.now()
        
        for i in range(min(12, months)):  # 只显示前12期
            date = start_date + timedelta(days=30*i)
            schedule.append({
                'period': i + 1,
                'date': date.strftime('%Y-%m-%d'),
                'amount': round(monthly_amount, 2),
                'cumulative': round(monthly_amount * (i + 1), 2)
            })
        
        if months > 12:
            schedule.append({
                'period': '...',
                'date': '...',
                'amount': '...',
                'cumulative': '...'
            })
            
            final_date = start_date + timedelta(days=30*(months-1))
            schedule.append({
                'period': months,
                'date': final_date.strftime('%Y-%m-%d'),
                'amount': round(monthly_amount, 2),
                'cumulative': round(monthly_amount * months, 2)
            })
        
        return schedule
    
    def _calculate_projections(self, monthly_amount: float, months: int, 
                               expected_return: float) -> Dict:
        """计算各阶段预期"""
        monthly_r = (1 + expected_return) ** (1/12) - 1
        
        projections = {}
        milestones = [12, 24, 36, 60, 120, months]
        
        for m in milestones:
            if m <= months:
                fv = monthly_amount * ((1 + monthly_r) ** m - 1) / monthly_r
                invested = monthly_amount * m
                projections[f'{m}个月'] = {
                    'projected_value': round(fv, 2),
                    'total_invested': round(invested, 2),
                    'projected_profit': round(fv - invested, 2),
                    'return_rate': round((fv - invested) / invested * 100, 2) if invested > 0 else 0
                }
        
        return projections
    
    def _analyze_target(self, target_amount: float, monthly_amount: float,
                        months: int, expected_return: float) -> Dict:
        """分析目标可行性"""
        monthly_r = (1 + expected_return) ** (1/12) - 1
        
        # 计算达成目标所需时间
        if monthly_amount <= 0:
            months_to_target = float('inf')
        else:
            # FV = PMT * [(1+r)^n - 1] / r
            # n = ln(FV*r/PMT + 1) / ln(1+r)
            fv_per_pmt = target_amount * monthly_r / monthly_amount
            if fv_per_pmt <= 0:
                months_to_target = float('inf')
            else:
                months_to_target = math.log(fv_per_pmt + 1) / math.log(1 + monthly_r)
        
        # 评估压力
        monthly_income_estimate = 10000  # 假设月收入1万
        pressure_ratio = monthly_amount / monthly_income_estimate
        
        if pressure_ratio <= 0.10:
            pressure_level = "低"
            pressure_color = "🟢"
        elif pressure_ratio <= 0.20:
            pressure_level = "中"
            pressure_color = "🟡"
        elif pressure_ratio <= 0.30:
            pressure_level = "较高"
            pressure_color = "🟠"
        else:
            pressure_level = "高"
            pressure_color = "🔴"
        
        return {
            'months_to_target': round(months_to_target, 1),
            'years_to_target': round(months_to_target / 12, 1),
            'monthly_pressure_ratio': round(pressure_ratio * 100, 1),
            'pressure_level': pressure_level,
            'pressure_emoji': pressure_color,
            'feasibility': '可行' if months_to_target <= months else '需调整'
        }
    
    def _generate_recommendations(self, years: int, expected_return: float) -> List[str]:
        """生成建议"""
        recommendations = [
            f"建议设置止盈线：{expected_return*100*2:.0f}%（约{expected_return*100:.0f}%年化×2年）",
            "建议设置止损线：-15%到-20%",
            "市场大跌时可考虑加码定投（金字塔策略）",
            "坚持3年以上，平滑市场波动"
        ]
        
        if years < 3:
            recommendations.append("⚠️ 定投建议持有3年以上，短期波动较大")
        
        return recommendations


def main():
    parser = argparse.ArgumentParser(description='基金定投规划')
    parser.add_argument('--target', type=float, required=True, help='目标金额')
    parser.add_argument('--years', type=int, required=True, help='投资年限')
    parser.add_argument('--return', type=float, default=0.08, dest='expected_return',
                       help='预期年化收益率 (默认8%)')
    parser.add_argument('--json', action='store_true', help='输出JSON格式')
    parser.add_argument('--use-real-data', action='store_true', default=True,
                       help='使用真实数据')
    parser.add_argument('--use-mock-data', action='store_true',
                       help='使用模拟数据')
    
    args = parser.parse_args()
    
    use_real = args.use_real_data and not args.use_mock_data
    planner = SIPPlanner(use_real_data=use_real)
    
    result = planner.calculate_sip(
        target_amount=args.target,
        years=args.years,
        expected_return=args.expected_return
    )
    
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        plan = result['plan']
        print("\n" + "=" * 60)
        print(f"📊 定投计划 ({plan['data_source']})")
        print("=" * 60)
        print(f"计划ID: {plan['plan_id']}")
        print(f"目标金额: ¥{plan['target_amount']:,.0f}")
        print(f"投资年限: {plan['years']}年")
        print(f"每月定投: ¥{plan['monthly_amount']:,.0f}")
        print(f"预期年化收益: {plan['expected_return']:.1%}")
        print(f"预期终值: ¥{plan['projected_value']:,.0f}")
        print(f"预期收益: ¥{plan['projected_profit']:,.0f}")
        
        analysis = result['target_analysis']
        print(f"\n目标分析:")
        print(f"  达成时间: {analysis['years_to_target']:.1f}年")
        print(f"  资金压力: {analysis['pressure_emoji']} {analysis['pressure_level']} ({analysis['monthly_pressure_ratio']}%)")
        print(f"  可行性: {analysis['feasibility']}")
        
        print("\n建议:")
        for rec in result['recommendations']:
            print(f"  • {rec}")


if __name__ == '__main__':
    main()
