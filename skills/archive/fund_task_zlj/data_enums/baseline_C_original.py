#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件 31-50: C类数据 - 静态参考类数据
改造前: 字典映射
改造后: Enum枚举类或常量定义
"""

# ========== 文件 31: region_codes.py (改造前) ==========
"""
# 改造前 - 硬编码区域代码
REGION_CODES = {
    "北京": "110000",
    "天津": "120000",
    "河北": "130000",
    "山西": "140000",
    "内蒙古": "150000",
    "辽宁": "210000",
    "吉林": "220000",
    "黑龙江": "230000",
    "上海": "310000",
    "江苏": "320000",
    "浙江": "330000",
    "安徽": "340000",
    "福建": "350000",
    "江西": "360000",
    "山东": "370000",
    "河南": "410000",
    "湖北": "420000",
    "湖南": "430000",
    "广东": "440000",
    "广西": "450000",
    "海南": "460000",
    "重庆": "500000",
    "四川": "510000",
    "贵州": "520000",
    "云南": "530000",
    "西藏": "540000",
    "陕西": "610000",
    "甘肃": "620000",
    "青海": "630000",
    "宁夏": "640000",
    "新疆": "650000"
}

CITY_CODES = {
    "北京": {"code": "110000", "districts": {
        "东城区": "110101", "西城区": "110102", "朝阳区": "110105",
        "海淀区": "110108", "丰台区": "110106", "石景山区": "110107"
    }},
    "上海": {"code": "310000", "districts": {
        "黄浦区": "310101", "徐汇区": "310104", "长宁区": "310105",
        "静安区": "310106", "普陀区": "310107", "虹口区": "310109",
        "浦东新区": "310115"
    }}
}
"""

# ========== 文件 32: industry_classifications.py (改造前) ==========
"""
# 改造前 - 硬编码行业分类
CSRC_INDUSTRY = {
    "A": {"name": "农、林、牧、渔业", "sub": {
        "01": "农业", "02": "林业", "03": "畜牧业", "04": "渔业", "05": "农、林、牧、渔服务业"
    }},
    "B": {"name": "采矿业", "sub": {
        "06": "煤炭开采和洗选业", "07": "石油和天然气开采业", "08": "黑色金属矿采选业"
    }},
    "C": {"name": "制造业", "sub": {
        "13": "农副食品加工业", "14": "食品制造业", "15": "酒、饮料和精制茶制造业",
        "26": "化学原料和化学制品制造业", "27": "医药制造业", "34": "通用设备制造业",
        "35": "专用设备制造业", "36": "汽车制造业", "37": "铁路、船舶、航空航天和其他运输设备制造业",
        "39": "计算机、通信和其他电子设备制造业", "40": "仪器仪表制造业"
    }},
    "D": {"name": "电力、热力、燃气及水生产和供应业", "sub": {
        "44": "电力、热力生产和供应业", "45": "燃气生产和供应业"
    }},
    "F": {"name": "批发和零售业", "sub": {
        "51": "批发业", "52": "零售业"
    }},
    "G": {"name": "交通运输、仓储和邮政业", "sub": {
        "53": "铁路运输业", "54": "道路运输业", "55": "水上运输业", "56": "航空运输业"
    }},
    "I": {"name": "信息传输、软件和信息技术服务业", "sub": {
        "63": "电信、广播电视和卫星传输服务", "64": "互联网和相关服务", "65": "软件和信息技术服务业"
    }},
    "J": {"name": "金融业", "sub": {
        "66": "货币金融服务", "67": "资本市场服务", "68": "保险业", "69": "其他金融业"
    }},
    "K": {"name": "房地产业", "sub": {
        "70": "房地产业"
    }}
}

