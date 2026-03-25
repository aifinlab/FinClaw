#!/usr/bin/env python3
"""
基金风险分析器核心模块 - AkShare版
Fund Risk Analyzer Core Module - AkShare Edition

功能：VaR/CVaR、风险指标、回撤分析、Beta/Alpha
数据：通过AkShare接入实时基金数据
"""

import sys
import os
sys.path.insert(0, '/root/.openclaw/workspace/skillsChoice/fund-suite/fund-risk-analyzer/scripts')

import json
import argparse
import math
import random
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta

# 尝试导入科学计算库
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    print("警告：numpy未安装，使用基础数学计算")

# scipy可选，用于高级统计功能
try:
    from scipy import stats
    HAS_SCIPY = True
except (ImportError, ValueError):
    HAS_SCIPY = False

# 导入AkShare
try:
    import akshare as ak
    AKSHARE_AVAILABLE = True
except ImportError:
    AKSHARE_AVAILABLE = False
    print("警告：AkShare未安装，将使用模拟数据")


@dataclass
class RiskMetrics:
    """风险指标数据类"""
    # 基础收益指标
    annual_return: float = 0.0
    volatility: float = 0.0
    
    # 风险调整收益
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    treynor_ratio: float = 0.0
    calmar_ratio: float = 0.0
    
    # 市场风险
    beta: float = 0.0
    alpha: float = 0.0
    r_squared: float = 0.0
    
    # 极端风险
    var_95: float = 0.0
    var_99: float = 0.0
    cvar_95: float = 0.0
    cvar_99: float = 0.0
    
    # 回撤指标
    max_drawdown: float = 0.0
    max_drawdown_duration: int = 0
    avg_drawdown: float = 0.0
    
    # 尾部风险
    skewness: float = 0.0
    kurtosis: float = 0.0
    
    # 波动率分解
    upside_vol: float = 0.0
    downside_vol: float = 0.0
    systematic_vol: float = 0.0
    unsystematic_vol: float = 0.0
    
    # 数据标注
    data_source: str = ""
    data_quality: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)


