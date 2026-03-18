from __future__ import annotations

from typing import Any, Dict, List


def parse_customer_need_signals(customer: Dict[str, Any]) -> Dict[str, Any]:
    """将客户原始信息转成可用于需求洞察的基础信号。

    输入为简单字典，输出为标准化信号字典。
    本脚本为轻量示例，不替代真实生产规则。
    """
    assets = customer.get("资产持仓", {})
    behaviors = customer.get("行为变化", {})
    interactions = customer.get("互动记录", {})

    signals: Dict[str, Any] = {
        "总资产区间": assets.get("总资产区间"),
        "主要配置": assets.get("主要配置", []),
        "到期资金": assets.get("到期资金"),
        "近期赎回": behaviors.get("近30天赎回"),
        "近期申购": behaviors.get("近30天申购"),
        "近期咨询": behaviors.get("近期咨询", []),
        "历史关注主题": interactions.get("历史关注主题", []),
        "客户经理备注": interactions.get("客户经理备注", ""),
    }

    tags: List[str] = []
    if signals["到期资金"]:
        tags.append("存在资金承接机会")
    if signals["近期赎回"] in {"较多", "明显增加"}:
        tags.append("可能关注流动性或波动控制")
    if "美元产品" in signals["近期咨询"]:
        tags.append("可能存在跨境或外币配置需求")
    if "传承" in signals["历史关注主题"]:
        tags.append("可能存在传承规划需求")

    signals["标签"] = tags
    return signals


if __name__ == "__main__":
    sample = {
        "资产持仓": {"总资产区间": "3000万-5000万", "主要配置": ["存款", "固收理财"], "到期资金": "3个月内1000万到期"},
        "行为变化": {"近30天赎回": "较多", "近30天申购": "较少", "近期咨询": ["美元产品"]},
        "互动记录": {"历史关注主题": ["传承"], "客户经理备注": "对波动较敏感"},
    }
    print(parse_customer_need_signals(sample))
