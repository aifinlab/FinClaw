#!/usr/bin/env python3
"""期货持仓追踪器 - 使用AkShare开源数据接口获取持仓排名"""

import akshare as ak
import pandas as pd
import json
from datetime import datetime
import argparse


class FuturesPositionTracker:
    """期货持仓追踪器 - 使用AkShare获取真实持仓数据"""
    
    def get_position_ranking(self, symbol: str) -> dict:
        """获取持仓排名 - 使用AkShare"""
        try:
            # 提取品种代码
            product_code = ''.join([c for c in symbol if c.isalpha()]).upper()
            
            # 使用AkShare获取持仓排名
            # 注意：AkShare的持仓排名接口需要指定交易所
            df = None
            
            # 尝试上期所
            try:
                df = ak.futures_shfe_position_rank(symbol)
            except Exception:
                pass
            
            # 尝试大商所
            if df is None or df.empty:
                try:
                    df = ak.futures_dce_position_rank(symbol)
                except Exception:
                    pass
            
            # 尝试郑商所
            if df is None or df.empty:
                try:
                    df = ak.futures_czce_position_rank(symbol)
                except Exception:
                    pass
            
            if df is None or df.empty:
                return {
                    "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "symbol": symbol,
                    "product_code": product_code,
                    "error": f"无法获取{symbol}的持仓排名数据",
                    "message": "请检查合约代码是否正确，或使用各交易所官网查询",
                    "exchange_websites": {
                        "上期所": "www.shfe.com.cn",
                        "大商所": "www.dce.com.cn",
                        "郑商所": "www.czce.com.cn",
                        "中金所": "www.cffex.com.cn"
                    }
                }
            
            # 解析持仓数据
            long_positions = []
            short_positions = []
            
            for _, row in df.iterrows():
                rank = row.get('名次', row.get('排名', 0))
                member = row.get('会员简称', row.get('期货公司', '未知'))
                volume = row.get('多单持仓', row.get('多单量', 0))
                change = row.get('增减', row.get('多单增减', 0))
                
                long_positions.append({
                    "rank": int(rank) if pd.notna(rank) else 0,
                    "member": member,
                    "volume": int(volume) if pd.notna(volume) else 0,
                    "change": int(change) if pd.notna(change) else 0
                })
            
            return {
                "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "symbol": symbol,
                "product_code": product_code,
                "position_ranking": {
                    "long_top": long_positions[:10],
                    "short_top": short_positions[:10]
                },
                "interpretation": {
                    "note": "持仓排名反映主力资金动向",
                    "long_concentration": f"多头前5名持仓集中度: 请查看详细数据",
                    "short_concentration": f"空头前5名持仓集中度: 请查看详细数据"
                },
                "data_source": "AkShare - 各期货交易所",
                "data_quality": "官方持仓排名",
                "note": "完整数据请访问交易所官网"
            }
        
        except Exception as e:
            return {
                "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "symbol": symbol,
                "error": f"获取持仓数据失败: {str(e)}",
                "message": "AkShare接口调用失败，请检查网络连接或合约代码"
            }
    
    def get_position_change_analysis(self, symbol: str = None) -> dict:
        """获取持仓变化分析"""
        try:
            # 获取市场主力合约持仓概览
            df = ak.futures_zh_realtime(symbol if symbol else "RB")
            
            if df is None or df.empty:
                return {
                    "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "message": "无法获取持仓数据"
                }
            
            # 提取持仓量信息
            positions = []
            for _, row in df.iterrows():
                contract = row.get('合约', row.get('symbol', '未知'))
                oi = row.get('持仓量', row.get('open_interest', 0))
                oi_change = row.get('日增仓', row.get('oi_change', 0))
                
                positions.append({
                    "contract": contract,
                    "open_interest": int(oi) if pd.notna(oi) else 0,
                    "oi_change": int(oi_change) if pd.notna(oi_change) else 0
                })
            
            # 按持仓量排序
            positions.sort(key=lambda x: x['open_interest'], reverse=True)
            
            return {
                "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "symbol": symbol or "市场概览",
                "top_positions": positions[:10],
                "analysis": {
                    "total_contracts": len(positions),
                    "method": "基于持仓量变化判断资金流向",
                    "note": "持仓量增加通常表示资金流入"
                },
                "data_source": "AkShare开源数据",
                "data_quality": "实时"
            }
        
        except Exception as e:
            return {
                "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "error": f"分析失败: {str(e)}"
            }
    
    def get_main_contracts(self) -> dict:
        """获取各品种主力合约"""
        try:
            # 获取主力合约列表
            contracts = []
            
            # 常见品种
            products = ['RB', 'HC', 'I', 'J', 'JM', 'M', 'Y', 'P', 'TA', 'MA', 'SC']
            
            for product in products:
                try:
                    df = ak.futures_zh_realtime(product)
                    if df is not None and not df.empty:
                        # 按持仓量找主力
                        if '持仓量' in df.columns:
                            main = df.loc[df['持仓量'].idxmax()]
                            contracts.append({
                                "product": product,
                                "main_contract": main.get('合约', f'{product}主力'),
                                "price": main.get('最新价', 0),
                                "open_interest": main.get('持仓量', 0)
                            })
                except Exception:
                    continue
            
            return {
                "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "main_contracts": contracts,
                "data_source": "AkShare开源数据",
                "data_quality": "实时"
            }
        
        except Exception as e:
            return {
                "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "error": str(e)
            }


def main():
    parser = argparse.ArgumentParser(description="期货持仓追踪器 - AkShare数据")
    parser.add_argument("--symbol", help="合约代码 (如: RB2505)")
    parser.add_argument("--analysis", action="store_true", help="持仓变化分析")
    parser.add_argument("--main", action="store_true", help="主力合约列表")
    
    args = parser.parse_args()
    tracker = FuturesPositionTracker()
    
    if args.main:
        result = tracker.get_main_contracts()
    elif args.analysis:
        result = tracker.get_position_change_analysis(args.symbol)
    elif args.symbol:
        result = tracker.get_position_ranking(args.symbol)
    else:
        result = {
            "message": "请指定参数",
            "usage": {
                "查询持仓排名": "--symbol RB2505",
                "持仓变化分析": "--analysis --symbol RB",
                "主力合约列表": "--main"
            },
            "data_source": "AkShare开源数据"
        }
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
