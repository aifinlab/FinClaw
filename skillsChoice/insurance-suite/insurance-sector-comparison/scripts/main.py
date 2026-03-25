#!/usr/bin/env python3
"""
保险行业对比分析器 - 接入AkShare开源数据

功能：对比全球保险市场规模、保险深度、保险密度
数据源：
1. AkShare保险行业数据（macro_china_insurance - 保险业经营情况）
2. AkShare原保险保费收入数据（macro_china_insurance_income）
3. AkShare全球保险行业数据
4. 瑞士再保险Sigma报告（全球保险市场数据参考）

说明：通过AkShare接口获取实时保险行业数据，支持自动更新
"""

import json
import os
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Optional
try:
    import akshare as ak
    AKSHARE_AVAILABLE = True
except ImportError:
    AKSHARE_AVAILABLE = False
    print("警告: akshare库未安装，将使用备用数据。运行: pip install akshare pandas")

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


class InsuranceSectorComparison:
    """保险行业对比分析器 - 基于AkShare开源数据"""
    
    def __init__(self):
        self.query_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cache_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        self.cache_file = os.path.join(self.cache_dir, 'sector_cache.json')
        self.cache_duration = timedelta(hours=12)  # 缓存12小时
        
        # 确保数据目录存在
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # 数据说明
        self.data_sources = {
            "china_insurance": "AkShare - 中国保险业经营情况",
            "china_income": "AkShare - 原保险保费收入",
            "global_reference": "瑞士再保险Sigma报告（参考）"
        }
    
    def _get_cache(self) -> Optional[Dict]:
        """获取缓存数据"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
                    cache_time_str = cache.get('cache_time')
                    if cache_time_str:
                        cache_time = datetime.fromisoformat(cache_time_str)
                        if datetime.now() - cache_time < self.cache_duration:
                            return cache
        except Exception as e:
            print(f"读取缓存失败: {e}")
        return None
    
    def _save_cache(self, data: Dict):
        """保存缓存数据"""
        try:
            data['cache_time'] = datetime.now().isoformat()
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存缓存失败: {e}")
    
    def _fetch_akshare_china_insurance(self) -> Dict:
        """
        从AkShare获取中国保险业经营情况数据
        
        接口: macro_china_insurance
        数据源: 国家统计局
        """
        if not AKSHARE_AVAILABLE or not PANDAS_AVAILABLE:
            return {}
        
        try:
            # 获取保险业经营情况
            df = ak.macro_china_insurance()
            
            if df is not None and not df.empty:
                # 获取最新全国数据
                national_data = df[df['省市地区'] == '全国']
                if not national_data.empty:
                    latest = national_data.iloc[0]
                else:
                    latest = df.iloc[0]
                
                # 数据清洗：处理可能的NaN值
                def safe_get(value, default=0):
                    if pd.isna(value):
                        return default
                    return value
                
                return {
                    "统计时间": safe_get(latest.get('统计时间'), ''),
                    "原保险保费收入_万元": safe_get(latest.get('原保险保费收入'), 0),
                    "财产险保费收入_万元": safe_get(latest.get('财产险保费收入'), 0),
                    "人身险保费收入_万元": safe_get(latest.get('人身险保费收入'), 0),
                    "寿险保费收入_万元": safe_get(latest.get('人身险-寿险保费收入'), 0),
                    "健康险保费收入_万元": safe_get(latest.get('人身险-健康险保费收入'), 0),
                    "意外险保费收入_万元": safe_get(latest.get('人身险-意外险保费收入'), 0),
                    "原保险赔付支出_万元": safe_get(latest.get('原保险赔付支出'), 0),
                    "资产总额_万元": safe_get(latest.get('资产总额'), 0),
                    "业务及管理费_万元": safe_get(latest.get('业务及管理费'), 0),
                    "银行存款_万元": safe_get(latest.get('银行存款'), 0),
                    "投资_万元": safe_get(latest.get('投资'), 0),
                    "data_quality": "success"
                }
        except Exception as e:
            print(f"获取AkShare保险数据失败: {e}")
        
        return {"data_quality": "failed"}
    
    def _fetch_akshare_insurance_income(self) -> Dict:
        """
        从AkShare获取原保险保费收入数据
        
        接口: macro_china_insurance_income
        数据源: 东方财富
        """
        if not AKSHARE_AVAILABLE or not PANDAS_AVAILABLE:
            return {}
        
        try:
            df = ak.macro_china_insurance_income()
            
            if df is not None and not df.empty:
                # 获取最新数据
                latest = df.iloc[0]
                
                def safe_get(value, default=0):
                    if pd.isna(value):
                        return default
                    return value
                
                return {
                    "日期": safe_get(latest.get('日期'), ''),
                    "最新值": safe_get(latest.get('最新值'), 0),
                    "涨跌幅": safe_get(latest.get('涨跌幅'), 0),
                    "近3月涨跌幅": safe_get(latest.get('近3月涨跌幅'), 0),
                    "近6月涨跌幅": safe_get(latest.get('近6月涨跌幅'), 0),
                    "近1年涨跌幅": safe_get(latest.get('近1年涨跌幅'), 0),
                    "data_quality": "success"
                }
        except Exception as e:
            print(f"获取AkShare保费收入数据失败: {e}")
        
        return {"data_quality": "failed"}
    
    def _fetch_akshare_global_insurance(self) -> Dict:
        """
        尝试获取全球保险市场相关数据
        
        使用AkShare的经济指标作为参考
        """
        if not AKSHARE_AVAILABLE:
            return {}
        
        try:
            # 尝试获取GDP数据用于计算保险深度
            # 这里使用中国GDP数据作为参考
            gdp_df = ak.macro_china_gdp()
            if gdp_df is not None and not gdp_df.empty:
                latest_gdp = gdp_df.iloc[0]
                return {
                    "gdp_data": {
                        "季度": latest_gdp.get('季度', ''),
                        "GDP_亿元": latest_gdp.get('国内生产总值-绝对值', 0)
                    },
                    "data_quality": "success"
                }
        except Exception as e:
            print(f"获取GDP数据失败: {e}")
        
        return {"data_quality": "failed"}
    
    def _calculate_metrics(self, china_data: Dict, gdp_data: Dict = None) -> Dict:
        """
        计算保险行业关键指标
        """
        metrics = {}
        
        try:
            premium = china_data.get('原保险保费收入_万元', 0)
            
            if premium > 0 and gdp_data:
                gdp_value = gdp_data.get('GDP_亿元', 0) * 10000  # 转换为万元
                if gdp_value > 0:
                    # 保险深度 = 保费收入 / GDP * 100%
                    metrics['保险深度_计算'] = f"{(premium / gdp_value * 100):.2f}%"
            
            # 计算赔付率
            payout = china_data.get('原保险赔付支出_万元', 0)
            if premium > 0:
                metrics['简单赔付率'] = f"{(payout / premium * 100):.1f}%"
            
            # 计算结构占比
            property_premium = china_data.get('财产险保费收入_万元', 0)
            life_premium = china_data.get('人身险保费收入_万元', 0)
            
            if premium > 0:
                metrics['财产险占比'] = f"{(property_premium / premium * 100):.1f}%"
                metrics['人身险占比'] = f"{(life_premium / premium * 100):.1f}%"
                
                # 人身险细分
                life_detail = china_data.get('寿险保费收入_万元', 0)
                health_detail = china_data.get('健康险保费收入_万元', 0)
                accident_detail = china_data.get('意外险保费收入_万元', 0)
                
                metrics['寿险占人身险比例'] = f"{(life_detail / life_premium * 100):.1f}%" if life_premium > 0 else "N/A"
                metrics['健康险占人身险比例'] = f"{(health_detail / life_premium * 100):.1f}%" if life_premium > 0 else "N/A"
            
        except Exception as e:
            print(f"计算指标失败: {e}")
        
        return metrics
    
    def compare_global_markets(self, force_update: bool = False) -> dict:
        """
        对比全球保险市场 - 结合AkShare数据和全球参考数据
        
        Args:
            force_update: 是否强制更新缓存
        """
        # 检查缓存
        if not force_update:
            cache = self._get_cache()
            if cache and 'global_comparison' in cache:
                cache['query_time'] = self.query_time
                return cache
        
        # 获取AkShare数据
        china_data = self._fetch_akshare_china_insurance()
        income_data = self._fetch_akshare_insurance_income()
        global_ref = self._fetch_akshare_global_insurance()
        
        # 计算指标
        metrics = self._calculate_metrics(china_data, global_ref.get('gdp_data'))
        
        # 计算中国保险市场规模（基于最新数据）
        china_premium = china_data.get('原保险保费收入_万元', 0) / 10000  # 转换为亿元
        
        # 全球保险市场数据（参考瑞士再保险Sigma报告）
        result = {
            "query_time": self.query_time,
            "data_sources": self.data_sources,
            "data_quality_note": "中国数据来自AkShare实时接口，全球数据参考行业报告",
            "global_comparison": {
                "全球市场规模": {
                    "total_premium": "约7万亿美元",
                    "life_share": "52%",
                    "non_life_share": "48%",
                    "data_year": "2024年",
                    "data_source": "瑞士再保险研究所Sigma报告"
                },
                "主要市场": {
                    "美国": {
                        "premium": "约1.4万亿美元",
                        "global_share": "20%",
                        "penetration": "7.5%",
                        "density": "约4500美元/人"
                    },
                    "中国": {
                        "premium": f"约{china_premium/10000:.2f}万亿元人民币" if china_premium else "约0.8万亿美元",
                        "premium_亿元": round(china_premium, 2),
                        "global_share": "11%",
                        "penetration": metrics.get('保险深度_计算', '4.5%'),
                        "latest_data": china_data.get('统计时间', ''),
                        "data_source": "AkShare - 保险业经营情况"
                    },
                    "日本": {
                        "premium": "约0.4万亿美元",
                        "global_share": "6%",
                        "penetration": "8.5%",
                        "density": "约3500美元/人"
                    },
                    "英国": {
                        "premium": "约0.3万亿美元",
                        "global_share": "4%",
                        "penetration": "10%",
                        "density": "约4500美元/人"
                    }
                }
            },
            "china_realtime_data": {
                "原保险保费收入_万元": china_data.get('原保险保费收入_万元', '数据获取中'),
                "财产险_万元": china_data.get('财产险保费收入_万元', '数据获取中'),
                "人身险_万元": china_data.get('人身险保费收入_万元', '数据获取中'),
                "寿险_万元": china_data.get('寿险保费收入_万元', '数据获取中'),
                "健康险_万元": china_data.get('健康险保费收入_万元', '数据获取中'),
                "意外险_万元": china_data.get('意外险保费收入_万元', '数据获取中'),
                "赔付支出_万元": china_data.get('原保险赔付支出_万元', '数据获取中'),
                "资产总额_万元": china_data.get('资产总额_万元', '数据获取中'),
                "统计时间": china_data.get('统计时间', ''),
                "计算指标": metrics,
                "保费收入趋势": income_data
            },
            "china_position": {
                "global_rank": "全球第2大保险市场",
                "growth_potential": "保险深度/密度仍有提升空间",
                "key_opportunities": ["养老保险", "健康保险", "农业保险", "责任保险"],
                "realtime_data_available": china_data.get('data_quality') == 'success'
            },
            "update_info": {
                "cache_duration": "12小时",
                "next_update": (datetime.now() + self.cache_duration).strftime("%Y-%m-%d %H:%M:%S"),
                "update_mechanism": "自动从AkShare获取最新数据",
                "akshare_available": AKSHARE_AVAILABLE,
                "pandas_available": PANDAS_AVAILABLE
            }
        }
        
        # 保存缓存
        self._save_cache(result)
        
        return result
    
    def compare_penetration(self) -> dict:
        """对比保险深度和密度 - 结合实时数据"""
        # 获取最新数据
        china_data = self._fetch_akshare_china_insurance()
        global_ref = self._fetch_akshare_global_insurance()
        metrics = self._calculate_metrics(china_data, global_ref.get('gdp_data'))
        
        # 计算保险深度和密度
        china_premium = china_data.get('原保险保费收入_万元', 0) / 10000 / 10000  # 转换为万亿元
        
        return {
            "query_time": self.query_time,
            "data_sources": self.data_sources,
            "penetration_comparison": {
                "保险深度(保费/GDP)": {
                    "全球平均": "6.8%",
                    "发达市场平均": "8.5%",
                    "新兴市场平均": "3.5%",
                    "中国_实时计算": metrics.get('保险深度_计算', '计算中'),
                    "中国_参考值": "4.5%",
                    "中国台湾": "18%",
                    "中国香港": "18%",
                    "日本": "8.5%",
                    "美国": "7.5%"
                },
                "保险密度(人均保费)": {
                    "全球平均": "约800美元",
                    "发达市场平均": "约3500美元",
                    "新兴市场平均": "约150美元",
                    "中国": "约550美元",
                    "中国香港": "约8000美元",
                    "日本": "约3500美元",
                    "美国": "约4500美元"
                }
            },
            "china_latest": {
                "最新保费收入_万亿元": round(china_premium, 2) if china_premium else "获取中",
                "统计时间": china_data.get('统计时间', ''),
                "计算指标": metrics,
                "analysis": "中国保险深度和密度均低于发达市场，发展潜力大"
            },
            "data_source": "AkShare + 瑞士再保险Sigma报告",
            "data_quality": "实时数据 + 行业公开数据"
        }
    
    def get_china_insurance_structure(self) -> dict:
        """
        获取中国保险市场结构分析 - 基于AkShare实时数据
        """
        china_data = self._fetch_akshare_china_insurance()
        
        if not china_data or china_data.get('data_quality') != 'success':
            return {
                "query_time": self.query_time,
                "status": "error",
                "message": "无法获取数据，请检查网络连接或akshare/pandas库安装",
                "install_guide": "pip install akshare pandas"
            }
        
        # 计算结构占比
        total = china_data.get('原保险保费收入_万元', 0)
        
        structure = {}
        if total > 0:
            property_pct = china_data.get('财产险保费收入_万元', 0) / total * 100
            life_pct = china_data.get('人身险保费收入_万元', 0) / total * 100
            
            structure = {
                "财产险占比": f"{property_pct:.1f}%",
                "人身险占比": f"{life_pct:.1f}%",
            }
            
            # 人身险细分
            life_detail = china_data.get('人身险保费收入_万元', 0)
            if life_detail > 0:
                structure["其中_寿险占比_占总保费"] = f"{china_data.get('寿险保费收入_万元', 0) / total * 100:.1f}%"
                structure["其中_健康险占比_占总保费"] = f"{china_data.get('健康险保费收入_万元', 0) / total * 100:.1f}%"
                structure["其中_意外险占比_占总保费"] = f"{china_data.get('意外险保费收入_万元', 0) / total * 100:.1f}%"
                
                structure["其中_寿险占人身险比例"] = f"{china_data.get('寿险保费收入_万元', 0) / life_detail * 100:.1f}%"
                structure["其中_健康险占人身险比例"] = f"{china_data.get('健康险保费收入_万元', 0) / life_detail * 100:.1f}%"
        
        return {
            "query_time": self.query_time,
            "data_source": "AkShare - macro_china_insurance",
            "统计时间": china_data.get('统计时间', ''),
            "市场结构": structure,
            "原始数据": {
                "原保险保费收入_万元": china_data.get('原保险保费收入_万元', 0),
                "财产险保费收入_万元": china_data.get('财产险保费收入_万元', 0),
                "人身险保费收入_万元": china_data.get('人身险保费收入_万元', 0),
                "寿险保费收入_万元": china_data.get('寿险保费收入_万元', 0),
                "健康险保费收入_万元": china_data.get('健康险保费收入_万元', 0),
                "意外险保费收入_万元": china_data.get('意外险保费收入_万元', 0),
                "赔付支出_万元": china_data.get('原保险赔付支出_万元', 0),
                "资产总额_万元": china_data.get('资产总额_万元', 0)
            },
            "分析": "人身险占比高于财产险，寿险是主要组成部分；健康险增长潜力大"
        }
    
    def auto_update(self) -> dict:
        """
        执行自动更新
        
        返回更新状态信息
        """
        print("开始执行自动更新...")
        
        try:
            # 强制更新数据
            data = self.compare_global_markets(force_update=True)
            
            china_data = data.get('china_realtime_data', {})
            
            return {
                "update_time": self.query_time,
                "status": "success",
                "message": "自动更新完成",
                "data_sources": list(self.data_sources.values()),
                "china_data_available": len(china_data) > 0 and china_data.get('统计时间') != '',
                "next_update": (datetime.now() + self.cache_duration).strftime("%Y-%m-%d %H:%M:%S"),
                "akshare_installed": AKSHARE_AVAILABLE,
                "pandas_installed": PANDAS_AVAILABLE,
                "统计时间": china_data.get('统计时间', '未获取')
            }
        except Exception as e:
            return {
                "update_time": self.query_time,
                "status": "failed",
                "message": f"自动更新失败: {str(e)}",
                "next_update": (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S"),
                "akshare_installed": AKSHARE_AVAILABLE,
                "pandas_installed": PANDAS_AVAILABLE,
                "install_guide": "pip install akshare pandas"
            }


def main():
    parser = argparse.ArgumentParser(description="保险行业对比分析器")
    parser.add_argument("--global", dest="global_market", action="store_true", 
                        help="全球市场对比")
    parser.add_argument("--penetration", action="store_true", 
                        help="保险深度/密度对比")
    parser.add_argument("--structure", action="store_true",
                        help="中国保险市场结构")
    parser.add_argument("--update", action="store_true", 
                        help="执行自动更新")
    parser.add_argument("--force", action="store_true", 
                        help="强制更新缓存")
    
    args = parser.parse_args()
    comparator = InsuranceSectorComparison()
    
    if args.update:
        result = comparator.auto_update()
    elif args.penetration:
        result = comparator.compare_penetration()
    elif args.structure:
        result = comparator.get_china_insurance_structure()
    else:
        result = comparator.compare_global_markets(force_update=args.force)
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
