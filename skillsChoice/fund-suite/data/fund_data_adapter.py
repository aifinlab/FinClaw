#!/usr/bin/env python3
"""
Fund Suite 数据适配器 - 统一数据获取接口
Fund Suite Data Adapter Layer

支持数据源：
- AkShare（开源优先，免费）
- 同花顺iFinD API（付费，数据更全面）
- 东方财富/腾讯财经（免费备选）

自动降级策略：iFinD → AkShare → 模拟数据
"""

import os
import json
import time
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from functools import lru_cache

import pandas as pd

# 尝试导入AkShare
try:
    import akshare as ak
    AKSHARE_AVAILABLE = True
except ImportError:
    AKSHARE_AVAILABLE = False
    print("警告：AkShare未安装，使用备用数据源")

# 尝试导入同花顺适配器
try:
    from ths_fund_adapter import ThsFundAdapter
    THS_ADAPTER_AVAILABLE = True
except ImportError:
    THS_ADAPTER_AVAILABLE = False


@dataclass
class FundBasicInfo:
    """基金基础信息"""
    fund_code: str
    fund_name: str
    fund_type: str  # 股票型/混合型/债券型/货币型/QDII/FOF
    manager: str
    company: str
    establish_date: str
    nav: float  # 单位净值
    acc_nav: float  # 累计净值
    update_date: str
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class FundNetValue:
    """基金净值数据"""
    fund_code: str
    date: str
    nav: float
    acc_nav: float
    daily_return: float
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class FundPerformance:
    """基金业绩数据"""
    fund_code: str
    return_1m: float
    return_3m: float
    return_6m: float
    return_1y: float
    return_2y: float
    return_3y: float
    return_ytd: float
    return_total: float
    annualized_return: float
    max_drawdown: float
    sharpe_ratio: float
    volatility: float
    update_date: str
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class FundHolding:
    """基金持仓数据"""
    fund_code: str
    stock_code: str
    stock_name: str
    weight: float
    change: float  # 较上期变化
    sector: str
    quarter: str
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class FundSectorAllocation:
    """基金行业配置"""
    fund_code: str
    sector: str
    weight: float
    change: float
    quarter: str
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class FundManagerInfo:
    """基金经理信息"""
    fund_code: str
    manager_name: str
    tenure_start: str
    tenure_days: int
    return_during_tenure: float
    
    def to_dict(self) -> Dict:
        return asdict(self)


class DataSourceAdapter(ABC):
    """数据源适配器基类"""
    
    @abstractmethod
    def get_name(self) -> str:
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        pass
    
    @abstractmethod
    def get_fund_basic(self, fund_code: str) -> Optional[FundBasicInfo]:
        """获取基金基础信息"""
        pass
    
    @abstractmethod
    def get_fund_nav(self, fund_code: str, days: int = 30) -> List[FundNetValue]:
        """获取基金净值历史"""
        pass
    
    @abstractmethod
    def get_fund_performance(self, fund_code: str) -> Optional[FundPerformance]:
        """获取基金业绩表现"""
        pass
    
    @abstractmethod
    def get_fund_holdings(self, fund_code: str, quarter: str = None) -> List[FundHolding]:
        """获取基金持仓"""
        pass
    
    @abstractmethod
    def search_funds(self, keyword: str) -> List[FundBasicInfo]:
        """搜索基金"""
        pass


