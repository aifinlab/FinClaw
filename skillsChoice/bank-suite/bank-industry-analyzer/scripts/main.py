#!/usr/bin/env python3
"""
银行业宏观分析器
获取银行业整体数据，包括资产规模、存贷款、利润、资产质量等指标
"""

import akshare as ak
import pandas as pd
import requests
from datetime import datetime, timedelta
import json
import argparse


class BankIndustryAnalyzer:
    """银行业宏观分析器"""
    
    def __init__(self):
        self.data_cache = {}
    
    def get_industry_overview(self) -> dict:
        """
        获取银行业概览数据
        包括：机构数量、资产规模、存贷款余额等
        """
        try:
            # 获取银行业金融机构资产负债表
            # AkShare提供银行业总体数据
            df_assets = ak.bank_total_banking_institution()
            
            latest = df_assets.iloc[-1] if not df_assets.empty else {}
            
            result = {
                "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "data_type": "银行业概览",
                "indicators": {
                    "total_assets": {
                        "value": latest.get("总资产", "N/A"),
                        "unit": "万亿元",
                        "description": "银行业金融机构总资产"
                    },
                    "total_liabilities": {
                        "value": latest.get("总负债", "N/A"),
                        "unit": "万亿元",
                        "description": "银行业金融机构总负债"
                    },
                    "deposit_balance": {
                        "value": latest.get("各项存款", "N/A"),
                        "unit": "万亿元",
                        "description": "各项存款余额"
                    },
                    "loan_balance": {
                        "value": latest.get("各项贷款", "N/A"),
                        "unit": "万亿元",
                        "description": "各项贷款余额"
                    }
                },
                "data_source": "AkShare - 银行业金融机构资产负债表",
                "note": "数据来源于中国人民银行统计数据"
            }
            return result
            
        except Exception as e:
            return self._get_fallback_overview(str(e))
    
    def get_asset_quality(self) -> dict:
        """
        获取银行业资产质量数据
        包括：不良率、拨备覆盖率、资本充足率等
        """
        try:
            # 使用AkShare获取银行业资产质量指标
            # 注意：这里使用AkShare的宏观经济数据接口
            
            # 尝试获取不良贷款率数据
            df_npl = ak.macro_china_npl_ratio()
            
            if df_npl is not None and not df_npl.empty:
                latest = df_npl.iloc[-1]
                result = {
                    "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "data_type": "银行业资产质量",
                    "indicators": {
                        "npl_ratio": {
                            "value": f"{latest.get('不良贷款率', 'N/A')}%",
                            "description": "商业银行不良贷款率",
                            "benchmark": "<5%"
                        },
                        "provision_coverage": {
                            "value": f"{latest.get('拨备覆盖率', 'N/A')}%",
                            "description": "拨备覆盖率",
                            "benchmark": ">150%"
                        },
                        "capital_adequacy": {
                            "value": f"{latest.get('资本充足率', 'N/A')}%",
                            "description": "资本充足率",
                            "benchmark": ">10.5%"
                        }
                    },
                    "data_source": "国家金融监督管理总局",
                    "analysis": self._analyze_asset_quality(latest)
                }
                return result
            else:
                return self._get_fallback_asset_quality("无数据")
                
        except Exception as e:
            return self._get_fallback_asset_quality(str(e))
    
    def get_monetary_policy(self, year: int = None) -> dict:
        """
        获取货币政策数据
        包括：存款准备金率、LPR利率等
        """
        try:
            if year is None:
                year = datetime.now().year
            
            # 获取LPR数据
            df_lpr = ak.macro_china_lpr()
            
            # 获取存款准备金率数据
            df_rrr = ak.macro_china_reserve_requirement_ratio()
            
            result = {
                "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "data_type": "货币政策",
                "year": year,
                "indicators": {}
            }
            
            # 处理LPR数据
            if df_lpr is not None and not df_lpr.empty:
                latest_lpr = df_lpr.iloc[-1]
                result["indicators"]["lpr_1y"] = {
                    "value": f"{latest_lpr.get('1年期LPR', 'N/A')}%",
                    "description": "1年期贷款市场报价利率",
                    "trend": self._get_trend(df_lpr, '1年期LPR')
                }
                result["indicators"]["lpr_5y"] = {
                    "value": f"{latest_lpr.get('5年期LPR', 'N/A')}%",
                    "description": "5年期以上贷款市场报价利率",
                    "trend": self._get_trend(df_lpr, '5年期LPR')
                }
            
            # 处理存款准备金率数据
            if df_rrr is not None and not df_rrr.empty:
                latest_rrr = df_rrr.iloc[-1]
                result["indicators"]["rrr_large"] = {
                    "value": f"{latest_rrr.get('大型金融机构', 'N/A')}%",
                    "description": "大型金融机构存款准备金率"
                }
                result["indicators"]["rrr_small"] = {
                    "value": f"{latest_rrr.get('中小金融机构', 'N/A')}%",
                    "description": "中小金融机构存款准备金率"
                }
            
            result["data_source"] = "中国人民银行"
            result["analysis"] = self._analyze_monetary_policy(result["indicators"])
            
            return result
            
        except Exception as e:
            return self._get_fallback_monetary_policy(str(e))
    
    def get_deposit_loan_growth(self) -> dict:
        """获取存贷款增长数据"""
        try:
            # 获取金融机构人民币信贷收支表
            df = ak.macro_china_financial_institution_deposit()
            
            if df is not None and not df.empty:
                latest = df.iloc[-1]
                
                result = {
                    "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "data_type": "存贷款增长",
                    "indicators": {
                        "deposit_yoy": {
                            "value": f"{latest.get('存款同比', 'N/A')}%",
                            "description": "各项存款同比增速"
                        },
                        "loan_yoy": {
                            "value": f"{latest.get('贷款同比', 'N/A')}%",
                            "description": "各项贷款同比增速"
                        }
                    },
                    "data_source": "中国人民银行",
                    "historical_trend": df.tail(12).to_dict('records') if len(df) >= 12 else df.to_dict('records')
                }
                return result
            else:
                return {"error": "无法获取存贷款增长数据"}
                
        except Exception as e:
            return {"error": f"获取存贷款增长数据失败: {str(e)}"}
    
    def generate_report(self) -> str:
        """生成银行业宏观分析报告"""
        overview = self.get_industry_overview()
        asset_quality = self.get_asset_quality()
        monetary = self.get_monetary_policy()
        
        report_lines = [
            "=" * 60,
            "银行业宏观分析报告",
            f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 60,
            "",
            "【一、行业概览】",
            json.dumps(overview, ensure_ascii=False, indent=2),
            "",
            "【二、资产质量】",
            json.dumps(asset_quality, ensure_ascii=False, indent=2),
            "",
            "【三、货币政策环境】",
            json.dumps(monetary, ensure_ascii=False, indent=2),
            "",
            "=" * 60,
            "数据来源: 中国人民银行、国家金融监督管理总局、AkShare",
            "=" * 60
        ]
        
        return "\n".join(report_lines)
    
    def _analyze_asset_quality(self, data: pd.Series) -> str:
        """分析资产质量"""
        try:
            npl_ratio = float(data.get('不良贷款率', 0))
            provision = float(data.get('拨备覆盖率', 0))
            
            if npl_ratio < 1.5 and provision > 200:
                return "资产质量优良，风险抵补能力充足"
            elif npl_ratio < 2 and provision > 150:
                return "资产质量良好，风险抵补能力适中"
            else:
                return "需关注资产质量变化"
        except:
            return "分析数据不足"
    
    def _analyze_monetary_policy(self, indicators: dict) -> str:
        """分析货币政策环境"""
        analysis = []
        
        if "lpr_1y" in indicators:
            lpr_1y = indicators["lpr_1y"]["value"]
            analysis.append(f"1年期LPR为{lpr_1y}，{'宽松' if float(lpr_1y.replace('%','')) < 3.5 else '中性'}")
        
        return "; ".join(analysis) if analysis else "数据不足"
    
    def _get_trend(self, df: pd.DataFrame, column: str) -> str:
        """获取趋势方向"""
        try:
            if len(df) >= 2:
                recent = float(df[column].iloc[-1])
                prev = float(df[column].iloc[-2])
                if recent > prev:
                    return "up"
                elif recent < prev:
                    return "down"
                else:
                    return "flat"
        except:
            pass
        return "unknown"
    
    def _get_fallback_overview(self, error_msg: str) -> dict:
        """获取备用概览数据"""
        return {
            "error": f"获取数据失败: {error_msg}",
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "suggestion": "请检查网络连接或稍后重试"
        }
    
    def _get_fallback_asset_quality(self, error_msg: str) -> dict:
        """获取备用资产质量数据"""
        return {
            "error": f"获取资产质量数据失败: {error_msg}",
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "note": "资产质量数据通常每季度更新"
        }
    
    def _get_fallback_monetary_policy(self, error_msg: str) -> dict:
        """获取备用货币政策数据"""
        return {
            "error": f"获取货币政策数据失败: {error_msg}",
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "alternative": "请访问央行官网查询最新LPR和准备金率"
        }


def main():
    parser = argparse.ArgumentParser(description="银行业宏观分析器")
    parser.add_argument("--action", choices=["overview", "asset-quality", "monetary-policy", "deposit-loan", "report"],
                       default="overview", help="执行的操作")
    parser.add_argument("--year", type=int, help="查询年份")
    parser.add_argument("--output", help="输出文件路径")
    
    args = parser.parse_args()
    
    analyzer = BankIndustryAnalyzer()
    
    if args.action == "overview":
        result = analyzer.get_industry_overview()
    elif args.action == "asset-quality":
        result = analyzer.get_asset_quality()
    elif args.action == "monetary-policy":
        result = analyzer.get_monetary_policy(args.year)
    elif args.action == "deposit-loan":
        result = analyzer.get_deposit_loan_growth()
    elif args.action == "report":
        result = analyzer.generate_report()
    else:
        result = {"error": "未知的操作类型"}
    
    output = json.dumps(result, ensure_ascii=False, indent=2) if isinstance(result, dict) else result
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"结果已保存到: {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
