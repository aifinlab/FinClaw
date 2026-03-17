#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
收益归因分析器

功能：
1. 基准对比法：计算 Alpha/Beta 收益
2. Brinson 归因法：配置效应 + 选择效应
3. 因子归因法：风格因子暴露分析
4. 收益来源分解：市场/配置/选股/择时

使用示例：
    from return_attribution import ReturnAttribution
    
    # 基准对比法
    ra = ReturnAttribution()
    result = ra.benchmark_attribution(
        portfolio_return=0.15,  # 组合收益 15%
        benchmark_return=0.10,  # 基准收益 10%
        beta=1.0,
    )
    print(result)
    
    # Brinson 归因
    result = ra.brinson_attribution(
        portfolio_weights=[0.4, 0.3, 0.3],  # 股票/债券/现金
        benchmark_weights=[0.5, 0.4, 0.1],
        portfolio_returns=[0.20, 0.05, 0.02],  # 各类资产收益
        benchmark_returns=[0.18, 0.04, 0.02],
    )
    print(result)
"""

from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class AssetClass:
    """资产类别"""
    name: str
    weight: float  # 权重
    return_rate: float  # 收益率


class ReturnAttribution:
    """收益归因分析器"""
    
    def __init__(self):
        pass
    
    def benchmark_attribution(
        self,
        portfolio_return: float,
        benchmark_return: float,
        beta: float = 1.0,
    ) -> Dict:
        """
        基准对比法：计算 Alpha 和 Beta 收益
        
        Args:
            portfolio_return: 组合收益率（如 0.15 表示 15%）
            benchmark_return: 基准收益率
            beta: 组合相对于基准的 Beta 系数
        
        Returns:
            归因结果字典
        """
        # Beta 收益 = 基准收益 × Beta
        beta_return = benchmark_return * beta
        
        # Alpha 收益 = 组合收益 - Beta 收益
        alpha_return = portfolio_return - beta_return
        
        # 总收益分解
        total = portfolio_return
        
        return {
            "method": "基准对比法",
            "portfolio_return": f"{portfolio_return * 100:.2f}%",
            "benchmark_return": f"{benchmark_return * 100:.2f}%",
            "beta": beta,
            "beta_return": f"{beta_return * 100:.2f}%",
            "alpha_return": f"{alpha_return * 100:.2f}%",
            "alpha_ratio": f"{alpha_return / portfolio_return * 100:.1f}%" if portfolio_return != 0 else "N/A",
            "summary": (
                f"组合收益 {portfolio_return * 100:.2f}% 中，"
                f"{beta_return * 100:.2f}% 来自市场 Beta，"
                f"{alpha_return * 100:.2f}% 来自超额 Alpha"
            ),
        }
    
    def brinson_attribution(
        self,
        portfolio_weights: List[float],
        benchmark_weights: List[float],
        portfolio_returns: List[float],
        benchmark_returns: List[float],
        asset_names: List[str] = None,
    ) -> Dict:
        """
        Brinson 归因法：分解为配置效应和选择效应
        
        公式：
        - 配置效应 = ∑(wp - wb) × rb
        - 选择效应 = ∑wb × (rp - rb)
        - 交互效应 = ∑(wp - wb) × (rp - rb)
        
        Args:
            portfolio_weights: 组合各类资产权重
            benchmark_weights: 基准各类资产权重
            portfolio_returns: 组合各类资产收益率
            benchmark_returns: 基准各类资产收益率
            asset_names: 资产类别名称
        
        Returns:
            Brinson 归因结果
        """
        n = len(portfolio_weights)
        if asset_names is None:
            asset_names = [f"资产{i+1}" for i in range(n)]
        
        # 计算总收益
        portfolio_total = sum(w * r for w, r in zip(portfolio_weights, portfolio_returns))
        benchmark_total = sum(w * r for w, r in zip(benchmark_weights, benchmark_returns))
        
        # 各项效应分解
        allocation_effect = 0  # 配置效应
        selection_effect = 0   # 选择效应
        interaction_effect = 0 # 交互效应
        
        asset_details = []
        
        for i in range(n):
            wp = portfolio_weights[i]
            wb = benchmark_weights[i]
            rp = portfolio_returns[i]
            rb = benchmark_returns[i]
            
            # 配置效应 = (wp - wb) × rb
            alloc = (wp - wb) * rb
            
            # 选择效应 = wb × (rp - rb)
            select = wb * (rp - rb)
            
            # 交互效应 = (wp - wb) × (rp - rb)
            interact = (wp - wb) * (rp - rb)
            
            allocation_effect += alloc
            selection_effect += select
            interaction_effect += interact
            
            asset_details.append({
                "name": asset_names[i],
                "portfolio_weight": f"{wp * 100:.1f}%",
                "benchmark_weight": f"{wb * 100:.1f}%",
                "portfolio_return": f"{rp * 100:.2f}%",
                "benchmark_return": f"{rb * 100:.2f}%",
                "allocation_effect": f"{alloc * 100:.2f}%",
                "selection_effect": f"{select * 100:.2f}%",
                "interaction_effect": f"{interact * 100:.2f}%",
                "overweight": wp > wb,
            })
        
        # 验证：总超额收益 = 配置 + 选择 + 交互
        excess_return = portfolio_total - benchmark_total
        total_attribution = allocation_effect + selection_effect + interaction_effect
        
        return {
            "method": "Brinson 归因法",
            "portfolio_return": f"{portfolio_total * 100:.2f}%",
            "benchmark_return": f"{benchmark_total * 100:.2f}%",
            "excess_return": f"{excess_return * 100:.2f}%",
            "allocation_effect": f"{allocation_effect * 100:.2f}%",
            "selection_effect": f"{selection_effect * 100:.2f}%",
            "interaction_effect": f"{interaction_effect * 100:.2f}%",
            "attribution_check": f"{total_attribution * 100:.2f}%",
            "is_balanced": abs(excess_return - total_attribution) < 0.0001,
            "asset_details": asset_details,
            "summary": self._brinson_summary(
                allocation_effect, selection_effect, interaction_effect, excess_return
            ),
        }
    
    def _brinson_summary(
        self,
        allocation: float,
        selection: float,
        interaction: float,
        excess: float,
    ) -> str:
        """生成 Brinson 归因总结"""
        parts = []
        
        if abs(allocation) > 0.001:
            if allocation > 0:
                parts.append(f"资产配置贡献 {allocation * 100:.2f}%")
            else:
                parts.append(f"资产配置拖累 {abs(allocation) * 100:.2f}%")
        
        if abs(selection) > 0.001:
            if selection > 0:
                parts.append(f"个券选择贡献 {selection * 100:.2f}%")
            else:
                parts.append(f"个券选择拖累 {abs(selection) * 100:.2f}%")
        
        if abs(interaction) > 0.001:
            parts.append(f"交互效应 {interaction * 100:.2f}%")
        
        if parts:
            return "超额收益主要来自：" + "，".join(parts)
        else:
            return "超额收益不显著"
    
    def sector_attribution(
        self,
        portfolio_sector_weights: Dict[str, float],
        benchmark_sector_weights: Dict[str, float],
        sector_returns: Dict[str, float],
    ) -> Dict:
        """
        行业配置归因
        
        Args:
            portfolio_sector_weights: 组合各行业权重
            benchmark_sector_weights: 基准各行业权重
            sector_returns: 各行业收益率
        
        Returns:
            行业归因结果
        """
        sectors = set(portfolio_sector_weights.keys()) | set(benchmark_sector_weights.keys())
        
        total_allocation = 0
        total_selection = 0
        sector_details = []
        
        for sector in sectors:
            wp = portfolio_sector_weights.get(sector, 0)
            wb = benchmark_sector_weights.get(sector, 0)
            r = sector_returns.get(sector, 0)
            
            # 配置效应：超配/低配决策的贡献
            allocation = (wp - wb) * r
            
            # 选择效应：行业内选股（简化为行业收益差异）
            # 这里简化处理，实际需要考虑行业内个股选择
            selection = 0
            
            total_allocation += allocation
            total_selection += selection
            
            sector_details.append({
                "sector": sector,
                "portfolio_weight": f"{wp * 100:.2f}%",
                "benchmark_weight": f"{wb * 100:.2f}%",
                "difference": f"{(wp - wb) * 100:.2f}%",
                "return": f"{r * 100:.2f}%",
                "allocation_effect": f"{allocation * 100:.2f}%",
                "overweight": wp > wb,
                "good_call": (wp > wb and r > 0) or (wp < wb and r < 0),
            })
        
        # 排序：按配置效应贡献
        sector_details.sort(key=lambda x: x["allocation_effect"], reverse=True)
        
        # 找出最佳和最差配置决策
        best_calls = [s for s in sector_details if s["good_call"]]
        worst_calls = [s for s in sector_details if not s["good_call"]]
        
        return {
            "method": "行业配置归因",
            "total_allocation_effect": f"{total_allocation * 100:.2f}%",
            "total_selection_effect": f"{total_selection * 100:.2f}%",
            "sector_details": sector_details,
            "best_calls": best_calls[:3],  # 最佳 3 个配置
            "worst_calls": worst_calls[:3],  # 最差 3 个配置
            "summary": self._sector_summary(sector_details),
        }
    
    def _sector_summary(self, sector_details: List[Dict]) -> str:
        """生成行业归因总结"""
        if not sector_details:
            return "无行业配置数据"
        
        # 最佳配置
        good_calls = [s for s in sector_details if s["good_call"] and abs(s["allocation_effect"]) > 0.001]
        bad_calls = [s for s in sector_details if not s["good_call"] and abs(s["allocation_effect"]) > 0.001]
        
        parts = []
        
        if good_calls:
            best = good_calls[0]
            direction = "超配" if best["overweight"] else "低配"
            parts.append(f"成功{direction}{best['sector']}（收益{best['return']}）")
        
        if bad_calls:
            worst = bad_calls[0]
            direction = "超配" if worst["overweight"] else "低配"
            parts.append(f"失误{direction}{worst['sector']}（收益{worst['return']}）")
        
        return "行业配置：" + "，".join(parts) if parts else "行业配置中性"
    
    def calculate_sharpe_ratio(
        self,
        portfolio_return: float,
        risk_free_rate: float = 0.03,
        portfolio_volatility: float = None,
    ) -> Dict:
        """
        计算夏普比率
        
        Args:
            portfolio_return: 组合收益率
            risk_free_rate: 无风险利率
            portfolio_volatility: 组合波动率
        
        Returns:
            夏普比率计算结果
        """
        excess_return = portfolio_return - risk_free_rate
        
        if portfolio_volatility and portfolio_volatility > 0:
            sharpe = excess_return / portfolio_volatility
        else:
            sharpe = None
        
        return {
            "portfolio_return": f"{portfolio_return * 100:.2f}%",
            "risk_free_rate": f"{risk_free_rate * 100:.2f}%",
            "excess_return": f"{excess_return * 100:.2f}%",
            "volatility": f"{portfolio_volatility * 100:.2f}%" if portfolio_volatility else "N/A",
            "sharpe_ratio": f"{sharpe:.3f}" if sharpe else "N/A",
            "interpretation": self._sharpe_interpretation(sharpe),
        }
    
    def _sharpe_interpretation(self, sharpe: Optional[float]) -> str:
        """夏普比率解释"""
        if sharpe is None:
            return "无法计算"
        elif sharpe > 2:
            return "优秀（风险调整后收益很高）"
        elif sharpe > 1:
            return "良好（风险调整后收益较好）"
        elif sharpe > 0:
            return "一般（风险调整后收益为正）"
        else:
            return "较差（风险调整后收益为负）"
    
    def generate_report(
        self,
        portfolio_return: float,
        benchmark_return: float,
        beta: float = 1.0,
        portfolio_volatility: float = None,
        risk_free_rate: float = 0.03,
    ) -> str:
        """
        生成完整收益归因报告
        
        Args:
            portfolio_return: 组合收益率
            benchmark_return: 基准收益率
            beta: Beta 系数
            portfolio_volatility: 组合波动率
            risk_free_rate: 无风险利率
        
        Returns:
            格式化报告文本
        """
        lines = []
        lines.append("=" * 60)
        lines.append("收益归因分析报告")
        lines.append("=" * 60)
        lines.append("")
        
        # 收益概览
        lines.append("【收益概览】")
        lines.append(f"组合收益率：{portfolio_return * 100:.2f}%")
        lines.append(f"基准收益率：{benchmark_return * 100:.2f}%")
        lines.append(f"超额收益：{(portfolio_return - benchmark_return) * 100:.2f}%")
        lines.append("")
        
        # Alpha/Beta 分解
        lines.append("【Alpha/Beta 分解】")
        alpha_beta = self.benchmark_attribution(portfolio_return, benchmark_return, beta)
        lines.append(f"Beta 收益：{alpha_beta['beta_return']}（市场贡献）")
        lines.append(f"Alpha 收益：{alpha_beta['alpha_return']}（超额收益）")
        lines.append(f"Alpha 占比：{alpha_beta['alpha_ratio']}")
        lines.append("")
        
        # 风险调整收益
        lines.append("【风险调整收益】")
        sharpe = self.calculate_sharpe_ratio(portfolio_return, risk_free_rate, portfolio_volatility)
        lines.append(f"夏普比率：{sharpe['sharpe_ratio']}")
        lines.append(f"评价：{sharpe['interpretation']}")
        lines.append("")
        
        lines.append("=" * 60)
        lines.append("注：如需 Brinson 归因和行业归因，请提供资产配置和行业权重数据")
        
        return "\n".join(lines)


# 快速测试
if __name__ == "__main__":
    ra = ReturnAttribution()
    
    # 测试基准对比法
    print(ra.generate_report(
        portfolio_return=0.15,
        benchmark_return=0.10,
        beta=1.1,
        portfolio_volatility=0.18,
    ))
    
    print("\n" + "=" * 60 + "\n")
    
    # 测试 Brinson 归因
    result = ra.brinson_attribution(
        portfolio_weights=[0.6, 0.3, 0.1],
        benchmark_weights=[0.5, 0.4, 0.1],
        portfolio_returns=[0.20, 0.05, 0.02],
        benchmark_returns=[0.15, 0.04, 0.02],
        asset_names=["股票", "债券", "现金"],
    )
    
    print("Brinson 归因结果:")
    print(f"组合收益：{result['portfolio_return']}")
    print(f"基准收益：{result['benchmark_return']}")
    print(f"超额收益：{result['excess_return']}")
    print(f"配置效应：{result['allocation_effect']}")
    print(f"选择效应：{result['selection_effect']}")
    print(f"交互效应：{result['interaction_effect']}")
    print(f"总结：{result['summary']}")