SW_INDUSTRY = {
    "一级": [
        "农林牧渔", "基础化工", "钢铁", "有色金属", "建筑材料", "建筑装饰", "电气设备",
        "机械设备", "国防军工", "汽车", "家用电器", "纺织服装", "轻工制造", "商业贸易",
        "农林牧渔", "食品饮料", "休闲服务", "医药生物", "公用事业", "交通运输", "房地产",
        "电子", "计算机", "传媒", "通信", "银行", "非银金融", "综合"
    ],
    "银行二级": ["国有大型银行", "股份制银行", "城商行", "农商行"],
    "医药二级": ["化学制药", "生物制品", "医疗器械", "医药商业", "中药", "医疗服务"]
}
"""

# ========== 文件 33: fund_types.py (改造前) ==========
"""
# 改造前 - 硬编码基金类型
FUND_TYPE_CODES = {
    # 按投资对象分类
    "股票型": {"code": "EQUITY", "risk_level": "高", "description": "80%以上资产投资于股票"},
    "债券型": {"code": "BOND", "risk_level": "中低", "description": "80%以上资产投资于债券"},
    "混合型": {"code": "HYBRID", "risk_level": "中高", "description": "股票和债券投资比例灵活"},
    "货币型": {"code": "MMF", "risk_level": "低", "description": "投资于货币市场工具"},
    "QDII": {"code": "QDII", "risk_level": "高", "description": "投资境外证券市场"},
    "FOF": {"code": "FOF", "risk_level": "中", "description": "投资于其他基金份额"},
    "REITs": {"code": "REITs", "risk_level": "中", "description": "投资于基础设施项目"},
    "商品型": {"code": "COMMODITY", "risk_level": "高", "description": "投资于大宗商品"},
    
    # 按运作方式分类
    "开放式": {"code": "OPEN", "description": "份额不固定，可申购赎回"},
    "封闭式": {"code": "CLOSED", "description": "份额固定，二级市场交易"},
    "定开式": {"code": "PERIODIC", "description": "定期开放申购赎回"},
    "持有期": {"code": "HOLDING", "description": "持有期满后可赎回"},
    
    # 按投资风格分类
    "主动型": {"code": "ACTIVE", "description": "主动选股择时"},
    "被动型": {"code": "PASSIVE", "description": "跟踪指数"},
    "指数型": {"code": "INDEX", "description": "复制指数表现"},
    "ETF": {"code": "ETF", "description": "交易所交易基金"},
    "LOF": {"code": "LOF", "description": "上市开放式基金"}
}

FUND_SUBTYPES = {
    "股票型细分": ["普通股票型", "被动指数型", "增强指数型"],
    "债券型细分": ["纯债型", "一级债基", "二级债基", "可转债", "指数债基"],
    "混合型细分": ["偏股混合型", "偏债混合型", "平衡混合型", "灵活配置型"]
}
"""

# ========== 文件 34: risk_levels.py (改造前) ==========
"""
# 改造前 - 硬编码风险等级
RISK_LEVEL_DEFINITIONS = {
    "R1": {
        "name": "低风险",
        "description": "产品结构简单，过往业绩及净值的历史波动率低",
        "suitable_investors": "保守型",
        "product_types": ["货币基金", "同业存单基金", "国债", "银行存款"]
    },
    "R2": {
        "name": "中低风险",
        "description": "产品结构简单，过往业绩及净值的历史波动率较低",
        "suitable_investors": "稳健型",
        "product_types": ["债券基金", "偏债混合", "固收+"]
    },
    "R3": {
        "name": "中等风险",
        "description": "产品结构较简单，过往业绩及净值的历史波动率一般",
        "suitable_investors": "平衡型",
        "product_types": ["混合基金", "指数基金", "FOF", "REITs"]
    },
    "R4": {
        "name": "中高风险",
        "description": "产品结构较复杂，过往业绩及净值的历史波动率较高",
        "suitable_investors": "成长型",
        "product_types": ["股票基金", "QDII", "商品基金", "杠杆基金"]
    },
    "R5": {
        "name": "高风险",
        "description": "产品结构复杂，过往业绩及净值的历史波动率很高",
        "suitable_investors": "进取型",
        "product_types": ["衍生品基金", "复杂结构化产品", "私募股权投资"]
    }
}

INVESTOR_RISK_TYPES = {
    "C1": {"name": "保守型", "risk_tolerance": "低", "investment_horizon": "短期"},
    "C2": {"name": "稳健型", "risk_tolerance": "中低", "investment_horizon": "中短期"},
    "C3": {"name": "平衡型", "risk_tolerance": "中等", "investment_horizon": "中期"},
    "C4": {"name": "成长型", "risk_tolerance": "中高", "investment_horizon": "中长期"},
    "C5": {"name": "进取型", "risk_tolerance": "高", "investment_horizon": "长期"}
}
"""

# ========== 文件 35: exchange_codes.py (改造前) ==========
"""
# 改造前 - 硬编码交易所代码
EXCHANGE_CODES = {
    "上海证券交易所": {"code": "SSE", "short": "上交所", "market": "SH"},
    "深圳证券交易所": {"code": "SZSE", "short": "深交所", "market": "SZ"},
    "北京证券交易所": {"code": "BSE", "short": "北交所", "market": "BJ"},
    "香港交易所": {"code": "HKEX", "short": "港交所", "market": "HK"},
    "纽约证券交易所": {"code": "NYSE", "short": "纽交所", "market": "US"},
    "纳斯达克": {"code": "NASDAQ", "short": "纳斯达克", "market": "US"},
    "伦敦证券交易所": {"code": "LSE", "short": "伦交所", "market": "UK"},
    "东京证券交易所": {"code": "TSE", "short": "东交所", "market": "JP"},
    "新加坡交易所": {"code": "SGX", "short": "新交所", "market": "SG"}
}