class AkShareAdapter(DataSourceAdapter):
    """AkShare数据适配器 - 开源免费"""
    
    def __init__(self):
        self.name = "AkShare"
        self._cache = {}
        self._cache_time = {}
        self.cache_duration = 300  # 缓存5分钟
    
    def get_name(self) -> str:
        return self.name
    
    def is_available(self) -> bool:
        return AKSHARE_AVAILABLE
    
    def _get_cached(self, key: str) -> Any:
        """获取缓存"""
        if key in self._cache:
            cache_time = self._cache_time.get(key, 0)
            if time.time() - cache_time < self.cache_duration:
                return self._cache[key]
        return None
    
    def _set_cache(self, key: str, data: Any):
        """设置缓存"""
        self._cache[key] = data
        self._cache_time[key] = time.time()
    
    def get_fund_basic(self, fund_code: str) -> Optional[FundBasicInfo]:
        """获取基金基础信息 - 使用AkShare"""
        cache_key = f"basic_{fund_code}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        try:
            # 获取基金实时行情
            df = ak.fund_open_fund_daily_em()
            fund_row = df[df['基金代码'] == fund_code]
            
            if fund_row.empty:
                return None
            
            row = fund_row.iloc[0]
            
            # 获取基金名称 (列名可能是'基金名称'或'基金简称')
            fund_name = row.get('基金名称', '') or row.get('基金简称', '')
            nav = row.get('单位净值', 0) or row.get('最新净值', 0)
            acc_nav = row.get('累计净值', 0)
            
            info = FundBasicInfo(
                fund_code=fund_code,
                fund_name=fund_name,
                fund_type=self._detect_fund_type(fund_name),
                manager='',  # AkShare需要单独获取
                company='',  # AkShare需要单独获取
                establish_date='',
                nav=float(nav) if pd.notna(nav) else 0.0,
                acc_nav=float(acc_nav) if pd.notna(acc_nav) else 0.0,
                update_date=row.get('日期', datetime.now().strftime('%Y-%m-%d'))
            )
            
            self._set_cache(cache_key, info)
            return info
            
        except Exception as e:
            print(f"AkShare获取基金基础信息失败: {e}")
            return None
    
    def get_fund_nav(self, fund_code: str, days: int = 30) -> List[FundNetValue]:
        """获取基金净值历史 - 使用AkShare"""
        cache_key = f"nav_{fund_code}_{days}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        try:
            # 获取历史净值
            df = ak.fund_open_fund_info_em(symbol=fund_code)
            
            if df.empty:
                return []
            
            # 取最近N天
            df = df.head(days)
            
            nav_list = []
            
            for _, row in df.iterrows():
                nav = float(row.get('单位净值', 0)) if pd.notna(row.get('单位净值')) else 0.0
                # 日增长率直接来自数据
                daily_return_pct = row.get('日增长率', 0)
                if pd.notna(daily_return_pct) and isinstance(daily_return_pct, str):
                    daily_return_pct = daily_return_pct.replace('%', '')
                daily_return = float(daily_return_pct) / 100 if daily_return_pct else 0.0
                
                nav_data = FundNetValue(
                    fund_code=fund_code,
                    date=row.get('净值日期', ''),
                    nav=nav,
                    acc_nav=nav,  # AkShare此接口不返回累计净值，用单位净值代替
                    daily_return=daily_return
                )
                nav_list.append(nav_data)
            
            self._set_cache(cache_key, nav_list)
            return nav_list
            
        except Exception as e:
            print(f"AkShare获取基金净值失败: {e}")
            return []
    
    def get_fund_performance(self, fund_code: str) -> Optional[FundPerformance]:
        """获取基金业绩 - 使用AkShare"""
        cache_key = f"perf_{fund_code}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        try:
            # 使用正确的函数名获取基金排行
            df = ak.fund_open_fund_rank_em()
            fund_row = df[df['基金代码'] == fund_code]
            
            if fund_row.empty:
                return None
            
            row = fund_row.iloc[0]
            
            # 解析百分比字符串
            def parse_pct(val):
                if pd.isna(val):
                    return 0.0
                if isinstance(val, str):
                    return float(val.replace('%', '')) / 100
                return float(val) / 100 if val else 0.0
            
            perf = FundPerformance(
                fund_code=fund_code,
                return_1m=parse_pct(row.get('近1月')),
                return_3m=parse_pct(row.get('近3月')),
                return_6m=parse_pct(row.get('近6月')),
                return_1y=parse_pct(row.get('近1年')),
                return_2y=parse_pct(row.get('近2年')),
                return_3y=parse_pct(row.get('近3年')),
                return_ytd=parse_pct(row.get('今年来')),
                return_total=parse_pct(row.get('成立来')),
                annualized_return=0.0,  # 需要计算
                max_drawdown=0.0,  # AkShare不直接提供
                sharpe_ratio=0.0,  # 需要计算
                volatility=0.0,  # 需要计算
                update_date=datetime.now().strftime('%Y-%m-%d')
            )
            
            self._set_cache(cache_key, perf)
            return perf
            
        except Exception as e:
            print(f"AkShare获取基金业绩失败: {e}")
            return None
    
    def get_fund_holdings(self, fund_code: str, quarter: str = None) -> List[FundHolding]:
        """获取基金持仓 - 使用AkShare"""
        cache_key = f"holdings_{fund_code}_{quarter}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        try:
            # 获取基金持仓 - 使用正确的函数名
            if quarter:
                df = ak.fund_portfolio_hold_em(symbol=fund_code, date=quarter)
            else:
                # 默认获取最新季度
                df = ak.fund_portfolio_hold_em(symbol=fund_code)
            
            if df.empty:
                return []
            
            holdings = []
            for _, row in df.iterrows():
                weight_val = row.get('占净值比例', 0)
                if pd.notna(weight_val):
                    if isinstance(weight_val, str):
                        weight_val = float(weight_val.replace('%', '')) / 100
                    else:
                        weight_val = float(weight_val) / 100
                else:
                    weight_val = 0.0
                
                holding = FundHolding(
                    fund_code=fund_code,
                    stock_code=str(row.get('股票代码', '')),
                    stock_name=str(row.get('股票名称', '')),
                    weight=weight_val,
                    change=0.0,  # 需要对比上一期
                    sector=str(row.get('行业', '')),
                    quarter=quarter or datetime.now().strftime('%YQ%q')
                )
                holdings.append(holding)
            
            self._set_cache(cache_key, holdings)
            return holdings
            
        except Exception as e:
            print(f"AkShare获取基金持仓失败: {e}")
            return []
    
    def search_funds(self, keyword: str) -> List[FundBasicInfo]:
        """搜索基金 - 使用AkShare"""
        try:
            # 获取所有基金列表
            df = ak.fund_name_em()
            
            # 模糊匹配 (使用正确的列名)
            matched = df[df['基金简称'].str.contains(keyword, na=False) | 
                        df['基金代码'].str.contains(keyword, na=False)]
            
            funds = []
            for _, row in matched.head(20).iterrows():  # 限制返回数量
                fund = FundBasicInfo(
                    fund_code=row.get('基金代码', ''),
                    fund_name=row.get('基金简称', ''),
                    fund_type=row.get('基金类型', ''),
                    manager='',
                    company='',
                    establish_date='',
                    nav=0.0,
                    acc_nav=0.0,
                    update_date=''
                )
                funds.append(fund)
            
            return funds
            
        except Exception as e:
            print(f"AkShare搜索基金失败: {e}")
            return []
    
    def _detect_fund_type(self, fund_name: str) -> str:
        """根据基金名称识别类型"""
        name = fund_name.upper()
        if '货币' in name or '现金' in name:
            return '货币型'
        elif '债券' in name or '纯债' in name or '短债' in name:
            return '债券型'
        elif '指数' in name or 'ETF' in name:
            return '指数型'
        elif '混合' in name or '灵活' in name:
            return '混合型'
        elif '股票' in name or ' equity'.upper() in name:
            return '股票型'
        elif 'FOF' in name:
            return 'FOF'
        elif 'QDII' in name:
            return 'QDII'
        return '混合型'


