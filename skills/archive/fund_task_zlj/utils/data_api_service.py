#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A类数据 API化改造 - 数据获取模块
统一封装API调用，支持缓存机制
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from functools import wraps
from typing import Dict, List, Optional, Any, Callable
            import akshare as ak
            import akshare as ak
            import akshare as ak
            import akshare as ak

# 缓存配置
CACHE_DIR = "/tmp/fund_data_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

@dataclass
class CacheConfig:
    """缓存配置"""
    ttl_seconds: int = 3600  # 默认缓存1小时
    enabled: bool = True

class DataCache:
    """数据缓存管理器"""

    def __init__(self, cache_dir: str = CACHE_DIR):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

    def _get_cache_key(self, func_name: str, *args, **kwargs) -> str:
        """生成缓存key"""
        key_data = f"{func_name}:{str(args)}:{str(kwargs)}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def _get_cache_path(self, cache_key: str) -> str:
        """获取缓存文件路径"""
        return os.path.join(self.cache_dir, f"{cache_key}.json")

    def get(self, cache_key: str) -> Optional[Any]:
        """获取缓存数据"""
        cache_path = self._get_cache_path(cache_key)
        if not os.path.exists(cache_path):
            return None

        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)

            # 检查是否过期
            if cache_data.get('expire_time', 0) < time.time():
                os.remove(cache_path)
                return None

            return cache_data.get('data')
        except Exception:
            return None

    def set(self, cache_key: str, data: Any, ttl_seconds: int = 3600):
        """设置缓存数据"""
        cache_path = self._get_cache_path(cache_key)
        cache_data = {
            'expire_time': time.time() + ttl_seconds,
            'created_at': datetime.now().isoformat(),
            'data': data
        }
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Cache write error: {e}")

    def clear(self):
        """清空缓存"""
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.json'):
                os.remove(os.path.join(self.cache_dir, filename))


def cached(ttl_seconds: int = 3600, enabled: bool = True):
    """缓存装饰器"""
    cache = DataCache()

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not enabled:
                return func(*args, **kwargs)

            cache_key = cache._get_cache_key(func.__name__, *args, **kwargs)
            cached_data = cache.get(cache_key)

            if cached_data is not None:
                return cached_data

            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl_seconds)
            return result

        return wrapper
    return decorator


# ========== 股票数据 API ==========

class StockDataAPI:
    """股票数据API封装"""

    @staticmethod
    @cached(ttl_seconds=3600)
    def get_stock_list(market: str = "all") -> List[Dict]:
        """
        获取股票列表

        改造前: STOCK_LIST = ["000001", "000002", ...]
        改造后: API实时获取
        """
        try:
            import akshare as ak

            if market == "sh":
                df = ak.stock_sh_a_spot_em()
            elif market == "sz":
                df = ak.stock_sz_a_spot_em()
            else:
                df = ak.stock_zh_a_spot_em()

            return df.to_dict('records')
        except (ImportError, Exception):
            # 模拟数据（当akshare不可用时或网络异常）
            return StockDataAPI._mock_stock_list(market)

    @staticmethod
    def _mock_stock_list(market: str) -> List[Dict]:
        """模拟股票列表（用于演示）"""
        mock_data = []
        sh_codes = ["600000", "600004", "600036", "601318", "601398"]
        sz_codes = ["000001", "000002", "000333", "000538", "000858"]

        codes = sh_codes if market == "sh" else sz_codes if market == "sz" else sh_codes + sz_codes

        for code in codes:
            mock_data.append({
                "代码": code,
                "名称": f"股票{code}",
                "最新价": 10.0,
                "涨跌幅": 0.5
            })
        return mock_data

    @staticmethod
    @cached(ttl_seconds=1800)
    def get_index_components(index_code: str) -> List[str]:
        """
        获取指数成分股

        改造前: HS300_STOCKS = ["000001", "000002", ...]
        改造后: API实时获取
        """
        try:
            import akshare as ak

            index_map = {
                "000300": "沪深300",
                "000905": "中证500",
                "000016": "上证50"
            }

            if index_code in index_map:
                df = ak.index_stock_cons_weight_csindex(symbol=index_code)
                return df["成分券代码"].tolist() if "成分券代码" in df.columns else df["代码"].tolist()

            return []
        except ImportError:
            return []

    @staticmethod
    @cached(ttl_seconds=3600)
    def get_sector_stocks(sector: str) -> List[str]:
        """
        获取行业板块股票

        改造前: TECH_SECTOR_STOCKS = {"半导体": [...], ...}
        改造后: API实时获取
        """
        try:
            import akshare as ak

            # 获取行业板块数据
            df = ak.stock_board_industry_name_em()
            if sector in df["板块名称"].values:
                stocks_df = ak.stock_board_industry_cons_em(symbol=sector)
                return stocks_df["代码"].tolist() if "代码" in stocks_df.columns else []

            return []
        except ImportError:
            return []


