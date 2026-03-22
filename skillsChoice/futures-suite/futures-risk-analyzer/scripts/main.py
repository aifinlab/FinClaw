#!/usr/bin/env python3
"""期货风险分析器"""

import akshare as ak
import pandas as pd
import numpy as np
import json
from datetime import datetime
import argparse


class FuturesRiskAnalyzer:
    """期货风险分析器"""
    
    def analyze_risk(self, symbol: str, lookback: int = 60) -> dict:
        """分析期货风险指标"""
        try:
            df = ak.futures_zh_daily(symbol=symbol)
            
            if df is None or df.empty or len(df) < lookback:
                return {"error": "数据不足"}
            
            df = df.sort_values('date').tail(lookback)
            
            # 计算收益率
            df['return'] = df['收盘'].pct_change()
            returns = df['return'].dropna()
            
            # 风险指标
            volatility = returns.std() * np.sqrt(252)  # 年化波动率
            var_95 = np.percentile(returns, 5)  # 95% VaR
            var_99 = np.percentile(returns, 1)  # 99% VaR
            
            # 最大回撤
            cumulative = (1 + returns).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            max_drawdown = drawdown.min()
            
            # 夏普比率（假设无风险利率2%）
            sharpe = (returns.mean() * 252 - 0.02) / (returns.std() * np.sqrt(252))
            
            return {
                "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "symbol": symbol,
                "lookback_days": lookback,
                "volatility_annual": f"{volatility*100:.2f}%",
                "var_95_daily": f"{var_95*100:.2f}%",
                "var_99_daily": f"{var_99*100:.2f}%",
                "max_drawdown": f"{max_drawdown*100:.2f}%",
                "sharpe_ratio": f"{sharpe:.2f}",
                "risk_level": self._assess_risk(volatility),
                "data_source": "AkShare"
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _assess_risk(self, volatility: float) -> str:
        """评估风险等级"""
        if volatility > 0.5:
            return "高风险"
        elif volatility > 0.3:
            return "中高风险"
        elif volatility > 0.2:
            return "中等风险"
        else:
            return "低风险"


def main():
    parser = argparse.ArgumentParser(description="期货风险分析器")
    parser.add_argument("--symbol", required=True, help="合约代码")
    parser.add_argument("--lookback", type=int, default=60, help="回看天数")
    
    args = parser.parse_args()
    analyzer = FuturesRiskAnalyzer()
    result = analyzer.analyze_risk(args.symbol, args.lookback)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
