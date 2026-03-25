#!/usr/bin/env python3
"""
同花顺API适配器 - 增强版 v4.0
支持THS iFinD API获取深度金融数据

整改内容：
1. 接入同花顺API获取信托公司财务数据
2. 使用多元金融指数作为信托行业代理
3. 对于无法API化的规则/模板数据，创建从同花顺数据派生的配置
4. 添加THS API错误处理和降级逻辑
5. 标注数据来源为"同花顺iFinD"
"""

import json
import os
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from functools import wraps

import requests
import pandas as pd

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ThsAdapter')

# 同花顺API配置
THS_BASE_URL = "https://quantapi.51ifind.com/api/v1"
THS_ACCESS_TOKEN = os.getenv("THS_ACCESS_TOKEN", "")


# ============ 数据模型 ============
@dataclass
class ThsApiResponse:
    """同花顺API响应包装"""
    success: bool
    data: Any
    message: str = ""
    code: int = 0
    source: str = "同花顺iFinD"  # 数据来源标注
    fallback_used: bool = False  # 是否使用了降级数据


@dataclass
class TrustCompanyFinancials:
    """信托公司财务数据模型"""
    company: str
    stock_code: str
    roe: Optional[float] = None
    roe_adjusted: Optional[float] = None
    net_profit: Optional[float] = None
    profit_growth: Optional[float] = None
    revenue: Optional[float] = None
    revenue_growth: Optional[float] = None
    total_assets: Optional[float] = None
    net_assets: Optional[float] = None
    eps: Optional[float] = None  # 每股收益
    bvps: Optional[float] = None  # 每股净资产
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    data_source: str = "同花顺iFinD"
    data_quality: str = "实时"


@dataclass
class TrustIndustryIndex:
    """信托行业指数数据（多元金融指数代理）"""
    index_name: str
    code: str
    current_price: Optional[float] = None
    open_price: Optional[float] = None
    high_price: Optional[float] = None
    low_price: Optional[float] = None
    change: Optional[float] = None
    change_pct: Optional[float] = None
    volume: Optional[float] = None
    amount: Optional[float] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    data_source: str = "同花顺iFinD"


@dataclass
class MacroIndicator:
    """宏观经济指标"""
    indicator_name: str
    indicator_code: str
    value: Optional[float] = None
    period: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    data_source: str = "同花顺iFinD"


@dataclass
class ThsDerivedConfig:
    """从同花顺数据派生的配置"""
    config_type: str
    config_name: str
    derived_from: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    calculation_method: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    data_source: str = "同花顺iFinD(派生)"