# ========== 基金数据 API ==========

class FundDataAPI:
    """基金数据API封装"""

    @staticmethod
    @cached(ttl_seconds=3600)
    def get_fund_list(fund_type: str = "all") -> List[Dict]:
        """
        获取基金列表

        改造前: EQUITY_FUNDS = ["000001", ...]
        改造后: API实时获取
        """
        try:
            import akshare as ak

            type_map = {
                "equity": "股票型",
                "bond": "债券型",
                "hybrid": "混合型",
                "mmf": "货币型"
            }

            df = ak.fund_name_em()

            if fund_type in type_map:
                df = df[df["基金类型"].str.contains(type_map[fund_type], na=False)]

            return df.to_dict('records')
        except ImportError:
            return FundDataAPI._mock_fund_list(fund_type)

    @staticmethod
    def _mock_fund_list(fund_type: str) -> List[Dict]:
        """模拟基金列表"""
        mock_data = []
        equity_codes = ["000001", "000011", "000021", "110022", "005827"]
        bond_codes = ["000032", "000042", "110008", "000171"]

        codes = equity_codes if fund_type == "equity" else bond_codes if fund_type == "bond" else equity_codes + bond_codes

        for code in codes:
            mock_data.append({
                "基金代码": code,
                "基金简称": f"基金{code}",
                "基金类型": "股票型" if code in equity_codes else "债券型"
            })
        return mock_data

    @staticmethod
    @cached(ttl_seconds=7200)
    def get_fund_manager_info(manager_name: str) -> Optional[Dict]:
        """
        获取基金经理信息

        改造前: FUND_MANAGERS = [{"name": "张坤", ...}, ...]
        改造后: API实时获取
        """
        try:
            import akshare as ak

            df = ak.fund_manager_em()
            manager_data = df[df["姓名"] == manager_name]

            if not manager_data.empty:
                return manager_data.iloc[0].to_dict()
            return None
        except ImportError:
            return None

    @staticmethod
    @cached(ttl_seconds=1800)
    def get_fund_nav(fund_code: str) -> Optional[Dict]:
        """
        获取基金净值

        改造前: 硬编码历史净值数据
        改造后: API实时获取
        """
        try:
            import akshare as ak

            df = ak.fund_open_fund_daily_em()
            fund_data = df[df["基金代码"] == fund_code]

            if not fund_data.empty:
                return {
                    "code": fund_code,
                    "nav": fund_data.iloc[0].get("单位净值"),
                    "acc_nav": fund_data.iloc[0].get("累计净值"),
                    "date": fund_data.iloc[0].get("日期")
                }
            return None
        except ImportError:
            return None


# ========== 市场数据 API ==========

