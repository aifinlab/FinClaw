#!/usr/bin/env python3
"""
同花顺iFinD API适配器 - 基金数据对接
支持THS iFinD API获取深度基金数据

需要配置环境变量: THS_ACCESS_TOKEN
"""

import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

import requests
import pandas as pd

# 同花顺API配置
THS_BASE_URL = "https://quantapi.51ifind.com/api/v1"
THS_ACCESS_TOKEN = os.getenv("THS_ACCESS_TOKEN", "")


@dataclass
class ThsApiResponse:
    """同花顺API响应包装"""
    success: bool
    data: Any
    message: str = ""
    code: int = 0


class ThsFundAdapter:
    """同花顺iFinD基金数据适配器"""
    
    def __init__(self, access_token: str = None):
        self.access_token = access_token or THS_ACCESS_TOKEN
        self.base_url = THS_BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'access_token': self.access_token
        })
        self._cache = {}
        self._cache_time = {}
        self.cache_duration = 1800  # 缓存30分钟
    
    def get_name(self) -> str:
        return "同花顺iFinD"
    
    def is_available(self) -> bool:
        """检查iFinD是否可用"""
        if not self.access_token:
            return False
        
        # 简单测试API连通性
        try:
            response = self._make_request(' heartbeat', timeout=5)
            return response.success
        except:
            return False
    
    def _get_cached(self, key: str) -> Any:
        """获取缓存数据"""
        if key in self._cache:
            cache_time = self._cache_time.get(key, 0)
            if time.time() - cache_time < self.cache_duration:
                return self._cache[key]
        return None
    
    def _set_cache(self, key: str, data: Any):
        """设置缓存"""
        self._cache[key] = data
        self._cache_time[key] = time.time()
    
    def _make_request(self, endpoint: str, data: Dict = None, timeout: int = 15) -> ThsApiResponse:
        """发送API请求"""
        url = f"{self.base_url}/{endpoint.strip()}"
        
        try:
            response = self.session.post(url, json=data, timeout=timeout)
            response.raise_for_status()
            
            result = response.json()
            
            errorcode = result.get('errorcode', 0)
            if errorcode != 0:
                return ThsApiResponse(
                    success=False,
                    data=None,
                    message=result.get('errmsg', f'API错误码: {errorcode}'),
                    code=errorcode
                )
            
            return ThsApiResponse(
                success=True,
                data=result.get('tables') or result.get('data'),
                message='',
                code=0
            )
                
        except requests.exceptions.RequestException as e:
            return ThsApiResponse(
                success=False,
                data=None,
                message=f"网络错误: {str(e)}",
                code=-2
            )
        except json.JSONDecodeError as e:
            return ThsApiResponse(
                success=False,
                data=None,
                message=f"解析错误: {str(e)}",
                code=-3
            )
    
    def get_fund_basic(self, fund_code: str) -> Optional[Dict]:
        """获取基金基础信息"""
        cache_key = f"ths_basic_{fund_code}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        # iFinD接口: 获取基金基本信息
        # 指标示例: ths_fund_code, ths_fund_name, ths_fund_type, ths_fund_manager
        request_data = {
            'indicator': 'ths_fund_code;ths_fund_name;ths_fund_type;ths_fund_manager;ths_fund_company;ths_fund_establish_date;ths_fund_nav',
            'scode': fund_code,
            'params': ''
        }
        
        response = self._make_request('basic_data_service', request_data)
        
        if not response.success:
            print(f"iFinD获取基金基础信息失败: {response.message}")
            return None
        
        try:
            # 解析返回数据
            tables = response.data
            if not tables or len(tables) == 0:
                return None
            
            # 提取数据
            info = {
                'fund_code': fund_code,
                'fund_name': tables[0].get('ths_fund_name', ''),
                'fund_type': tables[0].get('ths_fund_type', ''),
                'manager': tables[0].get('ths_fund_manager', ''),
                'company': tables[0].get('ths_fund_company', ''),
                'establish_date': tables[0].get('ths_fund_establish_date', ''),
                'nav': float(tables[0].get('ths_fund_nav', 0)),
                'update_date': datetime.now().strftime('%Y-%m-%d')
            }
            
            self._set_cache(cache_key, info)
            return info
            
        except Exception as e:
            print(f"解析iFinD基金基础信息失败: {e}")
            return None
    
    def get_fund_nav(self, fund_code: str, days: int = 30) -> List[Dict]:
        """获取基金净值历史"""
        cache_key = f"ths_nav_{fund_code}_{days}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        # 计算日期范围
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days * 1.5)  # 多取一些防止节假日
        
        # iFinD接口: 获取历史净值序列
        request_data = {
            'scode': fund_code,
            'indicator': 'ths_fund_nav;ths_fund_acc_nav',
            'startdate': start_date.strftime('%Y-%m-%d'),
            'enddate': end_date.strftime('%Y-%m-%d')
        }
        
        response = self._make_request('date_sequence', request_data)
        
        if not response.success:
            print(f"iFinD获取基金净值失败: {response.message}")
            return []
        
        try:
            tables = response.data
            if not tables or len(tables) == 0:
                return []
            
            nav_list = []
            prev_nav = None
            
            for row in tables[:days]:
                nav = float(row.get('ths_fund_nav', 0))
                acc_nav = float(row.get('ths_fund_acc_nav', 0))
                date = row.get('date', '')
                
                # 计算日收益率
                daily_return = 0.0
                if prev_nav and prev_nav > 0:
                    daily_return = (nav - prev_nav) / prev_nav
                prev_nav = nav
                
                nav_list.append({
                    'fund_code': fund_code,
                    'date': date,
                    'nav': nav,
                    'acc_nav': acc_nav,
                    'daily_return': daily_return
                })
            
            self._set_cache(cache_key, nav_list)
            return nav_list
            
        except Exception as e:
            print(f"解析iFinD基金净值失败: {e}")
            return []
    
    def get_fund_performance(self, fund_code: str) -> Optional[Dict]:
        """获取基金业绩表现"""
        cache_key = f"ths_perf_{fund_code}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        # iFinD接口: 获取基金业绩指标
        # 指标: 近1月/3月/6月/1年/2年/3年/成立来收益, 最大回撤, 夏普比率等
        indicators = [
            'ths_fund_return_1m',
            'ths_fund_return_3m', 
            'ths_fund_return_6m',
            'ths_fund_return_1y',
            'ths_fund_return_2y',
            'ths_fund_return_3y',
            'ths_fund_return_total',
            'ths_fund_max_drawdown',
            'ths_fund_sharpe_ratio',
            'ths_fund_volatility'
        ]
        
        request_data = {
            'scode': fund_code,
            'indicator': ';'.join(indicators)
        }
        
        response = self._make_request('basic_data_service', request_data)
        
        if not response.success:
            print(f"iFinD获取基金业绩失败: {response.message}")
            return None
        
        try:
            tables = response.data
            if not tables or len(tables) == 0:
                return None
            
            row = tables[0]
            
            perf = {
                'fund_code': fund_code,
                'return_1m': float(row.get('ths_fund_return_1m', 0)) / 100,
                'return_3m': float(row.get('ths_fund_return_3m', 0)) / 100,
                'return_6m': float(row.get('ths_fund_return_6m', 0)) / 100,
                'return_1y': float(row.get('ths_fund_return_1y', 0)) / 100,
                'return_2y': float(row.get('ths_fund_return_2y', 0)) / 100,
                'return_3y': float(row.get('ths_fund_return_3y', 0)) / 100,
                'return_total': float(row.get('ths_fund_return_total', 0)) / 100,
                'max_drawdown': float(row.get('ths_fund_max_drawdown', 0)) / 100,
                'sharpe_ratio': float(row.get('ths_fund_sharpe_ratio', 0)),
                'volatility': float(row.get('ths_fund_volatility', 0)) / 100,
                'update_date': datetime.now().strftime('%Y-%m-%d')
            }
            
            self._set_cache(cache_key, perf)
            return perf
            
        except Exception as e:
            print(f"解析iFinD基金业绩失败: {e}")
            return None
    
    def search_funds(self, keyword: str) -> List[Dict]:
        """搜索基金"""
        # iFinD没有直接的搜索接口，使用report_query获取基金列表后过滤
        # 这里使用模拟数据作为示例
        return []


# 测试代码
if __name__ == '__main__':
    print("=" * 60)
    print("同花顺iFinD基金适配器测试")
    print("=" * 60)
    
    if not THS_ACCESS_TOKEN:
        print("\n⚠️ 未配置THS_ACCESS_TOKEN环境变量")
        print("请设置: export THS_ACCESS_TOKEN='your_token'")
    else:
        adapter = ThsFundAdapter()
        print(f"\n适配器可用: {adapter.is_available()}")
        
        if adapter.is_available():
            # 测试获取基金信息
            test_code = "000001"  # 华夏成长
            print(f"\n获取基金 {test_code} 信息:")
            info = adapter.get_fund_basic(test_code)
            if info:
                print(f"  名称: {info.get('fund_name')}")
                print(f"  类型: {info.get('fund_type')}")
                print(f"  净值: {info.get('nav')}")
            else:
                print("  获取失败")
