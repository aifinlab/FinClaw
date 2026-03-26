#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
China Backtest Expert - 质量门禁主程序
中国金融市场策略回测质量审查与验证
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import argparse
import json
import numpy as np
import pandas as pd
import yaml


@dataclass
class CheckResult:
    """单项检查结果"""
    status: str  # passed, warning, failed, not_applicable
    score: float  # 0-100
    details: List[Dict]

    def to_dict(self):
        return asdict(self)


@dataclass
class QualityReport:
    """质量报告"""
    verdict: str  # PASS, REVISE, REJECT
    overall_score: float
    summary: Dict
    checks: Dict
    metrics: Dict
    recommendations: List[Dict]

    def to_dict(self):
        return {
            'verdict': self.verdict,
            'overall_score': self.overall_score,
            'summary': self.summary,
            'checks': {k: v.to_dict() if isinstance(v, CheckResult) else v
                      for k, v in self.checks.items()},
            'metrics': self.metrics,
            'recommendations': self.recommendations
        }


class ChinaBacktestExpert:
    """中国回测专家主类"""

    def __init__(self, config: Dict):
        self.config = config
        self.market_type = config.get('market', {}).get('type', 'ashare')
        self.strict_level = config.get('quality_checks', {}).get('strict_level', 'professional')
        self.check_results = {}

        # 根据严格程度设置阈值
        self.thresholds = self._get_thresholds()

    def _get_thresholds(self) -> Dict:
        """根据严格程度获取阈值"""
        levels = {
            'institution': {
                'min_sharpe': 1.2,
                'max_drawdown': 0.20,
                'max_overfit_prob': 0.3,
                'min_oos_sharpe': 0.8
            },
            'professional': {
                'min_sharpe': 1.0,
                'max_drawdown': 0.25,
                'max_overfit_prob': 0.5,
                'min_oos_sharpe': 0.6
            },
            'standard': {
                'min_sharpe': 0.8,
                'max_drawdown': 0.30,
                'max_overfit_prob': 0.7,
                'min_oos_sharpe': 0.4
            }
        }
        return levels.get(self.strict_level, levels['professional'])

    def check_data_quality(self, data: pd.DataFrame) -> CheckResult:
        """检查数据质量"""
        details = []
        score = 100

        # 检查缺失值
        missing_ratio = data.isnull().sum().sum() / (data.shape[0] * data.shape[1])
        if missing_ratio > 0.05:
            details.append({
                'item': '缺失值检查',
                'status': 'warning',
                'message': f'数据缺失率{mising_ratio:.2%}，建议检查数据源',
                'evidence': f'missing_ratio={missing_ratio:.4f}'
            })
            score -= 10
        else:
            details.append({
                'item': '缺失值检查',
                'status': 'passed',
                'message': f'数据缺失率{mising_ratio:.2%}，在可接受范围内',
                'evidence': f'missing_ratio={missing_ratio:.4f}'
            })

        # 检查时间连续性
        if 'date' in data.columns:
            dates = pd.to_datetime(data['date'])
            date_diff = dates.diff().dropna()
            expected_diff = pd.Timedelta(days=1)
            gaps = (date_diff > expected_diff * 5).sum()  # 超过5天的间隔

            if gaps > 0:
                details.append({
                    'item': '时间连续性',
                    'status': 'warning',
                    'message': f'发现{gaps}处时间间隔超过5天，可能存在停牌或数据缺失',
                    'evidence': f'gaps={gaps}'
                })
                score -= 5
            else:
                details.append({
                    'item': '时间连续性',
                    'status': 'passed',
                    'message': '时间序列连续，无明显缺失',
                    'evidence': 'no_gaps'
                })

        # 检查价格合理性
        if 'close' in data.columns:
            negative_prices = (data['close'] <= 0).sum()
            if negative_prices > 0:
                details.append({
                    'item': '价格合理性',
                    'status': 'failed',
                    'message': f'发现{negative_prices}条非正价格记录',
                    'evidence': f'negative_prices={negative_prices}'
                })
                score -= 20
            else:
                details.append({
                    'item': '价格合理性',
                    'status': 'passed',
                    'message': '所有价格记录均为正值',
                    'evidence': 'all_positive'
                })

        status = 'passed' if score >= 80 else 'warning' if score >= 60 else 'failed'
        return CheckResult(status=status, score=score, details=details)

    def check_look_ahead_bias(self, strategy_code: str, data: pd.DataFrame) -> CheckResult:
        """检查未来函数"""
        details = []
        score = 100

        # 检查常见的未来函数模式
        dangerous_patterns = [
            ('.shift(-', '使用未来数据（shift负数）'),
            ('rolling.*min_periods=0', '滚动窗口min_periods=0可能引入未来数据'),
            ('expanding', 'expanding操作可能使用未来统计量'),
        ]

        for pattern, desc in dangerous_patterns:
            if pattern in strategy_code:
                details.append({
                    'item': '代码模式检查',
                    'status': 'failed',
                    'message': f'检测到潜在未来函数: {desc}',
                    'evidence': f'pattern={pattern}'
                })
                score -= 30

        # 如果没有发现明显问题
        if not details:
            details.append({
                'item': '代码模式检查',
                'status': 'passed',
                'message': '未发现明显的未来函数模式',
                'evidence': 'no_dangerous_patterns'
            })

        status = 'passed' if score >= 80 else 'failed'
        return CheckResult(status=status, score=score, details=details)

    def check_market_regulation(self, trades: pd.DataFrame) -> CheckResult:
        """检查交易制度合规性"""
        details = []
        score = 100

        config = self.config.get('market', {}).get('ashare_config', {})

        # T+1检查
        if config.get('t1_constraint', True):
            # 简化检查：假设同一天买入又卖出即为违规
            # 实际实现需要更复杂的持仓追踪
            details.append({
                'item': 'T+1约束检查',
                'status': 'passed',
                'message': 'T+1约束已启用，策略逻辑需外部验证',
                'evidence': 't1_enabled'
            })

        # 涨跌停检查
        if config.get('price_limit', True) and 'close' in trades.columns:
            # 计算日涨跌幅
            if 'prev_close' in trades.columns:
                daily_return = (trades['close'] - trades['prev_close']) / trades['prev_close']
                limit_breach = (daily_return.abs() > 0.11).sum()  # 超过11%

                if limit_breach > 0:
                    details.append({
                        'item': '涨跌停检查',
                        'status': 'warning',
                        'message': f'发现{limit_breach}个交易日涨跌幅超过11%，可能未考虑涨跌停限制',
                        'evidence': f'limit_breach={limit_breach}'
                    })
                    score -= 10
                else:
                    details.append({
                        'item': '涨跌停检查',
                        'status': 'passed',
                        'message': '未发现明显涨跌停违规',
                        'evidence': 'no_limit_breach'
                    })

        status = 'passed' if score >= 80 else 'warning'
        return CheckResult(status=status, score=score, details=details)

    def check_overfitting(self, returns: pd.Series) -> CheckResult:
        """检查过拟合（简化版CSCV）"""
        details = []
        score = 100

        # 简化实现：检查IS/OOS表现差异
        # 实际CSCV需要更复杂的组合对称交叉验证

        n = len(returns)
        split_point = int(n * 0.7)  # 70%样本内

        is_returns = returns[:split_point]
        oos_returns = returns[split_point:]

        is_sharpe = is_returns.mean() / is_returns.std() * np.sqrt(252)
        oos_sharpe = oos_returns.mean() / oos_returns.std() * np.sqrt(252)

        sharpe_decay = (is_sharpe - oos_sharpe) / abs(is_sharpe) if is_sharpe != 0 else 0

        details.append({
            'item': '样本内夏普比率',
            'status': 'info',
            'message': f'样本内年化夏普: {is_sharpe:.2f}',
            'evidence': f'is_sharpe={is_sharpe:.4f}'
        })

        details.append({
            'item': '样本外夏普比率',
            'status': 'info',
            'message': f'样本外年化夏普: {oos_sharpe:.2f}',
            'evidence': f'oos_sharpe={oos_sharpe:.4f}'
        })

        if sharpe_decay > 0.5:
            details.append({
                'item': '夏普比率衰减',
                'status': 'failed',
                'message': f'样本外夏普较样本内衰减{sharpe_decay:.1%}，存在过拟合风险',
                'evidence': f'sharpe_decay={sharpe_decay:.4f}'
            })
            score -= 30
        elif sharpe_decay > 0.3:
            details.append({
                'item': '夏普比率衰减',
                'status': 'warning',
                'message': f'样本外夏普较样本内衰减{sharpe_decay:.1%}，需关注',
                'evidence': f'sharpe_decay={sharpe_decay:.4f}'
            })
            score -= 15
        else:
            details.append({
                'item': '夏普比率衰减',
                'status': 'passed',
                'message': f'夏普比率衰减{sharpe_decay:.1%}，在可接受范围内',
                'evidence': f'sharpe_decay={sharpe_decay:.4f}'
            })

        status = 'passed' if score >= 80 else 'warning' if score >= 60 else 'failed'
        return CheckResult(status=status, score=score, details=details)

    def calculate_metrics(self, returns: pd.Series, trades: pd.DataFrame = None) -> Dict:
        """计算关键指标"""
        metrics = {}

        # 收益指标
        metrics['returns'] = {
            'annual_return': returns.mean() * 252,
            'annual_volatility': returns.std() * np.sqrt(252),
            'sharpe_ratio': (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() > 0 else 0
        }

        # 风险指标
        cumulative = (1 + returns).cumprod()
        rolling_max = cumulative.expanding().max()
        drawdown = (cumulative - rolling_max) / rolling_max

        metrics['risk'] = {
            'max_drawdown': drawdown.min(),
            'max_drawdown_duration': self._get_max_drawdown_duration(drawdown)
        }

        # 交易指标
        if trades is not None and len(trades) > 0:
            metrics['trading'] = {
                'total_trades': len(trades),
                'win_rate': (trades.get('pnl', pd.Series()) > 0).mean(),
                'avg_holding_days': trades.get('holding_days', pd.Series()).mean()
            }

        return metrics

    def _get_max_drawdown_duration(self, drawdown: pd.Series) -> int:
        """计算最大回撤持续时间"""
        is_drawdown = drawdown < 0
        if not is_drawdown.any():
            return 0

        # 找到最长的连续回撤期
        durations = []
        current_duration = 0

        for in_dd in is_drawdown:
            if in_dd:
                current_duration += 1
            else:
                if current_duration > 0:
                    durations.append(current_duration)
                current_duration = 0

        if current_duration > 0:
            durations.append(current_duration)

        return max(durations) if durations else 0

    def determine_verdict(self, check_results: Dict, metrics: Dict) -> Tuple[str, float]:
        """确定最终判决"""
        scores = [r.score for r in check_results.values() if isinstance(r, CheckResult)]
        overall_score = np.mean(scores) if scores else 0

        # 检查关键失败项
        critical_failures = sum(1 for r in check_results.values()
                               if isinstance(r, CheckResult) and r.status == 'failed')

        sharpe = metrics.get('returns', {}).get('sharpe_ratio', 0)
        max_dd = metrics.get('risk', {}).get('max_drawdown', 0)

        # 判决逻辑
        if critical_failures >= 2 or sharpe < 0 or max_dd < -0.5:
            return 'REJECT', overall_score
        elif critical_failures == 1 or sharpe < self.thresholds['min_sharpe'] or overall_score < 70:
            return 'REVISE', overall_score
        else:
            return 'PASS', overall_score

    def generate_recommendations(self, check_results: Dict, metrics: Dict) -> List[Dict]:
        """生成修正建议"""
        recommendations = []

        for check_name, result in check_results.items():
            if isinstance(result, CheckResult) and result.status in ['warning', 'failed']:
                for detail in result.details:
                    if detail['status'] in ['warning', 'failed']:
                        recommendations.append({
                            'priority': 'high' if result.status == 'failed' else 'medium',
                            'category': check_name,
                            'issue': detail['item'],
                            'suggestion': detail['message'],
                            'expected_improvement': '根据具体修改内容评估'
                        })

        return recommendations

    def review(self, strategy_code: str = None, backtest_data: pd.DataFrame = None,
               returns: pd.Series = None, trades: pd.DataFrame = None) -> Dict:
        """主审查入口"""

        # 运行各项检查
        if backtest_data is not None:
            self.check_results['data_quality'] = self.check_data_quality(backtest_data)

        if strategy_code is not None and backtest_data is not None:
            self.check_results['look_ahead_bias'] = self.check_look_ahead_bias(strategy_code, backtest_data)

        if trades is not None:
            self.check_results['market_regulation'] = self.check_market_regulation(trades)

        if returns is not None:
            self.check_results['overfitting'] = self.check_overfitting(returns)
            metrics = self.calculate_metrics(returns, trades)
        else:
            metrics = {}

        # 确定判决
        verdict, overall_score = self.determine_verdict(self.check_results, metrics)

        # 生成建议
        recommendations = self.generate_recommendations(self.check_results, metrics)

        # 构建报告
        summary = {
            'strategy_name': 'Unknown',
            'market_type': self.market_type,
            'overall_score': overall_score,
            'key_findings': [f"{k}: {v.status}" for k, v in self.check_results.items()],
            'critical_issues': [r['issue'] for r in recommendations if r['priority'] == 'high']
        }

        report = QualityReport(
            verdict=verdict,
            overall_score=overall_score,
            summary=summary,
            checks=self.check_results,
            metrics=metrics,
            recommendations=recommendations
        )

        return report.to_dict()


def main():
    parser = argparse.ArgumentParser(description='China Backtest Expert - 策略质量门禁')
    parser.add_argument('--strategy-file', type=str, help='策略文件路径')
    parser.add_argument('--backtest-result', type=str, help='回测结果文件路径')
    parser.add_argument('--config', type=str, help='配置文件路径')
    parser.add_argument('--data-source', type=str, default='tushare',
                       choices=['tushare', 'akshare', 'joinquant', 'csv'])
    parser.add_argument('--start-date', type=str, help='开始日期 (YYYYMMDD)')
    parser.add_argument('--end-date', type=str, help='结束日期 (YYYYMMDD)')
    parser.add_argument('--market', type=str, default='ashare',
                       choices=['ashare', 'futures', 'fund'])
    parser.add_argument('--output-format', type=str, default='json',
                       choices=['json', 'yaml', 'text'])
    parser.add_argument('--report', type=str, help='输出报告路径')

    args = parser.parse_args()

    # 加载配置
    config = {
        'market': {'type': args.market, 'ashare_config': {'t1_constraint': True, 'price_limit': True}},
        'quality_checks': {'strict_level': 'professional', 'oos_ratio': 0.3}
    }

    if args.config and Path(args.config).exists():
        with open(args.config, 'r', encoding='utf-8') as f:
            config.update(yaml.safe_load(f))

    # 初始化专家
    expert = ChinaBacktestExpert(config)

    # 加载数据（简化版，实际需要更复杂的数据加载逻辑）
    strategy_code = ""
    if args.strategy_file and Path(args.strategy_file).exists():
        with open(args.strategy_file, 'r', encoding='utf-8') as f:
            strategy_code = f.read()

    backtest_data = None
    returns = None
    trades = None

    if args.backtest_result and Path(args.backtest_result).exists():
        # 支持CSV和Pickle格式
        if args.backtest_result.endswith('.csv'):
            backtest_data = pd.read_csv(args.backtest_result)
            if 'return' in backtest_data.columns:
                returns = pd.Series(backtest_data['return'].values)
        elif args.backtest_result.endswith('.pkl'):
            backtest_data = pd.read_pickle(args.backtest_result)

    # 运行审查
    result = expert.review(
        strategy_code=strategy_code,
        backtest_data=backtest_data,
        returns=returns,
        trades=trades
    )

    # 输出结果
    if args.output_format == 'json':
        output = json.dumps(result, ensure_ascii=False, indent=2)
    elif args.output_format == 'yaml':
        output = yaml.dump(result, allow_unicode=True, sort_keys=False)
    else:
        # 文本格式
        lines = [
            f"=== 中国回测专家质量报告 ===",
            f"判决: {result['verdict']}",
            f"综合评分: {result['overall_score']:.1f}/100",
            "",
            "检查项:",
        ]
        for check_name, check_result in result['checks'].items():
            lines.append(f"  {check_name}: {check_result['status']} (得分: {check_result['score']:.1f})")

        if result['recommendations']:
            lines.extend(["", "修正建议:"])
            for rec in result['recommendations']:
                lines.append(f"  [{rec['priority']}] {rec['category']} - {rec['issue']}")

        output = '\n'.join(lines)

    if args.report:
        with open(args.report, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"报告已保存至: {args.report}")
    else:
        print(output)


if __name__ == '__main__':
    main()
