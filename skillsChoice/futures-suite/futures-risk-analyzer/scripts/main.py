#!/usr/bin/env python3
"""期货风险分析器 - 使用AkShare开源数据接口

功能：分析期货品种风险指标
数据源：AkShare开源金融数据接口
说明：风险数据需基于历史行情计算
"""

import akshare as ak
import json
from datetime import datetime
import argparse
import math


class FuturesRiskAnalyzer:
    """期货风险分析器 - 使用AkShare获取历史数据计算风险指标"""
    
    def __init__(self):
        self.query_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _get_hist_data(self, symbol: str) -> list:
        """获取历史行情 - 使用AkShare"""
        try:
            df = ak.futures_zh_daily(symbol=symbol)
            if df is not None and not df.empty:
                return df['close'].tolist()
        except Exception:
            return []
        return []
    
    def _calculate_volatility(self, prices: list) -> float:
        """计算历史波动率"""
        if len(prices) < 2:
            return None
        
        returns = []
        for i in range(1, len(prices)):
            if prices[i-1] != 0:
                ret = (prices[i] - prices[i-1]) / prices[i-1]
                returns.append(ret)
        
        if not returns:
            return None
        
        # 计算标准差（日收益率）
        mean = sum(returns) / len(returns)
        variance = sum((r - mean) ** 2 for r in returns) / len(returns)
        daily_vol = math.sqrt(variance)
        
        # 年化波动率（假设252个交易日）
        annual_vol = daily_vol * math.sqrt(252)
        
        return round(annual_vol * 100, 2)  # 返回百分比
    
    def _calculate_max_dd(self, prices: list) -> float:
        """计算最大回撤"""
        if len(prices) < 2:
            return None
        
        max_price = prices[0]
        max_dd = 0
        
        for price in prices:
            if price > max_price:
                max_price = price
            dd = (max_price - price) / max_price if max_price > 0 else 0
            if dd > max_dd:
                max_dd = dd
        
        return round(max_dd * 100, 2)  # 返回百分比
    
    def analyze_risk(self, symbol: str, lookback: int = 60) -> dict:
        """分析期货风险指标"""
        product_code = ''.join([c for c in symbol if c.isalpha()]).upper()
        
        result = {
            "query_time": self.query_time,
            "symbol": symbol,
            "product_code": product_code,
            "lookback_days": lookback
        }
        
        # 获取历史数据
        prices = self._get_hist_data(symbol)
        
        if len(prices) >= lookback:
            recent_prices = prices[-lookback:]
            
            # 计算风险指标
            volatility = self._calculate_volatility(recent_prices)
            max_dd = self._calculate_max_dd(recent_prices)
            
            if volatility:
                result["risk_indicators"] = {
                    "volatility_annual_pct": f"{volatility}%",
                    "max_drawdown_pct": f"{max_dd}%" if max_dd else None,
                    "var_95_pct": f"{-1.645 * volatility / math.sqrt(252):.2f}%" if volatility else None
                }
            else:
                result["note"] = "历史数据不足，无法计算风险指标"
        else:
            result["note"] = f"历史数据不足（仅{len(prices)}天），需要{lookback}天"
        
        result["risk_framework"] = {
            "风险提示": [
                "杠杆风险：期货交易采用保证金制度，盈亏放大",
                "流动性风险：部分品种成交量较小",
                "基差风险：期货与现货价格差异波动",
                "交割风险：近月合约需关注交割规则"
            ]
        }
        
        result["data_source"] = "AkShare开源数据"
        result["data_quality"] = "基于历史行情计算"
        
        return result


def main():
    parser = argparse.ArgumentParser(description="期货风险分析器")
    parser.add_argument("--symbol", help="合约代码(如: RB, CU, SC)")
    parser.add_argument("--days", type=int, default=60, help="回 lookback天数")
    
    args = parser.parse_args()
    analyzer = FuturesRiskAnalyzer()
    
    if args.symbol:
        result = analyzer.analyze_risk(args.symbol, args.days)
    else:
        result = {
            "usage": "--symbol RB --days 60"
        }
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
