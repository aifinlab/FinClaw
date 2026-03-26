#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
C类数据 枚举化改造 - Enum枚举类定义
"""

from dataclasses import dataclass
from enum import Enum, auto, IntEnum
from typing import Dict, List, Optional


# ========== 文件 31: region_codes.py (改造后) ==========

class RegionCode(Enum):
    """
    区域代码枚举 - 改造前: REGION_CODES = {"北京": "110000", ...}
    """
    BEIJING = ("110000", "北京")
    TIANJIN = ("120000", "天津")
    HEBEI = ("130000", "河北")
    SHANXI = ("140000", "山西")
    INNER_MONGOLIA = ("150000", "内蒙古")
    LIAONING = ("210000", "辽宁")
    JILIN = ("220000", "吉林")
    HEILONGJIANG = ("230000", "黑龙江")
    SHANGHAI = ("310000", "上海")
    JIANGSU = ("320000", "江苏")
    ZHEJIANG = ("330000", "浙江")
    ANHUI = ("340000", "安徽")
    FUJIAN = ("350000", "福建")
    JIANGXI = ("360000", "江西")
    SHANDONG = ("370000", "山东")
    HENAN = ("410000", "河南")
    HUBEI = ("420000", "湖北")
    HUNAN = ("430000", "湖南")
    GUANGDONG = ("440000", "广东")
    GUANGXI = ("450000", "广西")
    HAINAN = ("460000", "海南")
    CHONGQING = ("500000", "重庆")
    SICHUAN = ("510000", "四川")
    GUIZHOU = ("520000", "贵州")
    YUNNAN = ("530000", "云南")
    TIBET = ("540000", "西藏")
    SHAANXI = ("610000", "陕西")
    GANSU = ("620000", "甘肃")
    QINGHAI = ("630000", "青海")
    NINGXIA = ("640000", "宁夏")
    XINJIANG = ("650000", "新疆")

    def __init__(self, code: str, name: str):
        self.code = code
        self.cn_name = name

    @classmethod
    def get_by_code(cls, code: str) -> Optional["RegionCode"]:
        """根据代码获取枚举"""
        for member in cls:
            if member.code == code:
                return member
        return None

    @classmethod
    def get_by_name(cls, name: str) -> Optional["RegionCode"]:
        """根据名称获取枚举"""
        for member in cls:
            if member.cn_name == name:
                return member
        return None


# ========== 文件 32: industry_classifications.py (改造后) ==========

class CSRCIndustryCode(Enum):
    """
    证监会行业分类代码 - 改造前: CSRC_INDUSTRY = {"A": {...}, ...}
    """
    A = ("A", "农、林、牧、渔业")
    B = ("B", "采矿业")
    C = ("C", "制造业")
    D = ("D", "电力、热力、燃气及水生产和供应业")
    E = ("E", "建筑业")
    F = ("F", "批发和零售业")
    G = ("G", "交通运输、仓储和邮政业")
    H = ("H", "住宿和餐饮业")
    I = ("I", "信息传输、软件和信息技术服务业")
    J = ("J", "金融业")
    K = ("K", "房地产业")
    L = ("L", "租赁和商务服务业")
    M = ("M", "科学研究和技术服务业")
    N = ("N", "水利、环境和公共设施管理业")
    O = ("O", "居民服务、修理和其他服务业")
    P = ("P", "教育")
    Q = ("Q", "卫生和社会工作")
    R = ("R", "文化、体育和娱乐业")
    S = ("S", "综合")

    def __init__(self, code: str, name: str):
        self.code = code
        self.cn_name = name


class SWIndustryLevel1(Enum):
    """申万一级行业"""
    AGRICULTURE = ("801010", "农林牧渔")
    CHEMICAL = ("801030", "基础化工")
    STEEL = ("801040", "钢铁")
    NONFERROUS = ("801050", "有色金属")
    BUILDING_MATERIALS = ("801060", "建筑材料")
    CONSTRUCTION = ("801070", "建筑装饰")
    ELECTRICAL_EQUIP = ("801080", "电力设备")
    MACHINERY = ("801090", "机械设备")
    DEFENSE = ("801100", "国防军工")
    AUTOMOBILE = ("801110", "汽车")
    APPLIANCE = ("801120", "家用电器")
    TEXTILE = ("801130", "纺织服饰")
    LIGHT_INDUSTRY = ("801140", "轻工制造")
    COMMERCE = ("801150", "商贸零售")
    FOOD_BEVERAGE = ("801160", "食品饮料")
    LEISURE = ("801170", "社会服务")
    PHARMACEUTICAL = ("801180", "医药生物")
    UTILITIES = ("801190", "公用事业")
    TRANSPORTATION = ("801200", "交通运输")
    REAL_ESTATE = ("801210", "房地产")
    ELECTRONICS = ("801220", "电子")
    COMPUTER = ("801230", "计算机")
    MEDIA = ("801240", "传媒")
    COMMUNICATION = ("801250", "通信")
    BANK = ("801260", "银行")
    NON_BANK_FINANCE = ("801270", "非银金融")
    COMPREHENSIVE = ("801280", "综合")

    def __init__(self, code: str, name: str):
        self.code = code
        self.cn_name = name


# ========== 文件 33: fund_types.py (改造后) ==========

class FundInvestmentType(Enum):
    """
    基金投资类型 - 改造前: FUND_TYPE_CODES = {"股票型": {...}, ...}
    """
    EQUITY = ("EQUITY", "股票型", "高", "80%以上资产投资于股票")
    BOND = ("BOND", "债券型", "中低", "80%以上资产投资于债券")
    HYBRID = ("HYBRID", "混合型", "中高", "股票和债券投资比例灵活")
    MMF = ("MMF", "货币型", "低", "投资于货币市场工具")
    QDII = ("QDII", "QDII", "高", "投资境外证券市场")
    FOF = ("FOF", "FOF", "中", "投资于其他基金份额")
    REITS = ("REITS", "REITs", "中", "投资于基础设施项目")
    COMMODITY = ("COMMODITY", "商品型", "高", "投资于大宗商品")

    def __init__(self, code: str, cn_name: str, risk_level: str, description: str):
        self.code = code
        self.cn_name = cn_name
        self.risk_level = risk_level
        self.description = description


class FundOperationType(Enum):
    """基金运作方式"""
    OPEN = ("OPEN", "开放式", "份额不固定，可申购赎回")
    CLOSED = ("CLOSED", "封闭式", "份额固定，二级市场交易")
    PERIODIC = ("PERIODIC", "定开式", "定期开放申购赎回")
    HOLDING = ("HOLDING", "持有期", "持有期满后可赎回")

    def __init__(self, code: str, cn_name: str, description: str):
        self.code = code
        self.cn_name = cn_name
        self.description = description


class FundStyle(Enum):
    """基金投资风格"""
    ACTIVE = ("ACTIVE", "主动型", "主动选股择时")
    PASSIVE = ("PASSIVE", "被动型", "跟踪指数")
    INDEX = ("INDEX", "指数型", "复制指数表现")
    ETF = ("ETF", "ETF", "交易所交易基金")
    LOF = ("LOF", "LOF", "上市开放式基金")

    def __init__(self, code: str, cn_name: str, description: str):
        self.code = code
        self.cn_name = cn_name
        self.description = description


# ========== 文件 34: risk_levels.py (改造后) ==========

class ProductRiskLevel(IntEnum):
    """
    产品风险等级 - 改造前: RISK_LEVEL_DEFINITIONS = {"R1": {...}, ...}
    """
    R1_LOW = 1  # 低风险
    R2_LOW_MEDIUM = 2  # 中低风险
    R3_MEDIUM = 3  # 中等风险
    R4_MEDIUM_HIGH = 4  # 中高风险
    R5_HIGH = 5  # 高风险

    @property
    def cn_name(self) -> str:
        names = {
            1: "低风险",
            2: "中低风险",
            3: "中等风险",
            4: "中高风险",
            5: "高风险"
        }
        return names[self.value]

    @property
    def description(self) -> str:
        descriptions = {
            1: "产品结构简单，过往业绩及净值的历史波动率低",
            2: "产品结构简单，过往业绩及净值的历史波动率较低",
            3: "产品结构较简单，过往业绩及净值的历史波动率一般",
            4: "产品结构较复杂，过往业绩及净值的历史波动率较高",
            5: "产品结构复杂，过往业绩及净值的历史波动率很高"
        }
        return descriptions[self.value]

    @property
    def suitable_investor_types(self) -> List[str]:
        """获取适合的投资者类型"""
        suitability = {
            1: ["C1", "C2", "C3", "C4", "C5"],
            2: ["C2", "C3", "C4", "C5"],
            3: ["C3", "C4", "C5"],
            4: ["C4", "C5"],
            5: ["C5"]
        }
        return suitability[self.value]


class InvestorRiskType(Enum):
    """投资者风险类型"""
    C1_CONSERVATIVE = ("C1", "保守型", "低", "短期")
    C2_STEADY = ("C2", "稳健型", "中低", "中短期")
    C3_BALANCED = ("C3", "平衡型", "中等", "中期")
    C4_GROWTH = ("C4", "成长型", "中高", "中长期")
    C5_AGGRESSIVE = ("C5", "进取型", "高", "长期")

    def __init__(self, code: str, cn_name: str, risk_tolerance: str, investment_horizon: str):
        self.code = code
        self.cn_name = cn_name
        self.risk_tolerance = risk_tolerance
        self.investment_horizon = investment_horizon


# ========== 文件 35: exchange_codes.py (改造后) ==========

class ExchangeCode(Enum):
    """
    交易所代码 - 改造前: EXCHANGE_CODES = {"上海证券交易所": {...}, ...}
    """
    SSE = ("SSE", "上海证券交易所", "上交所", "SH", "中国")
    SZSE = ("SZSE", "深圳证券交易所", "深交所", "SZ", "中国")
    BSE = ("BSE", "北京证券交易所", "北交所", "BJ", "中国")
    HKEX = ("HKEX", "香港交易所", "港交所", "HK", "中国香港")
    NYSE = ("NYSE", "纽约证券交易所", "纽交所", "US", "美国")
    NASDAQ = ("NASDAQ", "纳斯达克", "纳斯达克", "US", "美国")
    LSE = ("LSE", "伦敦证券交易所", "伦交所", "UK", "英国")
    TSE = ("TSE", "东京证券交易所", "东交所", "JP", "日本")
    SGX = ("SGX", "新加坡交易所", "新交所", "SG", "新加坡")

    def __init__(self, code: str, full_name: str, short_name: str, market: str, country: str):
        self.code = code
        self.full_name = full_name
        self.short_name = short_name
        self.market = market
        self.country = country


class BoardType(Enum):
    """板块类型"""
    MAIN = ("MAIN", "主板", ["600", "601", "603", "605", "000", "001", "002"])
    CHINEXT = ("CHINEXT", "创业板", ["300", "301"])
    STAR = ("STAR", "科创板", ["688", "689"])
    BSE_BOARD = ("BSE", "北交所", ["43", "83", "87", "88"])

    def __init__(self, code: str, cn_name: str, code_prefixes: List[str]):
        self.code = code
        self.cn_name = cn_name
        self.code_prefixes = code_prefixes

    def matches_code(self, stock_code: str) -> bool:
        """检查股票代码是否属于该板块"""
        return any(stock_code.startswith(prefix) for prefix in self.code_prefixes)


# ========== 文件 36: currency_codes.py (改造后) ==========

class CurrencyCode(Enum):
    """
    货币代码 - 改造前: CURRENCY_CODES = {"CNY": {...}, ...}
    """
    CNY = ("CNY", "人民币", "¥", "中国", True)
    USD = ("USD", "美元", "$", "美国", True)
    EUR = ("EUR", "欧元", "€", "欧元区", True)
    JPY = ("JPY", "日元", "¥", "日本", True)
    GBP = ("GBP", "英镑", "£", "英国", True)
    HKD = ("HKD", "港币", "HK$", "中国香港", False)
    AUD = ("AUD", "澳元", "A$", "澳大利亚", False)
    CAD = ("CAD", "加元", "C$", "加拿大", False)
    SGD = ("SGD", "新加坡元", "S$", "新加坡", False)
    CHF = ("CHF", "瑞士法郎", "Fr", "瑞士", False)

    def __init__(self, code: str, cn_name: str, symbol: str, country: str, is_base: bool):
        self.code = code
        self.cn_name = cn_name
        self.symbol = symbol
        self.country = country
        self.is_base = is_base  # 是否为主要储备货币


# ========== 文件 38: transaction_types.py (改造后) ==========

class TransactionType(Enum):
    """
    交易类型 - 改造前: TRANSACTION_TYPES = {"认购": {...}, ...}
    """
    SUBSCRIPTION = ("SUBS", "认购", "买入", "认购费")
    PURCHASE = ("PURC", "申购", "买入", "申购费")
    REDEMPTION = ("REDM", "赎回", "卖出", "赎回费")
    SIP = ("SIP", "定投", "买入", "申购费")
    CONVERSION = ("CONV", "转换", "转换", "转换费")
    DIV_CASH = ("DIVC", "现金分红", "分红", True)
    DIV_REINVEST = ("DIVR", "红利再投", "分红", False)

    def __init__(self, code: str, cn_name: str, direction: str, fee_or_taxable=None):
        self.code = code
        self.cn_name = cn_name
        self.direction = direction
        if isinstance(fee_or_taxable, str):
            self.fee_type = fee_or_taxable
            self.taxable = None
        else:
            self.fee_type = None
            self.taxable = fee_or_taxable


class OrderStatus(Enum):
    """订单状态"""
    UNCONFIRMED = ("UNCF", "未确认", "交易申请已受理，等待确认")
    SUCCESS = ("SUCC", "确认成功", "交易确认成功")
    FAILED = ("FAIL", "确认失败", "交易确认失败")
    PARTIAL = ("PART", "部分确认", "交易部分确认")
    CANCELLED = ("CNCL", "已撤单", "交易已撤销")
    DEFERRED = ("DEFR", "巨额赎回", "巨额赎回，顺延处理")

    def __init__(self, code: str, cn_name: str, description: str):
        self.code = code
        self.cn_name = cn_name
        self.description = description


# ========== 文件 39: fee_structures.py (改造后) ==========

class FundFeeRate:
    """
    基金费率结构 - 改造前: PURCHASE_FEE_RATES = {...}
    使用类方法来管理不同费率档次
    """

    PURCHASE_TIERS = {
        "EQUITY": [
            (0, 1000000, 0.0150),
            (1000000, 5000000, 0.0120),
            (5000000, 10000000, 0.0080),
            (10000000, float('inf'), 0.0100)
        ],
        "BOND": [
            (0, 1000000, 0.0080),
            (1000000, 5000000, 0.0050),
            (5000000, float('inf'), 0.0030)
        ],
        "HYBRID": [
            (0, 1000000, 0.0150),
            (1000000, 5000000, 0.0120),
            (5000000, float('inf'), 0.0080)
        ],
        "MMF": [
            (0, float('inf'), 0.0)
        ]
    }

    REDEMPTION_TIERS = {
        "EQUITY": [
            (0, 7, 0.0150),
            (7, 30, 0.0075),
            (30, 365, 0.0050),
            (365, float('inf'), 0.0)
        ],
        "BOND": [
            (0, 7, 0.0150),
            (7, 30, 0.0010),
            (30, float('inf'), 0.0)
        ]
    }

    MANAGEMENT_FEE = {
        "ACTIVE_EQUITY": 0.0150,
        "INDEX_EQUITY": 0.0050,
        "BOND": 0.0060,
        "HYBRID": 0.0120,
        "MMF": 0.0033,
        "FOF": 0.0100
    }

    CUSTODY_FEE = {
        "EQUITY": 0.0025,
        "BOND": 0.0020,
        "HYBRID": 0.0025,
        "MMF": 0.0010,
        "FOF": 0.0020
    }

    @classmethod
    def get_purchase_rate(cls, fund_type: str, amount: float) -> float:
        """获取申购费率"""
        tiers = cls.PURCHASE_TIERS.get(fund_type.upper(), [])
        for min_amt, max_amt, rate in tiers:
            if min_amt <= amount < max_amt:
                return rate
        return 0.0

    @classmethod
    def get_redemption_rate(cls, fund_type: str, holding_days: int) -> float:
        """获取赎回费率"""
        tiers = cls.REDEMPTION_TIERS.get(fund_type.upper(), [])
        for min_days, max_days, rate in tiers:
            if min_days <= holding_days < max_days:
                return rate
        return 0.0


# ========== 文件 40: document_types.py (改造后) ==========

class DocumentType(Enum):
    """
    文档类型 - 改造前: DOCUMENT_TYPES = {...}
    """
    FUND_CONTRACT = ("FUND_CTR", "基金合同", "募集", True, 20)
    PROSPECTUS = ("FUND_PROS", "招募说明书", "募集", True, 20)
    CUSTODY_AGREEMENT = ("CUST_AGR", "托管协议", "募集", True, 20)
    PRODUCT_SUMMARY = ("PROD_SUM", "产品资料概要", "募集", True, 20)
    RISK_DISCLOSURE = ("RISK_DISC", "风险揭示书", "募集", True, 20)
    QUARTERLY_REPORT = ("QTR_RPT", "季度报告", "定期", True, 20)
    SEMI_ANNUAL_REPORT = ("HALF_RPT", "中期报告", "定期", True, 20)
    ANNUAL_REPORT = ("ANNUAL_RPT", "年度报告", "定期", True, 20)
    MANAGER_CHANGE = ("MGR_CHG", "基金经理变更", "临时", True, None)
    DIVIDEND_NOTICE = ("DIV_ANN", "分红公告", "临时", True, None)

    def __init__(self, code: str, cn_name: str, category: str, required: bool, retention_years: Optional[int]):
        self.code = code
        self.cn_name = cn_name
        self.category = category
        self.required = required
        self.retention_years = retention_years


# ========== 文件 41: account_types.py (改造后) ==========

class AccountType(Enum):
    """
    账户类型 - 改造前: ACCOUNT_TYPES = {...}
    """
    INDIVIDUAL = ("IND", "个人")
    INSTITUTION = ("INS", "机构")
    PRODUCT = ("PROD", "产品")

    def __init__(self, code: str, cn_name: str):
        self.code = code
        self.cn_name = cn_name


class AccountSubtype(Enum):
    """账户子类型"""
    # 个人
    IND_NORMAL = ("IND_NOR", "普通账户", AccountType.INDIVIDUAL)
    IND_PROFESSIONAL = ("IND_PRO", "专业投资者", AccountType.INDIVIDUAL)
    IND_QUALIFIED = ("IND_QF", "合格投资者", AccountType.INDIVIDUAL)
    # 机构
    INS_ENTERPRISE = ("INS_ENT", "企业", AccountType.INSTITUTION)
    INS_FINANCIAL = ("INS_FIN", "金融机构", AccountType.INSTITUTION)
    INS_PUBLIC = ("INS_PUB", "事业单位", AccountType.INSTITUTION)
    # 产品
    PROD_PE = ("PROD_PE", "私募基金", AccountType.PRODUCT)
    PROD_AM = ("PROD_AM", "资管计划", AccountType.PRODUCT)

    def __init__(self, code: str, cn_name: str, parent: AccountType):
        self.code = code
        self.cn_name = cn_name
        self.parent = parent


class AccountStatus(Enum):
    """账户状态"""
    ACTIVE = ("ACT", "正常", "账户正常")
    FROZEN = ("FRZ", "冻结", "账户冻结，不可交易")
    LOST = ("LOST", "挂失", "账户挂失")
    CLOSED = ("CLOSED", "销户", "账户已销户")
    PENDING = ("PEND", "待激活", "账户待激活")

    def __init__(self, code: str, cn_name: str, description: str):
        self.code = code
        self.cn_name = cn_name
        self.description = description


# ========== 文件 42: sales_channels.py (改造后) ==========

class SalesChannel(Enum):
    """
    销售渠道 - 改造前: SALES_CHANNELS = {...}
    """
    DIRECT = ("DIRECT", "直销", 1.0)
    BANK = ("BANK", "银行代销", 0.6)
    SECURITIES = ("SEC", "券商代销", 0.4)
    THIRD_PARTY = ("3RD", "第三方销售", 0.1)

    def __init__(self, code: str, cn_name: str, fee_discount: float):
        self.code = code
        self.cn_name = cn_name
        self.fee_discount = fee_discount


class BankCode(Enum):
    """银行代码"""
    ICBC = ("ICBC", "工商银行")
    CCB = ("CCB", "建设银行")
    ABC = ("ABC", "农业银行")
    BOC = ("BOC", "中国银行")
    CMB = ("CMB", "招商银行")

    def __init__(self, code: str, cn_name: str):
        self.code = code
        self.cn_name = cn_name


# ========== 统一枚举服务 ==========

class EnumService:
    """统一枚举服务"""

    @staticmethod
    def get_all_regions() -> List[Dict]:
        """获取所有区域"""
        return [{"code": r.code, "name": r.cn_name} for r in RegionCode]

    @staticmethod
    def get_all_fund_types() -> List[Dict]:
        """获取所有基金类型"""
        return [{
            "code": t.code,
            "name": t.cn_name,
            "risk_level": t.risk_level,
            "description": t.description
        } for t in FundInvestmentType]

    @staticmethod
    def get_all_risk_levels() -> List[Dict]:
        """获取所有风险等级"""
        return [{
            "level": r.value,
            "name": r.cn_name,
            "description": r.description
        } for r in ProductRiskLevel]

    @staticmethod
    def get_all_exchanges() -> List[Dict]:
        """获取所有交易所"""
        return [{
            "code": e.code,
            "name": e.full_name,
            "short_name": e.short_name,
            "market": e.market
        } for e in ExchangeCode]

    @staticmethod
    def check_suitability(investor_type: InvestorRiskType, product_level: ProductRiskLevel) -> bool:
        """检查适当性匹配"""
        return investor_type.code in product_level.suitable_investor_types


# 全局枚举服务实例
enum_service = EnumService()


if __name__ == "__main__":
    # 测试枚举
    print("=== C类数据Enum测试 ===\n")

    # 测试区域代码
    print("【区域代码】")
    print(f"北京代码: {RegionCode.BEIJING.code}, 名称: {RegionCode.BEIJING.cn_name}")

    # 测试基金类型
    print("\n【基金类型】")
    for ft in FundInvestmentType:
        print(f"{ft.cn_name}: 风险等级-{ft.risk_level}")

    # 测试风险等级
    print("\n【风险等级】")
    for level in ProductRiskLevel:
        print(f"R{level.value}: {level.cn_name} - {level.description[:20]}...")

    # 测试适当性匹配
    print("\n【适当性匹配测试】")
    investor = InvestorRiskType.C3_BALANCED
    product = ProductRiskLevel.R3_MEDIUM
    match = enum_service.check_suitability(investor, product)
    print(f"投资者{investor.cn_name} 匹配 产品{product.cn_name}: {'✓' if match else '✗'}")

    # 测试费率计算
    print("\n【费率计算】")
    rate = FundFeeRate.get_purchase_rate("EQUITY", 500000)
    print(f"股票型基金申购50万元，费率: {rate*100}%")

    redemption_rate = FundFeeRate.get_redemption_rate("EQUITY", 60)
    print(f"股票型基金持有60天赎回，费率: {redemption_rate*100}%")

    # 测试交易所
    print("\n【交易所】")
    for ex in [ExchangeCode.SSE, ExchangeCode.SZSE, ExchangeCode.HKEX]:
        print(f"{ex.short_name}: {ex.full_name}")

    # 测试板块匹配
    print("\n【板块匹配】")
    print(f"600519属于主板: {BoardType.MAIN.matches_code('600519')}")
    print(f"300750属于创业板: {BoardType.CHINEXT.matches_code('300750')}")
    print(f"688008属于科创板: {BoardType.STAR.matches_code('688008')}")