class FundRiskAnalyzer:
    """基金风险分析器主类 - AkShare数据源"""
    
    # 无风险利率（年化）
    RISK_FREE_RATE = 0.025
    
    def __init__(self):
        self.fund_returns_cache = {}
        self.market_returns_cache = []
        self.fund_info = {}
        self._data_source = ""
        self._data_quality = ""
        self._akshare_available = AKSHARE_AVAILABLE
        
        # 检查数据源可用性
        if not self._akshare_available:
            self._load_default_data()
    
    def _fetch_fund_data_from_akshare(self, fund_code: str, period: int = 252) -> Tuple[List[float], Dict]:
        """
        从AkShare获取基金历史净值数据
        
        Args:
            fund_code: 基金代码
            period: 获取的历史数据天数
            
        Returns:
            (收益率列表, 基金信息字典)
        """
        try:
            # 使用akshare获取基金历史净值
            # fund_open_fund_info_em 获取基金净值信息
            df = ak.fund_open_fund_info_em(symbol=fund_code)
            
            if df.empty:
                return [], {}
            
            # 只取最近period条数据
            df = df.head(period)
            
            # 计算日收益率
            returns = []
            nav_list = []
            dates = []
            
            for _, row in df.iterrows():
                nav = row.get('单位净值', 0)
                date = row.get('净值日期', '')
                
                if nav and nav > 0:
                    nav_list.append(float(nav))
                    dates.append(date)
            
            # 从后往前计算收益率（时间顺序）
            nav_list.reverse()
            dates.reverse()
            
            for i in range(1, len(nav_list)):
                daily_return = (nav_list[i] - nav_list[i-1]) / nav_list[i-1]
                returns.append(daily_return)
            
            # 获取基金基本信息
            fund_name = ""
            try:
                fund_list = ak.fund_name_em()
                fund_match = fund_list[fund_list['基金代码'] == fund_code]
                if not fund_match.empty:
                    fund_name = fund_match.iloc[0].get('基金简称', '')
            except:
                pass
            
            fund_info = {
                'name': fund_name or fund_code,
                'type': self._detect_fund_type(fund_name),
                'nav_latest': nav_list[-1] if nav_list else 0,
                'date_start': dates[0] if dates else '',
                'date_end': dates[-1] if dates else ''
            }
            
            return returns, fund_info
            
        except Exception as e:
            print(f"⚠️ 从AkShare获取基金{fund_code}数据失败: {e}")
            return [], {}
    
    def _fetch_market_benchmark(self, period: int = 252) -> List[float]:
        """
        获取市场基准数据（使用沪深300指数）
        
        Args:
            period: 获取的历史数据天数
            
        Returns:
            市场收益率列表
        """
        try:
            # 获取沪深300指数历史数据
            # 使用 ak.index_zh_a_hist 获取指数历史行情
            from datetime import datetime, timedelta
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period * 1.5)  # 多取一些数据确保有足够交易日
            
            df = ak.index_zh_a_hist(
                symbol="000300",  # 沪深300
                period="daily",
                start_date=start_date.strftime("%Y%m%d"),
                end_date=end_date.strftime("%Y%m%d")
            )
            
            if df.empty:
                return self._generate_market_returns(period)
            
            # 计算日收益率
            returns = []
            closes = df['收盘'].tolist()
            closes.reverse()  # 时间顺序
            
            for i in range(1, len(closes)):
                daily_return = (closes[i] - closes[i-1]) / closes[i-1]
                returns.append(daily_return)
            
            # 如果数据不够，补充模拟数据
            while len(returns) < period:
                returns.insert(0, random.gauss(0.0005, 0.015))
            
            return returns[-period:]
            
        except Exception as e:
            print(f"⚠️ 获取市场基准数据失败: {e}")
            return self._generate_market_returns(period)
    
    def _generate_market_returns(self, n: int) -> List[float]:
        """生成模拟市场收益率序列（降级方案）"""
        if HAS_NUMPY:
            np.random.seed(42)
            returns = np.random.normal(0.0005, 0.015, n)
            return returns.tolist()
        else:
            random.seed(42)
            return [random.gauss(0.0005, 0.015) for _ in range(n)]
    
    def _detect_fund_type(self, fund_name: str) -> str:
        """根据基金名称识别类型"""
        if not fund_name:
            return "未知"
        name = fund_name.upper()
        if '货币' in name or '现金' in name:
            return '货币型'
        elif '债券' in name or '纯债' in name or '短债' in name:
            return '债券型'
        elif '指数' in name or 'ETF' in name:
            return '指数型'
        elif '混合' in name or '灵活' in name:
            return '混合型'
        elif '股票' in name:
            return '股票型'
        elif 'FOF' in name:
            return 'FOF'
        elif 'QDII' in name:
            return 'QDII'
        return '混合型'
    
    def _load_default_data(self):
        """加载默认模拟数据（降级方案）"""
        np.random.seed(42) if HAS_NUMPY else random.seed(42)
        
        # 默认基金数据
        default_funds = {
            '000001': {'mean': 0.0008, 'std': 0.018, 'name': '华夏成长混合', 'type': '混合型'},
            '000002': {'mean': 0.0007, 'std': 0.015, 'name': '易方达蓝筹精选', 'type': '混合型'},
            '000003': {'mean': 0.0009, 'std': 0.022, 'name': '中欧时代先锋', 'type': '股票型'},
            '000004': {'mean': 0.0010, 'std': 0.017, 'name': '富国天惠成长', 'type': '混合型'},
            '000005': {'mean': 0.0006, 'std': 0.025, 'name': '景顺长城新兴', 'type': '股票型'},
        }
        
        for code, config in default_funds.items():
            self.fund_returns_cache[code] = self._generate_returns(
                config['mean'], config['std'], 252
            )
            self.fund_info[code] = {'name': config['name'], 'type': config['type']}
        
        # 默认市场数据
        self.market_returns_cache = self._generate_returns(0.0005, 0.015, 252)
        
        self._data_source = "内置默认模拟数据(AkShare不可用)"
        self._data_quality = "sample"
    
    def _generate_returns(self, mean: float, std: float, n: int) -> List[float]:
        """生成模拟收益率序列"""
        if HAS_NUMPY:
            returns = np.random.normal(mean, std, n)
            return returns.tolist()
        else:
            return [random.gauss(mean, std) for _ in range(n)]
    
    def _ensure_fund_data(self, fund_code: str, period: int = 252) -> bool:
        """
        确保基金数据已加载（优先从AkShare获取）
        
        Returns:
            True: 成功获取真实数据
            False: 使用默认数据
        """
        if fund_code in self.fund_returns_cache and len(self.fund_returns_cache[fund_code]) >= period:
            return True
        
        if self._akshare_available:
            returns, fund_info = self._fetch_fund_data_from_akshare(fund_code, period)
            
            if returns and len(returns) >= 30:  # 至少需要30天数据
                self.fund_returns_cache[fund_code] = returns
                self.fund_info[fund_code] = fund_info
                self._data_source = f"AkShare实时数据 - 基金{fund_code}"
                self._data_quality = "real-time"
                return True
            else:
                print(f"⚠️ 基金{fund_code}从AkShare获取的数据不足，使用默认模拟数据")
        
        # 降级到默认数据
        if fund_code not in self.fund_returns_cache:
            self._load_default_data()
            # 如果没有该基金的默认数据，生成一个
            if fund_code not in self.fund_returns_cache:
                self.fund_returns_cache[fund_code] = self._generate_returns(0.0005, 0.018, period)
                self.fund_info[fund_code] = {'name': fund_code, 'type': '未知'}
                self._data_source = "内置默认模拟数据(基金不存在于默认数据集)"
                self._data_quality = "sample"
        
        return False
    
    def analyze(self, fund_code: str, period: int = 252) -> Dict:
        """
        全面风险分析
        
        Args:
            fund_code: 基金代码
            period: 分析周期（交易日数）
        
        Returns:
            风险分析报告
        """
        # 确保数据已加载
        is_real_data = self._ensure_fund_data(fund_code, period)
        
        if fund_code not in self.fund_returns_cache:
            return {
                'error': f'未找到基金: {fund_code}',
                'data_source': self._data_source,
                'data_quality': self._data_quality
            }
        
        returns = self.fund_returns_cache[fund_code][-period:]
        
        # 获取市场基准数据
        if not self.market_returns_cache or len(self.market_returns_cache) < period:
            if self._akshare_available:
                self.market_returns_cache = self._fetch_market_benchmark(period)
            else:
                self.market_returns_cache = self._generate_market_returns(period)
        
        market_returns = self.market_returns_cache[-period:]
        
        metrics = RiskMetrics()
        metrics.data_source = self._data_source
        metrics.data_quality = self._data_quality
        
        # 基础收益指标
        metrics.annual_return = self._calculate_annual_return(returns)
        metrics.volatility = self._calculate_volatility(returns) * 100
        
        # 风险调整收益
        metrics.sharpe_ratio = self._calculate_sharpe_ratio(returns)
        metrics.sortino_ratio = self._calculate_sortino_ratio(returns)
        
        # 市场风险
        beta, alpha, r2 = self._calculate_beta_alpha(returns, market_returns)
        metrics.beta = beta
        metrics.alpha = alpha * 100
        metrics.r_squared = r2
        
        metrics.treynor_ratio = self._calculate_treynor_ratio(returns, beta)
        
        # 极端风险
        var_95, var_99 = self._calculate_var(returns)
        metrics.var_95 = var_95 * 100
        metrics.var_99 = var_99 * 100
        
        cvar_95, cvar_99 = self._calculate_cvar(returns)
        metrics.cvar_95 = cvar_95 * 100
        metrics.cvar_99 = cvar_99 * 100
        
        # 回撤指标
        max_dd, dd_duration, avg_dd = self._calculate_drawdown(returns)
        metrics.max_drawdown = max_dd * 100
        metrics.max_drawdown_duration = dd_duration
        metrics.avg_drawdown = avg_dd * 100
        
        metrics.calmar_ratio = metrics.annual_return / abs(metrics.max_drawdown) if metrics.max_drawdown != 0 else 0
        
        # 尾部风险
        metrics.skewness = self._calculate_skewness(returns)
        metrics.kurtosis = self._calculate_kurtosis(returns)
        
        # 波动率分解
        metrics.upside_vol = self._calculate_upside_volatility(returns) * 100
        metrics.downside_vol = self._calculate_downside_volatility(returns) * 100
        metrics.systematic_vol = metrics.volatility * metrics.beta
        metrics.unsystematic_vol = metrics.volatility * math.sqrt(1 - r2) if r2 <= 1 else 0
        
        # 风险评估
        risk_level, risk_score = self._assess_risk(metrics)
        
        # 构建报告
        report = {
            'fund_code': fund_code,
            'fund_name': self.fund_info.get(fund_code, {}).get('name', fund_code),
            'analysis_date': datetime.now().strftime('%Y-%m-%d'),
            'period_days': period,
            'data_source': self._data_source,
            'data_quality': self._data_quality,
            'is_real_data': is_real_data,
            'risk_metrics': metrics.to_dict(),
            'risk_assessment': {
                'overall_risk_level': risk_level,
                'risk_score': risk_score,
                'confidence': '中等' if is_real_data else '低(使用模拟数据)'
            },
            'risk_alerts': self._generate_risk_alerts(metrics)
        }
        
        return report
    
    def calculate_var(self, fund_code: str, confidence: float = 0.95, 
                     method: str = 'historical') -> Dict:
        """
        计算VaR
        
        Args:
            fund_code: 基金代码
            confidence: 置信度（0.95或0.99）
            method: 计算方法（historical/parametric/monte_carlo）
        
        Returns:
            VaR计算结果
        """
        self._ensure_fund_data(fund_code)
        
        if fund_code not in self.fund_returns_cache:
            return {
                'error': f'未找到基金: {fund_code}',
                'data_source': self._data_source,
                'data_quality': self._data_quality
            }
        
        returns = self.fund_returns_cache[fund_code]
        
        if method == 'historical':
            var = self._var_historical(returns, confidence)
        elif method == 'parametric':
            var = self._var_parametric(returns, confidence)
        elif method == 'monte_carlo':
            var = self._var_monte_carlo(returns, confidence)
        else:
            return {'error': f'不支持的VaR计算方法: {method}'}
        
        return {
            'fund_code': fund_code,
            'fund_name': self.fund_info.get(fund_code, {}).get('name', fund_code),
            'var_method': method,
            'confidence': f'{confidence*100:.0f}%',
            'daily_var': f'{var*100:.2f}%',
            'monthly_var': f'{var*math.sqrt(21)*100:.2f}%',
            'annual_var': f'{var*math.sqrt(252)*100:.2f}%',
            'data_source': self._data_source,
            'data_quality': self._data_quality
        }
    
    def compare_risk(self, fund_codes: List[str]) -> Dict:
        """对比多只基金的风险指标"""
        comparison = {
            'funds': [],
            'rankings': {},
            'data_source': self._data_source,
            'data_quality': self._data_quality
        }
        
        for code in fund_codes:
            report = self.analyze(code)
            if 'error' not in report:
                comparison['funds'].append(report)
        
        # 计算各指标排名
        if comparison['funds']:
            metrics_to_rank = ['sharpe_ratio', 'sortino_ratio', 'calmar_ratio']
            for metric in metrics_to_rank:
                sorted_funds = sorted(comparison['funds'], 
                                    key=lambda x: x['risk_metrics'][metric], 
                                    reverse=True)
                comparison['rankings'][metric] = [
                    {'rank': i+1, 'fund_code': f['fund_code'], 'value': f['risk_metrics'][metric]}
                    for i, f in enumerate(sorted_funds)
                ]
        
        return comparison
    
    def check_risk_alerts(self, fund_code: str) -> List[Dict]:
        """检查风险预警"""
        report = self.analyze(fund_code)
        if 'error' in report:
            return [{
                'error': report['error'],
                'data_source': self._data_source,
                'data_quality': self._data_quality
            }]
        
        return report.get('risk_alerts', [])
    
    # ============ 计算方法 ============
    
    def _calculate_annual_return(self, returns: List[float]) -> float:
        """计算年化收益率"""
        if not returns:
            return 0.0
        avg_return = sum(returns) / len(returns)
        return (1 + avg_return) ** 252 - 1
    
    def _calculate_volatility(self, returns: List[float]) -> float:
        """计算年化波动率"""
        if len(returns) < 2:
            return 0.0
        
        if HAS_NUMPY:
            return np.std(returns, ddof=1) * math.sqrt(252)
        else:
            mean = sum(returns) / len(returns)
            variance = sum((r - mean) ** 2 for r in returns) / (len(returns) - 1)
            return math.sqrt(variance) * math.sqrt(252)
    
    def _calculate_sharpe_ratio(self, returns: List[float]) -> float:
        """计算夏普比率"""
        annual_return = self._calculate_annual_return(returns)
        volatility = self._calculate_volatility(returns)
        
        if volatility == 0:
            return 0.0
        return (annual_return - self.RISK_FREE_RATE) / volatility
    
    def _calculate_sortino_ratio(self, returns: List[float]) -> float:
        """计算索提诺比率（只考虑下行波动）"""
        annual_return = self._calculate_annual_return(returns)
        downside_returns = [r for r in returns if r < 0]
        
        if not downside_returns:
            return float('inf') if annual_return > self.RISK_FREE_RATE else 0.0
        
        downside_vol = self._calculate_downside_volatility(returns)
        if downside_vol == 0:
            return 0.0
        
        return (annual_return - self.RISK_FREE_RATE) / downside_vol
    
    def _calculate_beta_alpha(self, returns: List[float], market_returns: List[float]) -> Tuple[float, float, float]:
        """计算Beta和Alpha"""
        if len(returns) != len(market_returns) or len(returns) < 2:
            return 1.0, 0.0, 0.0
        
        if HAS_NUMPY:
            covariance = np.cov(returns, market_returns)[0][1]
            market_var = np.var(market_returns, ddof=1)
        else:
            mean_r = sum(returns) / len(returns)
            mean_m = sum(market_returns) / len(market_returns)
            covariance = sum((r - mean_r) * (m - mean_m) for r, m in zip(returns, market_returns)) / (len(returns) - 1)
            market_var = sum((m - mean_m) ** 2 for m in market_returns) / (len(market_returns) - 1)
        
        beta = covariance / market_var if market_var != 0 else 1.0
        
        # Alpha = 实际收益 - (无风险收益 + Beta * (市场收益 - 无风险收益))
        fund_return = sum(returns) / len(returns)
        market_return = sum(market_returns) / len(market_returns)
        alpha = fund_return - (self.RISK_FREE_RATE/252 + beta * (market_return - self.RISK_FREE_RATE/252))
        
        # R² = Cov² / (Var_fund * Var_market)
        if HAS_NUMPY:
            fund_var = np.var(returns, ddof=1)
            r_squared = (covariance ** 2) / (fund_var * market_var) if fund_var * market_var != 0 else 0.0
        else:
            fund_var = sum((r - mean_r) ** 2 for r in returns) / (len(returns) - 1)
            r_squared = (covariance ** 2) / (fund_var * market_var) if fund_var * market_var != 0 else 0.0
        
        return beta, alpha, min(r_squared, 1.0)
    
    def _calculate_treynor_ratio(self, returns: List[float], beta: float) -> float:
        """计算特雷诺比率"""
        if beta == 0:
            return 0.0
        annual_return = self._calculate_annual_return(returns)
        return (annual_return - self.RISK_FREE_RATE) / beta
    
    def _calculate_var(self, returns: List[float]) -> Tuple[float, float]:
        """计算VaR（95%和99%置信度）"""
        var_95 = self._var_historical(returns, 0.95)
        var_99 = self._var_historical(returns, 0.99)
        return var_95, var_99
    
    def _var_historical(self, returns: List[float], confidence: float) -> float:
        """历史模拟法VaR"""
        if not returns:
            return 0.0
        sorted_returns = sorted(returns)
        index = int(len(sorted_returns) * (1 - confidence))
        return sorted_returns[max(0, index)]
    
    def _var_parametric(self, returns: List[float], confidence: float) -> float:
        """参数法VaR"""
        if not returns:
            return 0.0
        
        mean = sum(returns) / len(returns)
        
        if HAS_NUMPY:
            std = np.std(returns, ddof=1)
            z_score = stats.norm.ppf(1 - confidence) if HAS_SCIPY else -1.645
        else:
            variance = sum((r - mean) ** 2 for r in returns) / (len(returns) - 1)
            std = math.sqrt(variance)
            z_score = -1.645 if confidence == 0.95 else (-2.326 if confidence == 0.99 else -1.645)
        
        return mean + z_score * std
    
    def _var_monte_carlo(self, returns: List[float], confidence: float, simulations: int = 10000) -> float:
        """蒙特卡洛模拟VaR"""
        if not returns:
            return 0.0
        
        mean = sum(returns) / len(returns)
        if HAS_NUMPY:
            std = np.std(returns, ddof=1)
            simulated_returns = np.random.normal(mean, std, simulations)
            return np.percentile(simulated_returns, (1 - confidence) * 100)
        else:
            variance = sum((r - mean) ** 2 for r in returns) / (len(returns) - 1)
            std = math.sqrt(variance)
            simulated_returns = [random.gauss(mean, std) for _ in range(simulations)]
            sorted_sim = sorted(simulated_returns)
            index = int(len(sorted_sim) * (1 - confidence))
            return sorted_sim[max(0, index)]
    
    def _calculate_cvar(self, returns: List[float]) -> Tuple[float, float]:
        """计算CVaR（条件VaR）"""
        var_95 = self._var_historical(returns, 0.95)
        var_99 = self._var_historical(returns, 0.99)
        
        # CVaR是超过VaR的平均损失
        losses_95 = [r for r in returns if r <= var_95]
        losses_99 = [r for r in returns if r <= var_99]
        
        cvar_95 = sum(losses_95) / len(losses_95) if losses_95 else var_95
        cvar_99 = sum(losses_99) / len(losses_99) if losses_99 else var_99
        
        return cvar_95, cvar_99
    
    def _calculate_drawdown(self, returns: List[float]) -> Tuple[float, int, float]:
        """计算回撤指标"""
        if not returns:
            return 0.0, 0, 0.0
        
        # 计算净值序列
        nav = [1.0]
        for r in returns:
            nav.append(nav[-1] * (1 + r))
        
        # 计算回撤
        max_dd = 0.0
        max_dd_duration = 0
        current_dd_start = 0
        peak = nav[0]
        
        drawdowns = []
        
        for i, n in enumerate(nav):
            if n > peak:
                peak = n
                current_dd_start = i
            
            dd = (peak - n) / peak
            drawdowns.append(dd)
            
            if dd > max_dd:
                max_dd = dd
                max_dd_duration = i - current_dd_start
        
        avg_dd = sum(drawdowns) / len(drawdowns) if drawdowns else 0.0
        
        return max_dd, max_dd_duration, avg_dd
    
    def _calculate_skewness(self, returns: List[float]) -> float:
        """计算偏度"""
        if len(returns) < 3:
            return 0.0
        
        mean = sum(returns) / len(returns)
        
        if HAS_NUMPY and HAS_SCIPY:
            return float(stats.skew(returns))
        else:
            # 手动计算偏度
            variance = sum((r - mean) ** 2 for r in returns) / len(returns)
            std = math.sqrt(variance) if variance > 0 else 1.0
            skew = sum(((r - mean) / std) ** 3 for r in returns) / len(returns)
            return skew
    
    def _calculate_kurtosis(self, returns: List[float]) -> float:
        """计算峰度"""
        if len(returns) < 4:
            return 3.0
        
        if HAS_NUMPY and HAS_SCIPY:
            return float(stats.kurtosis(returns, fisher=False))
        else:
            mean = sum(returns) / len(returns)
            variance = sum((r - mean) ** 2 for r in returns) / len(returns)
            std = math.sqrt(variance) if variance > 0 else 1.0
            kurt = sum(((r - mean) / std) ** 4 for r in returns) / len(returns)
            return kurt
    
    def _calculate_upside_volatility(self, returns: List[float]) -> float:
        """计算上行波动率"""
        upside_returns = [r for r in returns if r > 0]
        if not upside_returns:
            return 0.0
        
        if HAS_NUMPY:
            return np.std(upside_returns, ddof=1) * math.sqrt(252)
        else:
            mean = sum(upside_returns) / len(upside_returns)
            variance = sum((r - mean) ** 2 for r in upside_returns) / (len(upside_returns) - 1)
            return math.sqrt(variance) * math.sqrt(252)
    
    def _calculate_downside_volatility(self, returns: List[float]) -> float:
        """计算下行波动率"""
        downside_returns = [r for r in returns if r < 0]
        if not downside_returns:
            return 0.0
        
        if HAS_NUMPY:
            return np.std(downside_returns, ddof=1) * math.sqrt(252)
        else:
            mean = sum(downside_returns) / len(downside_returns)
            variance = sum((r - mean) ** 2 for r in downside_returns) / (len(downside_returns) - 1)
            return math.sqrt(variance) * math.sqrt(252)
    
    def _assess_risk(self, metrics: RiskMetrics) -> Tuple[str, int]:
        """评估整体风险等级"""
        # 风险评分 (0-100)
        score = 0
        
        # 波动率权重 30%
        if metrics.volatility < 10:
            score += 10
        elif metrics.volatility < 15:
            score += 20
        elif metrics.volatility < 20:
            score += 30
        elif metrics.volatility < 25:
            score += 40
        else:
            score += 50
        
        # 最大回撤权重 30%
        if abs(metrics.max_drawdown) < 5:
            score += 10
        elif abs(metrics.max_drawdown) < 10:
            score += 20
        elif abs(metrics.max_drawdown) < 15:
            score += 30
        elif abs(metrics.max_drawdown) < 20:
            score += 40
        else:
            score += 50
        
        # VaR权重 20%
        if abs(metrics.var_95) < 2:
            score += 5
        elif abs(metrics.var_95) < 3:
            score += 10
        elif abs(metrics.var_95) < 4:
            score += 15
        else:
            score += 20
        
        # Beta权重 20%
        if metrics.beta < 0.8:
            score += 5
        elif metrics.beta < 1.0:
            score += 10
        elif metrics.beta < 1.2:
            score += 15
        else:
            score += 20
        
        # 确定风险等级
        if score <= 30:
            level = "低风险"
        elif score <= 50:
            level = "中低风险"
        elif score <= 70:
            level = "中等风险"
        elif score <= 85:
            level = "中高风险"
        else:
            level = "高风险"
        
        return level, score
    
    def _generate_risk_alerts(self, metrics: RiskMetrics) -> List[Dict]:
        """生成风险预警"""
        alerts = []
        
        # 波动率预警
        if metrics.volatility > 25:
            alerts.append({
                'type': 'volatility',
                'level': 'high',
                'message': f'波动率({metrics.volatility:.1f}%)过高，高于25%阈值'
            })
        elif metrics.volatility > 20:
            alerts.append({
                'type': 'volatility',
                'level': 'warning',
                'message': f'波动率({metrics.volatility:.1f}%)较高，注意风险控制'
            })
        
        # 回撤预警
        if abs(metrics.max_drawdown) > 20:
            alerts.append({
                'type': 'drawdown',
                'level': 'high',
                'message': f'最大回撤({metrics.max_drawdown:.1f}%)过大，风险较高'
            })
        elif abs(metrics.max_drawdown) > 15:
            alerts.append({
                'type': 'drawdown',
                'level': 'warning',
                'message': f'最大回撤({metrics.max_drawdown:.1f}%)接近警戒线'
            })
        
        # VaR预警
        if abs(metrics.var_95) > 4:
            alerts.append({
                'type': 'var',
                'level': 'warning',
                'message': f'95%VaR({metrics.var_95:.2f}%)较高，极端风险上升'
            })
        
        # Beta预警
        if metrics.beta > 1.3:
            alerts.append({
                'type': 'beta',
                'level': 'warning',
                'message': f'Beta({metrics.beta:.2f})较高，对市场波动敏感'
            })
        
        # 尾部风险预警
        if metrics.skewness < -0.5:
            alerts.append({
                'type': 'tail_risk',
                'level': 'warning',
                'message': f'负偏度({metrics.skewness:.2f})，左尾风险较大'
            })
        
        return alerts