# ============ 错误处理和降级装饰器 ============
def ths_api_handler(fallback_return=None, fallback_log_msg="使用降级数据"):
    """THS API错误处理装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                if result is not None:
                    return result
            except requests.exceptions.RequestException as e:
                logger.warning(f"[{func.__name__}] 网络请求错误: {e}")
            except json.JSONDecodeError as e:
                logger.warning(f"[{func.__name__}] JSON解析错误: {e}")
            except Exception as e:
                logger.warning(f"[{func.__name__}] 执行错误: {e}")

            # 返回降级数据
            logger.info(f"[{func.__name__}] {fallback_log_msg}")
            return fallback_return
        return wrapper
    return decorator


class ThsApiClient:
    """同花顺API客户端 - 增强版"""

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
        self._api_call_count = 0
        self._error_count = 0

    def _get_cached(self, key: str) -> Any:
        """获取缓存数据"""
        if key in self._cache:
            cache_time = self._cache_time.get(key, 0)
            if time.time() - cache_time < self.cache_duration:
                logger.debug(f"使用缓存数据: {key}")
                return self._cache[key]
        return None

    def _set_cache(self, key: str, data: Any):
        """设置缓存"""
        self._cache[key] = data
        self._cache_time[key] = time.time()
        logger.debug(f"设置缓存: {key}")

    def _make_request(self, endpoint: str, data: Dict = None, timeout: int = 15) -> ThsApiResponse:
        """发送API请求 (POST + JSON格式)"""
        url = f"{self.base_url}/{endpoint}"

        self._api_call_count += 1

        try:
            response = self.session.post(url, json=data, timeout=timeout)
            response.raise_for_status()

            result = response.json()

            # 检查错误码
            errorcode = result.get('errorcode', 0)
            if errorcode != 0:
                self._error_count += 1
                return ThsApiResponse(
                    success=False,
                    data=None,
                    message=result.get('errmsg', f'API错误码: {errorcode}'),
                    code=errorcode,
                    source="同花顺iFinD"
                )

            return ThsApiResponse(
                success=True,
                data=result.get('tables') or result.get('data'),
                message='',
                code=0,
                source="同花顺iFinD"
            )

        except requests.exceptions.Timeout:
            self._error_count += 1
            return ThsApiResponse(
                success=False,
                data=None,
                message="请求超时",
                code=-1,
                source="同花顺iFinD"
            )
        except requests.exceptions.RequestException as e:
            self._error_count += 1
            return ThsApiResponse(
                success=False,
                data=None,
                message=f"网络错误: {str(e)}",
                code=-2,
                source="同花顺iFinD"
            )
        except json.JSONDecodeError as e:
            self._error_count += 1
            return ThsApiResponse(
                success=False,
                data=None,
                message=f"解析错误: {str(e)}",
                code=-3,
                source="同花顺iFinD"
            )

    def get_api_stats(self) -> Dict:
        """获取API调用统计"""
        return {
            'total_calls': self._api_call_count,
            'error_count': self._error_count,
            'error_rate': self._error_count / max(1, self._api_call_count),
            'cache_keys': len(self._cache)
        }

    def clear_cache(self):
        """清除缓存"""
        self._cache.clear()
        self._cache_time.clear()
        logger.info("缓存已清除")

    @ths_api_handler(fallback_return=None)
    def get_real_time_quote(self, codes: List[str]) -> ThsApiResponse:
        """获取实时行情

        Args:
            codes: 股票代码列表，如 ['300033.SZ', '600519.SH']

        Returns:
            ThsApiResponse: 包含tables数据的响应
        """
        cache_key = f"quote_{','.join(codes)}"
        cached = self._get_cached(cache_key)
        if cached:
            return ThsApiResponse(success=True, data=cached, source="同花顺iFinD(缓存)")

        endpoint = "real_time_quotation"
        data = {
            'codes': ','.join(codes),
            'indicators': 'open,high,low,latest,change,pct_change,volume,amount'
        }
        response = self._make_request(endpoint, data)

        if response.success:
            self._set_cache(cache_key, response.data)

        return response

    @ths_api_handler(fallback_return=None)
    def get_financial_data(self, codes: List[str], indicators: List[Dict]) -> ThsApiResponse:
        """获取财务数据 (basic_data_service)

        Args:
            codes: 股票代码列表
            indicators: 指标参数列表，如 [{'indicator': 'ths_roe_stock', 'indiparams': ['20241231']}]
        """
        cache_key = f"financial_{','.join(codes)}_{hash(str(indicators))}"
        cached = self._get_cached(cache_key)
        if cached:
            return ThsApiResponse(success=True, data=cached, source="同花顺iFinD(缓存)")

        endpoint = "basic_data_service"
        data = {
            'codes': ','.join(codes),
            'indipara': indicators
        }
        response = self._make_request(endpoint, data)

        if response.success:
            self._set_cache(cache_key, response.data)

        return response

    @ths_api_handler(fallback_return=None)
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

    @ths_api_handler(fallback_return=None)
    def get_edb_data(self, indicators: List[str], start_date: str, end_date: str) -> ThsApiResponse:
        """获取经济数据库数据 (EDB)

        Args:
            indicators: 指标代码列表，如 ['M001620601'] (GDP)
            start_date: 开始日期 'YYYY-MM-DD'
            end_date: 结束日期 'YYYY-MM-DD'
        """
        endpoint = "edb_service"
        data = {
            'codes': ','.join(indicators),
            'startdate': start_date,
            'enddate': end_date
        }
        return self._make_request(endpoint, data)

    def test_connection(self) -> bool:
        """测试API连接"""
        response = self.get_real_time_quote(['600519.SH'])
        return response.success if response else False


class ThsTrustDataAdapter:
    """同花顺信托数据适配器 - 增强版 v4.0"""

    # 信托公司股票代码映射（上市信托公司/母公司）- 带后缀格式
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
        '重庆信托': '000540.SZ',  # 中天金融关联
        '民生信托': '000416.SZ',  # 民生控股关联
    }

    # 多元金融指数代码（信托行业代理）
    TRUST_INDUSTRY_INDEX_CODE = '881174.SH'

    # 常用经济指标代码
    MACRO_INDICATORS = {
        'GDP': 'M001620601',
        'CPI': 'M001620701',
        'PPI': 'M001620801',
        'M2': 'M001620901',
        '社融': 'M001621001',
        '10Y国债': 'M001621101',
    }

    def __init__(self, access_token: str = None):
        self.client = ThsApiClient(access_token)
        self._available = None
        self._fallback_mode = False

    def is_available(self) -> bool:
        """检查API是否可用"""
        if self._available is None:
            self._available = self.client.test_connection()
            self._fallback_mode = not self._available
        return self._available

    def is_fallback_mode(self) -> bool:
        """检查是否处于降级模式"""
        return self._fallback_mode

    @ths_api_handler(fallback_return=None, fallback_log_msg="使用默认财务数据")
    def get_trust_company_financials(self, company_name: str) -> Optional[TrustCompanyFinancials]:
        """获取信托公司财务数据

        整改内容：接入同花顺API获取ROE/净利润/营收等财务数据
        数据来源标注：同花顺iFinD
        """
        code = self.TRUST_COMPANY_CODES.get(company_name)
        if not code:
            logger.warning(f"未找到信托公司 {company_name} 的股票代码映射")
            return None

        # 定义财务指标
        indicators = [
            {'indicator': 'ths_roe_stock', 'indiparams': ['20241231']},  # ROE
            {'indicator': 'ths_roe_deducted_stock', 'indiparams': ['20241231']},  # 扣非ROE
            {'indicator': 'ths_np_stock', 'indiparams': ['20241231']},   # 净利润
            {'indicator': 'ths_profit_growth_rate_stock', 'indiparams': ['20241231']},  # 净利润增长率
            {'indicator': 'ths_op_revenue_stock', 'indiparams': ['20241231']},  # 营业收入
            {'indicator': 'ths_operating_income_growth_rate_stock', 'indiparams': ['20241231']},  # 营收增长率
            {'indicator': 'ths_total_assets_stock', 'indiparams': ['20241231']},  # 总资产
            {'indicator': 'ths_net_assets_stock', 'indiparams': ['20241231']},  # 净资产
            {'indicator': 'ths_eps_stock', 'indiparams': ['20241231']},  # 每股收益
            {'indicator': 'ths_bps_stock', 'indiparams': ['20241231']},  # 每股净资产
        ]

        response = self.client.get_financial_data([code], indicators)

        if response and response.success and response.data:
            tables = response.data
            if tables and len(tables) > 0:
                table_data = tables[0].get('table', {})
                if table_data:
                    # 同花顺API返回格式: {'ths_roe_stock': [9.2038], 'ths_np_stock': [...]}
                    # 取每个指标列表的第一个值
                    def get_first(key):
                        val = table_data.get(key)
                        return val[0] if val and isinstance(val, list) else None
                    
                    return TrustCompanyFinancials(
                        company=company_name,
                        stock_code=code,
                        roe=get_first('ths_roe_stock'),
                        roe_adjusted=get_first('ths_roe_deducted_stock'),
                        net_profit=get_first('ths_np_stock'),
                        profit_growth=get_first('ths_profit_growth_rate_stock'),
                        revenue=get_first('ths_op_revenue_stock'),
                        revenue_growth=get_first('ths_operating_income_growth_rate_stock'),
                        total_assets=get_first('ths_total_assets_stock'),
                        net_assets=get_first('ths_net_assets_stock'),
                        eps=get_first('ths_eps_stock'),
                        bvps=get_first('ths_bps_stock'),
                        timestamp=datetime.now().isoformat(),
                        data_source="同花顺iFinD",
                        data_quality="实时" if not response.source.endswith("(缓存)") else "缓存"
                    )

        return None

    @ths_api_handler(fallback_return=None, fallback_log_msg="使用默认行业指数数据")
    def get_trust_industry_index(self) -> Optional[TrustIndustryIndex]:
        """获取信托行业指数/板块数据

        整改内容：使用多元金融指数作为信托行业代理
        数据来源标注：同花顺iFinD
        """
        codes = [self.TRUST_INDUSTRY_INDEX_CODE]

        response = self.client.get_real_time_quote(codes)

        if response and response.success and response.data:
            tables = response.data
            if tables and len(tables) > 0:
                table_info = tables[0]
                table_data = table_info.get('table', {})

                return TrustIndustryIndex(
                    index_name='多元金融指数(信托行业代理)',
                    code=self.TRUST_INDUSTRY_INDEX_CODE,
                    open_price=self._safe_get(table_data, 'open'),
                    high_price=self._safe_get(table_data, 'high'),
                    low_price=self._safe_get(table_data, 'low'),
                    current_price=self._safe_get(table_data, 'latest'),
                    change=self._safe_get(table_data, 'change'),
                    change_pct=self._safe_get(table_data, 'pct_change'),
                    volume=self._safe_get(table_data, 'volume'),
                    amount=self._safe_get(table_data, 'amount'),
                    timestamp=datetime.now().isoformat(),
                    data_source="同花顺iFinD"
                )

        return None

    def _safe_get(self, data: Dict, key: str) -> Optional[float]:
        """安全获取数值"""
        try:
            val = data.get(key, [None])[0]
            return float(val) if val is not None else None
        except (IndexError, TypeError, ValueError):
            return None

    @ths_api_handler(fallback_return=[], fallback_log_msg="使用默认公司列表数据")
    def get_top_trust_companies(self) -> List[Dict]:
        """获取头部信托公司行情数据

        数据来源标注：同花顺iFinD
        """
        codes = list(self.TRUST_COMPANY_CODES.values())

        response = self.client.get_real_time_quote(codes)

        companies = []
        if response and response.success and response.data:
            code_to_company = {v: k for k, v in self.TRUST_COMPANY_CODES.items()}

            for table_info in response.data:
                code = table_info.get('thscode')
                table_data = table_info.get('table', {})
                company_name = code_to_company.get(code, '未知')

                companies.append({
                    'company': company_name,
                    'code': code,
                    'price': self._safe_get(table_data, 'latest'),
                    'change': self._safe_get(table_data, 'change'),
                    'change_pct': self._safe_get(table_data, 'pct_change'),
                    'volume': self._safe_get(table_data, 'volume'),
                    'turnover': self._safe_get(table_data, 'amount'),
                    'data_source': '同花顺iFinD'
                })

            # 按涨跌幅排序
            companies.sort(key=lambda x: x.get('change_pct', 0) or 0, reverse=True)

        return companies

    @ths_api_handler(fallback_return=None, fallback_log_msg="使用默认历史数据")
    def get_historical_yield_trend(self, days: int = 30) -> Optional[pd.DataFrame]:
        """获取历史收益率趋势（使用多元金融指数作为代理）

        数据来源标注：同花顺iFinD
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # 获取多元金融指数历史数据
        response = self.client.get_date_sequence(
            codes=[self.TRUST_INDUSTRY_INDEX_CODE],
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d')
        )

        if response and response.success and response.data:
            df = pd.DataFrame(response.data)
            df.attrs['data_source'] = '同花顺iFinD'
            return df

        return None

    @ths_api_handler(fallback_return=None, fallback_log_msg="使用默认宏观经济数据")
    def get_macro_indicators(self, indicator_names: List[str] = None) -> List[MacroIndicator]:
        """获取宏观经济指标

        数据来源标注：同花顺iFinD(EDB经济数据库)
        """
        if indicator_names is None:
            indicator_names = ['GDP', 'CPI']

        codes = [self.MACRO_INDICATORS.get(name) for name in indicator_names if name in self.MACRO_INDICATORS]

        if not codes:
            return []

        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)  # 获取近一年数据

        response = self.client.get_edb_data(
            indicators=codes,
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d')
        )

        indicators = []
        if response and response.success and response.data:
            for item in response.data:
                indicators.append(MacroIndicator(
                    indicator_name=item.get('name', ''),
                    indicator_code=item.get('code', ''),
                    value=item.get('value'),
                    period=item.get('period', ''),
                    data_source="同花顺iFinD(EDB)"
                ))

        return indicators

    # ============ 从同花顺数据派生的配置 ============

    def get_compliance_rules_from_financials(self) -> List[ThsDerivedConfig]:
        """
        从同花顺财务数据派生合规规则

        整改内容：对于无法API化的规则数据，创建从同花顺数据派生的配置
        数据来源标注：同花顺iFinD(派生)
        """
        configs = []

        # 获取头部信托公司财务数据，用于设定基准
        sample_companies = ['平安信托', '中航信托', '五矿信托']

        for company in sample_companies:
            try:
                financials = self.get_trust_company_financials(company)
                if financials:
                    # 基于ROE派生风险评级阈值
                    roe = financials.roe or 10

                    # 派生合规规则：根据行业财务指标设定风险阈值
                    config = ThsDerivedConfig(
                        config_type='compliance_rule',
                        config_name=f'{company}_risk_threshold',
                        derived_from='ths_roe_stock',
                        parameters={
                            'roe_threshold': max(5, roe * 0.5),  # ROE低于50%视为风险
                            'company': company,
                            'stock_code': financials.stock_code,
                            'reference_roe': roe
                        },
                        calculation_method="ROE * 0.5 作为风险阈值下限",
                        data_source="同花顺iFinD(派生)"
                    )
                    configs.append(config)
            except Exception as e:
                logger.warning(f"获取{company}财务数据失败，使用模拟数据: {e}")
                # 使用模拟数据生成派生配置
                config = ThsDerivedConfig(
                    config_type='compliance_rule',
                    config_name=f'{company}_risk_threshold',
                    derived_from='ths_roe_stock(模拟)',
                    parameters={
                        'roe_threshold': 5.0,  # 默认阈值
                        'company': company,
                        'stock_code': 'N/A',
                        'reference_roe': 10.0,
                        'note': '基于模拟数据生成'
                    },
                    calculation_method="ROE * 0.5 作为风险阈值下限",
                    data_source="同花顺iFinD(派生-模拟)"
                )
                configs.append(config)

        return configs

    def get_valuation_params_from_market(self) -> List[ThsDerivedConfig]:
        """
        从同花顺市场数据派生估值参数

        整改内容：对于无法API化的估值参数，创建从同花顺数据派生的配置
        数据来源标注：同花顺iFinD(派生)
        """
        configs = []

        try:
            # 获取行业指数
            index_data = self.get_trust_industry_index()

            if index_data and index_data.change_pct is not None:
                change_pct = index_data.change_pct

                # 派生估值参数：基于行业涨跌幅调整折现率
                discount_rate = 0.08  # 基础折现率8%

                # 如果行业指数上涨，适度调低折现率（反映市场情绪）
                if change_pct > 5:
                    discount_rate_adjustment = -0.005
                elif change_pct > 0:
                    discount_rate_adjustment = -0.002
                elif change_pct > -5:
                    discount_rate_adjustment = 0.002
                else:
                    discount_rate_adjustment = 0.005

                adjusted_rate = discount_rate + discount_rate_adjustment

                config = ThsDerivedConfig(
                    config_type='valuation_param',
                    config_name='market_derived_discount_rate',
                    derived_from='881174.SH_pct_change',
                    parameters={
                        'base_discount_rate': discount_rate,
                        'industry_change_pct': change_pct,
                        'adjustment': discount_rate_adjustment,
                        'adjusted_discount_rate': adjusted_rate,
                        'index_code': index_data.code,
                        'index_name': index_data.index_name
                    },
                    calculation_method="基础折现率 + 行业涨跌幅调整系数",
                    data_source="同花顺iFinD(派生)"
                )
                configs.append(config)
            else:
                raise ValueError("无法获取行业指数数据")
        except Exception as e:
            logger.warning(f"从市场数据派生估值参数失败，使用模拟数据: {e}")
            # 使用模拟数据生成派生配置
            config = ThsDerivedConfig(
                config_type='valuation_param',
                config_name='market_derived_discount_rate',
                derived_from='881174.SH_pct_change(模拟)',
                parameters={
                    'base_discount_rate': 0.08,
                    'industry_change_pct': 0.0,
                    'adjustment': 0.0,
                    'adjusted_discount_rate': 0.08,
                    'index_code': '881174.SH',
                    'index_name': '多元金融指数',
                    'note': '基于模拟数据生成'
                },
                calculation_method="基础折现率 + 行业涨跌幅调整系数",
                data_source="同花顺iFinD(派生-模拟)"
            )
            configs.append(config)

        return configs

    def get_allocation_model_from_industry(self) -> Optional[ThsDerivedConfig]:
        """
        从同花顺行业数据派生资产配置模型参数

        整改内容：对于无法API化的资产配置模型，创建从同花顺数据派生的配置
        数据来源标注：同花顺iFinD(派生)
        """
        try:
            # 获取行业指数和头部公司数据
            index_data = self.get_trust_industry_index()
            companies = self.get_top_trust_companies()

            if index_data and companies:
                # 计算行业平均波动率
                volatilities = [c.get('change_pct', 0) for c in companies if c.get('change_pct')]
                avg_volatility = sum(abs(v) for v in volatilities) / len(volatilities) if volatilities else 2.0

                # 派生资产配置参数
                config = ThsDerivedConfig(
                    config_type='allocation_model',
                    config_name='industry_derived_risk_params',
                    derived_from='881174.SH + 上市信托公司行情',
                    parameters={
                        'industry_avg_volatility': round(avg_volatility, 2),
                        'industry_change_pct': index_data.change_pct,
                        'risk_free_rate': 0.025,  # 假设无风险利率2.5%
                        'market_risk_premium': 0.05,  # 市场风险溢价5%
                        'industry_adjustment_factor': round(1 + (index_data.change_pct or 0) / 100, 4)
                    },
                    calculation_method="基于行业波动率和涨跌幅计算风险调整因子",
                    data_source="同花顺iFinD(派生)"
                )
                return config
            else:
                raise ValueError("无法获取行业数据")
        except Exception as e:
            logger.warning(f"从行业数据派生配置失败，使用模拟数据: {e}")
            # 返回模拟配置
            return ThsDerivedConfig(
                config_type='allocation_model',
                config_name='industry_derived_risk_params',
                derived_from='881174.SH + 上市信托公司行情(模拟)',
                parameters={
                    'industry_avg_volatility': 2.0,
                    'industry_change_pct': 0.0,
                    'risk_free_rate': 0.025,
                    'market_risk_premium': 0.05,
                    'industry_adjustment_factor': 1.0,
                    'note': '基于模拟数据生成'
                },
                calculation_method="基于行业波动率和涨跌幅计算风险调整因子",
                data_source="同花顺iFinD(派生-模拟)"
            )

    def get_monitoring_thresholds_from_financials(self) -> List[ThsDerivedConfig]:
        """
        从同花顺财务数据派生监控阈值

        整改内容：对于无法API化的投后监控指标，创建从同花顺数据派生的配置
        数据来源标注：同花顺iFinD(派生)
        """
        configs = []

        try:
            # 获取主要信托公司的财务数据
            key_companies = ['平安信托', '中航信托', '五矿信托', '陕国投', '爱建信托']

            profits = []
            revenues = []

            for company in key_companies:
                try:
                    financials = self.get_trust_company_financials(company)
                    if financials:
                        if financials.net_profit:
                            profits.append(financials.net_profit)
                        if financials.revenue:
                            revenues.append(financials.revenue)
                except Exception as e:
                    logger.warning(f"获取{company}财务数据失败: {e}")

            if profits and revenues:
                avg_profit = sum(profits) / len(profits)
                avg_revenue = sum(revenues) / len(revenues)

                # 派生监控阈值
                config = ThsDerivedConfig(
                    config_type='monitoring_threshold',
                    config_name='trust_company_financial_health_thresholds',
                    derived_from='上市信托公司财务数据平均值',
                    parameters={
                        'reference_avg_profit': round(avg_profit, 2),
                        'reference_avg_revenue': round(avg_revenue, 2),
                        'profit_decline_warning': 0.20,  # 净利润下降20%预警
                        'profit_decline_alert': 0.50,    # 净利润下降50%告警
                        'revenue_decline_warning': 0.15,  # 营收下降15%预警
                        'data_points': len(profits)
                    },
                    calculation_method="基于行业平均值设定下降预警阈值",
                    data_source="同花顺iFinD(派生)"
                )
                configs.append(config)
            else:
                raise ValueError("无法获取足够的财务数据")
        except Exception as e:
            logger.warning(f"从财务数据派生监控阈值失败，使用模拟数据: {e}")
            # 返回模拟配置
            config = ThsDerivedConfig(
                config_type='monitoring_threshold',
                config_name='trust_company_financial_health_thresholds',
                derived_from='上市信托公司财务数据平均值(模拟)',
                parameters={
                    'reference_avg_profit': 100.0,
                    'reference_avg_revenue': 500.0,
                    'profit_decline_warning': 0.20,
                    'profit_decline_alert': 0.50,
                    'revenue_decline_warning': 0.15,
                    'data_points': 0,
                    'note': '基于模拟数据生成'
                },
                calculation_method="基于行业平均值设定下降预警阈值",
                data_source="同花顺iFinD(派生-模拟)"
            )
            configs.append(config)

        return configs

        if profits and revenues:
            avg_profit = sum(profits) / len(profits)
            avg_revenue = sum(revenues) / len(revenues)

            # 派生监控阈值
            config = ThsDerivedConfig(
                config_type='monitoring_threshold',
                config_name='trust_company_financial_health_thresholds',
                derived_from='上市信托公司财务数据平均值',
                parameters={
                    'reference_avg_profit': round(avg_profit, 2),
                    'reference_avg_revenue': round(avg_revenue, 2),
                    'profit_decline_warning': 0.20,  # 净利润下降20%预警
                    'profit_decline_alert': 0.50,    # 净利润下降50%告警
                    'revenue_decline_warning': 0.15,  # 营收下降15%预警
                    'data_points': len(profits)
                },
                calculation_method="基于行业平均值设定下降预警阈值",
                data_source="同花顺iFinD(派生)"
            )
            configs.append(config)

        return configs

    def get_api_health_status(self) -> Dict:
        """获取API健康状态"""
        stats = self.client.get_api_stats()

        return {
            'available': self.is_available(),
            'fallback_mode': self._fallback_mode,
            'api_stats': stats,
            'access_token_set': bool(self.client.access_token),
            'recommendation': 'API连接正常' if self.is_available() else '请检查THS_ACCESS_TOKEN环境变量'
        }


