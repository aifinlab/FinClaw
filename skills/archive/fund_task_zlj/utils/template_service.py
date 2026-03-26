#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
B类数据 模板化改造 - JSON/YAML配置 + Jinja2模板
"""

from dataclasses import dataclass, asdict
from enum import Enum
from jinja2 import Template, Environment, FileSystemLoader, BaseLoader
from pathlib import Path
from typing import Dict, Any, Optional
import json
import yaml
import sys

# ========== 配置加载器 ==========

class ConfigLoader:
    """配置文件加载器"""

    @staticmethod
    def load_json(path: str) -> Dict:
        """加载JSON配置"""
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    @staticmethod
    def load_yaml(path: str) -> Dict:
        """加载YAML配置"""
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    @staticmethod
    def save_json(data: Dict, path: str):
        """保存JSON配置"""
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @staticmethod
    def save_yaml(data: Dict, path: str):
        """保存YAML配置"""
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)


# ========== 模板引擎 ==========

class TemplateEngine:
    """Jinja2模板引擎封装"""

    def __init__(self, template_dir: Optional[str] = None):
        if template_dir:
            self.env = Environment(loader=FileSystemLoader(template_dir))
        else:
            self.env = Environment(loader=BaseLoader())

        # 添加自定义过滤器
        self.env.filters['format_currency'] = self._format_currency
        self.env.filters['format_percent'] = self._format_percent

    @staticmethod
    def _format_currency(value: float, symbol: str = "¥") -> str:
        """格式化货币"""
        return f"{symbol}{value:,.2f}"

    @staticmethod
    def _format_percent(value: float, decimals: int = 2) -> str:
        """格式化百分比"""
        return f"{value:.{decimals}f}%"

    def render_string(self, template_str: str, context: Dict) -> str:
        """渲染字符串模板"""
        template = self.env.from_string(template_str)
        return template.render(**context)

    def render_file(self, template_name: str, context: Dict) -> str:
        """渲染文件模板"""
        template = self.env.get_template(template_name)
        return template.render(**context)


# ========== 合同模板类 ==========

class ContractTemplate:
    """合同模板 - 改造前: 硬编码字符串"""

    TEMPLATE = """
基金购买协议

甲方（投资者）：{{ party_a }}
乙方（基金管理人）：{{ party_b }}

鉴于甲方愿意购买乙方管理的基金产品，双方本着平等自愿的原则，达成如下协议：

第一条 基金产品信息
基金名称：{{ fund_name }}
基金代码：{{ fund_code }}
基金类型：{{ fund_type }}
风险等级：{{ risk_level }}

第二条 购买金额
甲方同意以人民币 {{ amount | format_currency }} 元购买上述基金产品。

第三条 费用说明
申购费率：{{ purchase_fee }}%
管理费率：{{ management_fee }}%
托管费率：{{ custody_fee }}%

第四条 风险提示
基金投资有风险，过往业绩不代表未来表现。甲方应充分了解基金风险后再做投资决定。

签署日期：{{ sign_date }}
"""

    def __init__(self):
        self.engine = TemplateEngine()

    def render(self, context: Dict) -> str:
        """渲染合同"""
        return self.engine.render_string(self.TEMPLATE, context)


class RiskDisclosureTemplate:
    """风险揭示书模板"""

    TEMPLATE = """
风险揭示书

尊敬的投资者：

感谢您选择购买{{ fund_name }}基金。在您做出投资决策前，请仔细阅读以下内容：

{% for risk in risks %}
{{ loop.index }}. {{ risk.type }}：{{ risk.description }}
{% endfor %}

本人已充分理解上述风险，自愿承担投资风险。

投资者签名：__________ 日期：__________
"""

    def __init__(self):
        self.engine = TemplateEngine()

    def render(self, fund_name: str, risks: list) -> str:
        """渲染风险揭示书"""
        return self.engine.render_string(self.TEMPLATE, {
            "fund_name": fund_name,
            "risks": risks
        })


# ========== 报告模板类 ==========

class MonthlyReportTemplate:
    """月度报告模板"""

    TEMPLATE = """
{{ fund_name }}月度运作报告
报告期间：{{ start_date }} 至 {{ end_date }}

一、基金概况
基金名称：{{ fund_name }}
基金代码：{{ fund_code }}
基金类型：{{ fund_type }}
成立日期：{{ establish_date }}
报告期末规模：{{ aum }} 亿元

二、业绩表现
报告期内净值增长率：{{ period_return }}%
业绩比较基准收益率：{{ benchmark_return }}%
超额收益：{{ alpha }}%

三、市场回顾
{{ market_review }}

四、投资策略回顾
{{ strategy_review }}

五、持仓分析
前十大重仓股：
{% for stock in top_holdings %}
- {{ stock.code }} {{ stock.name }}: {{ stock.weight }}%
{% endfor %}

