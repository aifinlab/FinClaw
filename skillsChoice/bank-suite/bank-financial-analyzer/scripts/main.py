#!/usr/bin/env python3
"""
商业银行财务分析器
深度分析上市银行的财务报表和核心指标
"""

import os
import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime
import json
import argparse


class BankFinancialAnalyzer:
    """商业银行财务分析器"""
    
    # A股上市银行代码映射
    BANK_CODES = {
        # 国有大行
        "工商银行": "601398",
        "农业银行": "601288",
        "中国银行": "601988",
        "建设银行": "601939",
        "交通银行": "601328",
        "邮储银行": "601658",
        # 股份制银行
        "招商银行": "600036",
        "兴业银行": "601166",
        "浦发银行": "600000",
        "中信银行": "601998",
        "民生银行": "600016",
        "光大银行": "601818",
        "平安银行": "000001",
        "华夏银行": "600015",
        "浙商银行": "601916",
        # 主要城商行
        "北京银行": "601169",
        "上海银行": "601229",
        "江苏银行": "600919",
        "南京银行": "601009",
        "宁波银行": "002142",
        "杭州银行": "600926",
        "成都银行": "601838",
        "长沙银行": "601577",
        "重庆银行": "601963",
        "贵阳银行": "601997",
        "苏州银行": "002966",
        "郑州银行": "002936",
        "青岛银行": "002948",
        "西安银行": "600928",
        "厦门银行": "601187",
    }
    
    def __init__(self):
        self.tushare_token = os.getenv("TUSHARE_TOKEN", "")
        self.ths_token = os.getenv("THS_ACCESS_TOKEN", "")
    
    def get_bank_code(self, bank_name: str) -> str:
        """根据银行名称获取股票代码"""
        # 直接匹配
        if bank_name in self.BANK_CODES:
            return self.BANK_CODES[bank_name]
        
        # 模糊匹配
        for name, code in self.BANK_CODES.items():
            if bank_name in name or name in bank_name:
                return code
        
        # 尝试使用akshare搜索
        try:
            df = ak.stock_zh_a_spot_em()
            mask = df['名称'].str.contains(bank_name, na=False)
            if mask.any():
                return df[mask].iloc[0]['代码']
        except:
            pass
        
        return None
    
    def analyze_bank(self, bank_name: str) -> dict:
        """
        深度分析单家银行
        """
        code = self.get_bank_code(bank_name)
        if not code:
            return {"error": f"未找到银行: {bank_name}"}
        
        result = {
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "bank_name": bank_name,
            "stock_code": code,
            "analysis": {}
        }
        
        try:
            # 获取实时行情
            result["realtime"] = self._get_realtime_quote(code)
            
            # 获取财务指标
            result["financial_indicators"] = self._get_financial_indicators(code)
            
            # 获取资产负债表摘要
            result["balance_sheet"] = self._get_balance_sheet_summary(code)
            
            # 获取利润表摘要
            result["income_statement"] = self._get_income_summary(code)
            
            # 计算核心指标
            result["core_metrics"] = self._calculate_core_metrics(result)
            
            # 综合评价
            result["assessment"] = self._assess_bank(result)
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def compare_banks(self, bank_names: list) -> dict:
        """
        对比多家银行
        """
        results = []
        for name in bank_names:
            analysis = self.analyze_bank(name.strip())
            if "error" not in analysis:
                results.append({
                    "name": name,
                    "code": analysis.get("stock_code"),
                    "metrics": analysis.get("core_metrics", {}),
                    "realtime": analysis.get("realtime", {})
                })
        
        # 构建对比表
        comparison = {
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "banks": [r["name"] for r in results],
            "comparison": {}
        }
        
        if results:
            # 提取共同指标进行对比
            metrics_keys = results[0]["metrics"].keys()
            for key in metrics_keys:
                comparison["comparison"][key] = {
                    r["name"]: r["metrics"].get(key, "N/A") for r in results
                }
        
        return comparison
    
    def get_financial_trend(self, code: str, metric: str = "ROE", periods: int = 8) -> dict:
        """
        获取财务指标历史趋势
        """
        try:
            # 获取历史财务数据
            df = ak.stock_financial_analysis_indicator(symbol=code)
            
            if df is None or df.empty:
                return {"error": "无法获取财务数据"}
            
            # 映射指标名称
            metric_map = {
                "ROE": "净资产收益率",
                "ROA": "总资产收益率",
                "NIM": "净息差",
                "EPS": "基本每股收益"
            }
            
            col_name = metric_map.get(metric, metric)
            
            if col_name not in df.columns:
                return {"error": f"未找到指标: {metric}"}
            
            # 提取最近N期数据
            recent_data = df.head(periods)[["报告期", col_name]].copy()
            recent_data = recent_data.sort_values("报告期")
            
            return {
                "stock_code": code,
                "metric": metric,
                "metric_name": col_name,
                "periods": periods,
                "data": recent_data.to_dict('records'),
                "trend": self._analyze_trend(recent_data[col_name])
            }
            
        except Exception as e:
            return {"error": f"获取趋势失败: {str(e)}"}
    
    def _get_realtime_quote(self, code: str) -> dict:
        """获取实时行情"""
        try:
            df = ak.stock_zh_a_spot_em()
            stock = df[df['代码'] == code]
            
            if stock.empty:
                return {}
            
            s = stock.iloc[0]
            return {
                "price": s.get('最新价'),
                "change_pct": s.get('涨跌幅'),
                "volume": s.get('成交量'),
                "market_cap": s.get('总市值'),
                "pb": s.get('市净率'),
                "pe": s.get('市盈率')
            }
        except:
            return {}
    
    def _get_financial_indicators(self, code: str) -> dict:
        """获取财务指标"""
        try:
            df = ak.stock_financial_analysis_indicator(symbol=code)
            
            if df is None or df.empty:
                return {}
            
            latest = df.iloc[0]
            
            return {
                "roe": latest.get('净资产收益率'),
                "roa": latest.get('总资产收益率'),
                "eps": latest.get('基本每股收益'),
                "bvps": latest.get('每股净资产'),
                "report_date": latest.get('报告期')
            }
        except:
            return {}
    
    def _get_balance_sheet_summary(self, code: str) -> dict:
        """获取资产负债表摘要"""
        try:
            # 使用AkShare获取资产负债表
            df = ak.stock_balance_sheet_by_report_em(symbol=code)
            
            if df is None or df.empty:
                return {}
            
            latest = df.iloc[0]
            
            return {
                "total_assets": latest.get('资产总计'),
                "total_liabilities": latest.get('负债合计'),
                "total_equity": latest.get('所有者权益合计'),
                "deposits": latest.get('吸收存款'),
                "loans": latest.get('发放贷款和垫款'),
                "report_date": latest.get('报告期')
            }
        except:
            return {}
    
    def _get_income_summary(self, code: str) -> dict:
        """获取利润表摘要"""
        try:
            df = ak.stock_profit_sheet_by_report_em(symbol=code)
            
            if df is None or df.empty:
                return {}
            
            latest = df.iloc[0]
            
            return {
                "total_revenue": latest.get('营业总收入'),
                "net_profit": latest.get('净利润'),
                "net_interest_income": latest.get('利息净收入'),
                "fee_income": latest.get('手续费及佣金收入'),
                "report_date": latest.get('报告期')
            }
        except:
            return {}
    
    def _calculate_core_metrics(self, analysis: dict) -> dict:
        """计算核心指标"""
        metrics = {}
        
        realtime = analysis.get("realtime", {})
        indicators = analysis.get("financial_indicators", {})
        income = analysis.get("income_statement", {})
        
        # 从财务指标直接获取
        if indicators.get("roe"):
            metrics["ROE"] = f"{indicators['roe']}%"
        if indicators.get("roa"):
            metrics["ROA"] = f"{indicators['roa']}%"
        
        # 估值指标
        if realtime.get("pb"):
            metrics["PB"] = realtime["pb"]
        if realtime.get("pe"):
            metrics["PE"] = realtime["pe"]
        
        # 计算收入结构
        total_revenue = income.get("total_revenue")
        fee_income = income.get("fee_income")
        if total_revenue and fee_income:
            try:
                fee_ratio = float(fee_income) / float(total_revenue) * 100
                metrics["非息收入占比"] = f"{fee_ratio:.2f}%"
            except:
                pass
        
        return metrics
    
    def _assess_bank(self, analysis: dict) -> dict:
        """综合评价银行"""
        assessment = {
            "rating": "",
            "strengths": [],
            "concerns": []
        }
        
        metrics = analysis.get("core_metrics", {})
        
        # ROE评价
        roe_str = metrics.get("ROE", "0%").replace("%", "")
        try:
            roe = float(roe_str)
            if roe >= 15:
                assessment["strengths"].append("ROE优秀，盈利能力强")
            elif roe >= 10:
                assessment["rating"] = "良好"
            else:
                assessment["concerns"].append("ROE偏低，盈利能力待提升")
        except:
            pass
        
        # PB评价
        pb = metrics.get("PB")
        if pb and float(pb) < 0.8:
            assessment["concerns"].append("PB低于0.8，可能存在估值折价")
        
        if not assessment["rating"]:
            assessment["rating"] = "中等"
        
        return assessment
    
    def _analyze_trend(self, series: pd.Series) -> str:
        """分析趋势"""
        try:
            values = series.dropna().astype(float)
            if len(values) >= 2:
                if values.iloc[-1] > values.iloc[0]:
                    return "上升"
                elif values.iloc[-1] < values.iloc[0]:
                    return "下降"
                else:
                    return "平稳"
        except:
            pass
        return "未知"


def main():
    parser = argparse.ArgumentParser(description="商业银行财务分析器")
    parser.add_argument("--bank", help="银行名称")
    parser.add_argument("--banks", help="多家银行，逗号分隔")
    parser.add_argument("--code", help="股票代码")
    parser.add_argument("--action", choices=["analyze", "compare", "trend"],
                       default="analyze", help="操作类型")
    parser.add_argument("--metric", default="ROE", help="趋势分析指标")
    parser.add_argument("--output", help="输出文件")
    
    args = parser.parse_args()
    
    analyzer = BankFinancialAnalyzer()
    
    if args.action == "analyze" and args.bank:
        result = analyzer.analyze_bank(args.bank)
    elif args.action == "compare" and args.banks:
        bank_list = args.banks.split(",")
        result = analyzer.compare_banks(bank_list)
    elif args.action == "trend" and args.code:
        result = analyzer.get_financial_trend(args.code, args.metric)
    else:
        result = {"error": "参数不足，请检查输入"}
    
    output = json.dumps(result, ensure_ascii=False, indent=2)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"结果已保存: {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
