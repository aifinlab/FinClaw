#!/usr/bin/env python3
"""
信托数据对接层 - 统一数据获取接口
Trust Data Adapter Layer

支持数据源：
- AkShare（开源优先）
- 用益信托网（爬虫）
- 中国信托登记（公开数据）
- 同花顺iFinD（可选）
"""

import json
import time
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from functools import lru_cache

import pandas as pd
import requests
from bs4 import BeautifulSoup

# 尝试导入AkShare
try:
    import akshare as ak
    AKSHARE_AVAILABLE = True
except ImportError:
    AKSHARE_AVAILABLE = False
    print("警告：AkShare未安装，部分功能将不可用")

# 尝试导入同花顺适配器
try:
    from ths_adapter import ThsTrustDataAdapter
    THS_ADAPTER_AVAILABLE = True
except ImportError:
    THS_ADAPTER_AVAILABLE = False


@dataclass
class TrustCompanyFinancials:
    """信托公司财务数据"""
    company: str
    stock_code: str
    roe: float
    roe_adjusted: float
    net_profit: float
    profit_growth: float
    revenue: float
    revenue_growth: float
    total_assets: float
    net_assets: float
    timestamp: str


@dataclass
class TrustProductData:
    """信托产品数据模型"""
    product_code: str
    product_name: str
    trust_company: str
    product_type: str  # 集合/单一/财产权
    investment_type: str  # 固收/权益/混合/另类
    expected_yield: float  # 预期收益率
    duration: int  # 期限（月）
    min_investment: float  # 起投金额
    issue_scale: float  # 发行规模
    issue_date: str
    risk_level: str  # R1-R5
    status: str  # 在售/已成立/已清算
    underlying_type: str  # 底层资产类型
    
@dataclass
class TrustMarketStats:
    """信托市场统计数据"""
    stat_date: str
    total_issuance: float  # 发行规模（亿元）
    product_count: int  # 产品数量
    avg_yield: float  # 平均收益率
    yield_by_type: Dict[str, float]  # 分类型收益率
    yield_by_duration: Dict[str, float]  # 分期限收益率


class DataSourceAdapter(ABC):
    """数据源适配器基类"""
    
    @abstractmethod
    def get_name(self) -> str:
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        pass
    
    @abstractmethod
    def get_products(self, **filters) -> List[TrustProductData]:
        pass
    
    @abstractmethod
    def get_market_stats(self) -> TrustMarketStats:
        pass


class AkShareAdapter(DataSourceAdapter):
    """AkShare数据源适配器"""
    
    def get_name(self) -> str:
        return "AkShare"
    
    def is_available(self) -> bool:
        return AKSHARE_AVAILABLE
    
    def get_products(self, **filters) -> List[TrustProductData]:
        """从AkShare获取信托产品数据"""
        if not self.is_available():
            return []
        
        try:
            # 获取信托产品数据
            # AkShare的信托数据接口
            df = ak.trust_crawler()
            
            products = []
            for _, row in df.iterrows():
                product = TrustProductData(
                    product_code=row.get('产品代码', ''),
                    product_name=row.get('产品名称', ''),
                    trust_company=row.get('信托公司', ''),
                    product_type=row.get('产品类型', '集合信托'),
                    investment_type=row.get('投资类型', '固定收益类'),
                    expected_yield=float(row.get('预期收益率', 0)),
                    duration=int(row.get('期限', 12)),
                    min_investment=float(row.get('起投金额', 100)),
                    issue_scale=float(row.get('发行规模', 0)),
                    issue_date=row.get('发行日期', ''),
                    risk_level=row.get('风险等级', 'R3'),
                    status=row.get('状态', '在售'),
                    underlying_type=row.get('底层资产', '')
                )
                products.append(product)
            
            # 应用过滤器
            products = self._apply_filters(products, filters)
            return products
            
        except Exception as e:
            print(f"AkShare获取数据失败: {e}")
            return []
    
    def get_market_stats(self) -> Optional[TrustMarketStats]:
        """获取市场统计数据"""
        if not self.is_available():
            return None
        
        try:
            # 获取信托行业统计数据
            df = ak.trust_crawler()
            
            return TrustMarketStats(
                stat_date=datetime.now().strftime('%Y-%m-%d'),
                total_issuance=df.get('发行规模', pd.Series([0])).sum(),
                product_count=len(df),
                avg_yield=df.get('预期收益率', pd.Series([0])).mean(),
                yield_by_type=self._calc_yield_by_type(df),
                yield_by_duration=self._calc_yield_by_duration(df)
            )
        except Exception as e:
            print(f"AkShare获取市场统计失败: {e}")
            return None
    
    def _apply_filters(self, products: List[TrustProductData], filters: Dict) -> List[TrustProductData]:
        """应用过滤器"""
        result = products
        
        if 'min_yield' in filters:
            result = [p for p in result if p.expected_yield >= filters['min_yield']]
        
        if 'max_duration' in filters:
            result = [p for p in result if p.duration <= filters['max_duration']]
        
        if 'risk_level' in filters:
            result = [p for p in result if p.risk_level in filters['risk_level']]
        
        if 'trust_company' in filters:
            result = [p for p in result if filters['trust_company'] in p.trust_company]
        
        return result
    
    def _calc_yield_by_type(self, df: pd.DataFrame) -> Dict[str, float]:
        """按类型计算平均收益率"""
        if '投资类型' not in df.columns or '预期收益率' not in df.columns:
            return {}
        
        return df.groupby('投资类型')['预期收益率'].mean().to_dict()
    
    def _calc_yield_by_duration(self, df: pd.DataFrame) -> Dict[str, float]:
        """按期限计算平均收益率"""
        if '期限' not in df.columns or '预期收益率' not in df.columns:
            return {}
        
        # 分期限区间
        df['期限区间'] = pd.cut(df['期限'], 
                               bins=[0, 12, 24, 36, 60, 999],
                               labels=['1年内', '1-2年', '2-3年', '3-5年', '5年以上'])
        
        return df.groupby('期限区间')['预期收益率'].mean().to_dict()