def print_risk_report(report: Dict):
    """打印风险分析报告"""
    print("\n" + "=" * 80)
    print(f"📊 {report['fund_name']} ({report['fund_code']}) - 风险分析报告")
    print("=" * 80)
    print(f"分析日期: {report['analysis_date']} | 分析周期: {report['period_days']}个交易日")
    print(f"数据来源: {report.get('data_source', '未知')}")
    print(f"数据质量: {report.get('data_quality', 'unknown')}")
    print(f"真实数据: {'✅ 是' if report.get('is_real_data') else '⚠️ 否(模拟数据)'}")
    print()
    
    m = report['risk_metrics']
    
    # 风险等级
    assessment = report['risk_assessment']
    print(f"🎯 风险等级: {assessment['overall_risk_level']} (评分: {assessment['risk_score']}/100)")
    print(f"置信度: {assessment['confidence']}")
    print()
    
    # 收益风险指标
    print("📈 风险调整收益指标:")
    sharpe_stars = "⭐" * int(min(m['sharpe_ratio'], 5))
    sortino_stars = "⭐" * int(min(m['sortino_ratio'], 5))
    print(f"  夏普比率: {m['sharpe_ratio']:.2f} {sharpe_stars}")
    print(f"  索提诺比率: {m['sortino_ratio']:.2f} {sortino_stars}")
    print(f"  特雷诺比率: {m['treynor_ratio']:.3f}")
    print(f"  卡玛比率: {m['calmar_ratio']:.2f}")
    print()
    
    # 市场风险
    print("📊 市场风险指标:")
    print(f"  Beta系数: {m['beta']:.2f} {'(波动大于市场)' if m['beta'] > 1 else '(波动小于市场)'}")
    print(f"  Alpha超额收益: {m['alpha']:+.2f}%")
    print(f"  R²: {m['r_squared']:.2%} ({'高度相关' if m['r_squared'] > 0.7 else '中度相关' if m['r_squared'] > 0.4 else '低度相关'})")
    print()
    
    # 极端风险
    print("⚠️ 极端风险指标:")
    print(f"  95% VaR (日度): {m['var_95']:+.2f}%")
    print(f"  99% VaR (日度): {m['var_99']:+.2f}%")
    print(f"  95% CVaR (日度): {m['cvar_95']:+.2f}%")
    print(f"  99% CVaR (日度): {m['cvar_99']:+.2f}%")
    print(f"  最大回撤: {m['max_drawdown']:+.2f}%")
    print(f"  回撤持续期: {m['max_drawdown_duration']}天")
    print()
    
    # 波动率分解
    print("📉 波动率分解:")
    print(f"  总波动率: {m['volatility']:.2f}%")
    print(f"  上行波动率: {m['upside_vol']:.2f}%")
    print(f"  下行波动率: {m['downside_vol']:.2f}%")
    print(f"  系统性风险: {m['systematic_vol']:.2f}%")
    print(f"  非系统性风险: {m['unsystematic_vol']:.2f}%")
    print()
    
    # 尾部风险
    print("🔺 尾部风险指标:")
    print(f"  偏度: {m['skewness']:+.2f} ({'左偏' if m['skewness'] < 0 else '右偏'})")
    print(f"  峰度: {m['kurtosis']:.2f} ({'厚尾' if m['kurtosis'] > 3 else '正常'})")
    print()
    
    # 预警
    if report['risk_alerts']:
        print("🚨 风险预警:")
        for alert in report['risk_alerts']:
            emoji = "🔴" if alert['level'] == 'high' else "🟡"
            print(f"  {emoji} [{alert['type']}] {alert['message']}")
    else:
        print("✅ 无重大风险预警")
    
    print("=" * 80)


