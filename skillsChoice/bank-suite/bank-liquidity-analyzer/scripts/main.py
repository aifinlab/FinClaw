#!/usr/bin/env python3
"""银行流动性分析器 - 使用AkShare开源数据接口

功能：分析银行流动性指标、资金面状况
数据源：AkShare开源金融数据接口
说明：详细流动性指标需参考各银行定期报告
"""

import akshare as ak
import json
from datetime import datetime
import argparse


class BankLiquidityAnalyzer:
    """银行流动性分析器 - 基于市场资金面数据"""
    
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
    
    def _get_interbank_rate(self) -> dict:
        """获取银行间利率 - 使用AkShare"""
        try:
            df = ak.macro_china_interbank_rate()
            if df is not None and not df.empty:
                latest = df.iloc[-1]
                return {
                    "隔夜利率": latest.get('隔夜', 'N/A'),
                    "7天利率": latest.get('7天', 'N/A'),
                    "1个月利率": latest.get('1个月', 'N/A'),
                    "data_source": "AkShare - 银行间同业拆借"
                }
        except Exception:
            return None
        return None
    
    def _get_shibor(self) -> dict:
        """获取Shibor数据 - 使用AkShare"""
        try:
            df = ak.macro_china_shibor_all()
            if df is not None and not df.empty:
                latest = df.iloc[-1]
                return {
                    "隔夜": latest.get('隔夜', 'N/A'),
                    "1周": latest.get('1周', 'N/A'),
                    "1个月": latest.get('1个月', 'N/A'),
                    "3个月": latest.get('3个月', 'N/A'),
                    "data_source": "AkShare - Shibor"
                }
        except Exception:
            return None
        return None
    
    def analyze_liquidity(self, bank_name: str = None) -> dict:
        """分析银行流动性 - 基于市场资金面数据"""
        result = {
            "query_time": self.query_time,
            "analysis_type": "银行流动性分析",
            "note": "详细流动性指标需参考各银行定期报告"
        }
        
        # 获取市场资金面数据
        interbank = self._get_interbank_rate()
        if interbank:
            result["interbank_market"] = interbank
        
        shibor = self._get_shibor()
        if shibor:
            result["shibor"] = shibor
        
        # 如果指定了银行，获取该银行行情
        if bank_name:
            code = self.BANK_CODES.get(bank_name)
            if not code:
                return {
                    "error": f"未找到银行: {bank_name}",
                    "available_banks": list(self.BANK_CODES.keys())
                }
            
            stock_data = self._get_realtime_data(code)
            if stock_data:
                result["bank"] = {
                    "name": bank_name,
                    "code": code,
                    "price": stock_data.get("price"),
                    "change_pct": f"{stock_data.get('change_pct')}%" if stock_data.get('change_pct') else None,
                    "pb": stock_data.get("pb")
                }
                
                # 基于PB估值的流动性推断
                pb = stock_data.get("pb")
                if pb:
                    if pb < 0.6:
                        result["liquidity_assessment"] = "估值较低，关注流动性状况"
                    elif pb < 0.8:
                        result["liquidity_assessment"] = "估值偏低"
                    else:
                        result["liquidity_assessment"] = "估值合理"
        else:
            # 返回所有银行行情
            banks = []
            for name, code in self.BANK_CODES.items():
                stock_data = self._get_realtime_data(code)
                if stock_data:
                    banks.append({
                        "name": name,
                        "code": code,
                        "price": stock_data.get("price"),
                        "pb": stock_data.get("pb")
                    })
            
            banks.sort(key=lambda x: x.get("pb") or 999)
            result["banks"] = banks[:10]
        
        result["liquidity_indicators"] = {
            "监管指标说明": {
                "流动性覆盖率_LCR": "≥100%，优质流动性资产/未来30日净现金流出",
                "净稳定资金比例_NSFR": "≥100%，可用稳定资金/所需稳定资金",
                "存贷比_LDR": "观察指标，贷款/存款",
                "流动性比例": "≥25%，流动性资产/流动性负债"
            },
            "关注要点": [
                "LCR和NSFR是否达标",
                "存贷比是否处于合理区间",
                "市场资金面松紧程度",
                "央行货币政策动向"
            ],
            "数据来源说明": "详细流动性指标参考各银行年报/季报"
        }
        
        result["data_source"] = "AkShare开源数据 + 行业分析"
        result["data_quality"] = "实时市场数据 + 定性分析"
        
        return result


def main():
    parser = argparse.ArgumentParser(description="银行流动性分析器")
    parser.add_argument("--bank", help="银行名称")
    
    args = parser.parse_args()
    analyzer = BankLiquidityAnalyzer()
    result = analyzer.analyze_liquidity(args.bank)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
