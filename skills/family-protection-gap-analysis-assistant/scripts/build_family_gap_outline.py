import argparse
import json
from pathlib import Path


def load_json(path: str):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def summarize_members(members):
    lines = []
    for member in members:
        role = member.get("关系", "未说明")
        name = member.get("姓名", "未命名成员")
        age = member.get("年龄", "未说明")
        income = member.get("收入信息", "未说明")
        protections = "、".join(member.get("已有保障", [])) or "暂未明确"
        pillar = "是" if member.get("是否主要经济支柱") else "否"
        lines.append(
            f"- {name}（{role}，年龄：{age}，主要经济支柱：{pillar}，收入：{income}，已有保障：{protections}）"
        )
    return "\n".join(lines) if lines else "- 暂无可确认家庭成员信息"


def build_markdown(data):
    members = data.get("家庭成员摘要", [])
    concerns = "、".join(data.get("用户关注重点", [])) or "未说明"
    missing = "、".join(data.get("关键缺失项", [])) or "暂无明显缺失项"
    responsibilities = data.get("家庭责任", {})
    return f"""# 家庭保障分析报告草稿

一、家庭概况摘要
- 家庭成员结构：
{summarize_members(members)}
- 家庭当前阶段：{data.get("家庭阶段", "未说明")}
- 主要收入来源与责任概况：房贷{responsibilities.get("房贷", "未说明")}；车贷{responsibilities.get("车贷", "未说明")}；子女教育责任{responsibilities.get("子女教育责任", "未说明")}；老人赡养责任{responsibilities.get("老人赡养责任", "未说明")}。
- 当前保障规划重点：{concerns}

二、现有保障盘点
- 家庭经济支柱：请基于主要经济支柱成员，补充寿险、重疾、医疗、意外保障盘点。
- 配偶保障情况：请结合收入贡献与照护责任补充。
- 子女保障情况：请结合少儿医保、医疗险、意外险情况补充。
- 老人保障情况：请结合赡养责任和现实可配置空间补充。
- 当前已覆盖风险：请填写已明确覆盖的风险责任。
- 当前明显不足：请填写可确认的保障空白、保额不足或结构失衡点。

三、保障缺口分析
1. 家庭经济支柱保障缺口：请结合收入中断、身故责任、负债与赡养责任分析。
2. 重疾保障缺口：请结合治疗费用、康复费用和收入补偿分析。
3. 医疗保障缺口：请结合医保、团险、百万医疗和住院责任分析。
4. 意外保障缺口：请结合职业、通勤、差旅和家庭日常风险分析。
5. 子女保障缺口：请结合基础医疗、意外与教育规划顺序分析。
6. 养老或长期规划缺口：请结合家庭阶段、预算和长期目标分析。

四、重点风险提示
- 风险提示1：
- 风险提示2：
- 风险提示3：

五、保障配置优先级建议
- 第一优先级：
- 第二优先级：
- 第三优先级：
- 优先级判断依据：请围绕“先家庭支柱、后其他成员；先基础保障、后长期规划”说明。

六、后续方案方向
- 建议进一步确认的信息：{missing}
- 后续可细化的保障方向：
- 下一步方案设计重点：

七、边界说明
- 以下草稿仅用于家庭保障缺口分析与沟通准备。
- 不构成最终产品推荐、投资建议、承保结论或合规结论。
- 涉及高风险金融业务、精确保额测算或长期缴费安排时，需人工复核。
"""


def main():
    parser = argparse.ArgumentParser(description="根据标准化输入生成家庭保障分析报告草稿")
    parser.add_argument("--input", required=True, help="标准化 JSON 输入文件路径")
    parser.add_argument("--output", help="Markdown 输出文件路径")
    args = parser.parse_args()

    markdown = build_markdown(load_json(args.input))
    if args.output:
        Path(args.output).write_text(markdown, encoding="utf-8")
    else:
        print(markdown)


if __name__ == "__main__":
    main()