六、后市展望
{{ outlook }}

风险提示：基金过往业绩不代表未来表现，投资需谨慎。
"""

    def __init__(self):
        self.engine = TemplateEngine()

    def render(self, context: Dict) -> str:
        """渲染月度报告"""
        return self.engine.render_string(self.TEMPLATE, context)


class FundManagerChangeTemplate:
    """基金经理变更公告模板"""

    TEMPLATE = """
关于{{ fund_name }}基金经理变更的公告

公告日期：{{ announce_date }}
公告编号：{{ announce_no }}

一、基金经理变更情况
原基金经理：{{ former_manager }}
新任基金经理：{{ new_manager }}
变更原因：{{ change_reason }}
生效日期：{{ effective_date }}

二、新任基金经理简介
姓名：{{ manager.name }}
学历：{{ manager.education }}
从业年限：{{ manager.experience_years }}年
过往履历：{{ manager.career_history }}
管理产品：{{ manager.managed_products | join(', ') }}

三、其他事项
本次变更已按规定向中国证监会及相关机构备案。

特此公告。

{{ company_name }}
{{ announce_date }}
"""

    def __init__(self):
        self.engine = TemplateEngine()

    def render(self, context: Dict) -> str:
        """渲染基金经理变更公告"""
        return self.engine.render_string(self.TEMPLATE, context)


# ========== 通知模板类 ==========

class NotificationTemplate:
    """通知模板管理器"""

    TEMPLATES = {
        "trade_confirm": """
尊敬的投资者：

您于 {{ trade_date }} 提交的{{ trade_type }}申请已确认。

基金名称：{{ fund_name }}
基金代码：{{ fund_code }}
确认份额：{{ confirmed_shares }} 份
确认金额：{{ confirmed_amount | format_currency }} 元
确认净值：{{ nav }} 元
手续费：{{ fee | format_currency }} 元

如有疑问，请联系客服热线：400-xxx-xxxx
""",

        "dividend_notice": """
尊敬的投资者：

您持有的{{ fund_name }}将于{{ payment_date }}进行分红。

分红方案：每10份派{{ dividend }}元
您的持有份额：{{ shares }}份
预计分红金额：{{ expected_dividend | format_currency }}元

分红方式：{{ dividend_method }}

如有疑问，请联系客服热线：400-xxx-xxxx
""",

        "massive_redemption": """
尊敬的投资者：

您于 {{ trade_date }} 提交的赎回申请因巨额赎回被部分确认。

申请份额：{{ applied_shares }} 份
确认份额：{{ confirmed_shares }} 份
未确认份额：{{ unconfirmed_shares }} 份（将顺延至下一交易日处理）

如有疑问，请联系客服热线：400-xxx-xxxx
"""
    }

    def __init__(self):
        self.engine = TemplateEngine()

    def render(self, template_name: str, context: Dict) -> str:
        """渲染通知"""
        if template_name not in self.TEMPLATES:
            raise ValueError(f"未知模板: {template_name}")
        return self.engine.render_string(self.TEMPLATES[template_name], context)


# ========== 问答模板类 ==========

class QATemplate:
    """问答模板"""

    TEMPLATE = """
【问题】{{ question }}

【回答】
{{ answer }}

{% if related_questions %}
【相关问题】
{% for q in related_questions %}
- {{ q }}
{% endfor %}
{% endif %}
"""

    def __init__(self):
        self.engine = TemplateEngine()

    def render(self, question: str, answer: str, related_questions: list = None) -> str:
        """渲染问答"""
        return self.engine.render_string(self.TEMPLATE, {
            "question": question,
            "answer": answer,
            "related_questions": related_questions or []
        })


# ========== 营销模板类 ==========

class MarketingTemplate:
    """营销文案模板"""

    TEMPLATES = {
        "new_fund": """
🎉 {{ fund_name }} 火热发售中！

📊 产品亮点：
{% for highlight in highlights %}✨ {{ highlight }}
{% endfor %}

👨‍💼 基金经理：{{ manager.name }}
   {{ manager.introduction }}

📅 认购时间：{{ subscription_start }} 至 {{ subscription_end }}
💰 认购起点：{{ min_amount }}元

⚠️ 风险提示：基金有风险，投资需谨慎
""",

        "top_performer": """
🏆 {{ fund_name }} 业绩亮眼！

📈 业绩表现：
近一年：{{ return_1y }}%
近三年：{{ return_3y }}%
成立以来：{{ return_since_inception }}%

⭐ 获得{{ award_name }}奖项

📊 投资策略：{{ strategy }}

🔥 限时申购费率{{ discount }}折

⚠️ 风险提示：过往业绩不代表未来表现
""",

        "sip_promotion": """
💡 定投{{ fund_name }}，分享长期收益