BOARD_CODES = {
    "主板": {"exchanges": ["上交所", "深交所"], "code_prefix": ["600", "601", "603", "605", "000", "001", "002"]},
    "创业板": {"exchange": "深交所", "code_prefix": ["300", "301"]},
    "科创板": {"exchange": "上交所", "code_prefix": ["688", "689"]},
    "北交所": {"exchange": "北交所", "code_prefix": ["43", "83", "87", "88"]},
    "新三板": {"exchanges": ["全国股转系统"], "code_prefix": ["43", "83", "87"]},
    "港股主板": {"exchange": "港交所", "code_pattern": "数字代码"},
    "美股": {"exchanges": ["纽交所", "纳斯达克"], "code_pattern": "字母代码"}
}
"""

# ========== 文件 36: currency_codes.py (改造前) ==========
"""
# 改造前 - 硬编码货币代码
CURRENCY_CODES = {
    "CNY": {"name": "人民币", "symbol": "¥", "country": "中国", "is_base": True},
    "USD": {"name": "美元", "symbol": "$", "country": "美国", "is_base": True},
    "EUR": {"name": "欧元", "symbol": "€", "country": "欧元区", "is_base": True},
    "JPY": {"name": "日元", "symbol": "¥", "country": "日本", "is_base": True},
    "GBP": {"name": "英镑", "symbol": "£", "country": "英国", "is_base": True},
    "HKD": {"name": "港币", "symbol": "HK$", "country": "中国香港", "is_base": False},
    "AUD": {"name": "澳元", "symbol": "A$", "country": "澳大利亚", "is_base": False},
    "CAD": {"name": "加元", "symbol": "C$", "country": "加拿大", "is_base": False},
    "SGD": {"name": "新加坡元", "symbol": "S$", "country": "新加坡", "is_base": False},
    "CHF": {"name": "瑞士法郎", "symbol": "Fr", "country": "瑞士", "is_base": False}
}

CURRENCY_PAIRS = {
    "即期汇率": ["USD/CNY", "EUR/CNY", "JPY/CNY", "GBP/CNY", "HKD/CNY"],
    "交叉汇率": ["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD"]
}
"""

# ========== 文件 37: holiday_calendar.py (改造前) ==========
"""
# 改造前 - 硬编码节假日
TRADING_HOLIDAYS_2024 = [
    {"date": "2024-01-01", "name": "元旦", "type": "法定假日"},
    {"date": "2024-02-09", "name": "除夕", "type": "法定假日"},
    {"date": "2024-02-10", "name": "春节", "type": "法定假日"},
    {"date": "2024-02-11", "name": "春节", "type": "法定假日"},
    {"date": "2024-02-12", "name": "春节", "type": "法定假日"},
    {"date": "2024-02-13", "name": "春节", "type": "法定假日"},
    {"date": "2024-02-14", "name": "春节", "type": "法定假日"},
    {"date": "2024-02-15", "name": "春节", "type": "法定假日"},
    {"date": "2024-02-16", "name": "春节", "type": "法定假日"},
    {"date": "2024-02-17", "name": "春节", "type": "法定假日"},
    {"date": "2024-04-04", "name": "清明节", "type": "法定假日"},
    {"date": "2024-04-05", "name": "清明节", "type": "法定假日"},
    {"date": "2024-04-06", "name": "清明节", "type": "法定假日"},
    {"date": "2024-05-01", "name": "劳动节", "type": "法定假日"},
    {"date": "2024-05-02", "name": "劳动节", "type": "法定假日"},
    {"date": "2024-05-03", "name": "劳动节", "type": "法定假日"},
    {"date": "2024-05-04", "name": "劳动节", "type": "法定假日"},
    {"date": "2024-05-05", "name": "劳动节", "type": "法定假日"},
    {"date": "2024-06-10", "name": "端午节", "type": "法定假日"},
    {"date": "2024-09-15", "name": "中秋节", "type": "法定假日"},
    {"date": "2024-09-16", "name": "中秋节", "type": "法定假日"},
    {"date": "2024-09-17", "name": "中秋节", "type": "法定假日"},
    {"date": "2024-10-01", "name": "国庆节", "type": "法定假日"},
    {"date": "2024-10-02", "name": "国庆节", "type": "法定假日"},
    {"date": "2024-10-03", "name": "国庆节", "type": "法定假日"},
    {"date": "2024-10-04", "name": "国庆节", "type": "法定假日"},
    {"date": "2024-10-05", "name": "国庆节", "type": "法定假日"},
    {"date": "2024-10-06", "name": "国庆节", "type": "法定假日"},
    {"date": "2024-10-07", "name": "国庆节", "type": "法定假日"},
]

