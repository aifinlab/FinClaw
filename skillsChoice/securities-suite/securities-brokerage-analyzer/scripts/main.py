#!/usr/bin/env python3
"""券商经纪业务分析器 - 使用AkShare开源数据接口"""

import akshare as ak
import pandas as pd
import json
from datetime import datetime
import argparse


class SecuritiesBrokerageAnalyzer:
    """券商经纪业务分析器 - 使用AkShare获取市场数据"""
    
    def get_market_trading(self) -> dict:
        """获取市场成交数据 - 使用AkShare"""
        try:
            # 获取A股成交额数据
            df = ak.stock_zh_a_spot_em()
            
            if df is not None and not df.empty:
                # 计算总成交额
                total_amount = df['成交额'].sum() if '成交额' in df.columns else 0
                
                # 获取主要指数
                sh_index = df[df['代码'] == '000001']
                sz_index = df[df['代码'] == '399001']
                
                return {
                    "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "market_data": {
                        "当日总成交额_亿元": round(total_amount / 1e8, 2) if total_amount else None,
                        "data_source": "AkShare - 东方财富"
                    },
                    "note": "更多历史成交数据可通过stock_zh_index_daily等接口获取",
                    "data_source": "AkShare开源数据",
                    "data_quality": "实时行情"
                }
            else:
                return {
                    "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "error": "无法获取市场数据",
                    "data_source": "AkShare"
                }
        except Exception as e:
            return {
                "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "error": f"获取数据失败: {str(e)}",
                "data_source": "AkShare"
            }
    
    def get_investor_data(self) -> dict:
        """获取投资者数据"""
        # 投资者数据AkShare暂无直接接口，返回提示
        return {
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "message": "投资者数据需从中国结算官网获取",
            "source_url": "http://www.chinaclear.cn/",
            "data_source": "需外部数据源",
            "note": "AkShare暂无投资者数据接口"
        }
    
    def get_brokerage_ranking(self) -> dict:
        """获取经纪业务排名"""
        # 经纪业务排名数据AkShare暂无直接接口
        return {
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "message": "券商经纪业务排名需从证券业协会获取",
            "source_url": "https://www.sac.net.cn/",
            "data_source": "需外部数据源",
            "note": "AkShare暂无券商排名数据接口"
        }


def main():
    parser = argparse.ArgumentParser(description="券商经纪业务分析器")
    parser.add_argument("--market", action="store_true", help="市场成交数据")
    parser.add_argument("--investor", action="store_true", help="投资者数据")
    parser.add_argument("--ranking", action="store_true", help="经纪业务排名")
    
    args = parser.parse_args()
    analyzer = SecuritiesBrokerageAnalyzer()
    
    if args.market:
        result = analyzer.get_market_trading()
    elif args.investor:
        result = analyzer.get_investor_data()
    elif args.ranking:
        result = analyzer.get_brokerage_ranking()
    else:
        result = analyzer.get_market_trading()
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
