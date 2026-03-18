from __future__ import annotations

from typing import Any, Dict, List


def _lines(items: List[str]) -> str:
    if not items:
        return "- 无"
    return "\n".join(f"- {item}" for item in items)


def render_report(normalized: Dict[str, Any], result: Dict[str, Any]) -> str:
    basic = normalized.get("申请人基础信息", {})
    app = normalized.get("申请信息", {})
    job = normalized.get("职业收入信息", {})

    md = f"""# 个贷预审意见报告

## 一、申请概况

- 申请人：{basic.get('姓名') or '未提供'}
- 年龄：{basic.get('年龄') or '未提供'}
- 产品类型：{app.get('产品类型') or '未提供'}
- 申请金额：{app.get('申请金额') or '未提供'}
- 申请期限：{app.get('申请期限') or '未提供'}
- 申请用途：{app.get('申请用途') or '未提供'}
- 担保方式：{app.get('担保方式') or '未提供'}
- 单位：{job.get('单位') or '未提供'}
- 岗位：{job.get('岗位') or '未提供'}
- 月收入：{job.get('月收入') or '未提供'}

## 二、资料完整性检查

- 判断结果：{result.get('检查结果', {}).get('资料完整性', '未判断')}

### 缺失信息

{_lines(result.get('缺失信息', []))}

## 三、风险信号

{_lines(result.get('风险信号', []))}

## 四、预审结论

- 结论等级：{result.get('预审结论', '未判断')}
- 说明：基于当前输入材料形成初步判断，不能替代正式审批结论。

## 五、后续建议

- 对缺失信息先补充，再进入正式评审。
- 对风险信号逐项核验真实性与影响程度。
- 如涉及征信异常、收入不一致、用途不清等情况，建议人工重点复核。
"""
    return md


if __name__ == "__main__":
    normalized = {
        "申请人基础信息": {"姓名": "张三", "年龄": 33},
        "申请信息": {"产品类型": "个人消费贷", "申请金额": 300000, "申请期限": "36个月", "申请用途": "家装"},
        "职业收入信息": {"单位": "某科技公司", "岗位": "产品经理", "月收入": 28000},
    }
    result = {
        "检查结果": {"资料完整性": "基础判断所需信息基本具备"},
        "缺失信息": [],
        "风险信号": ["近期征信查询偏多，建议结合借贷行为进一步核验"],
        "预审结论": "有条件通过",
    }
    print(render_report(normalized, result))
