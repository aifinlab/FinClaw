#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
追保提醒生成脚本
用于生成客户追保通知和提醒
"""

import json
from datetime import datetime, timedelta

# 通知模板
NOTIFICATION_TEMPLATES = {
    "warning": """【XX 证券】维保比例预警通知

尊敬的 {client_name}：

您的信用账户当前维保比例为 {maintenance_ratio}%，已低于预警线 (140%)。

当前持仓情况：
- 总资产：{total_assets}万元
- 总负债：{total_liabilities}万元
- 维保比例：{maintenance_ratio}%

请您及时关注账户风险，可采取以下措施：
1. 追加担保物（现金或可充抵保证金证券）
2. 主动减仓降低负债
3. 偿还部分融资/融券负债

如维保比例持续低于警戒线 (130%)，我司将有权启动强制平仓程序。

详询您的客户经理：{manager_name} {manager_phone}

XX 证券股份有限公司
{date}
""",
    
    "margin_call": """【XX 证券】追保通知

尊敬的 {client_name}：

您的信用账户当前维保比例为 {maintenance_ratio}%，已低于警戒线 (130%)。

请您于 {deadline} 前追加担保物，使维保比例恢复至 150% 以上。

需追加金额：{required_amount}万元

追保方式：
1. 追加现金
2. 追加证券
3. 偿还负债
4. 主动减仓

如未按时追保，我司将启动强制平仓程序。

紧急联系人：{manager_name} {manager_phone}

XX 证券股份有限公司
{date}
""",
    
    "liquidation_warning": """【XX 证券】平仓预告通知

尊敬的 {client_name}：

您的信用账户当前维保比例为 {maintenance_ratio}%，已低于平仓线 (120%)。

经多次通知，您尚未追加担保物。我司将于 {liquidation_date} 启动强制平仓程序。

平仓顺序：
1. 高波动证券
2. 高集中度证券
3. 其他证券

平仓目标：维保比例恢复至 150% 以上。

如有疑问，请立即联系：{manager_name} {manager_phone}

XX 证券股份有限公司
{date}
"""
}

def calculate_required_amount(current_assets: float, current_liabilities: float, 
                               target_ratio: float = 150) -> float:
    """
    计算需追加金额
    
    Args:
        current_assets: 当前总资产
        current_liabilities: 当前总负债
        target_ratio: 目标维保比例
    
    Returns:
        需追加金额
    """
    # 目标资产 = 负债 × 目标维保比例
    target_assets = current_liabilities * (target_ratio / 100)
    required = target_assets - current_assets
    return round(max(0, required), 2)

def get_notification_type(maintenance_ratio: float) -> str:
    """
    根据维保比例确定通知类型
    
    Args:
        maintenance_ratio: 维保比例
    
    Returns:
        通知类型 (warning/margin_call/liquidation_warning)
    """
    if maintenance_ratio < 120:
        return "liquidation_warning"
    elif maintenance_ratio < 130:
        return "margin_call"
    elif maintenance_ratio < 140:
        return "warning"
    else:
        return None

def generate_notification(client_data: dict) -> dict:
    """
    生成追保通知
    
    Args:
        client_data: 客户数据
    
    Returns:
        通知内容
    """
    maintenance_ratio = client_data.get("maintenance_ratio", 0)
    notification_type = get_notification_type(maintenance_ratio)
    
    if not notification_type:
        return {
            "status": "no_action_required",
            "message": "维保比例正常，无需通知"
        }
    
    # 计算需追加金额
    required_amount = calculate_required_amount(
        client_data.get("total_assets", 0),
        client_data.get("total_liabilities", 0)
    )
    
    # 计算截止日期
    if notification_type == "warning":
        deadline = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")
    elif notification_type == "margin_call":
        deadline = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
    else:
        deadline = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    # 生成通知内容
    template = NOTIFICATION_TEMPLATES[notification_type]
    content = template.format(
        client_name=client_data.get("client_name", "客户"),
        maintenance_ratio=maintenance_ratio,
        total_assets=client_data.get("total_assets", 0) / 10000,
        total_liabilities=client_data.get("total_liabilities", 0) / 10000,
        required_amount=required_amount / 10000,
        deadline=deadline,
        liquidation_date=deadline,
        manager_name=client_data.get("manager_name", "客户经理"),
        manager_phone=client_data.get("manager_phone", "95XXX"),
        date=datetime.now().strftime("%Y-%m-%d")
    )
    
    return {
        "status": "notification_generated",
        "notification_type": notification_type,
        "maintenance_ratio": maintenance_ratio,
        "required_amount": required_amount,
        "deadline": deadline,
        "content": content,
        "channels": ["sms", "wechat", "phone"]
    }

def generate_reminder_list(clients: list) -> dict:
    """
    生成追保提醒列表
    
    Args:
        clients: 客户列表
    
    Returns:
        提醒列表
    """
    reminders = []
    
    for client in clients:
        notification = generate_notification(client)
        if notification["status"] == "notification_generated":
            reminders.append({
                "client_id": client.get("client_id"),
                "client_name": client.get("client_name"),
                "notification_type": notification["notification_type"],
                "maintenance_ratio": notification["maintenance_ratio"],
                "required_amount": notification["required_amount"],
                "deadline": notification["deadline"],
                "priority": get_priority(notification["notification_type"])
            })
    
    # 按优先级排序
    reminders.sort(key=lambda x: x["priority"], reverse=True)
    
    return {
        "generate_date": datetime.now().strftime("%Y-%m-%d"),
        "total_count": len(reminders),
        "reminders": reminders
    }

def get_priority(notification_type: str) -> int:
    """获取优先级"""
    priorities = {
        "liquidation_warning": 3,
        "margin_call": 2,
        "warning": 1
    }
    return priorities.get(notification_type, 0)

if __name__ == "__main__":
    # 示例数据
    sample_client = {
        "client_id": "C001",
        "client_name": "张三",
        "maintenance_ratio": 125,
        "total_assets": 1250000,
        "total_liabilities": 1000000,
        "manager_name": "李经理",
        "manager_phone": "13800138000"
    }
    
    notification = generate_notification(sample_client)
    print(json.dumps(notification, ensure_ascii=False, indent=2))
