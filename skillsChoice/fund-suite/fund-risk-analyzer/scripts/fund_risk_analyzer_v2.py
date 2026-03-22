#!/usr/bin/env python3
"""
基金风险分析核心模块（真实数据版）
Fund Risk Analyzer Core Module - Real Data Edition

功能：风险指标计算、压力测试、VaR分析
数据源：AkShare / 同花顺iFinD
"""

import sys
sys.path.insert(0, '/root/.openclaw/workspace/finclaw/skills/fund-suite/fund-risk-analyzer/scripts')
sys.path.insert(0, '/root/.openclaw/workspace/finclaw/skills/fund-suite/data')

import json
import argparse
import math
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta

# 导入数据适配器
try:
    from fund_data_adapter import get_fund_adapter
    DATA_ADAPTER_AVAILABLE = True
except ImportError as e:
    DATA_ADAPTER_AVAILABLE = False


class RiskAnalyzer:
    """风险分析器（真实数据版）"""
    
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
    
    def analyze_risk(self, fund_code: str = None, returns: List[float] = None) -> Dict:
        """
        分析基金风险
        
        Args:
            fund_code: 基金代码（用于获取真实数据）
            returns: 收益率序列（模拟数据）
        
        Returns:
            风险分析报告
        """
        # 尝试获取真实净值数据
        if fund_code and self.data_adapter:
            real_returns = self._get_real_returns(fund_code)
            if real_returns:
                returns = real_returns
                print(f"✅ 使用真实净值数据 ({len(returns)} 个数据点)")
        
        if not returns or len(returns) < 2:
            return {'error': '收益率数据不足'}
        
        # 计算风险指标
        n = len(returns)
        mean_return = sum(returns) / n
        
        # 标准差（年化）
        variance = sum((r - mean_return) ** 2 for r in returns) / n
        std = math.sqrt(variance)
        annual_volatility = std * math.sqrt(252)  # 假设日数据，年化252天
        
        # 最大回撤
        max_drawdown = self._calculate_max_drawdown(returns)
        
        # VaR (历史模拟法)
        var_95 = self._calculate_var(returns, 0.95)
        var_99 = self._calculate_var(returns, 0.99)
        
        # 夏普比率（假设无风险利率2.5%）
        risk_free_rate = 0.025
        sharpe_ratio = (mean_return * 252 - risk_free_rate) / annual_volatility if annual_volatility > 0 else 0
        
        # 下行标准差
        downside_returns = [r for r in returns if r < 0]
        if downside_returns:
            downside_std = math.sqrt(sum(r ** 2 for r in downside_returns) / len(downside_returns)) * math.sqrt(252)
            sortino_ratio = (mean_return * 252 - risk_free_rate) / downside_std if downside_std > 0 else 0
        else:
            downside_std = 0
            sortino_ratio = float('inf')
        
        # 风险评级
        risk_level = self._assess_risk_level(annual_volatility, max_drawdown)
        
        return {
            'analysis_date': datetime.now().strftime('%Y-%m-%d'),
            'data_source': self.data_source,
            'fund_code': fund_code,
            'sample_size': n,
            'risk_metrics': {
                'mean_daily_return': round(mean_return, 6),
                'annual_volatility': round(annual_volatility, 4),
                'max_drawdown': round(max_drawdown, 4),
                'sharpe_ratio': round(sharpe_ratio, 3),
                'sortino_ratio': round(sortino_ratio, 3) if sortino_ratio != float('inf') else 'N/A',
                'var_95': round(var_95, 4),
                'var_99': round(var_99, 4)
            },
            'risk_level': risk_level,
            'interpretation': self._interpret_risk(annual_volatility, max_drawdown, sharpe_ratio),
            'recommendations': self._generate_risk_recommendations(risk_level)
        }
    
    def _get_real_returns(self, fund_code: str) -> Optional[List[float]]:
        """从真实数据获取收益率"""
        if not self.data_adapter:
            return None
        
        try:
            navs = self.data_adapter.get_fund_nav(fund_code, days=60)
            if navs and len(navs) >= 10:
                returns = [nav.daily_return for nav in navs if nav.daily_return is not None]
                return returns
        except Exception as e:
            print(f"获取真实收益失败: {e}")
        
        return None
    
    def _calculate_max_drawdown(self, returns: List[float]) -> float:
        """计算最大回撤"""
        # 计算累计收益
        cumulative = [1.0]
        for r in returns:
            cumulative.append(cumulative[-1] * (1 + r))
        
        # 计算回撤
        max_dd = 0
        peak = cumulative[0]
        
        for value in cumulative:
            if value > peak:
                peak = value
            dd = (peak - value) / peak
            if dd > max_dd:
                max_dd = dd
        
        return -max_dd  # 返回负值表示回撤
    
    def _calculate_var(self, returns: List[float], confidence: float) -> float:
        """计算VaR"""
        sorted_returns = sorted(returns)
        index = int(len(sorted_returns) * (1 - confidence))
        return sorted_returns[max(0, index)]
    
    def _assess_risk_level(self, volatility: float, max_drawdown: float) -> str:
        """评估风险等级"""
        # 综合波动率和最大回撤
        risk_score = volatility * 0.5 + abs(max_drawdown) * 0.5
        
        if risk_score <= 0.10:
            return 'R1-低风险'
        elif risk_score <= 0.15:
            return 'R2-中低风险'
        elif risk_score <= 0.25:
            return 'R3-中等风险'
        elif risk_score <= 0.35:
            return 'R4-中高风险'
        else:
            return 'R5-高风险'
    
    def _interpret_risk(self, volatility: float, max_drawdown: float, sharpe: float) -> Dict:
        """解读风险"""
        vol_desc = "低波动" if volatility <= 0.15 else "中等波动" if volatility <= 0.25 else "高波动"
        dd_desc = "回撤可控" if abs(max_drawdown) <= 0.15 else "回撤较大" if abs(max_drawdown) <= 0.25 else "回撤剧烈"
        sharpe_desc = "风险调整后收益优秀" if sharpe > 1.0 else "风险调整后收益良好" if sharpe > 0.5 else "风险调整后收益一般"
        
        return {
            'volatility_description': vol_desc,
            'drawdown_description': dd_desc,
            'sharpe_description': sharpe_desc,
            'summary': f"该基金{vol_desc}，{dd_desc}，{sharpe_desc}"
        }
    
    def _generate_risk_recommendations(self, risk_level: str) -> List[str]:
        """生成风险建议"""
        recommendations = []
        
        if 'R1' in risk_level or 'R2' in risk_level:
            recommendations.append("✅ 风险水平较低，适合保守型投资者")
        elif 'R3' in risk_level:
            recommendations.append("⚠️ 风险水平适中，建议控制仓位")
        else:
            recommendations.append("⚠️ 风险水平较高，建议谨慎配置")
            recommendations.append("建议设置止损线，控制最大损失")
        
        recommendations.append("建议定期回顾风险指标，动态调整配置")
        
        return recommendations


