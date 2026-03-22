#!/usr/bin/env python3
"""
同花顺API适配器 - 信托数据对接
支持THS iFinD API获取深度金融数据
"""

import json
import os
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


class ThsApiClient:
    """同花顺API客户端"""
    
    def __init__(self, access_token: str = None):
        self.access_token = access_token or THS_ACCESS_TOKEN
        self.base_url = THS_BASE_URL
        self.session = requests.Session()
        # 根据API手册，使用access_token作为header
        self.session.headers.update({
            'Content-Type': 'application/json',
            'access_token': self.access_token
        })
        self._cache = {}
        self._cache_time = {}
        self.cache_duration = 1800  # 缓存30分钟
    
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
    
    def _make_request(self, endpoint: str, data: Dict = None) -> ThsApiResponse:
        """发送API请求 (POST + JSON格式)"""
        url = f"{self.base_url}/{endpoint}"
        
        try:
            # 使用POST + JSON body (根据API手册)
            response = self.session.post(url, json=data, timeout=15)
            response.raise_for_status()
            
            result = response.json()
            
            # 检查错误码
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
    
    def get_real_time_quote(self, codes: List[str]) -> ThsApiResponse:
        """获取实时行情
        
        Args:
            codes: 股票代码列表，如 ['300033.SZ', '600519.SH']
        """
        endpoint = "real_time_quotation"
        # 根据API手册，使用indicators参数
        data = {
            'codes': ','.join(codes),
            'indicators': 'open,high,low,latest,change,pct_change,volume,amount'
        }
        return self._make_request(endpoint, data)
    
    def get_financial_data(self, codes: List[str], indicators: List[Dict]) -> ThsApiResponse:
        """获取财务数据
        
        Args:
            codes: 股票代码列表
            indicators: 指标参数列表，如 [{'indicator': 'ths_roe_stock', 'indiparams': ['20241231']}]
        """
        endpoint = "basic_data_service"
        data = {
            'codes': ','.join(codes),
            'indipara': indicators
        }
        return self._make_request(endpoint, data)
    
    def get_date_sequence(self, codes: List[str], start_date: str, end_date: str,
                         indicators: List[Dict] = None) -> ThsApiResponse:
        """获取日期序列数据
        
        Args:
            codes: 股票代码列表
            start_date: 开始日期 'YYYY-MM-DD'
            end_date: 结束日期 'YYYY-MM-DD'
            indicators: 指标参数列表
        """
        endpoint = "date_sequence"
        data = {
            'codes': ','.join(codes),
            'startdate': start_date,
            'enddate': end_date
        }
        if indicators:
            data['indipara'] = indicators
        return self._make_request(endpoint, data)
    
    def test_connection(self) -> bool:
        """测试API连接"""
        # 使用贵州茅台测试 (带后缀的代码格式)
        response = self.get_real_time_quote(['600519.SH'])
        return response.success