📅 每月只需{{ min_amount }}元
🎯 坚持定投，复利效应
📊 历史回测数据显示：定投3年以上正收益概率{{ win_rate }}%

🎁 新客专享：首次定投免申购费

⚠️ 风险提示：定投不能规避基金投资风险
"""
    }

    def __init__(self):
        self.engine = TemplateEngine()

    def render(self, template_name: str, context: Dict) -> str:
        """渲染营销文案"""
        if template_name not in self.TEMPLATES:
            raise ValueError(f"未知模板: {template_name}")
        return self.engine.render_string(self.TEMPLATES[template_name], context)


# ========== 合规模板类 ==========

class ComplianceTemplate:
    """合规模板"""

    SUITABILITY_TEMPLATE = """
适当性匹配意见

客户信息：
- 客户名称：{{ client.name }}
- 风险承受能力：{{ client.risk_level }}
- 投资期限：{{ client.investment_horizon }}

产品信息：
- 产品名称：{{ product.name }}
- 产品类型：{{ product.type }}
- 风险等级：{{ product.risk_level }}

匹配结果：{{ match_result }}
匹配说明：{{ match_explanation }}

{% if warnings %}
⚠️ 风险提示：
{% for warning in warnings %}
- {{ warning }}
{% endfor %}
{% endif %}
"""

    def __init__(self):
        self.engine = TemplateEngine()

    def render_suitability(self, client: Dict, product: Dict,
                          match_result: str, match_explanation: str,
                          warnings: list = None) -> str:
        """渲染适当性匹配意见"""
        return self.engine.render_string(self.SUITABILITY_TEMPLATE, {
            "client": client,
            "product": product,
            "match_result": match_result,
            "match_explanation": match_explanation,
            "warnings": warnings or []
        })


# ========== 统一模板服务 ==========

class TemplateService:
    """统一模板服务"""

    def __init__(self):
        self.contract = ContractTemplate()
        self.risk_disclosure = RiskDisclosureTemplate()
        self.monthly_report = MonthlyReportTemplate()
        self.manager_change = FundManagerChangeTemplate()
        self.notification = NotificationTemplate()
        self.qa = QATemplate()
        self.marketing = MarketingTemplate()
        self.compliance = ComplianceTemplate()

    def render_contract(self, context: Dict) -> str:
        """渲染合同"""
        return self.contract.render(context)

    def render_risk_disclosure(self, fund_name: str, risks: list) -> str:
        """渲染风险揭示书"""
        return self.risk_disclosure.render(fund_name, risks)

    def render_monthly_report(self, context: Dict) -> str:
        """渲染月度报告"""
        return self.monthly_report.render(context)

    def render_manager_change(self, context: Dict) -> str:
        """渲染基金经理变更公告"""
        return self.manager_change.render(context)

    def render_notification(self, template_name: str, context: Dict) -> str:
        """渲染通知"""
        return self.notification.render(template_name, context)

    def render_qa(self, question: str, answer: str, related: list = None) -> str:
        """渲染问答"""
        return self.qa.render(question, answer, related)

    def render_marketing(self, template_name: str, context: Dict) -> str:
        """渲染营销文案"""
        return self.marketing.render(template_name, context)

    def render_suitability(self, client: Dict, product: Dict,
                          result: str, explanation: str, warnings: list = None) -> str:
        """渲染适当性匹配意见"""
        return self.compliance.render_suitability(client, product, result, explanation, warnings)


# 全局模板服务实例
template_service = TemplateService()



def main():


        # 测试模板渲染
        print("=== B类数据模板测试 ===\n")

        # 测试合同模板
        contract_context = {
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
        }
        print("【合同模板示例】")
        print(template_service.render_contract(contract_context))
        print("\n" + "="*50 + "\n")

        # 测试风险揭示书
        risks = [
            {"type": "市场风险", "description": "基金投资受证券市场波动影响"},
            {"type": "流动性风险", "description": "可能面临赎回困难"},
            {"type": "管理风险", "description": "基金管理人的能力影响业绩"}
        ]
        print("【风险揭示书模板示例】")
        print(template_service.render_risk_disclosure("XX价值精选混合", risks))
        print("\n" + "="*50 + "\n")

        # 测试营销模板
        marketing_context = {
            "fund_name": "XX科技创新混合",
            "highlights": [
                "聚焦科技创新龙头企业",
                "双基金经理联合管理",
                "历史业绩同类排名前10%"
            ],
            "manager": {
                "name": "李华",
                "introduction": "15年证券从业经验，擅长成长股投资"
            },
            "subscription_start": "2024-06-01",
            "subscription_end": "2024-06-14",
            "min_amount": 10
        }
        print("【营销模板示例】")
        print(template_service.render_marketing("new_fund", marketing_context))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n操作被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)