from __future__ import annotations

from typing import Any, Dict, List


def _list_block(items: List[str]) -> str:
    if not items:
        return "- 暂无\n"
    return "".join(f"- {item}\n" for item in items)


def render_report(data: Dict[str, Any]) -> str:
    signals = data.get("signals", [])
    signal_lines = []
    for s in signals:
        signal_lines.append(
            f"- 【{s.get('dimension', '')}】{s.get('signal', '')}（严重度：{s.get('severity', '')}；证据：{s.get('evidence', '')}）"
        )

    industry = data.get("industry_support", {})

    return f"""# 客户流失预警分析报告

## 一、客户基本信息
- 客户编号：{data.get('customer_id', '')}

## 二、预警结论
- 预警等级：{data.get('warning_level', '')}
- 综合分值：{data.get('overall_score', 0)}
- 行业数据支持程度：{industry.get('support_level', '弱')}
- 行业说明：{industry.get('note', '未提供')}

## 三、关键预警信号
{chr(10).join(signal_lines) if signal_lines else '- 暂无明显预警信号'}

## 四、主要原因解释
{_list_block(data.get('main_reasons', []))}
## 五、待核验事项
{_list_block(data.get('to_be_verified', []))}
## 六、客户经营与挽留建议
{_list_block(data.get('retention_actions', []))}
## 七、后续观察指标与复核计划
{_list_block(data.get('next_observation_points', []))}
"""


if __name__ == "__main__":
    sample = {
        "customer_id": "C001",
        "warning_level": "中",
        "overall_score": 28,
        "signals": [
            {"dimension": "资产", "signal": "近 90 天资产下降", "severity": "中", "evidence": "AUM 下降 18%"}
        ],
        "industry_support": {"support_level": "中", "note": "行业存在共性回撤，但该客户弱于同客群"},
        "main_reasons": ["资产连续下降", "交易活跃走弱"],
        "to_be_verified": ["是否存在客户在他行新开账户", "近期是否发生大额购房或教育支出"],
        "retention_actions": ["客户经理 3 日内完成一次电话触达", "提供资产承接与权益关怀方案"],
        "next_observation_points": ["观察未来 30 天 AUM 变化", "观察工资代发是否恢复"],
    }
    print(render_report(sample))
