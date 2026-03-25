#!/usr/bin/env python3
"""银行净息差(NIM)分析器 - 使用AkShare开源数据接口

功能：分析银行净息差、生息资产收益率、负债成本
数据源：AkShare开源金融数据接口
说明：详细NIM数据需参考各银行定期报告
"""

import akshare as ak
import json
from datetime import datetime
import argparse


class BankNIMAnalyzer:
    """银行净息差分析器 - 基于上市银行实时行情"""
    
    # 银行名称到股票代码映射
    BANK_CODES = {
        "招商银行": "600036", "工商银行": "601398", "建设银行": "601939",
        "农业银行": "601288", "中国银行": "601988", "交通银行": "601328",
        "邮储银行": "601658", "兴业银行": "601166", "平安银行": "000001",
        "宁波银行": "002142", "南京银行": "601009", "江苏银行": "600919"
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
    
    def _get_lpr_data(self) -> dict:
        """获取LPR数据 - 使用AkShare"""
        try:
            df = ak.macro_china_lpr()
            if df is not None and not df.empty:
                latest = df.iloc[0]
                return {
                    "LPR_1Y": latest.get('1年期', 'N/A'),
                    "LPR_5Y": latest.get('5年期', 'N/A'),
                    "data_source": "AkShare - 中国人民银行"
                }
        except Exception:
            return None
        return None
    
    def analyze_nim(self, bank_name: str) -> dict:
        """分析银行净息差 - 基于市场利率环境"""
        code = self.BANK_CODES.get(bank_name)
        if not code:
            return {
                "error": f"未找到银行: {bank_name}",
                "available_banks": list(self.BANK_CODES.keys())
            }
        
        result = {
            "query_time": self.query_time,
            "bank_name": bank_name,
            "stock_code": code,
            "note": "详细NIM数据需查阅各银行定期报告"
        }
        
        # 获取实时行情
        stock_data = self._get_realtime_data(code)
        if stock_data:
            result["market_data"] = {
                "price": stock_data.get("price"),
                "change_pct": f"{stock_data.get('change_pct')}%" if stock_data.get('change_pct') else None,
                "pb": stock_data.get("pb")
            }
        
        # 获取LPR数据
        lpr_data = self._get_lpr_data()
        if lpr_data:
            result["interest_rate_environment"] = lpr_data
        
        result["nim_analysis"] = {
            "净息差影响因素": [
                "LPR下行导致资产端收益率下降",
                "存款竞争激烈，负债成本刚性",
                "贷款重定价周期影响",
                "资产负债结构调整"
            ],
            "NIM趋势判断": "行业整体面临息差收窄压力",
            "不同类型银行特点": {
                "国有大行": "负债成本低，NIM相对稳定",
                "股份行": "负债成本较高，NIM承压明显",
                "城商行": "区位优势，NIM分化较大"
            },
            "关注要点": [
                "生息资产收益率变化",
                "计息负债成本率变化",
                "资产负债久期匹配",
                "存款结构优化"
            ],
            "数据来源说明": "详细NIM数据参考各银行年报/季报"
        }
        
        result["data_source"] = "AkShare开源数据 + 行业分析"
        result["data_quality"] = "实时行情 + 定性分析"
        
        return result
    
    def compare_nim(self, bank_names: list = None) -> dict:
        """对比银行NIM - 基于实时行情"""
        if bank_names is None:
            bank_names = list(self.BANK_CODES.keys())[:8]
        
        results = []
        for name in bank_names:
            code = self.BANK_CODES.get(name)
            if not code:
                continue
            
            stock_data = self._get_realtime_data(code)
            if stock_data:
                results.append({
                    "name": name,
                    "code": code,
                    "price": stock_data.get("price"),
                    "pb": stock_data.get("pb")
                })
        
        # 按PB排序
        results.sort(key=lambda x: x.get("pb") or 999)
        
        result = {
            "query_time": self.query_time,
            "nim_comparison_note": "NIM详细数据需查阅各银行定期报告",
            "banks": results,
            "total_banks": len(results)
        }
        
        # 获取LPR数据
        lpr_data = self._get_lpr_data()
        if lpr_data:
            result["interest_rate_environment"] = lpr_data
        
        result["comparison_analysis"] = {
            "NIM差异原因": [
                "负债结构差异（存款占比、成本）",
                "资产结构差异（贷款占比、收益率）",
                "客户结构差异（对公/零售占比）",
                "区域布局差异"
            ],
            "投资建议": "关注负债成本管控能力强、资产质量稳健的银行"
        }
        
        result["data_source"] = "AkShare开源数据 + 行业分析"
        result["data_quality"] = "实时行情 + 定性分析"
        
        return result


def main():
    parser = argparse.ArgumentParser(description="银行NIM分析器")
    parser.add_argument("--bank", help="银行名称")
    parser.add_argument("--compare", action="store_true", help="对比NIM")
    
    args = parser.parse_args()
    analyzer = BankNIMAnalyzer()
    
    if args.compare:
        result = analyzer.compare_nim()
    elif args.bank:
        result = analyzer.analyze_nim(args.bank)
    else:
        result = {
            "error": "请指定--bank或--compare",
            "available_banks": list(analyzer.BANK_CODES.keys())
        }
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
