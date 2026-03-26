#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
50个基线数据代码化 - 主入口模块
整合A/B/C三类数据的代码化改造
"""

from utils.data_api_service import (
    StockDataAPI, FundDataAPI, MarketDataAPI,
    FinancialMetricsAPI, TradingRulesAPI, MarginTradingAPI,
    fund_data_service
)
from utils.enum_definitions import (
from utils.template_service import template_service
# ===== AkShare开源数据支持（新增） =====
from skillsChoice.common.unified_data_api import (
    get_data_api,
    get_bond_list,
    get_fund_quote,
    get_futures_quote,
    get_stock_quote,
    get_financial_report,
    get_index_quote,
    get_stock_history,
)
# ====================================
    RegionCode, CSRCIndustryCode, SWIndustryLevel1,
    FundInvestmentType, FundOperationType, FundStyle,
    ProductRiskLevel, InvestorRiskType,
    ExchangeCode, BoardType,
    CurrencyCode, TransactionType, OrderStatus,
    FundFeeRate, DocumentType,
    AccountType, AccountSubtype, AccountStatus,
    SalesChannel, BankCode,
    enum_service
)

__version__ = "1.0.0"
__all__ = [
    # API服务
    "StockDataAPI", "FundDataAPI", "MarketDataAPI",
    "FinancialMetricsAPI", "TradingRulesAPI", "MarginTradingAPI",
    "fund_data_service",
    # 模板服务
    "template_service",
    # 枚举定义
    "RegionCode", "CSRCIndustryCode", "SWIndustryLevel1",
    "FundInvestmentType", "FundOperationType", "FundStyle",
    "ProductRiskLevel", "InvestorRiskType",
    "ExchangeCode", "BoardType",
    "CurrencyCode", "TransactionType", "OrderStatus",
    "FundFeeRate", "DocumentType",
    "AccountType", "AccountSubtype", "AccountStatus",
    "SalesChannel", "BankCode",
    "enum_service"
]


def demo_all():
    """演示所有代码化功能"""
    print("=" * 60)
    print("50个基线数据代码化 - 功能演示")
    print("=" * 60)

    # A类数据演示
    print("\n【A类数据 - API实时获取】")
    print("-" * 40)

    print("\n1. 股票列表API:")
    stocks = StockDataAPI.get_stock_list("all")
    print(f"   获取股票数量: {len(stocks)}")
    if stocks:
        print(f"   示例: {stocks[0].get('代码', 'N/A')} {stocks[0].get('名称', 'N/A')}")

    print("\n2. 基金列表API:")
    funds = FundDataAPI.get_fund_list("equity")
    print(f"   获取基金数量: {len(funds)}")

    print("\n3. 市场指数API:")
    indices = MarketDataAPI.get_market_indices()
    print(f"   获取指数数量: {len(indices)}")
    for name in list(indices.keys())[:2]:
        print(f"   - {name}: {indices[name].get('latest', 'N/A')}")

    print("\n4. 交易规则API:")
    hours = TradingRulesAPI.get_trading_hours("A股")
    print(f"   A股交易时间: {hours['morning']['start']}-{hours['morning']['end']}")

    # B类数据演示
    print("\n【B类数据 - Jinja2模板渲染】")
    print("-" * 40)

    print("\n1. 合同模板:")
    contract = template_service.render_contract({
        "party_a": "张三",
        "party_b": "XX基金管理有限公司",
        "fund_name": "XX价值精选混合",
        "fund_code": "005827",
        "fund_type": "混合型",
        "risk_level": "中高风险",
        "amount": 100000,
        "purchase_fee": 1.5,
        "management_fee": 1.2,
        "custody_fee": 0.2,
        "sign_date": "2024-06-01"
    })
    print(f"   合同长度: {len(contract)} 字符")
    print(f"   预览: {contract[:100]}...")

    print("\n2. 风险揭示书模板:")
    risks = [
        {"type": "市场风险", "description": "基金投资受证券市场波动影响"},
        {"type": "流动性风险", "description": "可能面临赎回困难"},
    ]
    disclosure = template_service.render_risk_disclosure("XX价值精选混合", risks)
    print(f"   揭示书长度: {len(disclosure)} 字符")

    print("\n3. 营销文案模板:")
    marketing = template_service.render_marketing("new_fund", {
        "fund_name": "XX科技创新混合",
        "highlights": ["聚焦科技龙头", "双基金经理管理"],
        "manager": {"name": "李华", "introduction": "15年从业经验"},
        "subscription_start": "2024-06-01",
        "subscription_end": "2024-06-14",
        "min_amount": 10
    })
    print(f"   文案长度: {len(marketing)} 字符")

    # C类数据演示
    print("\n【C类数据 - Enum枚举定义】")
    print("-" * 40)

    print("\n1. 区域代码枚举:")
    print(f"   北京: {RegionCode.BEIJING.code} - {RegionCode.BEIJING.cn_name}")
    print(f"   上海: {RegionCode.SHANGHAI.code} - {RegionCode.SHANGHAI.cn_name}")

    print("\n2. 基金类型枚举:")
    for ft in [FundInvestmentType.EQUITY, FundInvestmentType.BOND]:
        print(f"   {ft.cn_name}: 风险等级-{ft.risk_level}")

    print("\n3. 风险等级枚举:")
    for level in ProductRiskLevel:
        print(f"   R{level.value}: {level.cn_name}")

    print("\n4. 适当性匹配:")
    investor = InvestorRiskType.C3_BALANCED
    product = ProductRiskLevel.R3_MEDIUM
    match = enum_service.check_suitability(investor, product)
    print(f"   {investor.cn_name} 匹配 R{product.value}: {'✓ 适合' if match else '✗ 不适合'}")

    print("\n5. 费率计算:")
    rate = FundFeeRate.get_purchase_rate("EQUITY", 500000)
    print(f"   股票型基金申购50万费率: {rate*100}%")

    redemption_rate = FundFeeRate.get_redemption_rate("EQUITY", 60)
    print(f"   股票型基金持有60天赎回费率: {redemption_rate*100}%")

    print("\n6. 交易所枚举:")
    for ex in [ExchangeCode.SSE, ExchangeCode.SZSE]:
        print(f"   {ex.short_name}: {ex.full_name}")

    print("\n7. 板块匹配:")
    print(f"   600519属于主板: {BoardType.MAIN.matches_code('600519')}")
    print(f"   300750属于创业板: {BoardType.CHINEXT.matches_code('300750')}")
    print(f"   688008属于科创板: {BoardType.STAR.matches_code('688008')}")

    print("\n8. 交易类型枚举:")
    print(f"   申购: {TransactionType.PURCHASE.code} - {TransactionType.PURCHASE.cn_name}")
    print(f"   赎回: {TransactionType.REDEMPTION.code} - {TransactionType.REDEMPTION.cn_name}")

    print("\n9. 销售渠道枚举:")
    for ch in [SalesChannel.DIRECT, SalesChannel.BANK]:
        print(f"   {ch.cn_name}: 费率折扣 {ch.fee_discount}")

    print("\n" + "=" * 60)
    print("演示完成!")
    print("=" * 60)


if __name__ == "__main__":
    demo_all()
