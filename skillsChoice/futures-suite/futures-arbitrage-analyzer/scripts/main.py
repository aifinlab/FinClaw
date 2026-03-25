#!/usr/bin/env python3
"""期货套利分析器 - 使用AkShare开源数据接口获取实时行情"""

import akshare as ak
import pandas as pd
import json
from datetime import datetime
import argparse
import numpy as np


class FuturesArbitrageAnalyzer:
    """期货套利分析器 - 使用AkShare获取真实期货数据"""
    
    # 常用套利组合映射
    ARBITRAGE_PAIRS = {
        "RB-HC": {"name": "螺纹钢-热卷", "long": "RB", "short": "HC", "exchange": "上期所"},
        "M-RM": {"name": "豆粕-菜粕", "long": "M", "short": "RM", "exchange": "跨交易所"},
        "Y-P": {"name": "豆油-棕榈油", "long": "Y", "short": "P", "exchange": "大商所"},
        "JM-J": {"name": "焦煤-焦炭", "long": "JM", "short": "J", "exchange": "大商所"},
        "L-PP": {"name": "塑料-PP", "long": "L", "short": "PP", "exchange": "大商所"},
        "TA-EG": {"name": "PTA-乙二醇", "long": "TA", "short": "EG", "exchange": "跨交易所"}
    }
    
    def _get_futures_price(self, symbol: str) -> float:
        """从AkShare获取期货最新价格"""
        try:
            # 使用AkShare获取期货行情
            df = ak.futures_zh_realtime(symbol)
            if df is not None and not df.empty:
                # 获取最新价
                price = df.iloc[0].get('最新价', 0)
                return float(price) if price else 0
            return 0
        except Exception:
            return 0
    
    def _get_futures_hist(self, symbol: str, days: int = 60) -> pd.DataFrame:
        """获取期货历史行情计算统计值"""
        try:
            # 使用AkShare获取期货历史数据
            df = ak.futures_zh_daily(symbol=symbol)
            if df is not None and not df.empty:
                return df.tail(days)
            return pd.DataFrame()
        except Exception:
            return pd.DataFrame()
    
    def analyze_spread(self, symbol1: str, symbol2: str) -> dict:
        """分析两个合约价差 - 使用AkShare实时数据"""
        try:
            # 提取品种代码
            code1 = ''.join([c for c in symbol1 if c.isalpha()]).upper()
            code2 = ''.join([c for c in symbol2 if c.isalpha()]).upper()
            spread_key = f"{code1}-{code2}"
            
            # 获取实时价格
            price1 = self._get_futures_price(symbol1)
            price2 = self._get_futures_price(symbol2)
            
            if price1 <= 0 or price2 <= 0:
                return {
                    "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "symbol1": symbol1,
                    "symbol2": symbol2,
                    "error": f"无法获取{symbol1}或{symbol2}的价格数据",
                    "message": "请检查合约代码是否正确，或AkShare数据源是否可用"
                }
            
            # 获取历史数据计算统计值
            hist1 = self._get_futures_hist(symbol1, 60)
            hist2 = self._get_futures_hist(symbol2, 60)
            
            current_spread = price1 - price2
            
            # 计算历史价差的均值和标准差
            if not hist1.empty and not hist2.empty and len(hist1) == len(hist2):
                hist1['spread'] = hist1['close'] - hist2['close']
                mean = hist1['spread'].mean()
                std = hist1['spread'].std()
                z_score = (current_spread - mean) / std if std > 0 else 0
                percentile = (hist1['spread'] <= current_spread).mean() * 100
            else:
                mean = current_spread
                std = 0
                z_score = 0
                percentile = 50
            
            return {
                "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "symbol1": symbol1,
                "symbol2": symbol2,
                "symbol1_price": price1,
                "symbol2_price": price2,
                "spread_analysis": {
                    "current_spread": round(current_spread, 2),
                    "historical_mean": round(mean, 2),
                    "historical_std": round(std, 2),
                    "percentile": f"{percentile:.1f}%",
                    "z_score": round(z_score, 2)
                },
                "signal": self._generate_signal(current_spread, mean, std),
                "data_source": "AkShare开源数据",
                "data_quality": "实时行情+历史统计",
                "note": "基于近60日历史数据计算"
            }
        
        except Exception as e:
            return {
                "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "symbol1": symbol1,
                "symbol2": symbol2,
                "error": f"分析失败: {str(e)}",
                "message": "AkShare接口调用失败，请检查网络连接"
            }
    
    def _generate_signal(self, current, mean, std) -> str:
        """生成交易信号"""
        if std == 0 or std != std:  # std != std checks for NaN
            return "历史数据不足，无法生成信号"
        
        z_score = (current - mean) / std
        
        if z_score > 2:
            return "价差过高(+2σ以上)，考虑做空价差"
        elif z_score < -2:
            return "价差过低(-2σ以下)，考虑做多价差"
        elif z_score > 1:
            return "价差偏高(+1σ以上)，关注做空机会"
        elif z_score < -1:
            return "价差偏低(-1σ以下)，关注做多机会"
        else:
            return "价差在均值附近，无套利机会"
    
    def get_calendar_spread(self, product: str, near_month: str = None, far_month: str = None) -> dict:
        """获取跨期价差 - 使用AkShare实时数据"""
        try:
            product = product.upper()
            
            # 如果未指定合约月份，使用主力合约和次主力
            if not near_month or not far_month:
                # 获取该品种所有合约
                df_contracts = ak.futures_zh_realtime(product)
                if df_contracts is None or df_contracts.empty:
                    return {
                        "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "error": f"无法获取{product}的合约列表"
                    }
                
                # 按持仓量排序取前两个
                if '持仓量' in df_contracts.columns:
                    df_sorted = df_contracts.sort_values('持仓量', ascending=False)
                    near_contract = df_sorted.iloc[0]['合约'] if len(df_sorted) > 0 else f"{product}主力"
                    far_contract = df_sorted.iloc[1]['合约'] if len(df_sorted) > 1 else f"{product}次主力"
                else:
                    near_contract = f"{product}主力"
                    far_contract = f"{product}次主力"
            else:
                near_contract = f"{product}{near_month}"
                far_contract = f"{product}{far_month}"
            
            # 获取两个合约的价格
            near_price = self._get_futures_price(near_contract)
            far_price = self._get_futures_price(far_contract)
            
            if near_price <= 0 or far_price <= 0:
                return {
                    "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "product": product,
                    "error": "无法获取合约价格数据"
                }
            
            spread = near_price - far_price
            structure = "backwardation" if spread > 0 else "contango"
            
            return {
                "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "product": product,
                "near_contract": near_contract,
                "far_contract": far_contract,
                "near_price": near_price,
                "far_price": far_price,
                "spread": round(spread, 2),
                "structure": structure,
                "structure_desc": "近月升水(供应紧张)" if structure == "backwardation" else "近月贴水(供应充足)",
                "data_source": "AkShare开源数据",
                "data_quality": "实时行情"
            }
        
        except Exception as e:
            return {
                "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "product": product,
                "error": f"获取跨期价差失败: {str(e)}"
            }
    
    def get_available_pairs(self) -> dict:
        """获取支持的套利组合列表"""
        return {
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "available_pairs": self.ARBITRAGE_PAIRS,
            "note": "使用时请输入完整合约代码，如: RB2505, HC2505",
            "data_source": "AkShare开源数据"
        }


def main():
    parser = argparse.ArgumentParser(description="期货套利分析器 - AkShare数据")
    parser.add_argument("--symbol1", help="合约1 (如: RB2505)")
    parser.add_argument("--symbol2", help="合约2 (如: HC2505)")
    parser.add_argument("--calendar", help="跨期套利品种代码 (如: RB)")
    parser.add_argument("--near", help="近月合约月份 (如: 2505)")
    parser.add_argument("--far", help="远月合约月份 (如: 2510)")
    parser.add_argument("--list", action="store_true", help="显示支持的套利组合")
    
    args = parser.parse_args()
    analyzer = FuturesArbitrageAnalyzer()
    
    if args.list:
        result = analyzer.get_available_pairs()
    elif args.calendar:
        result = analyzer.get_calendar_spread(args.calendar, args.near, args.far)
    elif args.symbol1 and args.symbol2:
        result = analyzer.analyze_spread(args.symbol1, args.symbol2)
    else:
        result = {
            "message": "请指定参数",
            "usage": {
                "跨品种套利": "--symbol1 RB2505 --symbol2 HC2505",
                "跨期套利": "--calendar RB --near 2505 --far 2510",
                "查看支持组合": "--list"
            },
            "data_source": "AkShare开源数据"
        }
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