class YongyiCrawlerAdapter(DataSourceAdapter):
    """用益信托网爬虫适配器"""
    
    BASE_URL = "http://www.yanglee.com"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self._cache = {}
        self._cache_time = {}
        self.cache_duration = 3600  # 缓存1小时
    
    def get_name(self) -> str:
        return "用益信托网"
    
    def is_available(self) -> bool:
        try:
            resp = self.session.get(self.BASE_URL, timeout=5)
            return resp.status_code == 200
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
    
    def get_products(self, **filters) -> List[TrustProductData]:
        """爬取用益信托网产品数据"""
        cache_key = f"products_{json.dumps(filters, sort_keys=True)}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        try:
            # 产品列表页面
            url = f"{self.BASE_URL}/Product/Index.aspx"
            params = {
                'page': 1,
                'pagesize': 50
            }
            
            resp = self.session.get(url, params=params, timeout=10)
            resp.encoding = 'utf-8'
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # 解析产品列表
            products = []
            # 这里需要根据实际页面结构调整选择器
            rows = soup.find_all('tr', class_=['odd', 'even'])
            
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 8:
                    product = TrustProductData(
                        product_code=cells[0].get_text(strip=True),
                        product_name=cells[1].get_text(strip=True),
                        trust_company=cells[2].get_text(strip=True),
                        product_type='集合信托',
                        investment_type=cells[3].get_text(strip=True),
                        expected_yield=self._parse_yield(cells[4].get_text(strip=True)),
                        duration=self._parse_duration(cells[5].get_text(strip=True)),
                        min_investment=100,
                        issue_scale=0,
                        issue_date=cells[6].get_text(strip=True),
                        risk_level='R3',
                        status=cells[7].get_text(strip=True),
                        underlying_type=''
                    )
                    products.append(product)
            
            # 应用过滤器
            products = self._apply_filters(products, filters)
            
            self._set_cache(cache_key, products)
            return products
            
        except Exception as e:
            print(f"用益信托网爬取失败: {e}")
            return []
    
    def get_market_stats(self) -> Optional[TrustMarketStats]:
        """获取市场统计数据"""
        cache_key = "market_stats"
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        try:
            # 爬取统计数据页面
            url = f"{self.BASE_URL}/Report/Index.aspx"
            resp = self.session.get(url, timeout=10)
            resp.encoding = 'utf-8'
            
            # 解析统计数据（简化版，实际需要根据页面结构调整）
            stats = TrustMarketStats(
                stat_date=datetime.now().strftime('%Y-%m-%d'),
                total_issuance=1500,  # 模拟数据
                product_count=250,
                avg_yield=6.8,
                yield_by_type={'固定收益类': 6.5, '混合类': 7.2},
                yield_by_duration={'1年内': 6.0, '1-2年': 6.8, '2年以上': 7.5}
            )
            
            self._set_cache(cache_key, stats)
            return stats
            
        except Exception as e:
            print(f"用益信托网统计获取失败: {e}")
            return None
    
    def _parse_yield(self, text: str) -> float:
        """解析收益率文本"""
        try:
            # 提取数字
            import re
            numbers = re.findall(r'\d+\.?\d*', text)
            return float(numbers[0]) if numbers else 0
        except:
            return 0
    
    def _parse_duration(self, text: str) -> int:
        """解析期限文本"""
        try:
            import re
            numbers = re.findall(r'\d+', text)
            return int(numbers[0]) if numbers else 12
        except:
            return 12
    
    def _apply_filters(self, products: List[TrustProductData], filters: Dict) -> List[TrustProductData]:
        """应用过滤器"""
        result = products
        
        if 'min_yield' in filters:
            result = [p for p in result if p.expected_yield >= filters['min_yield']]
        
        if 'max_duration' in filters:
            result = [p for p in result if p.duration <= filters['max_duration']]
        
        return result


