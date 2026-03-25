#!/usr/bin/env python3
"""银行股估值分析器 - 使用AkShare开源数据接口"""

import akshare as ak
import pandas as pd
import json
from datetime import datetime
import argparse


class BankValuationAnalyzer:
    """银行股估值分析器 - 使用AkShare获取实时行情"""
    
    # 银行名称到股票代码映射
    BANK_CODES = {
        "招商银行": "600036", "工商银行": "601398", "建设银行": "601939",
        "农业银行": "601288", "中国银行": "601988", "交通银行": "601328",
        "邮储银行": "601658", "兴业银行": "601166", "浦发银行": "600000",
        "中信银行": "601998", "民生银行": "600016", "光大银行": "601818",
        "平安银行": "000001", "华夏银行": "600015", "浙商银行": "601916",
        "北京银行": "601169", "上海银行": "601229", "江苏银行": "600919",
        "南京银行": "601009", "宁波银行": "002142", "杭州银行": "600926"
    }
    
    def _get_realtime_quote(self, code: str) -> dict:
        """从AkShare获取实时行情"""
        try:
            df = ak.stock_zh_a_spot_em()
            stock_row = df[df['代码'] == code]
            
            if stock_row.empty:
                return None
            
            return {
                "price": float(stock_row['最新价'].values[0]) if '最新价' in stock_row.columns else None,
                "pb": float(stock_row['市净率'].values[0]) if '市净率' in stock_row.columns else None,
                "pe": float(stock_row['市盈率-动态'].values[0]) if '市盈率-动态' in stock_row.columns else None,
                "total_mv": float(stock_row['总市值'].values[0]) if '总市值' in stock_row.columns else None,
                "circ_mv": float(stock_row['流通市值'].values[0]) if '流通市值' in stock_row.columns else None,
                "turnover": float(stock_row['换手率'].values[0]) if '换手率' in stock_row.columns else None,
                "volume": int(stock_row['成交量'].values[0]) if '成交量' in stock_row.columns else None
            }
        except Exception as e:
            return None
    
    def analyze_valuation(self, bank_name: str) -> dict:
        """分析银行估值 - 使用AkShare实时数据"""
        code = self.BANK_CODES.get(bank_name)
        if not code:
            return {
                "error": f"未找到银行: {bank_name}",
                "available_banks": list(self.BANK_CODES.keys())
            }
        
        result = {
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "bank_name": bank_name,
            "stock_code": code
        }
        
        # 获取实时行情
        realtime = self._get_realtime_quote(code)
        
        if realtime:
            result["valuation_metrics"] = {
                "股价": realtime.get("price"),
                "市净率_PB": realtime.get("pb"),
                "市盈率_PE": realtime.get("pe"),
                "总市值_亿元": round(realtime.get("total_mv") / 1e8, 2) if realtime.get("total_mv") else None,
                "流通市值_亿元": round(realtime.get("circ_mv") / 1e8, 2) if realtime.get("circ_mv") else None,
                "换手率": realtime.get("turnover"),
                "成交量": realtime.get("volume")
            }
            result["data_source"] = "AkShare - 东方财富"
            result["data_quality"] = "实时行情"
            
            # 估值评价
            pb = realtime.get("pb")
            if pb:
                if pb < 0.5:
                    result["valuation_assessment"] = "深度破净，存在估值修复空间"
                    result["rating"] = "深度低估"
                elif pb < 0.6:
                    result["valuation_assessment"] = "严重破净，关注基本面改善"
                    result["rating"] = "低估"
                elif pb < 0.9:
                    result["valuation_assessment"] = "破净，具备配置价值"
                    result["rating"] = "偏低"
                elif pb > 1.2:
                    result["valuation_assessment"] = "估值溢价，质地优秀"
                    result["rating"] = "溢价"
                else:
                    result["valuation_assessment"] = "估值合理"
                    result["rating"] = "合理"
        else:
            result["error"] = "无法获取实时行情数据"
        
        return result
    
    def compare_valuation(self, bank_names: list = None) -> dict:
        """对比银行股估值 - 使用AkShare实时数据"""
        if bank_names is None:
            bank_names = list(self.BANK_CODES.keys())[:10]
        
        results = []
        for name in bank_names:
            code = self.BANK_CODES.get(name)
            if not code:
                continue
            
            realtime = self._get_realtime_quote(code)
            if realtime:
                results.append({
                    "name": name,
                    "code": code,
                    "price": realtime.get("price"),
                    "pb": realtime.get("pb"),
                    "pe": realtime.get("pe"),
                    "total_mv_yi": round(realtime.get("total_mv") / 1e8, 2) if realtime.get("total_mv") else None
                })
        
        # 按PB排序
        results.sort(key=lambda x: x.get("pb") or 999)
        
        # 计算行业平均
        valid_pb = [r["pb"] for r in results if r.get("pb")]
        avg_pb = sum(valid_pb) / len(valid_pb) if valid_pb else 0
        
        return {
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "valuation_ranking": results,
            "cheapest_pb": results[0] if results else None,
            "highest_pb": results[-1] if results else None,
            "industry_avg_pb": f"{avg_pb:.2f}",
            "total_banks": len(results),
            "data_source": "AkShare - 东方财富",
            "data_quality": "实时行情"
        }


def main():
    parser = argparse.ArgumentParser(description="银行股估值分析器")
    parser.add_argument("--bank", help="银行名称")
    parser.add_argument("--compare", action="store_true", help="对比所有银行")
    
    args = parser.parse_args()
    analyzer = BankValuationAnalyzer()
    
    if args.compare:
        result = analyzer.compare_valuation()
    elif args.bank:
        result = analyzer.analyze_valuation(args.bank)
    else:
        result = {
            "error": "请指定--bank或--compare",
            "available_banks": list(analyzer.BANK_CODES.keys())
        }
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