class FundDataAdapter:
    """Fund Suite统一数据适配器"""
    
    def __init__(self, prefer_ths: bool = False):
        """
        初始化数据适配器
        
        Args:
            prefer_ths: 是否优先使用同花顺iFinD (需要配置access_token)
        """
        self.prefer_ths = prefer_ths
        self.adapters: List[DataSourceAdapter] = []
        
        # 初始化适配器 (按优先级)
        if prefer_ths and THS_ADAPTER_AVAILABLE:
            ths_adapter = ThsFundAdapter()
            if ths_adapter.is_available():
                self.adapters.append(ths_adapter)
                print(f"✅ 已加载同花顺iFinD适配器")
        
        if AKSHARE_AVAILABLE:
            ak_adapter = AkShareAdapter()
            if ak_adapter.is_available():
                self.adapters.append(ak_adapter)
                print(f"✅ 已加载AkShare适配器")
        
        if not self.adapters:
            print("⚠️ 警告：无可用数据源适配器")
    
    def _get_adapter(self) -> Optional[DataSourceAdapter]:
        """获取可用的适配器"""
        for adapter in self.adapters:
            if adapter.is_available():
                return adapter
        return None
    
    def get_fund_basic(self, fund_code: str) -> Optional[FundBasicInfo]:
        """获取基金基础信息"""
        adapter = self._get_adapter()
        if adapter:
            return adapter.get_fund_basic(fund_code)
        return None
    
    def get_fund_nav(self, fund_code: str, days: int = 30) -> List[FundNetValue]:
        """获取基金净值历史"""
        adapter = self._get_adapter()
        if adapter:
            return adapter.get_fund_nav(fund_code, days)
        return []
    
    def get_fund_performance(self, fund_code: str) -> Optional[FundPerformance]:
        """获取基金业绩"""
        adapter = self._get_adapter()
        if adapter:
            return adapter.get_fund_performance(fund_code)
        return None
    
    def get_fund_holdings(self, fund_code: str, quarter: str = None) -> List[FundHolding]:
        """获取基金持仓"""
        adapter = self._get_adapter()
        if adapter:
            return adapter.get_fund_holdings(fund_code, quarter)
        return []
    
    def search_funds(self, keyword: str) -> List[FundBasicInfo]:
        """搜索基金"""
        adapter = self._get_adapter()
        if adapter:
            return adapter.search_funds(keyword)
        return []
    
    def get_data_source(self) -> str:
        """获取当前数据源名称"""
        adapter = self._get_adapter()
        return adapter.get_name() if adapter else "None"


# 全局适配器实例
_fund_adapter = None

def get_fund_adapter(prefer_ths: bool = False) -> FundDataAdapter:
    """获取Fund Suite数据适配器 (单例)"""
    global _fund_adapter
    if _fund_adapter is None:
        _fund_adapter = FundDataAdapter(prefer_ths=prefer_ths)
    return _fund_adapter


# 测试代码
if __name__ == '__main__':
    print("=" * 60)
    print("Fund Suite 数据适配器测试")
    print("=" * 60)
    
    adapter = get_fund_adapter()
    print(f"\n当前数据源: {adapter.get_data_source()}")
    
    # 测试搜索
    print("\n搜索基金 '华夏成长':")
    funds = adapter.search_funds("华夏成长")
    for fund in funds[:5]:
        print(f"  {fund.fund_code} - {fund.fund_name}")
    
    # 测试获取净值
    if funds:
        test_code = funds[0].fund_code
        print(f"\n获取基金 {test_code} 最近5天净值:")
        navs = adapter.get_fund_nav(test_code, days=5)
        for nav in navs:
            print(f"  {nav.date}: {nav.nav} ({nav.daily_return*100:+.2f}%)")