def main():
    """主函数 - CLI入口"""
    parser = argparse.ArgumentParser(description='基金风险分析器 - AkShare版')
    parser.add_argument('--code', required=True, help='基金代码')
    parser.add_argument('--period', type=int, default=252, help='分析周期（交易日）')
    parser.add_argument('--var', action='store_true', help='仅计算VaR')
    parser.add_argument('--confidence', type=float, default=0.95, help='VaR置信度')
    parser.add_argument('--method', default='historical', 
                       choices=['historical', 'parametric', 'monte_carlo'],
                       help='VaR计算方法')
    parser.add_argument('--compare', help='对比多只基金，逗号分隔')
    parser.add_argument('--alert', action='store_true', help='检查风险预警')
    parser.add_argument('--json', action='store_true', help='输出JSON格式')
    
    args = parser.parse_args()
    
    analyzer = FundRiskAnalyzer()
    
    # 仅计算VaR
    if args.var:
        result = analyzer.calculate_var(args.code, args.confidence, args.method)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"\n📊 {result.get('fund_name', args.code)} VaR计算结果")
            print(f"  计算方法: {result.get('var_method', 'historical')}")
            print(f"  置信度: {result.get('confidence', '95%')}")
            print(f"  日度VaR: {result.get('daily_var', 'N/A')}")
            print(f"  月度VaR: {result.get('monthly_var', 'N/A')}")
            print(f"  年度VaR: {result.get('annual_var', 'N/A')}")
            print(f"  数据来源: {result.get('data_source', '未知')}")
        return
    
    # 检查风险预警
    if args.alert:
        alerts = analyzer.check_risk_alerts(args.code)
        print(f"\n⚠️ {args.code} 风险预警:")
        for alert in alerts:
            if 'error' in alert:
                print(f"  错误: {alert['error']}")
            else:
                emoji = "🔴" if alert.get('level') == 'high' else "🟡"
                print(f"  {emoji} {alert.get('message', '')}")
        return
    
    # 对比基金
    if args.compare:
        codes = args.compare.split(',')
        comparison = analyzer.compare_risk(codes)
        print("\n基金风险对比:")
        print(json.dumps(comparison, ensure_ascii=False, indent=2))
        return
    
    # 全面风险分析
    report = analyzer.analyze(args.code, args.period)
    
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_risk_report(report)


if __name__ == '__main__':
    main()
