#!/usr/bin/env python3
"""券商自营业务分析器 - 使用AkShare开源数据接口

功能：分析券商自营业务表现、投资收益情况
数据源：AkShare开源金融数据接口
说明：详细自营数据需参考各券商定期报告
"""

import akshare as ak
import json
from datetime import datetime
import argparse


class SecuritiesProprietaryAnalyzer:
    """券商自营业务分析器 - 基于上市券商行情"""
    
    SECURITIES_CODES = {
        "中信证券": "600030", "华泰证券": "601688", "海通证券": "600837",
        "国泰君安": "601211", "招商证券": "600999", "广发证券": "000776",
        "中国银河": "601881", "中信建投": "601066", "东方证券": "600958",
        "兴业证券": "601377", "东方财富": "300059"
    }
    
    def __init__(self):
        self.query_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _get_realtime_data(self, code: str) -> dict:
        """获取实时行情 - 使用AkShare"""
        try:
            df = ak.stock_zh_a_spot_em()
            stock_row = df[df['代码'] == code]
            
            if stock_row.empty:
                return None
            
            return {
                "price": float(stock_row['最新价'].values[0]) if '最新价' in stock_row.columns else None,
                "change_pct": float(stock_row['涨跌幅'].values[0]) if '涨跌幅' in stock_row.columns else None,
                "pb": float(stock_row['市净率'].values[0]) if '市净率' in stock_row.columns else None,
                "total_mv": float(stock_row['总市值'].values[0]) if '总市值' in stock_row.columns else None
            }
        except Exception:
            return None
    
    def _get_index_data(self) -> dict:
        """获取市场指数数据 - 使用AkShare"""
        try:
            # 获取沪深300数据
            df = ak.index_zh_a_hist(symbol="000300", period="daily",
                                   start_date="20240101", end_date=datetime.now().strftime("%Y%m%d"))
            if df is not None and not df.empty:
                latest = df.iloc[-1]
                first = df.iloc[0]
                ytd_return = (latest['收盘'] - first['收盘']) / first['收盘'] * 100
                return {
                    "沪深300点位": latest.get('收盘'),
                    "沪深300_YTD涨跌幅": f"{ytd_return:.2f}%",
                    "data_source": "AkShare - 东方财富"
                }
        except Exception:
            return None
        return None
    
    def analyze_proprietary(self, name: str) -> dict:
        """分析券商自营业务 - 基于市场行情"""
        code = self.SECURITIES_CODES.get(name)
        if not code:
            return {
                "error": f"未找到券商: {name}",
                "available_securities": list(self.SECURITIES_CODES.keys())
            }
        
        result = {
            "query_time": self.query_time,
            "securities_name": name,
            "stock_code": code,
            "note": "详细自营数据需查阅各券商定期报告"
        }
        
        # 获取实时行情
        stock_data = self._get_realtime_data(code)
        if stock_data:
            result["market_data"] = {
                "price": stock_data.get("price"),
                "change_pct": f"{stock_data.get('change_pct')}%" if stock_data.get('change_pct') else None,
                "pb": stock_data.get("pb")
            }
        
        # 获取市场指数数据
        index_data = self._get_index_data()
        if index_data:
            result["market_environment"] = index_data
        
        result["proprietary_analysis"] = {
            "自营业务构成": [
                "权益类投资（股票、基金）",
                "固定收益投资（债券）",
                "衍生品投资",
                "做市业务",
                "另类投资"
            ],
            "影响因素": [
                "A股市场整体表现",
                "债券市场利率走势",
                "衍生品市场活跃度",
                "科创板/北交所做市机会"
            ],
            "关注要点": [
                "自营收入占比",
                "投资收益率",
                "风险敞口控制",
                "去方向化转型进展"
            ],
            "数据来源说明": "详细自营数据参考各券商年报/季报"
        }
        
        result["data_source"] = "AkShare开源数据 + 行业分析"
        result["data_quality"] = "实时行情 + 定性分析"
        
        return result
    
    def compare_proprietary(self) -> dict:
        """对比券商自营业务 - 基于市场行情"""
        results = []
        
        for name, code in self.SECURITIES_CODES.items():
            stock_data = self._get_realtime_data(code)
            if stock_data:
                results.append({
                    "name": name,
                    "code": code,
                    "price": stock_data.get("price"),
                    "change_pct": f"{stock_data.get('change_pct')}%" if stock_data.get('change_pct') else None,
                    "pb": stock_data.get("pb")
                })
        
        # 按涨跌幅排序
        results.sort(key=lambda x: float(x.get("change_pct", "0%").replace("%", "")) if x.get("change_pct") else 0, reverse=True)
        
        result = {
            "query_time": self.query_time,
            "comparison_note": "自营业务详细数据需查阅各券商定期报告",
            "securities": results
        }
        
        # 获取市场指数
        index_data = self._get_index_data()
        if index_data:
            result["market_environment"] = index_data
        
        result["comparison_analysis"] = {
            "自营差异原因": [
                "投资规模和结构差异",
                "风险偏好的不同",
                "去方向化转型进度",
                "衍生品业务开展情况"
            ],
            "投资建议": "关注自营收入稳定、去方向化转型领先的券商"
        }
        
        result["data_source"] = "AkShare开源数据 + 行业分析"
        result["data_quality"] = "实时行情 + 定性分析"
        
        return result


def main():
    parser = argparse.ArgumentParser(description="券商自营业务分析器")
    parser.add_argument("--securities", help="券商名称")
    parser.add_argument("--compare", action="store_true", help="对比")
    
    args = parser.parse_args()
    analyzer = SecuritiesProprietaryAnalyzer()
    
    if args.compare:
        result = analyzer.compare_proprietary()
    elif args.securities:
        result = analyzer.analyze_proprietary(args.securities)
    else:
        result = {
            "error": "请指定--securities或--compare",
            "available_securities": list(analyzer.SECURITIES_CODES.keys())
        }
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
