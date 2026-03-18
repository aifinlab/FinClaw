import argparse
import json
import sys
from pathlib import Path


def load_json(path: str | None):
    if path:
        return json.loads(Path(path).read_text(encoding="utf-8-sig"))
    return json.load(sys.stdin)


def as_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def member_summary(member):
    return {
        "姓名": member.get("姓名") or member.get("名称") or "未命名成员",
        "关系": member.get("关系", "未说明"),
        "年龄": member.get("年龄", "未说明"),
        "职业": member.get("职业", "未说明"),
        "是否主要经济支柱": bool(member.get("是否主要经济支柱", False)),
        "收入信息": member.get("年收入") or member.get("收入") or "未说明",
        "已有保障": as_list(member.get("已有保障")),
        "待确认信息": [
            key
            for key in ["年龄", "职业", "年收入", "已有保障"]
            if key not in member
        ],
    }


def normalize(data):
    members = [member_summary(item) for item in as_list(data.get("家庭成员"))]
    responsibilities = data.get("家庭责任", {})
    result = {
        "案例名称": data.get("案例名称", "未命名中产客户保障分析"),
        "家庭阶段": data.get("家庭阶段", "未说明"),
        "年度可承受保费预算": data.get("年度可承受保费预算", "未说明"),
        "家庭成员摘要": members,
        "家庭责任": {
            "房贷": responsibilities.get("房贷", "未说明"),
            "车贷": responsibilities.get("车贷", "未说明"),
            "子女教育责任": responsibilities.get("子女教育责任", "未说明"),
            "老人赡养责任": responsibilities.get("老人赡养责任", "未说明"),
            "家庭生活成本": responsibilities.get("家庭生活成本", "未说明"),
            "其他责任": responsibilities.get("其他责任", "未说明")
        },
        "用户关注重点": as_list(data.get("用户关注重点")),
        "关键缺失项": []
    }

    if not members:
        result["关键缺失项"].append("缺少家庭成员信息")
    if responsibilities == {}:
        result["关键缺失项"].append("缺少家庭责任信息")
    if result["年度可承受保费预算"] == "未说明":
        result["关键缺失项"].append("缺少保费预算信息")

    return result


def main():
    parser = argparse.ArgumentParser(description="标准化中产客户保障分析输入")
    parser.add_argument("--input", help="输入 JSON 文件路径")
    parser.add_argument("--output", help="输出 JSON 文件路径")
    args = parser.parse_args()

    normalized = normalize(load_json(args.input))
    text = json.dumps(normalized, ensure_ascii=False, indent=2)

    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    else:
        print(text)


if __name__ == "__main__":
    main()