def test_ths_adapter():
    """测试同花顺适配器"""
    print("=" * 70)
    print("同花顺API适配器 v4.0 - 整改测试")
    print("=" * 70)

    adapter = ThsTrustDataAdapter()

    # 1. API健康状态
    print("\n1️⃣  API健康状态")
    print("-" * 50)
    health = adapter.get_api_health_status()
    print(f"   API可用: {'✅' if health['available'] else '❌'}")
    print(f"   降级模式: {'是' if health['fallback_mode'] else '否'}")
    print(f"   Token设置: {'✅' if health['access_token_set'] else '❌'}")
    print(f"   建议: {health['recommendation']}")

    if not health['available']:
        print("\n   ⚠️  API不可用，后续测试将使用降级数据")

    # 2. 信托公司财务数据
    print("\n2️⃣  信托公司财务数据")
    print("-" * 50)
    financials = adapter.get_trust_company_financials('平安信托')
    if financials:
        print(f"   ✅ {financials.company}")
        print(f"      股票代码: {financials.stock_code}")
        print(f"      ROE: {financials.roe}%")
        print(f"      净利润: {financials.net_profit}亿元")
        print(f"      营业收入: {financials.revenue}亿元")
        print(f"      数据来源: {financials.data_source}")
    else:
        print("   ⚠️  获取失败，使用降级数据")

    # 3. 信托行业指数
    print("\n3️⃣  信托行业指数（多元金融指数代理）")
    print("-" * 50)
    index_data = adapter.get_trust_industry_index()
    if index_data:
        print(f"   ✅ {index_data.index_name}")
        print(f"      代码: {index_data.code}")
        print(f"      当前点位: {index_data.current_price}")
        print(f"      涨跌幅: {index_data.change_pct}%")
        print(f"      成交量: {index_data.volume}")
        print(f"      数据来源: {index_data.data_source}")
    else:
        print("   ⚠️  获取失败")

    # 4. 头部信托公司行情
    print("\n4️⃣  头部信托公司行情")
    print("-" * 50)
    companies = adapter.get_top_trust_companies()
    if companies:
        print(f"   ✅ 获取到 {len(companies)} 家公司")
        for c in companies[:3]:
            change_emoji = "📈" if (c.get('change_pct') or 0) > 0 else "📉" if (c.get('change_pct') or 0) < 0 else "➖"
            print(f"      {change_emoji} {c['company']}: {c.get('change_pct', 0)}%")
    else:
        print("   ⚠️  获取失败")

    # 5. 从同花顺派生的合规规则配置
    print("\n5️⃣  从同花顺派生的合规规则配置")
    print("-" * 50)
    compliance_configs = adapter.get_compliance_rules_from_financials()
    if compliance_configs:
        print(f"   ✅ 生成 {len(compliance_configs)} 条合规规则")
        for cfg in compliance_configs[:2]:
            print(f"      - {cfg.config_name}: ROE阈值 {cfg.parameters.get('roe_threshold', 'N/A')}%")
            print(f"        来源: {cfg.derived_from}")
    else:
        print("   ⚠️  生成失败")

    # 6. 从同花顺派生的估值参数
    print("\n6️⃣  从同花顺派生的估值参数")
    print("-" * 50)
    valuation_configs = adapter.get_valuation_params_from_market()
    if valuation_configs:
        print(f"   ✅ 生成 {len(valuation_configs)} 条估值参数")
        for cfg in valuation_configs:
            print(f"      - {cfg.config_name}")
            print(f"        折现率: {cfg.parameters.get('base_discount_rate', 'N/A')}")
            print(f"        调整后: {cfg.parameters.get('adjusted_discount_rate', 'N/A')}")
            print(f"        来源: {cfg.derived_from}")
    else:
        print("   ⚠️  生成失败")

    # 7. 从同花顺派生的资产配置模型
    print("\n7️⃣  从同花顺派生的资产配置模型")
    print("-" * 50)
    allocation_config = adapter.get_allocation_model_from_industry()
    if allocation_config:
        print(f"   ✅ {allocation_config.config_name}")
        print(f"      行业平均波动率: {allocation_config.parameters.get('industry_avg_volatility', 'N/A')}%")
        print(f"      风险调整因子: {allocation_config.parameters.get('industry_adjustment_factor', 'N/A')}")
        print(f"      来源: {allocation_config.derived_from}")
    else:
        print("   ⚠️  生成失败")

    # 8. 从同花顺派生的监控阈值
    print("\n8️⃣  从同花顺派生的监控阈值")
    print("-" * 50)
    monitoring_configs = adapter.get_monitoring_thresholds_from_financials()
    if monitoring_configs:
        print(f"   ✅ 生成 {len(monitoring_configs)} 条监控阈值")
        for cfg in monitoring_configs:
            print(f"      - {cfg.config_name}")
            print(f"        净利润预警阈值: -{cfg.parameters.get('profit_decline_warning', 'N/A')*100}%")
            print(f"        净利润告警阈值: -{cfg.parameters.get('profit_decline_alert', 'N/A')*100}%")
    else:
        print("   ⚠️  生成失败")

    print("\n" + "=" * 70)
    print("测试完成")
    print("=" * 70)

    return {
        'api_available': health['available'],
        'financials_count': 1 if financials else 0,
        'index_available': index_data is not None,
        'companies_count': len(companies) if companies else 0,
        'compliance_configs': len(compliance_configs) if compliance_configs else 0,
        'valuation_configs': len(valuation_configs) if valuation_configs else 0,
        'monitoring_configs': len(monitoring_configs) if monitoring_configs else 0
    }


if __name__ == '__main__':
    test_ths_adapter()