HONG_KONG_HOLIDAYS_2024 = [
    {"date": "2024-01-01", "name": "元旦"},
    {"date": "2024-02-10", "name": "春节"},
    {"date": "2024-02-12", "name": "春节补假"},
    {"date": "2024-02-13", "name": "春节补假"},
    {"date": "2024-03-29", "name": "耶稣受难节"},
    {"date": "2024-04-01", "name": "复活节"},
    {"date": "2024-04-04", "name": "清明节"},
    {"date": "2024-05-01", "name": "劳动节"},
    {"date": "2024-05-15", "name": "佛诞"},
    {"date": "2024-06-10", "name": "端午节"},
    {"date": "2024-07-01", "name": "香港回归"},
    {"date": "2024-09-18", "name": "中秋节后补假"},
    {"date": "2024-10-01", "name": "国庆"},
    {"date": "2024-10-11", "name": "重阳节"},
    {"date": "2024-12-25", "name": "圣诞节"},
    {"date": "2024-12-26", "name": "圣诞节后补假"},
]
"""

# ========== 文件 38: transaction_types.py (改造前) ==========
"""
# 改造前 - 硬编码交易类型
TRANSACTION_TYPES = {
    # 申购赎回
    "认购": {"code": "SUBS", "direction": "买入", "fee_type": "认购费"},
    "申购": {"code": "PURC", "direction": "买入", "fee_type": "申购费"},
    "赎回": {"code": "REDM", "direction": "卖出", "fee_type": "赎回费"},
    "定投": {"code": "SIP", "direction": "买入", "fee_type": "申购费"},
    "转换": {"code": "CONV", "direction": "转换", "fee_type": "转换费"},
    
    # 分红
    "现金分红": {"code": "DIVC", "type": "分红", "taxable": True},
    "红利再投": {"code": "DIVR", "type": "分红", "taxable": False},
    
    # 账户类
    "开户": {"code": "ACOP", "type": "账户"},
    "销户": {"code": "ACCL", "type": "账户"},
    "修改资料": {"code": "ACMD", "type": "账户"},
    "风险测评": {"code": "RISK", "type": "账户"},
    
    # 其他
    "强增": {"code": "FORC_ADD", "type": "特殊"},
    "强减": {"code": "FORC_SUB", "type": "特殊"},
    "非交易过户": {"code": "TRAN", "type": "特殊"},
    "份额冻结": {"code": "FRZ", "type": "特殊"},
    "份额解冻": {"code": "UNFRZ", "type": "特殊"}
}

ORDER_STATUS = {
    "未确认": {"code": "UNCF", "description": "交易申请已受理，等待确认"},
    "确认成功": {"code": "SUCC", "description": "交易确认成功"},
    "确认失败": {"code": "FAIL", "description": "交易确认失败"},
    "部分确认": {"code": "PART", "description": "交易部分确认"},
    "已撤单": {"code": "CNCL", "description": "交易已撤销"},
    "巨额赎回": {"code": "DEFR", "description": "巨额赎回，顺延处理"}
}
"""

# ========== 文件 39: fee_structures.py (改造前) ==========
"""
# 改造前 - 硬编码费率结构
PURCHASE_FEE_RATES = {
    "股票型": [
        {"min": 0, "max": 1000000, "rate": 0.0150},
        {"min": 1000000, "max": 5000000, "rate": 0.0120},
        {"min": 5000000, "max": 10000000, "rate": 0.0080},
        {"min": 10000000, "max": None, "rate": 0.0100}  # 固定费用
    ],
    "债券型": [
        {"min": 0, "max": 1000000, "rate": 0.0080},
        {"min": 1000000, "max": 5000000, "rate": 0.0050},
        {"min": 5000000, "max": None, "rate": 0.0030}
    ],
    "混合型": [
        {"min": 0, "max": 1000000, "rate": 0.0150},
        {"min": 1000000, "max": 5000000, "rate": 0.0120},
        {"min": 5000000, "max": None, "rate": 0.0080}
    ],
    "货币型": [
        {"min": 0, "max": None, "rate": 0.0000}
    ]
}

