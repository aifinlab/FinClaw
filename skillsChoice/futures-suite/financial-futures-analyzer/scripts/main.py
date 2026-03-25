#!/usr/bin/env python3
"""金融期货分析器 - 使用AkShare开源数据接口获取实时行情"""

import akshare as ak
import pandas as pd
import json
from datetime import datetime
import argparse


class FinancialFuturesAnalyzer:
    """金融期货分析器 - 使用AkShare获取真实数据"""
    
    # 股指期货映射
    INDEX_FUTURES = {
        "IF": {"name": "沪深300", "index_code": "000300", "multiplier": 300},
        "IC": {"name": "中证500", "index_code": "000905", "multiplier": 200},
        "IH": {"name": "上证50", "index_code": "000016", "multiplier": 300},
        "IM": {"name": "中证1000", "index_code": "000852", "multiplier": 200}
    }
    
    # 国债期货映射
    BOND_FUTURES = {
        "T": {"name": "10年期国债", "underlying": "10Y国债", "multiplier": 10000},
        "TF": {"name": "5年期国债", "underlying": "5Y国债", "multiplier": 10000},
        "TS": {"name": "2年期国债", "underlying": "2Y国债", "multiplier": 10000}
    }
    
    def _get_futures_price(self, symbol: str) -> dict:
        """获取期货实时价格"""
        try:
            df = ak.futures_zh_realtime(symbol)
            if df is not None and not df.empty:
                row = df.iloc[0]
                return {
                    "price": float(row.get('最新价', 0)),
                    "volume": int(row.get('成交量', 0)) if pd.notna(row.get('成交量')) else 0,
                    "oi": int(row.get('持仓量', 0)) if pd.notna(row.get('持仓量')) else 0,
                    "open": float(row.get('开盘价', 0)),
                    "high": float(row.get('最高价', 0)),
                    "low": float(row.get('最低价', 0)),
                    "pre_settle": float(row.get('昨结', 0))
                }
            return None
        except Exception:
            return None
    
    def _get_index_price(self, index_code: str) -> float:
        """获取现货指数价格"""
        try:
            # 使用AkShare获取指数行情
            if index_code in ['000300', '000905', '000016', '000852']:
                # 需要添加市场前缀
                symbol = f"sh{index_code}"
                df = ak.stock_zh_index_daily(symbol=symbol)
                if df is not None and not df.empty:
                    return float(df.iloc[-1]['close'])
            return 0
        except Exception:
            return 0
    
    def analyze_basis(self, symbol: str) -> dict:
        """分析股指期货基差 - 使用AkShare实时数据"""
        try:
            # 提取合约代码
            product_code = ''.join([c for c in symbol if c.isalpha()]).upper()
            
            if product_code not in self.INDEX_FUTURES:
                return {
                    "error": "不支持的品种",
                    "supported": list(self.INDEX_FUTURES.keys())
                }
            
            index_info = self.INDEX_FUTURES[product_code]
            
            # 获取期货价格
            futures_data = self._get_futures_price(symbol)
            if not futures_data:
                return {
                    "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "symbol": symbol,
                    "error": f"无法获取{symbol}的期货价格",
                    "message": "请检查合约代码是否正确"
                }
            
            futures_price = futures_data["price"]
            
            # 获取现货指数价格
            spot_price = self._get_index_price(index_info["index_code"])
            
            if spot_price <= 0:
                return {
                    "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "symbol": symbol,
                    "futures_price": futures_price,
                    "error": "无法获取现货指数价格",
                    "message": "现货数据暂时不可用"
                }
            
            # 计算基差
            basis = futures_price - spot_price
            discount_rate = (basis / spot_price * 100) if spot_price > 0 else 0
            
            return {
                "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "symbol": symbol,
                "index_name": index_info["name"],
                "contract_multiplier": index_info["multiplier"],
                "basis_analysis": {
                    "futures_price": round(futures_price, 2),
                    "spot_index": round(spot_price, 2),
                    "basis": round(basis, 2),
                    "discount_rate": f"{discount_rate:.2f}%",
                    "basis_status": "贴水" if basis < 0 else "升水"
                },
                "trading_data": {
                    "volume": futures_data["volume"],
                    "open_interest": futures_data["oi"],
                    "open": futures_data["open"],
                    "high": futures_data["high"],
                    "low": futures_data["low"],
                    "pre_settle": futures_data["pre_settle"]
                },
                "interpretation": "基差为负表示期货贴水，市场情绪偏谨慎；基差为正表示升水，情绪偏乐观",
                "data_source": "AkShare开源数据",
                "data_quality": "实时行情"
            }
        
        except Exception as e:
            return {
                "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "symbol": symbol,
                "error": f"分析失败: {str(e)}"
            }
    
    def get_all_basis(self, contract_month: str = None) -> dict:
        """获取所有股指期货基差"""
        try:
            # 如果未指定合约月份，自动计算
            if not contract_month:
                now = datetime.now()
                months = [3, 6, 9, 12]
                current_month = now.month
                for m in months:
                    if m >= current_month:
                        contract_month = f"{now.strftime('%y')}{m:02d}"
                        break
                else:
                    contract_month = f"{int(now.strftime('%y'))+1}03"
            
            results = []
            for code in self.INDEX_FUTURES.keys():
                symbol = f"{code}{contract_month}"
                r = self.analyze_basis(symbol)
                if "error" not in r and "basis_analysis" in r:
                    results.append({
                        "symbol": code,
                        "name": r["index_name"],
                        "basis": r["basis_analysis"]["basis"],
                        "discount_rate": r["basis_analysis"]["discount_rate"],
                        "futures_price": r["basis_analysis"]["futures_price"],
                        "spot_price": r["basis_analysis"]["spot_index"]
                    })
            
            # 计算市场情绪
            avg_discount = sum([float(r["discount_rate"].replace('%', '')) for r in results]) / len(results) if results else 0
            sentiment = "整体贴水，情绪偏谨慎" if avg_discount < 0 else "整体升水，情绪偏乐观" if avg_discount > 0 else "平水，情绪中性"
            
            return {
                "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "contract_month": contract_month,
                "all_basis": results,
                "market_sentiment": sentiment,
                "data_source": "AkShare开源数据",
                "data_quality": "实时行情"
            }
        
        except Exception as e:
            return {
                "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "error": f"获取数据失败: {str(e)}"
            }
    
    def get_bond_futures(self) -> dict:
        """获取国债期货数据"""
        try:
            results = []
            for code, info in self.BOND_FUTURES.items():
                # 获取主力合约
                try:
                    df = ak.futures_zh_realtime(code)
                    if df is not None and not df.empty:
                        main_contract = df.loc[df['持仓量'].idxmax()] if '持仓量' in df.columns else df.iloc[0]
                        results.append({
                            "code": code,
                            "name": info["name"],
                            "main_contract": main_contract.get('合约', f'{code}主力'),
                            "price": main_contract.get('最新价', 0),
                            "change": main_contract.get('涨跌', 0),
                            "volume": main_contract.get('成交量', 0)
                        })
                except Exception:
                    continue
            
            return {
                "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "bond_futures": results,
                "data_source": "AkShare开源数据",
                "data_quality": "实时行情"
            }
        
        except Exception as e:
            return {
                "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "error": str(e)
            }


def main():
    parser = argparse.ArgumentParser(description="金融期货分析器 - AkShare数据")
    parser.add_argument("--symbol", help="合约代码(如: IF2506)")
    parser.add_argument("--all", action="store_true", help="全部股指期货基差")
    parser.add_argument("--bond", action="store_true", help="国债期货数据")
    
    args = parser.parse_args()
    analyzer = FinancialFuturesAnalyzer()
    
    if args.bond:
        result = analyzer.get_bond_futures()
    elif args.all:
        result = analyzer.get_all_basis()
    elif args.symbol:
        result = analyzer.analyze_basis(args.symbol)
    else:
        result = {
            "supported_index_futures": list(analyzer.INDEX_FUTURES.keys()),
            "supported_bond_futures": list(analyzer.BOND_FUTURES.keys()),
            "data_source": "AkShare开源数据",
            "usage": {
                "分析单个合约": "--symbol IF2506",
                "全部股指期货": "--all",
                "国债期货": "--bond"
            }
        }
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
