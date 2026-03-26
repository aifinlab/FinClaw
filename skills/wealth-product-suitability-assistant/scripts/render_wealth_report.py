from __future__ import annotations
from typing import Any, Dict, List
import json

def render_report(customer_summary: Dict[str, Any], recommendations: List[Dict[str, Any]]) -> str:
    recommendations = sorted(recommendations, key=lambda x: x.get("适配得分", 0), reverse=True)
    primary = recommendations[0] if recommendations else {}
    alternatives = recommendations[1:3] if len(recommendations) > 1 else []

    lines = [
        "# 理财产品适配报告",
        "",
        "## 一、客户画像摘要",
    ]
    for k, v in customer_summary.items():
        if k == "待核验事项":
            continue
        lines.append(f"- {k}：{v}")
    lines.append("")
    lines.append("## 二、主推荐方案")
    if primary:
        lines.append(f"- 产品名称：{primary.get('产品名称')}")
        lines.append(f"- 适配得分：{primary.get('适配得分')}")
        lines.append(f"- 适配等级：{primary.get('适配等级')}")
        lines.append(f"- 推荐理由：{'；'.join(primary.get('推荐理由', [])) or '暂无'}")
        lines.append(f"- 风险提示：{'；'.join(primary.get('风险提示', [])) or '暂无'}")
    else:
        lines.append("- 暂无可推荐产品")
    lines.append("")
    lines.append("## 三、备选方案")
    if alternatives:
        for idx, item in enumerate(alternatives, start=1):
            lines.append(f"### 备选方案{idx}")
            lines.append(f"- 产品名称：{item.get('产品名称')}")
            lines.append(f"- 适配等级：{item.get('适配等级')}")
            lines.append(f"- 推荐理由：{'；'.join(item.get('推荐理由', [])) or '暂无'}")
            lines.append(f"- 风险提示：{'；'.join(item.get('风险提示', [])) or '暂无'}")
    else:
        lines.append("- 无")
    lines.append("")
    lines.append("## 四、待核验事项")
    pending = customer_summary.get("待核验事项", [])
    if pending:
        for item in pending:
            lines.append(f"- {item}")
    else:
        lines.append("- 无")
    lines.append("")
    lines.append("## 五、客户经理沟通建议")
    lines.append("- 先确认客户对波动、期限和流动性的真实接受度")
    lines.append("- 解释主方案与备选方案的差异，不承诺收益")
    lines.append("- 如存在待核验事项，应先补全信息再推进正式推荐")
    return "\\n".join(lines)

if __name__ == "__main__":
    customer_summary = {
        "客户名称": "张三",
        "风险等级": "稳健型",
        "投资目标": "稳健增值",
        "可投资期限(月)": 12,
        "流动性需求": "中",
        "待核验事项": []
    }
    recommendations = [
        {"产品名称": "稳盈12M", "适配得分": 88, "适配等级": "高适配", "推荐理由": ["风险匹配", "期限匹配"], "风险提示": ["净值有波动"]},
        {"产品名称": "现金管理A", "适配得分": 76, "适配等级": "中适配", "推荐理由": ["流动性较好"], "风险提示": ["收益弹性有限"]},
    ]
    print(render_report(customer_summary, recommendations))