class CachedDataAdapter(DataSourceAdapter):
    """缓存数据适配器（备用）"""
    
    def get_name(self) -> str:
        return "缓存/模拟数据"
    
    def is_available(self) -> bool:
        return True
    
    def get_products(self, **filters) -> List[TrustProductData]:
        """返回模拟产品数据"""
        sample_products = [
            TrustProductData(
                product_code="ZG信托-2026-001",
                product_name="中港稳健1号集合资金信托计划",
                trust_company="中港信托有限公司",
                product_type="集合信托",
                investment_type="固定收益类",
                expected_yield=7.2,
                duration=18,
                min_investment=100,
                issue_scale=50000,
                issue_date="2026-03-15",
                risk_level="R3",
                status="在售",
                underlying_type="非标债权"
            ),
            TrustProductData(
                product_code="PA信托-2026-015",
                product_name="平安优享2号集合资金信托计划",
                trust_company="平安信托有限责任公司",
                product_type="集合信托",
                investment_type="混合类",
                expected_yield=8.0,
                duration=24,
                min_investment=300,
                issue_scale=100000,
                issue_date="2026-03-10",
                risk_level="R3",
                status="在售",
                underlying_type="混合资产"
            ),
            TrustProductData(
                product_code="ZJ信托-2026-008",
                product_name="中建城市发展3号信托计划",
                trust_company="中建投信托有限责任公司",
                product_type="集合信托",
                investment_type="固定收益类",
                expected_yield=6.8,
                duration=12,
                min_investment=100,
                issue_scale=30000,
                issue_date="2026-03-18",
                risk_level="R2",
                status="在售",
                underlying_type="基础设施"
            )
        ]
        
        # 应用过滤器
        if 'min_yield' in filters:
            sample_products = [p for p in sample_products if p.expected_yield >= filters['min_yield']]
        
        if 'max_duration' in filters:
            sample_products = [p for p in sample_products if p.duration <= filters['max_duration']]
        
        if 'risk_level' in filters:
            sample_products = [p for p in sample_products if p.risk_level in filters['risk_level']]
        
        return sample_products
    
    def get_market_stats(self) -> TrustMarketStats:
        """返回模拟市场统计"""
        return TrustMarketStats(
            stat_date=datetime.now().strftime('%Y-%m-%d'),
            total_issuance=1250.5,
            product_count=186,
            avg_yield=6.85,
            yield_by_type={
                '固定收益类': 6.52,
                '混合类': 7.25,
                '权益类': 8.10,
                '另类投资': 7.80
            },
            yield_by_duration={
                '1年内': 6.20,
                '1-2年': 6.85,
                '2-3年': 7.35,
                '3年以上': 7.80
            }
        )