REDEMPTION_FEE_RATES = {
    "股票型_标准": [
        {"holding_days": "0-7", "rate": 0.0150},
        {"holding_days": "7-30", "rate": 0.0075},
        {"holding_days": "30-365", "rate": 0.0050},
        {"holding_days": "365+", "rate": 0.0000}
    ],
    "债券型_标准": [
        {"holding_days": "0-7", "rate": 0.0150},
        {"holding_days": "7-30", "rate": 0.0010},
        {"holding_days": "30+", "rate": 0.0000}
    ]
}

MANAGEMENT_FEE_RATES = {
    "主动股票型": 0.0150,
    "指数股票型": 0.0050,
    "债券型": 0.0060,
    "混合型": 0.0120,
    "货币型": 0.0033,
    "FOF": 0.0100
}

CUSTODY_FEE_RATES = {
    "股票型": 0.0025,
    "债券型": 0.0020,
    "混合型": 0.0025,
    "货币型": 0.0010,
    "FOF": 0.0020
}
"""

# ========== 文件 40: document_types.py (改造前) ==========
"""
# 改造前 - 硬编码文档类型
DOCUMENT_TYPES = {
    # 基金募集期文档
    "基金合同": {"code": "FUND_CTR", "category": "募集", "required": True, "retention_years": 20},
    "招募说明书": {"code": "FUND_PROS", "category": "募集", "required": True, "retention_years": 20},
    "托管协议": {"code": "CUST_AGR", "category": "募集", "required": True, "retention_years": 20},
    "产品资料概要": {"code": "PROD_SUM", "category": "募集", "required": True, "retention_years": 20},
    "风险揭示书": {"code": "RISK_DISC", "category": "募集", "required": True, "retention_years": 20},
    
    # 定期报告
    "季度报告": {"code": "QTR_RPT", "category": "定期", "frequency": "季度", "retention_years": 20},
    "中期报告": {"code": "HALF_RPT", "category": "定期", "frequency": "半年", "retention_years": 20},
    "年度报告": {"code": "ANNUAL_RPT", "category": "定期", "frequency": "年度", "retention_years": 20},
    
    # 临时公告
    "基金经理变更": {"code": "MGR_CHG", "category": "临时", "disclosure_hours": 2},
    "分红公告": {"code": "DIV_ANN", "category": "临时", "disclosure_hours": 24},
    "巨额赎回": {"code": "MASS_RED", "category": "临时", "disclosure_hours": 24},
    "清盘公告": {"code": "LIQ_ANN", "category": "临时", "disclosure_hours": 24},
    
    # 合规文档
    "适当性匹配意见": {"code": "SUIT_OP", "category": "合规", "retention_years": 20},
    "风险测评问卷": {"code": "RISK_QUES", "category": "合规", "retention_years": 20},
    "录音录像": {"code": "REC", "category": "合规", "retention_years": 20},
    "投诉记录": {"code": "COMP_REC", "category": "合规", "retention_years": 20}
}
"""

# ========== 文件 41: account_types.py (改造前) ==========
"""
# 改造前 - 硬编码账户类型
ACCOUNT_TYPES = {
    "个人": {
        "code": "IND",
        "subtypes": {
            "普通账户": "IND_NOR",
            "专业投资者": "IND_PRO",
            "合格投资者": "IND_QF"
        },
        "id_types": ["身份证", "护照", "军官证", "港澳台居民证"]
    },
    "机构": {
        "code": "INS",
        "subtypes": {
            "企业": "INS_ENT",
            "金融机构": "INS_FIN",
            "事业单位": "INS_PUB",
            "社保基金": "INS_SS",
            "企业年金": "INS_EA"
        },
        "id_types": ["营业执照", "组织机构代码证", "统一社会信用代码"]
    },
    "产品": {
        "code": "PROD",
        "subtypes": {
            "私募基金": "PROD_PE",
            "资管计划": "PROD_AM",
            "信托计划": "PROD_TR",
            "理财产品": "PROD_WM"
        }
    }
}