class MarketDataAPI:
    """市场数据API封装"""

    @staticmethod
    @cached(ttl_seconds=300)  # 5分钟缓存
    def get_market_indices() -> Dict[str, Dict]:
        """
        获取市场指数行情

        改造前: MARKET_INDICES = {"上证指数": {"latest": 3050.23, ...}, ...}
        改造后: API实时获取
        """
        try:
            import akshare as ak

            # 使用正确的API方法
            df = ak.index_zh_a_spot()
            indices = {}

            for _, row in df.iterrows():
                name = row.get("名称", "")
                indices[name] = {
                    "latest": row.get("最新价"),
                    "change": row.get("涨跌幅"),
                    "volume": row.get("成交量")
                }

            return indices
        except (ImportError, Exception):
            # 返回模拟数据
            return {
                "上证指数": {"latest": 3050.23, "change": 0.52, "volume": 2850.5},
                "深证成指": {"latest": 9876.45, "change": 0.38, "volume": 3650.2}
            }

    @staticmethod
    @cached(ttl_seconds=3600)
    def get_industry_performance() -> List[Dict]:
        """
        获取行业表现

        改造前: INDUSTRY_PERFORMANCE = [{"name": "计算机", ...}, ...]
        改造后: API实时获取
        """
        try:
            import akshare as ak

            df = ak.stock_board_industry_name_em()
            industries = []

            for _, row in df.head(10).iterrows():
                industries.append({
                    "name": row.get("板块名称"),
                    "change": row.get("涨跌幅"),
                    "leading": []  # 需要通过另一个API获取领涨股
                })

            return industries
        except ImportError:
            return [
                {"name": "计算机", "change": 2.35, "leading": []},
                {"name": "通信", "change": 1.98, "leading": []}
            ]

    @staticmethod
    @cached(ttl_seconds=3600)
    def get_historical_prices(code: str, period: str = "1y") -> List[Dict]:
        """
        获取历史价格数据

        改造前: HISTORICAL_PRICES = {"600519": [...], ...}
        改造后: API实时获取
        """
        try:
            import akshare as ak

            if code.startswith("6") or code.startswith("0") or code.startswith("3"):
                df = ak.stock_zh_a_hist(symbol=code, period="daily",
                                        start_date="20230101", end_date="20241231")
                return df.to_dict('records')

            return []
        except ImportError:
            return []

    @staticmethod
    @cached(ttl_seconds=86400)  # 每日更新
    def get_dividend_data() -> List[Dict]:
        """
        获取分红数据

        改造前: DIVIDEND_RECORDS = [{"code": "600519", ...}, ...]
        改造后: API实时获取
        """
        try:
            import akshare as ak

            df = ak.stock_dividend_cninfo()
            return df.to_dict('records')
        except ImportError:
            return []


# ========== 财务指标 API ==========

class FinancialMetricsAPI:
    """财务指标API封装"""

    @staticmethod
    @cached(ttl_seconds=86400)  # 每日更新
    def get_stock_financial_metrics(code: str) -> Optional[Dict]:
        """
        获取股票财务指标

        改造前: FINANCIAL_METRICS = {"ROE": {...}, ...}
        改造后: API实时获取
        """
        try:
import hashlib

            # 获取主要财务指标
            df = ak.stock_financial_analysis_indicator(symbol=code)

            if not df.empty:
                latest = df.iloc[0]
                return {
                    "code": code,
                    "roe": latest.get("净资产收益率"),
                    "pe": latest.get("市盈率"),
                    "pb": latest.get("市净率"),
                    "debt_ratio": latest.get("资产负债率")
                }
            return None
        except ImportError:
            return None

    @staticmethod
    @cached(ttl_seconds=3600)
    def get_index_valuation(index_code: str) -> Optional[Dict]:
        """
        获取指数估值数据

        改造前: BENCHMARK_VALUES = {"沪深300_PE": 12.5, ...}
        改造后: API实时获取
        """
        try:
import json

            # 指数估值数据
            df = ak.index_value_hist_funddb(symbol=index_code)

            if not df.empty:
                latest = df.iloc[-1]
                return {
                    "index": index_code,
                    "pe": latest.get("PE"),
                    "pb": latest.get("PB"),
                    "date": latest.get("日期")
                }
            return None
        except ImportError:
            return None


# ========== 交易规则 API ==========

