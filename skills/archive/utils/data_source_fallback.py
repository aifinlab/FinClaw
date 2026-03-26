#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FinClaw 数据源自动切换模块
当主数据源（如同花顺）不可用时，自动切换到备用数据源

使用方法:
    from data_fetcher import FinClawDataFetcher, FetchResult
    result = get_stock_data_with_fallback("600519", prefer_realtime=True)
"""

    from data_source_fallback import get_stock_data_with_fallback
        from datetime import datetime
    from finclaw.core.data_fetcher import FinClawDataFetcher, FetchResult
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple

# 添加核心模块路径
sys.path.insert(0, str(Path(__file__).parent.parent / "finclaw-workspace" / "finclaw" / "core"))

try:
import json
except ImportError:
    # 备用导入路径
    sys.path.insert(0, '/root/.openclaw/workspace/finclaw-workspace')
import os


class DataSourceFallback:
    """
    数据源自动切换管理器
    根据配置自动选择可用数据源
    """

    def __init__(self):
        self.fetcher = FinClawDataFetcher()
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """加载数据源配置"""
        config_path = Path("/root/.openclaw/workspace/finclaw-workspace/finclaw/config/data_source_config.yaml")
        try:
import sys
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"⚠️ 无法加载配置文件: {e}")
            return {}

    def is_source_available(self, source_name: str) -> bool:
        """检查数据源是否可用"""
        source_config = self.config.get('source_config', {})
        source = source_config.get(source_name, {})
        status = source.get('status', 'unknown')
        return status == 'active'

    def get_stock_realtime_with_fallback(self, stock_code: str) -> FetchResult:
        """
        获取股票实时行情（带自动切换）
        优先级: 腾讯财经 → 新浪财经
        """
        # 直接调用fetcher，它内部已经实现了故障转移
        return self.fetcher.get_stock_realtime(stock_code)

    def get_stock_batch_realtime(self, stock_codes: List[str]) -> Dict[str, FetchResult]:
        """
        批量获取股票实时行情

        Args:
            stock_codes: 股票代码列表，如 ['600519', '000001', '300750']

        Returns:
            Dict: {code: FetchResult}
        """
        results = {}
        for code in stock_codes:
            result = self.get_stock_realtime_with_fallback(code)
            results[code] = result
        return results

    def get_industry_chain_data(self, industry_name: str) -> Dict[str, Any]:
        """
        获取产业链数据（带备用数据源）
        当同花顺不可用时，使用akshare-stock获取个股数据再聚合

        Args:
            industry_name: 产业链名称，如"新能源电池"

        Returns:
            Dict: 产业链数据
        """
        # 产业链股票映射
        industry_stocks = {
            "新能源电池": {
                "上游-原材料": ["002460", "002466", "603799"],  # 赣锋锂业、天齐锂业、华友钴业
                "中游-电池制造": ["300919", "300750", "002594"],  # 中伟股份、宁德时代、比亚迪
                "下游-整车应用": ["002074", "300014", "601127", "000625", "601633"],  # 国轩高科、亿纬锂能、赛力斯、长安、长城
            },
            "半导体": {
                "上游-设备材料": ["688012", "688019", "300316"],  # 中微公司、安集科技、晶盛机电
                "中游-设计制造": ["688981", "600584", "002371"],  # 中芯国际、长电科技、北方华创
                "下游-封测应用": ["002156", "603501", "603893"],  # 通富微电、韦尔股份、瑞芯微
            },
            "光伏": {
                "上游-硅料": ["600438", "002129"],  # 通威股份、中环股份
                "中游-硅片电池": ["601012", "688599", "600732"],  # 隆基绿能、天合光能、爱旭股份
                "下游-组件电站": ["688223", "002459", "600011"],  # 晶科能源、晶澳科技、华能国际
            }
        }

        if industry_name not in industry_stocks:
            return {
                "success": False,
                "error": f"暂不支持产业链: {industry_name}",
                "supported": list(industry_stocks.keys())
            }

        # 获取产业链各环节的实时数据
        chain_data = {
            "industry": industry_name,
            "data_source": "tencent_finance",  # 使用腾讯财经
            "segments": {},
            "summary": {}
        }

        total_change_pct = 0
        count = 0

        for segment, codes in industry_stocks[industry_name].items():
            segment_data = {
                "stocks": [],
                "avg_change_pct": 0,
                "leaders": []
            }

            segment_changes = []

            for code in codes:
                result = self.get_stock_realtime_with_fallback(code)
                if result.success:
                    data = result.data
                    stock_info = {
                        "code": code,
                        "name": data.get('name', code),
                        "price": data.get('price', 0),
                        "change_pct": data.get('change_pct', 0)
                    }
                    segment_data["stocks"].append(stock_info)
                    segment_changes.append(stock_info["change_pct"])
                    total_change_pct += stock_info["change_pct"]
                    count += 1

            if segment_changes:
                segment_data["avg_change_pct"] = sum(segment_changes) / len(segment_changes)
                # 找出涨幅前三
                sorted_stocks = sorted(segment_data["stocks"], key=lambda x: x["change_pct"], reverse=True)
                segment_data["leaders"] = sorted_stocks[:3]

            chain_data["segments"][segment] = segment_data

        # 计算整体景气度
        if count > 0:
            overall_change = total_change_pct / count
            if overall_change > 2:
                sentiment = "🔥 高热"
            elif overall_change > 0.5:
                sentiment = "📈 向好"
            elif overall_change > -0.5:
                sentiment = "➡️ 平稳"
            elif overall_change > -2:
                sentiment = "📉 调整"
            else:
                sentiment = "❄️ 低迷"

            chain_data["summary"] = {
                "overall_change_pct": round(overall_change, 2),
                "sentiment": sentiment,
                "total_stocks": count,
                "data_source": "tencent_finance (via fallback from ths)"
            }
            chain_data["success"] = True
        else:
            chain_data["success"] = False
            chain_data["error"] = "无法获取任何股票数据"

        return chain_data

    def get_alert_monitor_data(self, watch_list: List[str]) -> Dict[str, Any]:
        """
        获取异常波动监控数据

        Args:
            watch_list: 关注股票代码列表

        Returns:
            Dict: 监控结果
        """
        results = {
            "timestamp": None,
            "data_source": "tencent_finance",
            "stocks": {},
            "alerts": []
        }

            import yaml
        results["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for code in watch_list:
            result = self.get_stock_realtime_with_fallback(code)
            if result.success:
                data = result.data
                change_pct = abs(data.get('change_pct', 0))

                stock_data = {
                    "name": data.get('name', code),
                    "price": data.get('price', 0),
                    "change_pct": data.get('change_pct', 0),
                    "volume": data.get('volume', 'N/A'),
                    "source": result.source
                }
                results["stocks"][code] = stock_data

                # 检查异常波动阈值 (>5%)
                if change_pct > 5:
                    alert = {
                        "code": code,
                        "name": stock_data["name"],
                        "change_pct": stock_data["change_pct"],
                        "level": "high" if change_pct > 7 else "medium",
                        "time": results["timestamp"]
                    }
                    results["alerts"].append(alert)

        results["total_monitored"] = len(watch_list)
        results["alerts_count"] = len(results["alerts"])

        return results


# ============================================
# 快捷函数
# ============================================

_fallback_manager = None

def get_fallback_manager() -> DataSourceFallback:
    """获取全局Fallback管理器实例"""
    global _fallback_manager
    if _fallback_manager is None:
        _fallback_manager = DataSourceFallback()
    return _fallback_manager

def get_stock_data_with_fallback(stock_code: str) -> FetchResult:
    """快捷获取股票数据（带自动切换）"""
    return get_fallback_manager().get_stock_realtime_with_fallback(stock_code)

def get_industry_chain(industry_name: str) -> Dict[str, Any]:
    """快捷获取产业链数据"""
    return get_fallback_manager().get_industry_chain_data(industry_name)

def get_alert_data(watch_list: List[str]) -> Dict[str, Any]:
    """快捷获取异常监控数据"""
    return get_fallback_manager().get_alert_monitor_data(watch_list)


# ============================================
# 测试代码
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("FinClaw 数据源自动切换模块测试")
    print("=" * 60)

    fallback = DataSourceFallback()

    # 测试1: 单股实时行情
    print("\n[测试1] 获取贵州茅台实时行情（带自动切换）")
    result = fallback.get_stock_realtime_with_fallback("600519")
    print(f"成功: {result.success}")
    print(f"数据源: {result.source}")
    if result.success:
        print(f"股票: {result.data.get('name')}")
        print(f"价格: ¥{result.data.get('price')}")
        print(f"涨跌: {result.data.get('change_pct', 0):.2f}%")

    # 测试2: 产业链数据
    print("\n[测试2] 获取新能源电池产业链数据")
    chain = fallback.get_industry_chain_data("新能源电池")
    if chain.get("success"):
        print(f"产业链: {chain['industry']}")
        print(f"整体景气度: {chain['summary']['sentiment']} ({chain['summary']['overall_change_pct']}%)")
        print(f"监控股票数: {chain['summary']['total_stocks']}")
        for segment, data in chain['segments'].items():
            print(f"  {segment}: {data['avg_change_pct']:.2f}% ({len(data['stocks'])}只股票)")
    else:
        print(f"错误: {chain.get('error')}")

    # 测试3: 异常监控
    print("\n[测试3] 异常波动监控（测试列表）")
    watch_list = ["600519", "000001", "300750"]
    alert_data = fallback.get_alert_monitor_data(watch_list)
    print(f"监控时间: {alert_data['timestamp']}")
    print(f"监控股票: {alert_data['total_monitored']}")
    print(f"异常预警: {alert_data['alerts_count']}")
    for code, data in alert_data['stocks'].items():
        print(f"  {code} ({data['name']}): {data['change_pct']:.2f}%")

    print("\n" + "=" * 60)
    print("测试完成")