ACCOUNT_STATUS = {
    "正常": {"code": "ACT", "description": "账户正常"},
    "冻结": {"code": "FRZ", "description": "账户冻结，不可交易"},
    "挂失": {"code": "LOST", "description": "账户挂失"},
    "销户": {"code": "CLOSED", "description": "账户已销户"},
    "待激活": {"code": "PEND", "description": "账户待激活"}
}
"""

# ========== 文件 42: sales_channels.py (改造前) ==========
"""
# 改造前 - 硬编码销售渠道
SALES_CHANNELS = {
    "直销": {
        "code": "DIRECT",
        "subchannels": {
            "柜台": "DIRECT_COUNTER",
            "网上直销": "DIRECT_WEB",
            "APP": "DIRECT_APP",
            "电话": "DIRECT_PHONE"
        },
        "fee_discount": 1.0
    },
    "银行代销": {
        "code": "BANK",
        "major_banks": [
            {"name": "工商银行", "code": "ICBC"},
            {"name": "建设银行", "code": "CCB"},
            {"name": "农业银行", "code": "ABC"},
            {"name": "中国银行", "code": "BOC"},
            {"name": "招商银行", "code": "CMB"}
        ],
        "fee_discount": 0.6
    },
    "券商代销": {
        "code": "SEC",
        "major_securities": [
            {"name": "中信证券", "code": "CITIC"},
            {"name": "华泰证券", "code": "HTSC"},
            {"name": "国泰君安", "code": "GTJA"},
            {"name": "招商证券", "code": "CMS"}
        ],
        "fee_discount": 0.4
    },
    "第三方销售": {
        "code": "3RD",
        "platforms": [
            {"name": "蚂蚁财富", "code": "ANT"},
            {"name": "天天基金", "code": "EASTMONEY"},
            {"name": "理财通", "code": "LC"},
            {"name": "京东金融", "code": "JD"}
        ],
        "fee_discount": 0.1
    }
}
"""

# ========== 文件 43: regulatory_organizations.py (改造前) ==========
"""
# 改造前 - 硬编码监管机构
REGULATORY_ORGS = {
    "中国证监会": {
        "code": "CSRC",
        "level": "国家级",
        "functions": ["法规制定", "市场监管", "机构审批", "处罚执法"],
        "website": "www.csrc.gov.cn"
    },
    "中国证券投资基金业协会": {
        "code": "AMAC",
        "level": "行业自律",
        "functions": ["登记备案", "自律管理", "会员服务", "纠纷调解"],
        "website": "www.amac.org.cn"
    },
    "上交所": {
        "code": "SSE",
        "type": "交易所",
        "functions": ["证券交易", "市场监管", "信息发布"]
    },
    "深交所": {
        "code": "SZSE",
        "type": "交易所",
        "functions": ["证券交易", "市场监管", "信息发布"]
    },
    "北交所": {
        "code": "BSE",
        "type": "交易所",
        "functions": ["证券交易", "服务中小企业"]
    },
    "中证登": {
        "code": "CSDC",
        "type": "登记结算",
        "functions": ["证券登记", "清算交收", "信息服务等"]
    }
}
"""

# ========== 文件 44: notification_types.py (改造前) ==========
"""
# 改造前 - 硬编码通知类型
NOTIFICATION_TYPES = {
    "交易类": {
        "交易确认": {"priority": "高", "channels": ["短信", "APP推送", "邮件"]},
        "分红通知": {"priority": "中", "channels": ["短信", "APP推送"]},
        "巨额赎回": {"priority": "高", "channels": ["短信", "电话", "APP推送"]},
        "赎回到账": {"priority": "中", "channels": ["短信", "APP推送"]}
    },
    "账户类": {
        "开户成功": {"priority": "中", "channels": ["短信", "邮件"]},
        "密码修改": {"priority": "高", "channels": ["短信"]},
        "资料变更": {"priority": "高", "channels": ["短信", "APP推送"]},
        "风险评估到期": {"priority": "中", "channels": ["短信", "APP推送", "邮件"]}
    },
    "营销类": {
        "产品推荐": {"priority": "低", "channels": ["APP推送", "邮件"]},
        "活动通知": {"priority": "低", "channels": ["APP推送", "短信"]},
        "市场资讯": {"priority": "低", "channels": ["APP推送"]}
    },
    "安全类": {
        "登录提醒": {"priority": "高", "channels": ["短信", "APP推送"]},
        "异常交易": {"priority": "高", "channels": ["短信", "电话", "APP推送"]},
        "风险警示": {"priority": "高", "channels": ["短信", "APP推送", "邮件"]}
    }
}
"""

# ========== 文件 45: data_frequencies.py (改造前) ==========
"""
# 改造前 - 硬编码数据频率
DATA_FREQUENCIES = {
    "实时": {"code": "RT", "interval_seconds": 0, "examples": ["行情数据", "交易确认"]},
    "分钟": {"code": "1M", "interval_seconds": 60, "examples": ["分钟K线", "分时图"]},
    "5分钟": {"code": "5M", "interval_seconds": 300, "examples": ["5分钟K线"]},
    "15分钟": {"code": "15M", "interval_seconds": 900, "examples": ["15分钟K线"]},
    "30分钟": {"code": "30M", "interval_seconds": 1800, "examples": ["30分钟K线"]},
    "小时": {"code": "1H", "interval_seconds": 3600, "examples": ["小时K线"]},
    "日": {"code": "D", "interval_seconds": 86400, "examples": ["日线", "日净值", "日收益"]},
    "周": {"code": "W", "interval_seconds": 604800, "examples": ["周线", "周收益"]},
    "月": {"code": "M", "interval_seconds": 2592000, "examples": ["月线", "月报", "月度收益"]},
    "季度": {"code": "Q", "examples": ["季报", "季度收益", "季度排名"]},
    "半年": {"code": "H", "examples": ["半年报", "半年收益"]},
    "年": {"code": "Y", "examples": ["年报", "年度收益", "年度排名"]}
}
"""

# ========== 文件 46: performance_metrics.py (改造前) ==========
"""
# 改造前 - 硬编码业绩指标
PERFORMANCE_METRICS = {
    "收益类": {
        "累计收益": {"code": "TOTAL_RETURN", "description": "投资期内的总收益率"},
        "年化收益": {"code": "ANNUAL_RETURN", "description": "换算为年化收益率"},
        "超额收益": {"code": "ALPHA", "description": "相对于基准的超额收益"},
        " Jensen's Alpha": {"code": "JENSEN_ALPHA", "description": "经风险调整的超额收益"}
    },
    "风险类": {
        "波动率": {"code": "VOLATILITY", "description": "收益率的标准差", "annualized": True},
        "最大回撤": {"code": "MAX_DRAWDOWN", "description": "从高点到低点的最大跌幅"},
        "下行波动率": {"code": "DOWNSIDE_VOL", "description": "下行风险的波动率"},
        "VaR": {"code": "VAR", "description": "风险价值"}
    },
    "风险调整收益": {
        "夏普比率": {"code": "SHARPE", "description": "(收益-无风险利率)/波动率"},
        "索提诺比率": {"code": "SORTINO", "description": "(收益-无风险利率)/下行波动率"},
        "特雷诺比率": {"code": "TREYNOR", "description": "(收益-无风险利率)/Beta"},
        "卡玛比率": {"code": "CALMAR", "description": "年化收益/最大回撤"},
        "信息比率": {"code": "INFO_RATIO", "description": "超额收益/跟踪误差"}
    },
    "其他": {
        "Beta": {"code": "BETA", "description": "相对于市场的敏感度"},
        "跟踪误差": {"code": "TRACK_ERROR", "description": "与基准的差异波动"},
        "胜率": {"code": "WIN_RATE", "description": "正收益交易日占比"}
    }
}
"""

# ========== 文件 47: benchmark_indices.py (改造前) ==========
"""
# 改造前 - 硬编码基准指数
BENCHMARK_INDICES = {
    "股票市场": {
        "沪深300": {"code": "000300.SH", "description": "A股大盘股代表指数"},
        "中证500": {"code": "000905.SH", "description": "A股中盘股代表指数"},
        "中证1000": {"code": "000852.SH", "description": "A股小盘股代表指数"},
        "创业板指": {"code": "399006.SZ", "description": "创业板核心指数"},
        "科创50": {"code": "000688.SH", "description": "科创板核心指数"},
        "上证50": {"code": "000016.SH", "description": "沪市超大盘股指数"},
        "深证100": {"code": "399330.SZ", "description": "深市大盘股指数"}
    },
    "债券市场": {
        "中债总财富指数": {"code": "CBA00101", "description": "全市场债券指数"},
        "中债国债指数": {"code": "CBA00601", "description": "国债指数"},
        "中债信用债指数": {"code": "CBA02701", "description": "信用债指数"}
    },
    "海外市场": {
        "标普500": {"code": "SPX", "market": "US", "description": "美股大盘股指数"},
        "纳斯达克100": {"code": "NDX", "market": "US", "description": "美股科技股指数"},
        "恒生指数": {"code": "HSI", "market": "HK", "description": "港股核心指数"},
        "日经225": {"code": "N225", "market": "JP", "description": "日股核心指数"},
        "欧洲斯托克50": {"code": "SX5E", "market": "EU", "description": "欧洲蓝筹股指数"}
    },
    "商品": {
        "黄金": {"code": "AU", "description": "黄金现货价格"},
        "原油": {"code": "WTI", "description": "WTI原油价格"},
        "CRB指数": {"code": "CRB", "description": "大宗商品综合指数"}
    }
}
"""

# ========== 文件 48: report_periods.py (改造前) ==========
"""
# 改造前 - 硬编码报告期
REPORT_PERIODS = {
    "年度报告": {
        "code": "ANNUAL",
        "months": [12],
        "deadline_days": 90,  # 次年4月底前
        "covers": "全年"
    },
    "半年度报告": {
        "code": "HALF_YEAR",
        "months": [6],
        "deadline_days": 60,  # 8月底前
        "covers": "上半年"
    },
    "季度报告": {
        "code": "QUARTERLY",
        "months": [3, 6, 9],
        "deadline_days": 15,  # 季后15工作日
        "covers": "季度"
    }
}

