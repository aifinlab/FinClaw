"""资产配置建议报告渲染脚本（示例）"""
from __future__ import annotations
import json
from typing import Dict, Any, List

def render_markdown(report: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# 资产配置建议报告")
    lines.append("")
    lines.append("## 一、任务摘要")
    lines.append(f"- 客户类型：{report.get('客户类型', '未提供')}")
    lines.append(f"- 结论级别：{report.get('结论级别', '未提供')}")
    lines.append("")
    lines.append("## 二、客户画像与约束")
    for item in report.get("客户画像摘要", []):
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## 三、当前持仓诊断")
    for item in report.get("当前持仓诊断", []):
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## 四、主配置方案")
    plan = report.get("主配置方案", {})
    for asset_name, asset_range in plan.items():
        lines.append(f"- {asset_name}：{asset_range}")
    lines.append("")
    lines.append("## 五、再平衡建议")
    for item in report.get("再平衡建议", []):
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## 六、风险提示")
    for item in report.get("风险提示", []):
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## 七、信息缺口")
    for item in report.get("信息缺口", []):
        lines.append(f"- {item}")
    return "\n".join(lines)

if __name__ == "__main__":
    sample = {
        "客户类型": "财富客户",
        "结论级别": "框架建议",
        "客户画像摘要": ["风险等级为平衡型", "目标为稳健增值", "未来一年存在教育支出安排"],
        "当前持仓诊断": ["现金类占比偏高", "权益类暴露不足"],
        "主配置方案": {"现金": "10%-15%", "固收": "35%-45%", "权益": "25%-35%", "多资产": "10%-15%"},
        "再平衡建议": ["优先分步降低低收益现金沉淀", "增加中长期固收与多资产配置"],
        "风险提示": ["市场波动可能导致净值回撤", "建议结合客户风险评级确认最终方案"],
        "信息缺口": ["缺少完整产品池准入信息", "缺少同业配置基准数据"],
    }
    print(render_markdown(sample))