class TradingRulesAPI:
    """交易规则API封装"""

    @staticmethod
    def get_trading_hours(market: str = "A股") -> Dict:
        """
        获取交易时间

        改造前: TRADING_HOURS = {"A股": {...}, ...}
        改造后: 配置文件 + API验证
        """
        # 基础配置（可通过配置文件管理）
        trading_hours = {
            "A股": {
                "morning": {"start": "09:30", "end": "11:30"},
                "afternoon": {"start": "13:00", "end": "15:00"}
            },
            "港股通": {
                "morning": {"start": "09:30", "end": "12:00"},
                "afternoon": {"start": "13:00", "end": "16:00"}
            }
        }
        return trading_hours.get(market, trading_hours["A股"])

    @staticmethod
    def get_price_limits(board: str = "主板") -> Dict:
        """
        获取涨跌幅限制

        改造前: PRICE_LIMITS = {"主板": {...}, ...}
        改造后: 配置管理
        """
        price_limits = {
            "主板": {"up": 0.10, "down": -0.10},
            "创业板": {"up": 0.20, "down": -0.20},
            "科创板": {"up": 0.20, "down": -0.20},
            "ST股票": {"up": 0.05, "down": -0.05},
            "北交所": {"up": 0.30, "down": -0.30}
        }
        return price_limits.get(board, price_limits["主板"])


# ========== 融资融券数据 API ==========

class MarginTradingAPI:
    """融资融券数据API封装"""

    @staticmethod
    @cached(ttl_seconds=3600)
    def get_margin_stocks() -> List[str]:
        """
        获取融资融券标的券

        改造前: MARGIN_STOCKS = {"标的券": [...], ...}
        改造后: API实时获取
        """
        try:
import os

            df = ak.stock_margin_detail_szse()
            return df["证券代码"].tolist() if "证券代码" in df.columns else []
        except ImportError:
            return []

    @staticmethod
    @cached(ttl_seconds=3600)
    def get_margin_balance() -> Dict:
        """
        获取融资融券余额

        改造前: 硬编码数据
        改造后: API实时获取
        """
        try:
import time

            df = ak.stock_margin_szse()

            if not df.empty:
                latest = df.iloc[-1]
                return {
                    "融资余额": latest.get("融资余额"),
                    "融券余额": latest.get("融券余额"),
                    "日期": latest.get("日期")
                }
            return {}
        except ImportError:
            return {}


# ========== 统一数据接口 ==========

class FundDataService:
    """统一基金数据服务入口"""

    def __init__(self):
        self.stock_api = StockDataAPI()
        self.fund_api = FundDataAPI()
        self.market_api = MarketDataAPI()
        self.financial_api = FinancialMetricsAPI()
        self.trading_api = TradingRulesAPI()
        self.margin_api = MarginTradingAPI()
        self.cache = DataCache()

    def clear_cache(self):
        """清空所有缓存"""
        self.cache.clear()

    def get_data_summary(self) -> Dict:
        """获取数据汇总"""
        return {
            "stock_list_count": len(self.stock_api.get_stock_list()),
            "market_indices": list(self.market_api.get_market_indices().keys()),
            "cache_status": "active"
        }


# 全局数据服务实例
fund_data_service = FundDataService()


if __name__ == "__main__":
    # 测试数据API
    print("=== A类数据API测试 ===")

    # 测试股票列表
    stocks = StockDataAPI.get_stock_list("all")
    print(f"获取股票数量: {len(stocks)}")

    # 测试基金列表
    funds = FundDataAPI.get_fund_list("equity")
    print(f"获取基金数量: {len(funds)}")

    # 测试市场指数
    indices = MarketDataAPI.get_market_indices()
    print(f"获取指数数量: {len(indices)}")

    # 测试缓存
    print("\n=== 缓存测试 ===")
    start = time.time()
    stocks1 = StockDataAPI.get_stock_list("all")
    time1 = time.time() - start

    start = time.time()
    stocks2 = StockDataAPI.get_stock_list("all")
    time2 = time.time() - start

    print(f"首次查询时间: {time1:.4f}s")
    print(f"缓存查询时间: {time2:.4f}s")
    print(f"缓存加速比: {time1/time2:.1f}x")
