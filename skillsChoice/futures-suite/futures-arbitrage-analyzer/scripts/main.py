#!/usr/bin/env python3
"""期货套利分析器"""

import akshare as ak
import pandas as pd
import json
from datetime import datetime
import argparse


class FuturesArbitrageAnalyzer:
    """期货套利分析器"""
    
    # 常用套利组合
    ARBITRAGE_PAIRS = {
        "螺纹钢-热卷": {"long": "RB", "short": "HC", "ratio": 1},
        "豆粕-菜粕": {"long": "M", "short": "RM", "ratio": 1},
        "豆油-棕榈油": {"long": "Y", "short": "P", "ratio": 1},
        "焦煤-焦炭": {"long": "JM", "short": "J", "ratio": 1.5},
        "塑料-PP": {"long": "L", "short": "PP", "ratio": 1},
        "PTA-乙二醇": {"long": "TA", "short": "EG", "ratio": 1},
    }
    
    def analyze_spread(self, symbol1: str, symbol2: str) -> dict:
        """分析两个合约价差"""
        try:
            # 获取历史数据
            df1 = ak.futures_zh_daily(symbol=symbol1)
            df2 = ak.futures_zh_daily(symbol=symbol2)
            
            if df1 is None or df2 is None or df1.empty or df2.empty:
                return {"error": "无法获取数据"}
            
            # 计算价差
            df1 = df1.sort_values('date')
            df2 = df2.sort_values('date')
            
            # 合并数据
            merged = pd.merge(df1[['date', '收盘']], df2[['date', '收盘']], on='date', suffixes=('_1', '_2'))
            merged['spread'] = merged['收盘_1'] - merged['收盘_2']
            
            # 统计
            spread_mean = merged['spread'].mean()
            spread_std = merged['spread'].std()
            current_spread = merged['spread'].iloc[-1]
            
            # 分位数
            percentile = (merged['spread'] < current_spread).mean() * 100
            
            return {
                "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "symbol1": symbol1,
                "symbol2": symbol2,
                "current_spread": current_spread,
                "spread_mean": spread_mean,
                "spread_std": spread_std,
                "percentile": f"{percentile:.1f}%",
                "z_score": (current_spread - spread_mean) / spread_std if spread_std else 0,
                "signal": self._generate_signal(current_spread, spread_mean, spread_std),
                "data_source": "AkShare"
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _generate_signal(self, current, mean, std) -> str:
        """生成交易信号"""
        if std == 0:
            return "数据不足"
        
        z_score = (current - mean) / std
        
        if z_score > 2:
            return "价差过高，考虑做空价差"
        elif z_score < -2:
            return "价差过低，考虑做多价差"
        elif z_score > 1:
            return "价差偏高，关注"
        elif z_score < -1:
            return "价差偏低，关注"
        else:
            return "价差正常，无套利机会"


def main():
    parser = argparse.ArgumentParser(description="期货套利分析器")
    parser.add_argument("--symbol1", required=True, help="合约1")
    parser.add_argument("--symbol2", required=True, help="合约2")
    
    args = parser.parse_args()
    analyzer = FuturesArbitrageAnalyzer()
    result = analyzer.analyze_spread(args.symbol1, args.symbol2)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