DISCLOSURE_DEADLINES = {
    "年度报告": {"date": "04-30", "working_day_adjust": False},
    "半年度报告": {"date": "08-31", "working_day_adjust": False},
    "一季度报告": {"date": "04-15", "working_day_adjust": True},
    "三季度报告": {"date": "10-15", "working_day_adjust": True}
}
"""

# ========== 文件 49: valuation_methods.py (改造前) ==========
"""
# 改造前 - 硬编码估值方法
VALUATION_METHODS = {
    "股票": {
        "上市流通股票": {"method": "市价法", "price_source": "收盘价"},
        "停牌股票": {"method": "指数收益法", "adjustment": "参考行业指数"},
        "限售股票": {"method": "流动性折扣法", "discount": "20-30%"},
        "新股": {"method": "成本价", "holding_days": "上市后首个交易日"}
    },
    "债券": {
        "交易所债券": {"method": "收盘价估值", "priority": "第三方估值"},
        "银行间债券": {"method": "中债/上清所估值", "source": "中债登/上清所"},
        "可转债": {"method": "收盘价估值", "special_treatment": "转股溢价过高时特殊处理"},
        "ABS": {"method": "现金流折现", "discount_rate": "同信用等级债券收益率+利差"}
    },
    "基金": {
        "上市ETF": {"method": "收盘价", "source": "交易所"},
        "非上市基金": {"method": "净值", "source": "管理人披露"},
        "QDII": {"method": "净值", "time_adjustment": "T-1"}
    },
    "衍生品": {
        "股指期货": {"method": "结算价", "source": "中金所"},
        "国债期货": {"method": "结算价", "source": "中金所"},
        "期权": {"method": "B-S模型", "volatility": "隐含波动率"}
    }
}
"""

# ========== 文件 50: system_configs.py (改造前) ==========
"""
# 改造前 - 硬编码系统配置
SYSTEM_CONFIGS = {
    "交易时间": {
        "open_time": "09:30",
        "close_time": "15:00",
        "am_close": "11:30",
        "pm_open": "13:00",
        "accept_order_start": "09:15",
        "accept_order_end": "15:00"
    },
    "净值披露": {
        "disclosure_time": "19:00",
        "backup_time": "21:00",
        "weekend_disclosure": False
    },
    "交易确认": {
        "t1_confirmation": True,
        "cutoff_time": "15:00",
        "large_amount_threshold": 10000000
    },
    "赎回": {
        "t1_settlement": True,
        "arrival_days": {
            "货币型": "T+1",
            "其他": "T+3到T+7"
        }
    },
    "费用": {
        "management_fee_accrual": "每日",
        "custody_fee_accrual": "每日",
        "subscription_fee_max": 0.015,
        "redemption_fee_max": 0.015
    }
}

API_LIMITS = {
    "max_requests_per_second": 100,
    "max_requests_per_minute": 3000,
    "max_requests_per_day": 100000,
    "batch_size": 500
}
"""

print("C类数据文件 (31-50) 定义完成 - 改造前版本")
print("这些数据需要改为Enum枚举类或常量定义")
