#!/usr/bin/env python3
"""银行存款利率分析器 - 使用AkShare开源数据接口"""

import akshare as ak
import pandas as pd
import json
from datetime import datetime
import argparse


class BankDepositRates:
    """银行存款利率分析器 - 使用AkShare获取真实数据"""
    
    def get_rates(self, bank_name: str = None) -> dict:
        """获取存款利率 - 从AkShare获取"""
        try:
            # 使用AkShare获取存款利率
            df = ak.bank_deposit_rate()
            
            if df is None or df.empty:
                return {
                    "error": "无法从数据源获取利率数据",
                    "message": "请检查AkShare连接或数据源可用性"
                }
            
            # 转换为字典格式
            rates_data = {}
            for _, row in df.iterrows():
                bank = row.get('银行名称', '未知银行')
                rates_data[bank] = {
                    "活期": row.get('活期存款利率', 0),
                    "3月": row.get('三个月定期', 0),
                    "6月": row.get('半年定期', 0),
                    "1年": row.get('一年定期', 0),
                    "2年": row.get('两年定期', 0),
                    "3年": row.get('三年定期', 0),
                    "5年": row.get('五年定期', 0)
                }
            
            if bank_name:
                rates = rates_data.get(bank_name)
                if not rates:
                    return {
                        "error": f"未找到银行: {bank_name}",
                        "available_banks": list(rates_data.keys())[:20]
                    }
                return {
                    "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "bank_name": bank_name,
                    "rates": rates,
                    "data_source": "AkShare开源数据",
                    "data_quality": "实时"
                }
            else:
                return {
                    "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "all_banks": rates_data,
                    "total_banks": len(rates_data),
                    "data_source": "AkShare开源数据",
                    "data_quality": "实时"
                }
        
        except Exception as e:
            return {
                "error": f"获取数据失败: {str(e)}",
                "message": "AkShare接口调用失败，请检查网络连接"
            }
    
    def compare_rates(self, term: str = "3年") -> dict:
        """对比各银行某期限利率"""
        result = self.get_rates()
        
        if "error" in result:
            return result
        
        rates_data = result.get("all_banks", {})
        
        comparison = []
        for bank, rates in rates_data.items():
            rate = rates.get(term)
            if rate and rate > 0:
                comparison.append({
                    "bank": bank,
                    "rate": float(rate),
                    "rate_pct": f"{float(rate)}%"
                })
        
        comparison.sort(key=lambda x: x["rate"], reverse=True)
        
        return {
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "term": term,
            "comparison": comparison[:30],  # 取前30家
            "highest": comparison[0] if comparison else None,
            "lowest": comparison[-1] if comparison else None,
            "data_source": "AkShare开源数据",
            "data_quality": "实时"
        }
    
    def get_lpr_history(self) -> dict:
        """获取LPR历史 - 使用AkShare"""
        try:
            # 获取LPR数据
            df = ak.macro_china_lpr()
            
            if df is None or df.empty:
                return {
                    "error": "无法获取LPR数据",
                    "message": "请检查AkShare连接"
                }
            
            # 取最近12条记录
            recent = df.head(12)
            lpr_trend = []
            for _, row in recent.iterrows():
                lpr_trend.append({
                    "date": str(row.get('日期', '')),
                    "1y": f"{row.get('1年期LPR', 'N/A')}%",
                    "5y": f"{row.get('5年期以上LPR', 'N/A')}%"
                })
            
            # 最新数据
            latest = df.iloc[0] if len(df) > 0 else None
            
            return {
                "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "latest_lpr": {
                    "1年期LPR": f"{latest.get('1年期LPR', 'N/A')}%" if latest is not None else "N/A",
                    "5年期以上LPR": f"{latest.get('5年期以上LPR', 'N/A')}%" if latest is not None else "N/A",
                    "update_date": str(latest.get('日期', '')) if latest is not None else "N/A"
                },
                "lpr_trend": lpr_trend,
                "data_source": "AkShare - 中国人民银行",
                "data_quality": "官方实时数据"
            }
        
        except Exception as e:
            return {
                "error": f"获取LPR数据失败: {str(e)}",
                "message": "AkShare接口调用失败"
            }


def main():
    parser = argparse.ArgumentParser(description="银行存款利率分析器")
    parser.add_argument("--bank", help="银行名称")
    parser.add_argument("--compare", help="对比期限(如: 3年)")
    parser.add_argument("--lpr", action="store_true", help="查询LPR")
    
    args = parser.parse_args()
    analyzer = BankDepositRates()
    
    if args.lpr:
        result = analyzer.get_lpr_history()
    elif args.compare:
        result = analyzer.compare_rates(args.compare)
    else:
        result = analyzer.get_rates(args.bank)
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