def main():
    parser = argparse.ArgumentParser(description='基金风险分析')
    parser.add_argument('--fund-code', help='基金代码')
    parser.add_argument('--json', action='store_true', help='输出JSON格式')
    parser.add_argument('--use-real-data', action='store_true', default=True,
                       help='使用真实数据')
    parser.add_argument('--use-mock-data', action='store_true',
                       help='使用模拟数据')
    
    args = parser.parse_args()
    
    use_real = args.use_real_data and not args.use_mock_data
    analyzer = RiskAnalyzer(use_real_data=use_real)
    
    # 模拟收益率数据
    mock_returns = [0.001, -0.002, 0.003, 0.001, -0.001, 0.002, 0.001, -0.003, 0.002, 0.001,
                    0.002, -0.001, 0.001, 0.003, -0.002, 0.001, 0.002, -0.001, 0.001, 0.002]
    
    result = analyzer.analyze_risk(args.fund_code, mock_returns)
    
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("\n" + "=" * 60)
        print(f"📊 基金风险分析报告 ({result.get('data_source', '模拟数据')})")
        print("=" * 60)
        
        if 'error' in result:
            print(f"错误: {result['error']}")
            return
        
        print(f"分析日期: {result['analysis_date']}")
        if result.get('fund_code'):
            print(f"基金代码: {result['fund_code']}")
        print(f"样本数量: {result['sample_size']}")
        
        metrics = result['risk_metrics']
        print(f"\n风险指标:")
        print(f"  年化波动率: {metrics['annual_volatility']:.1%}")
        print(f"  最大回撤: {metrics['max_drawdown']:.1%}")
        print(f"  夏普比率: {metrics['sharpe_ratio']:.2f}")
        print(f"  VaR (95%): {metrics['var_95']:.2%}")
        
        print(f"\n风险等级: {result['risk_level']}")
        
        interp = result['interpretation']
        print(f"\n解读: {interp['summary']}")
        
        print(f"\n建议:")
        for rec in result['recommendations']:
            print(f"  {rec}")


if __name__ == '__main__':
    main()
