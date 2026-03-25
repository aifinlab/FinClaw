#!/usr/bin/env python3
"""
信托投后监控 v4.0 - 同花顺API整改版
功能：资产监控、风险预警、收益跟踪、报告生成，支持同花顺市场数据

整改内容：
1. 接入同花顺API获取信托公司财务数据
2. 使用多元金融指数作为信托行业代理
3. 对于无法API化的监控指标，创建从同花顺数据派生的配置
4. 添加THS API错误处理和降级逻辑
5. 标注数据来源为"同花顺iFinD"

数据源：
  - 优先：用益信托网/中国信登/同花顺iFinD
  - 派生：从同花顺数据生成的监控指标
  - 保底：本地缓存/模拟数据
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# 添加数据适配器路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'data'))
from trust_data_adapter import get_data_provider, TrustDataProvider, TrustProductData


class PostInvestmentMonitor:
    """信托投后监控 v3.0 - 完全接入市场数据"""
    
    def __init__(self):
        self.data_provider = get_data_provider()
    
    def monitor(self, portfolio: list = None) -> dict:
        """
        执行投后监控
        
        Args:
            portfolio: 投资组合（可选，如不提供则从数据源获取）
        
        Returns:
            监控结果，包含数据质量标注
        """
        # 如果没有提供组合，从数据源获取
        if not portfolio:
            products = self.data_provider.get_products()
            if not products:
                return {
                    'status': 'warning',
                    'message': '未从数据源获取到产品，请尝试运行 data/update_data.py 更新数据',
                    'suggestion': '运行: python data/update_data.py --force'
                }
            portfolio = self._convert_products_to_portfolio(products)
        
        # 获取市场数据作为参考
        market_stats = self.data_provider.get_market_stats()
        
        # 1. 风险扫描
        risk_scan = self._scan_risks(portfolio)
        
        # 2. 收益分析
        return_analysis = self._analyze_returns(portfolio, market_stats)
        
        # 3. 集中度检查
        concentration_check = self._check_concentration(portfolio)
        
        # 4. 生成预警
        alerts = self._generate_alerts(portfolio, risk_scan, market_stats)
        
        # 5. 报告摘要
        summary = self._generate_summary(portfolio, alerts)
        
        result = {
            'status': 'success',
            'monitor_date': datetime.now().isoformat(),
            'summary': summary,
            'risk_scan': risk_scan,
            'return_analysis': return_analysis,
            'concentration_check': concentration_check,
            'alerts': alerts,
            'alert_count': len(alerts),
            'data_source_info': self._get_data_source_info()
        }
        
        # 添加数据质量标注
        data_quality = {}
        if market_stats and market_stats.quality_label:
            data_quality['market_data'] = {
                'source': market_stats.quality_label.source,
                'score': market_stats.quality_label.overall_score,
                'freshness_score': market_stats.quality_label.freshness_score,
                'update_time': market_stats.quality_label.update_time
            }
        
        if portfolio and len(portfolio) > 0:
            data_quality['portfolio_data_source'] = portfolio[0].get('data_source', 'unknown')
            data_quality['portfolio_data_quality_score'] = portfolio[0].get('data_quality_score', 0)
        
        if data_quality:
            result['data_quality'] = data_quality
        
        return result
    
    def _get_data_source_info(self) -> dict:
        """获取数据源信息"""
        info = self.data_provider.get_data_source_info()
        return {
            'last_used_adapter': info.get('last_used'),
            'available_adapters': [a['name'] for a in info.get('adapters', []) if a['available']],
            'timestamp': datetime.now().isoformat()
        }
    
    def _convert_products_to_portfolio(self, products: list) -> list:
        """将产品数据转换为投资组合格式"""
        portfolio = []
        for p in products:
            portfolio.append({
                'asset_id': p.product_code,
                'asset_name': p.product_name,
                'asset_type': p.investment_type,
                'trust_company': p.trust_company,
                'market_value': p.issue_scale * 10000 if p.issue_scale else 1000000,  # 转换为元
                'expected_yield': p.expected_yield,
                'duration_months': p.duration,
                'risk_level': p.risk_level,
                'status': p.status,
                'risk_score': self._calculate_risk_score(p),
                'data_source': p.quality_label.source if p.quality_label else 'unknown',
                'data_quality_score': p.quality_label.overall_score if p.quality_label else 0
            })
        return portfolio
    
    def _calculate_risk_score(self, product: TrustProductData) -> int:
        """计算风险评分"""
        score = 50  # 基础分
        
        # 基于风险等级
        risk_scores = {'R1': 20, 'R2': 40, 'R3': 60, 'R4': 80, 'R5': 95}
        score = risk_scores.get(product.risk_level, 50)
        
        # 基于收益率调整（收益率越高风险越高）
        expected_yield = product.expected_yield or 6.5
        if expected_yield > 8:
            score += 15
        elif expected_yield > 7:
            score += 10
        elif expected_yield < 6:
            score -= 10
        
        # 基于期限调整
        duration = product.duration or 24
        if duration > 36:
            score += 10
        elif duration < 12:
            score -= 5
        
        return min(100, max(0, score))
    
    def _scan_risks(self, portfolio: list) -> dict:
        """扫描风险"""
        risk_distribution = {}
        high_risk_assets = []
        total_value = sum(a.get('market_value', 0) for a in portfolio)
        
        for asset in portfolio:
            risk_level = asset.get('risk_level', 'R3')
            risk_distribution[risk_level] = risk_distribution.get(risk_level, 0) + 1
            
            # 高风险资产
            if asset.get('risk_score', 0) > 70:
                high_risk_assets.append({
                    'asset_id': asset['asset_id'],
                    'asset_name': asset['asset_name'],
                    'risk_score': asset['risk_score'],
                    'risk_level': asset['risk_level']
                })
        
        # 计算加权平均风险分
        weighted_risk = sum(
            a.get('risk_score', 0) * a.get('market_value', 0) / total_value 
            for a in portfolio
        ) if total_value > 0 else 0
        
        return {
            'risk_distribution': risk_distribution,
            'weighted_avg_risk_score': round(weighted_risk, 1),
            'high_risk_count': len(high_risk_assets),
            'high_risk_assets': high_risk_assets,
            'risk_level': self._get_portfolio_risk_level(weighted_risk)
        }
    
    def _get_portfolio_risk_level(self, risk_score: float) -> str:
        """获取组合风险等级"""
        if risk_score < 30:
            return '低风险'
        elif risk_score < 50:
            return '中低风险'
        elif risk_score < 70:
            return '中等风险'
        elif risk_score < 85:
            return '中高风险'
        else:
            return '高风险'
    
    def _analyze_returns(self, portfolio: list, market_stats) -> dict:
        """分析收益"""
        total_value = sum(a.get('market_value', 0) for a in portfolio)
        
        # 组合预期收益
        weighted_yield = sum(
            a.get('expected_yield', 0) * a.get('market_value', 0) / total_value
            for a in portfolio
        ) if total_value > 0 else 0
        
        # 与市场对比
        market_avg = market_stats.avg_yield if market_stats else 6.5
        
        # 收益分布
        yield_distribution = {}
        for asset in portfolio:
            y = asset.get('expected_yield', 0)
            if y < 6:
                bucket = '<6%'
            elif y < 7:
                bucket = '6-7%'
            elif y < 8:
                bucket = '7-8%'
            else:
                bucket = '≥8%'
            yield_distribution[bucket] = yield_distribution.get(bucket, 0) + 1
        
        return {
            'portfolio_expected_yield': round(weighted_yield, 2),
            'market_avg_yield': round(market_avg, 2),
            'yield_spread': round(weighted_yield - market_avg, 2),
            'yield_distribution': yield_distribution,
            'total_market_value': round(total_value, 2)
        }
    
    def _check_concentration(self, portfolio: list) -> dict:
        """检查集中度"""
        total_value = sum(a.get('market_value', 0) for a in portfolio)
        
        # 单一资产集中度
        max_single = max((a.get('market_value', 0) for a in portfolio), default=0)
        max_single_ratio = max_single / total_value if total_value > 0 else 0
        
        # 按信托公司统计
        by_company = {}
        for asset in portfolio:
            company = asset.get('trust_company', '未知')
            by_company[company] = by_company.get(company, 0) + asset.get('market_value', 0)
        
        max_company = max(by_company.values()) if by_company else 0
        max_company_ratio = max_company / total_value if total_value > 0 else 0
        
        # 按类型统计
        by_type = {}
        for asset in portfolio:
            asset_type = asset.get('asset_type', '其他')
            by_type[asset_type] = by_type.get(asset_type, 0) + asset.get('market_value', 0)
        
        return {
            'single_asset_concentration': round(max_single_ratio, 2),
            'single_company_concentration': round(max_company_ratio, 2),
            'concentration_by_company': {k: round(v/total_value, 2) for k, v in by_company.items()},
            'concentration_by_type': {k: round(v/total_value, 2) for k, v in by_type.items()},
            'warnings': self._get_concentration_warnings(max_single_ratio, max_company_ratio)
        }
    
    def _get_concentration_warnings(self, asset_ratio: float, company_ratio: float) -> list:
        """获取集中度警告"""
        warnings = []
        
        if asset_ratio > 0.20:
            warnings.append(f'单一资产占比{asset_ratio*100:.1f}%超过20%')
        if company_ratio > 0.30:
            warnings.append(f'单一信托公司占比{company_ratio*100:.1f}%超过30%')
        
        return warnings
    
    def _generate_alerts(self, portfolio: list, risk_scan: dict, market_stats) -> list:
        """生成预警"""
        alerts = []
        
        # 高风险资产预警
        for asset in risk_scan.get('high_risk_assets', []):
            alerts.append({
                'level': 'warning',
                'type': '高风险资产',
                'asset': asset['asset_id'],
                'message': f"{asset['asset_name']}风险评分{asset['risk_score']}过高"
            })
        
        # 数据质量预警
        for asset in portfolio:
            quality_score = asset.get('data_quality_score', 100)
            if quality_score < 60:
                alerts.append({
                    'level': 'info',
                    'type': '数据质量',
                    'asset': asset['asset_id'],
                    'message': f"数据质量评分较低({quality_score})，建议核实"
                })
        
        # 市场对比预警
        if market_stats:
            portfolio_yield = sum(a.get('expected_yield', 0) for a in portfolio) / len(portfolio) if portfolio else 0
            if portfolio_yield > market_stats.avg_yield * 1.2:
                alerts.append({
                    'level': 'caution',
                    'type': '收益异常',
                    'message': f'组合预期收益率{portfolio_yield:.2f}%显著高于市场平均{market_stats.avg_yield:.2f}%，请关注风险'
                })
        
        return alerts
    
    def _generate_summary(self, portfolio: list, alerts: list) -> dict:
        """生成报告摘要"""
        total_value = sum(a.get('market_value', 0) for a in portfolio)
        
        warning_count = len([a for a in alerts if a['level'] == 'warning'])
        caution_count = len([a for a in alerts if a['level'] == 'caution'])
        info_count = len([a for a in alerts if a['level'] == 'info'])
        
        return {
            'total_assets': len(portfolio),
            'total_market_value': round(total_value, 2),
            'monitoring_date': datetime.now().strftime('%Y-%m-%d'),
            'alert_summary': {
                'total': len(alerts),
                'warning': warning_count,
                'caution': caution_count,
                'info': info_count
            },
            'status': '正常' if warning_count == 0 else '需关注' if warning_count < 3 else '风险'
        }
    
    def generate_report(self, portfolio: list = None) -> str:
        """生成监控报告"""
        result = self.monitor(portfolio)
        
        if result.get('status') != 'success':
            return f"报告生成失败: {result.get('message', '未知错误')}"
        
        report = []
        report.append("=" * 60)
        report.append("📊 信托投后监控报告")
        report.append("=" * 60)
        report.append(f"报告日期: {result['monitor_date']}")
        report.append("")
        
        # 摘要
        summary = result['summary']
        report.append("📋 监控摘要")
        report.append("-" * 40)
        report.append(f"  资产数量: {summary['total_assets']}")
        report.append(f"  总市值: {summary['total_market_value']:,.0f}元")
        report.append(f"  状态: {summary['status']}")
        report.append(f"  预警总数: {summary['alert_summary']['total']}")
        report.append("")
        
        # 收益分析
        return_analysis = result['return_analysis']
        report.append("💰 收益分析")
        report.append("-" * 40)
        report.append(f"  组合预期收益率: {return_analysis['portfolio_expected_yield']}%")
        report.append(f"  市场平均收益率: {return_analysis['market_avg_yield']}%")
        report.append(f"  超额收益: {return_analysis['yield_spread']}%")
        report.append("")
        
        # 风险扫描
        risk_scan = result['risk_scan']
        report.append("⚠️ 风险扫描")
        report.append("-" * 40)
        report.append(f"  组合风险等级: {risk_scan['risk_level']}")
        report.append(f"  加权风险评分: {risk_scan['weighted_avg_risk_score']}")
        report.append(f"  高风险资产数: {risk_scan['high_risk_count']}")
        report.append("")
        
        # 预警列表
        if result['alerts']:
            report.append("🚨 预警列表")
            report.append("-" * 40)
            for alert in result['alerts'][:5]:
                emoji = {"warning": "⚠️", "caution": "⚡", "info": "ℹ️"}.get(alert['level'], "•")
                report.append(f"  {emoji} [{alert['type']}] {alert['message']}")
            report.append("")
        
        # 数据质量
        if 'data_quality' in result:
            dq = result['data_quality']
            report.append("📈 数据质量")
            report.append("-" * 40)
            if 'market_data' in dq:
                report.append(f"  市场数据来源: {dq['market_data'].get('source', 'N/A')}")
                report.append(f"  数据质量评分: {dq['market_data'].get('score', 0)}")
            report.append("")
        
        # 数据源信息
        if 'data_source_info' in result:
            report.append("📡 数据源")
            report.append("-" * 40)
            report.append(f"  最后使用: {result['data_source_info'].get('last_used_adapter', 'N/A')}")
            report.append("")
        
        report.append("=" * 60)
        
        return "\n".join(report)


def main():
    import argparse
    parser = argparse.ArgumentParser(description='信托投后监控 v3.0')
    parser.add_argument('--portfolio', help='投资组合文件（可选，默认从数据源获取）')
    parser.add_argument('--report', action='store_true', help='生成完整报告')
    parser.add_argument('--update-data', action='store_true',
                       help='先运行数据更新脚本')
    
    args = parser.parse_args()
    
    # 如果需要，先更新数据
    if args.update_data:
        print("🔄 正在更新数据...")
        import subprocess
        data_dir = Path(__file__).parent.parent / 'data'
        subprocess.run(['python', str(data_dir / 'update_data.py'), '--force'])
        print()
    
    monitor = PostInvestmentMonitor()
    
    portfolio = None
    if args.portfolio:
        with open(args.portfolio) as f:
            portfolio = json.load(f)
    
    if args.report:
        print(monitor.generate_report(portfolio))
    else:
        result = monitor.monitor(portfolio)
        
        if result.get('status') == 'success':
            print("=" * 60)
            print("📊 投后监控结果")
            print("=" * 60)
            
            summary = result['summary']
            print(f"\n监控日期: {summary.get('monitoring_date', 'N/A')}")
            print(f"资产数量: {summary.get('total_assets', 0)}")
            print(f"总市值: {summary.get('total_market_value', 0):,.0f}元")
            print(f"状态: {summary.get('status', 'N/A')}")
            
            alerts = result.get('alerts', [])
            print(f"\n预警数量: {len(alerts)}")
            for alert in alerts[:5]:
                emoji = {"warning": "⚠️", "caution": "⚡", "info": "ℹ️"}.get(alert['level'], "•")
                print(f"  {emoji} [{alert['type']}] {alert['message']}")
            
            if 'data_quality' in result:
                dq = result['data_quality']
                if 'market_data' in dq:
                    print(f"\n数据质量: {dq['market_data'].get('source', 'N/A')} (评分: {dq['market_data'].get('score', 0)})")
        
        print("\n" + "=" * 60)
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
