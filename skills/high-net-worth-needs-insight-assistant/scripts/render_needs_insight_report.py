from __future__ import annotations

from typing import Any, Dict, List


def render_report(customer_name: str, calibrated: Dict[str, Any]) -> str:
    tags: List[str] = calibrated.get("标签", [])
    lines = []
    lines.append(f"# {customer_name} 高净值需求洞察报告")
    lines.append("")
    lines.append("## 一、核心判断")
    if tags:
        for idx, tag in enumerate(tags, start=1):
            lines.append(f"{idx}. {tag}")
    else:
        lines.append("当前可直接识别的需求信号较少，建议优先补充客户资料并通过沟通验证。")
    lines.append("")
    lines.append("## 二、结论强度")
    lines.append(f"- 结论强度：{calibrated.get('结论强度', '未知')}")
    lines.append(f"- 基础置信度：{calibrated.get('基础置信度', '未知')}")
    lines.append(f"- 说明：{calibrated.get('说明', '')}")
    lines.append("")
    lines.append("## 三、下一步建议")
    lines.append("- 建议由客户经理围绕流动性安排、波动接受度、跨境配置、传承与保障主题做验证式沟通。")
    lines.append("- 若行业数据不足，应优先输出会前提问提纲，而不是直接推进产品推荐。")
    return "\n".join(lines)


if __name__ == "__main__":
    demo = {
        "标签": ["存在资金承接机会", "可能存在传承规划需求"],
        "结论强度": "中等或较强",
        "基础置信度": "较高",
        "说明": "已结合行业数据做初步校准，但仍需通过客户沟通进一步验证。",
    }
    print(render_report("示例客户", demo))
