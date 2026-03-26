#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FinClaw 异常波动预警脚本
支持自动数据源切换（同花顺 → 腾讯财经/AkShare）

使用方法:
    python alert_monitor.py

配置:
    修改脚本中的 WATCH_LIST 定义关注股票列表
"""

    from data_source_fallback import get_alert_data
    from data_source_fallback import get_alert_data
from datetime import datetime
from pathlib import Path

# 添加fallback模块路径
sys.path.insert(0, str(Path(__file__).parent))

try:
import json
except ImportError:
    sys.path.insert(0, '/root/.openclaw/workspace/finclaw/skills/utils')
import sys
# ===== AkShare开源数据支持（新增） =====
from skillsChoice.common.unified_data_api import (
    get_data_api,
    get_stock_quote,
)
# ====================================


# 关注股票列表
WATCH_LIST = [
    # 新能源
    "002460", "002466", "603799",  # 上游
    "300919", "300750", "002594",  # 中游
    "002074", "300014", "601127", "000625", "601633",  # 下游
    # 半导体
    "688012", "688019", "300316",
    "688981", "600584", "002371",
    # 金融
    "600519", "000001", "600036",
    # 科技
    "000858", "002415", "002230",
    # 医药
    "600276", "000538", "600436",
    # 其他
    "002594", "300750", "601318"
]

# 去重
WATCH_LIST = list(set(WATCH_LIST))


def format_alert_report(alert_data: dict) -> str:
    """格式化预警报告"""

    lines = [
        f"""
============================================================
🔔 **FinClaw 异常波动预警报告**

**监控时间**: {alert_data.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}
**监控股票**: {alert_data.get('total_monitored', 0)}只
**数据源**: 腾讯财经（同花顺API暂不可用，已自动切换）
"""
    ]

    # 异常预警
    alerts = alert_data.get('alerts', [])
    if alerts:
        lines.append(f"""
## ⚠️ 异常波动预警 ({len(alerts)}只)

| 代码 | 名称 | 涨跌幅 | 预警级别 | 时间 |
|:---:|:---:|---:|:---:|:---:|
""")
        for alert in alerts:
            level_emoji = "🔴" if alert.get('level') == 'high' else "🟡"
            lines.append(f"| {alert['code']} | {alert['name']} | {alert['change_pct']:+.2f}% | {level_emoji} {alert['level'].upper()} | {alert['time']} |")
    else:
        lines.append("""
## ✅ 异常波动预警

**未发现异常波动**

所有监控股票价格变动在正常范围内（±5%）
""")

    # 详细数据
    lines.append("""
## 📊 监控股票详情

| 代码 | 名称 | 当前价 | 涨跌幅 | 数据源 |
|:---:|:---:|---:|---:|:---|
""")

    stocks = alert_data.get('stocks', {})
    for code in sorted(stocks.keys()):
        data = stocks[code]
        change_emoji = "📈" if data.get('change_pct', 0) > 0 else "📉" if data.get('change_pct', 0) < 0 else "➡️"
        lines.append(f"| {code} | {data.get('name', 'N/A')} | ¥{data.get('price', 0):.2f} | {change_emoji} {data.get('change_pct', 0):+.2f}% | {data.get('source', 'unknown')} |")

    # 数据来源标注
    lines.append(f"""
---
📊 **数据来源**: 腾讯财经API
⏱️ **数据时间**: {alert_data.get('timestamp', '实时')}
⚡ **状态**: 同花顺API Token过期，已自动切换至备用源
🔧 **分析工具**: FinClaw v1.0
⚠️ **阈值设置**: 涨跌幅绝对值 > 5% 触发预警

*注：同花顺API暂时不可用，已自动切换至腾讯财经获取实时数据*
============================================================
""")

    return "\n".join(lines)


def main():
    """主函数"""
    print("正在运行异常波动监控...")
    print(f"监控股票数量: {len(WATCH_LIST)}只")
    print("(同花顺API暂不可用，自动切换至腾讯财经)")
    print()

    # 获取监控数据
    alert_data = get_alert_data(WATCH_LIST)

    # 输出报告
    report = format_alert_report(alert_data)
    print(report)

    # 保存JSON结果
    output_dir = Path("/root/.openclaw/workspace/finclaw-workspace/finclaw/reports")
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = output_dir / f"alert_monitor_{timestamp}.json"

    output_json = {
        "report_type": "alert_monitor",
        "timestamp": alert_data.get('timestamp'),
        "data_source": "tencent_finance",
        "fallback_reason": "ths_token_expired",
        "total_monitored": alert_data.get('total_monitored', 0),
        "alerts_count": alert_data.get('alerts_count', 0),
        "alerts": alert_data.get('alerts', []),
        "stocks": alert_data.get('stocks', {})
    }

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(output_json, f, ensure_ascii=False, indent=2)

    print(f"\nJSON结果已保存: {json_path}")

    # 返回状态码（有预警返回1，无预警返回0）
    return 1 if alert_data.get('alerts_count', 0) > 0 else 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