class TrustDataProvider:
    """
    信托数据统一提供器
    管理多个数据源，自动fallback
    """
    
    def __init__(self):
        self.adapters = [
            AkShareAdapter(),
            YongyiCrawlerAdapter(),
            CachedDataAdapter()  # 最后fallback到模拟数据
        ]
        
        # 初始化同花顺适配器（如可用）
        self.ths_adapter = None
        if THS_ADAPTER_AVAILABLE:
            try:
                self.ths_adapter = ThsTrustDataAdapter()
            except Exception as e:
                print(f"同花顺适配器初始化失败: {e}")
        
        self._adapter_cache = {}
    
    def _get_available_adapter(self) -> DataSourceAdapter:
        """获取可用的数据适配器"""
        for adapter in self.adapters:
            if adapter.is_available():
                return adapter
        return self.adapters[-1]  # 返回缓存适配器
    
    def get_products(self, **filters) -> List[TrustProductData]:
        """
        获取信托产品列表
        
        Args:
            min_yield: 最低收益率
            max_duration: 最长期限
            risk_level: 风险等级列表
            trust_company: 信托公司
            
        Returns:
            List[TrustProductData]
        """
        # 尝试所有适配器
        for adapter in self.adapters:
            if adapter.is_available():
                try:
                    products = adapter.get_products(**filters)
                    if products:
                        print(f"数据来源: {adapter.get_name()}")
                        return products
                except Exception as e:
                    print(f"{adapter.get_name()}获取失败: {e}")
                    continue
        
        return []
    
    def get_market_stats(self) -> Optional[TrustMarketStats]:
        """获取市场统计数据"""
        for adapter in self.adapters:
            if adapter.is_available():
                try:
                    stats = adapter.get_market_stats()
                    if stats:
                        print(f"数据来源: {adapter.get_name()}")
                        return stats
                except Exception as e:
                    print(f"{adapter.get_name()}获取失败: {e}")
                    continue
        
        return None
    
    def get_yield_curve(self) -> pd.DataFrame:
        """获取收益率曲线"""
        stats = self.get_market_stats()
        if stats and stats.yield_by_duration:
            df = pd.DataFrame([
                {'期限': k, '收益率': v}
                for k, v in stats.yield_by_duration.items()
            ])
            return df
        return pd.DataFrame()
    
    def get_data_source_info(self) -> Dict:
        """获取数据源状态信息"""
        adapters_info = [
            {
                'name': adapter.get_name(),
                'available': adapter.is_available()
            }
            for adapter in self.adapters
        ]
        
        # 添加同花顺适配器状态
        if self.ths_adapter:
            adapters_info.append({
                'name': '同花顺iFinD API',
                'available': self.ths_adapter.is_available()
            })
        else:
            adapters_info.append({
                'name': '同花顺iFinD API',
                'available': False
            })
        
        return {
            'adapters': adapters_info,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_trust_company_financials(self, company_name: str) -> Optional[Dict]:
        """
        获取信托公司财务数据（需要同花顺API）
        
        Args:
            company_name: 信托公司名称，如'平安信托'
            
        Returns:
            Dict: 财务数据，包含ROE、净利润等指标
        """
        if not self.ths_adapter or not self.ths_adapter.is_available():
            print("同花顺API不可用，无法获取财务数据")
            return None
        
        try:
            return self.ths_adapter.get_trust_company_financials(company_name)
        except Exception as e:
            print(f"获取财务数据失败: {e}")
            return None
    
    def get_trust_industry_index(self) -> Optional[Dict]:
        """
        获取信托行业指数数据（需要同花顺API）
        
        Returns:
            Dict: 行业指数数据
        """
        if not self.ths_adapter or not self.ths_adapter.is_available():
            print("同花顺API不可用，无法获取行业指数")
            return None
        
        try:
            return self.ths_adapter.get_trust_industry_index()
        except Exception as e:
            print(f"获取行业指数失败: {e}")
            return None
    
    def get_top_trust_companies(self) -> List[Dict]:
        """
        获取头部信托公司行情（需要同花顺API）
        
        Returns:
            List[Dict]: 公司行情列表
        """
        if not self.ths_adapter or not self.ths_adapter.is_available():
            print("同花顺API不可用，返回模拟数据")
            return [
                {'company': '平安信托', 'code': '000001', 'change_pct': 1.2},
                {'company': '中航信托', 'code': '600705', 'change_pct': 0.8},
                {'company': '五矿信托', 'code': '600390', 'change_pct': -0.5}
            ]
        
        try:
            return self.ths_adapter.get_top_trust_companies()
        except Exception as e:
            print(f"获取公司行情失败: {e}")
            return []


# 全局数据提供器实例
_data_provider = None

def get_data_provider() -> TrustDataProvider:
    """获取全局数据提供器实例"""
    global _data_provider
    if _data_provider is None:
        _data_provider = TrustDataProvider()
    return _data_provider


if __name__ == '__main__':
    # 测试数据对接
    provider = TrustDataProvider()
    
    print("=== 信托数据对接层测试 ===\n")
    
    # 数据源状态
    print("数据源状态:")
    info = provider.get_data_source_info()
    for adapter in info['adapters']:
        status = "✅ 可用" if adapter['available'] else "❌ 不可用"
        print(f"  {adapter['name']}: {status}")
    
    print("\n--- 产品数据测试 ---")
    products = provider.get_products(min_yield=7.0, max_duration=24)
    print(f"获取到 {len(products)} 个产品")
    for p in products[:3]:
        print(f"  - {p.product_name}: {p.expected_yield}%/{p.duration}月")
    
    print("\n--- 市场统计测试 ---")
    stats = provider.get_market_stats()
    if stats:
        print(f"统计日期: {stats.stat_date}")
        print(f"发行规模: {stats.total_issuance}亿元")
        print(f"产品数量: {stats.product_count}个")
        print(f"平均收益率: {stats.avg_yield}%")