class ThsTrustDataAdapter:
    """同花顺信托数据适配器"""
    
    # 信托公司股票代码映射（部分）- 带后缀格式
    TRUST_COMPANY_CODES = {
        '平安信托': '000001.SZ',  # 平安银行关联
        '中航信托': '600705.SH',  # 中航产融
        '五矿信托': '600390.SH',  # 五矿资本
        '中粮信托': '000423.SZ',  # 中粮资本关联
        '中融信托': '600291.SH',  # ST西水
        '爱建信托': '600643.SH',  # 爱建集团
        '陕国投': '000563.SZ',    # 陕国投A
        '安信信托': '600816.SH',  # 建元信托
        '江苏信托': '000544.SZ',  # 中原高速关联
        '昆仑信托': '000617.SZ',  # 中油资本
    }
    
    def __init__(self, access_token: str = None):
        self.client = ThsApiClient(access_token)
        self._available = None
    
    def is_available(self) -> bool:
        """检查API是否可用"""
        if self._available is None:
            self._available = self.client.test_connection()
        return self._available
    
    def get_trust_company_financials(self, company_name: str) -> Optional[Dict]:
        """获取信托公司财务数据"""
        code = self.TRUST_COMPANY_CODES.get(company_name)
        if not code:
            return None
        
        cache_key = f"trust_financial_{code}"
        cached = self.client._get_cached(cache_key)
        if cached:
            return cached
        
        # 根据API手册，使用indipara格式
        indicators = [
            {'indicator': 'ths_roe_stock', 'indiparams': ['20241231']},  # ROE
            {'indicator': 'ths_np_stock', 'indiparams': ['20241231']},   # 净利润
            {'indicator': 'ths_op Revenue_stock', 'indiparams': ['20241231']},  # 营业收入
        ]
        
        response = self.client.get_financial_data([code], indicators)
        
        if response.success and response.data:
            # 解析返回的tables数据
            tables = response.data
            if tables and len(tables) > 0:
                table_data = tables[0].get('table', [])
                if table_data and len(table_data) > 0:
                    row = table_data[0]
                    financials = {
                        'company': company_name,
                        'stock_code': code,
                        'roe': row.get('ths_roe_stock'),
                        'net_profit': row.get('ths_np_stock'),
                        'revenue': row.get('ths_op Revenue_stock'),
                        'timestamp': datetime.now().isoformat()
                    }
                    self.client._set_cache(cache_key, financials)
                    return financials
        
        return None
    
    def get_trust_industry_index(self) -> Optional[Dict]:
        """获取信托行业指数/板块数据"""
        # 使用多元金融板块作为信托行业代理
        codes = ['881174.SH']  # 多元金融指数
        
        cache_key = "trust_industry_index"
        cached = self.client._get_cached(cache_key)
        if cached:
            return cached
        
        response = self.client.get_real_time_quote(codes)
        
        if response.success and response.data:
            tables = response.data
            if tables and len(tables) > 0:
                table_info = tables[0]
                table_data = table_info.get('table', {})
                index_data = {
                    'index_name': '多元金融指数',
                    'code': table_info.get('thscode'),
                    'current_price': table_data.get('latest', [None])[0],
                    'change': table_data.get('change', [None])[0],
                    'volume': table_data.get('volume', [None])[0],
                    'amount': table_data.get('amount', [None])[0],
                    'timestamp': datetime.now().isoformat()
                }
                self.client._set_cache(cache_key, index_data)
                return index_data
        
        return None
    
    def get_top_trust_companies(self) -> List[Dict]:
        """获取头部信托公司行情数据"""
        codes = list(self.TRUST_COMPANY_CODES.values())
        
        cache_key = f"trust_companies_{','.join(codes)}"
        cached = self.client._get_cached(cache_key)
        if cached:
            return cached
        
        response = self.client.get_real_time_quote(codes)
        
        companies = []
        if response.success and response.data:
            # 解析返回的tables数据
            code_to_company = {v: k for k, v in self.TRUST_COMPANY_CODES.items()}
            
            for table_info in response.data:
                code = table_info.get('thscode')
                table_data = table_info.get('table', {})
                company_name = code_to_company.get(code, '未知')
                
                companies.append({
                    'company': company_name,
                    'code': code,
                    'price': table_data.get('latest', [None])[0],
                    'change': table_data.get('change', [None])[0],
                    'change_pct': table_data.get('pct_change', [None])[0],
                    'volume': table_data.get('volume', [None])[0],
                    'turnover': table_data.get('amount', [None])[0]
                })
            
            # 按涨跌幅排序
            companies.sort(key=lambda x: x.get('change', 0) or 0, reverse=True)
            self.client._set_cache(cache_key, companies)
        
        return companies
    
    def get_historical_yield_trend(self, days: int = 30) -> Optional[pd.DataFrame]:
        """获取历史收益率趋势（使用多元金融指数作为代理）"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        cache_key = f"yield_trend_{days}"
        cached = self.client._get_cached(cache_key)
        if cached:
            return cached
        
        # 获取多元金融指数历史数据
        response = self.client.get_date_sequence(
            code='881174',
            start_date=start_date.strftime('%Y%m%d'),
            end_date=end_date.strftime('%Y%m%d'),
            fields=['f43', 'f44', 'f45', 'f46', 'f47']
        )
        
        if response.success and response.data:
            df = pd.DataFrame(response.data)
            self.client._set_cache(cache_key, df)
            return df
        
        return None


def test_ths_api():
    """测试同花顺API"""
    print("=== 同花顺API对接测试 ===\n")
    
    # 检查token
    token = os.getenv("THS_ACCESS_TOKEN", "")
    if not token:
        print("❌ 未设置 THS_ACCESS_TOKEN 环境变量")
        return
    
    print(f"✓ Access Token: {token[:20]}...")
    
    # 初始化适配器
    adapter = ThsTrustDataAdapter()
    
    # 测试连接
    print("\n1. 测试API连接...")
    if adapter.is_available():
        print("   ✅ 同花顺API连接成功")
    else:
        print("   ❌ 同花顺API连接失败")
        return
    
    # 获取信托公司财务数据
    print("\n2. 获取信托公司财务数据...")
    financials = adapter.get_trust_company_financials('平安信托')
    if financials:
        print(f"   ✅ {financials['company']}")
        print(f"      ROE: {financials.get('roe')}%")
        print(f"      净利润: {financials.get('net_profit')}亿元")
    else:
        print("   ❌ 获取失败")
    
    # 获取行业指数
    print("\n3. 获取信托行业指数...")
    index_data = adapter.get_trust_industry_index()
    if index_data:
        print(f"   ✅ {index_data['index_name']}")
        print(f"      当前点位: {index_data.get('current_price')}")
        print(f"      涨跌幅: {index_data.get('change')}%")
    else:
        print("   ❌ 获取失败")
    
    # 获取头部公司
    print("\n4. 获取头部信托公司行情...")
    companies = adapter.get_top_trust_companies()
    if companies:
        print(f"   ✅ 获取到 {len(companies)} 家公司")
        for c in companies[:3]:
            print(f"      {c['company']}: {c.get('change_pct', 0)}%")
    else:
        print("   ❌ 获取失败")
    
    print("\n=== 测试完成 ===")


if __name__ == '__main__':
    test_ths_api()
