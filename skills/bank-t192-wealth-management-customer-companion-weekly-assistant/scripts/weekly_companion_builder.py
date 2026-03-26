from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import argparse
import json


@dataclass
class WeeklyCompanionInput:
    customer_profile: Dict[str, Any]
    risk_profile: Optional[Dict[str, Any]] = None
    holdings: List[Dict[str, Any]] = field(default_factory=list)
    weekly_events: List[Dict[str, Any]] = field(default_factory=list)
    market_view: Optional[str] = None
    communication_logs: List[Dict[str, Any]] = field(default_factory=list)
    todos: List[Dict[str, Any]] = field(default_factory=list)
    constraints: Optional[List[str]] = None
    report_date: Optional[str] = None


def validate_input(data: Dict[str, Any]) -> None:
    """验证输入参数"""
    if not isinstance(data, dict):
        raise ValueError("输入必须是字典类型")


def _format_section(title: str, lines: List[str]) -> str:
    if not lines:
        return ""
    body = "\n".join(f"- {line}" for line in lines)
    return f"## {title}\n{body}\n"


def _safe_get(obj: Dict[str, Any], key: str, default: str = "") -> str:
    value = obj.get(key)
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return str(value)
    return str(value)


def _build_summary(data: WeeklyCompanionInput) -> str:
    customer_name = _safe_get(data.customer_profile, "name", "客户")
    goals = _safe_get(data.customer_profile, "goals", "未提供")
    risk_level = _safe_get(data.risk_profile or {}, "level", "未提供")
    summary = (
        f"{customer_name}本周陪伴周报，目标侧重：{goals}。"
        f"风险偏好：{risk_level}。"
    )
    if data.market_view:
        summary += f"市场关注点：{data.market_view}。"
    return summary


def _build_key_points(data: WeeklyCompanionInput) -> List[str]:
    points: List[str] = []
    if data.weekly_events:
        points.append(f"本周记录事件 {len(data.weekly_events)} 条。")
    if data.communication_logs:
        points.append(f"本周沟通记录 {len(data.communication_logs)} 条。")
    if data.holdings:
        points.append("持仓/配置信息已更新，需结合适当性校验。")
    if data.todos:
        points.append(f"待办事项 {len(data.todos)} 项待跟进。")
    return points


def _build_risk_notes(data: WeeklyCompanionInput) -> List[str]:
    notes: List[str] = []
    if data.constraints:
        notes.extend([f"约束/限制：{item}" for item in data.constraints])
    if not data.risk_profile:
        notes.append("风险偏好未提供，涉及配置建议需补充确认。")
    if not data.holdings:
        notes.append("缺少持仓信息，建议补充以完善配置判断。")
    return notes


def _build_open_questions(data: WeeklyCompanionInput) -> List[str]:
    questions: List[str] = []
    if not _safe_get(data.customer_profile, "goals"):
        questions.append("客户投资目标尚未确认。")
    if not data.communication_logs:
        questions.append("本周客户沟通记录未提供。")
    return questions


def _build_next_actions(data: WeeklyCompanionInput) -> List[str]:
    actions: List[str] = []
    for todo in data.todos:
        owner = _safe_get(todo, "owner", "待定")
        due = _safe_get(todo, "due", "待定")
        title = _safe_get(todo, "title", "待办事项")
        actions.append(f"{title}（责任人：{owner}，时间：{due}）")
    if not actions:
        actions.append("暂无明确待办事项，建议补充下一步动作。")
    return actions


def build_report(data: WeeklyCompanionInput) -> Dict[str, Any]:
    summary = _build_summary(data)
    key_points = _build_key_points(data)
    risk_notes = _build_risk_notes(data)
    next_actions = _build_next_actions(data)
    open_questions = _build_open_questions(data)

    report_date = data.report_date or datetime.now().strftime("%Y-%m-%d")

    sections = [
        f"# 客户陪伴周报（{report_date}）\n",
        f"## 周度摘要\n{summary}\n",
        _format_section("重点事项", key_points),
        _format_section("风险提示", risk_notes),
        _format_section("后续动作", next_actions),
        _format_section("待确认事项", open_questions),
    ]

    markdown_report = "\n".join(section for section in sections if section)

    return {
        "summary": summary,
        "key_points": key_points,
        "risk_notes": risk_notes,
        "next_actions": next_actions,
        "open_questions": open_questions,
        "markdown_report": markdown_report,
    }


def parse_input(payload: Dict[str, Any]) -> WeeklyCompanionInput:
    if "customer_profile" not in payload:
        raise ValueError("缺少必要字段 customer_profile")
    return WeeklyCompanionInput(
        customer_profile=payload["customer_profile"],
        risk_profile=payload.get("risk_profile"),
        holdings=payload.get("holdings", []),
        weekly_events=payload.get("weekly_events", []),
        market_view=payload.get("market_view"),
        communication_logs=payload.get("communication_logs", []),
        todos=payload.get("todos", []),
        constraints=payload.get("constraints"),
        report_date=payload.get("report_date"),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="生成客户陪伴周报")
    parser.add_argument("--input", required=True, help="输入 JSON 文件路径")
    parser.add_argument("--output", required=True, help="输出 JSON 文件路径")
    parser.add_argument("--markdown", required=False, help="输出 Markdown 文件路径")
    args = parser.parse_args()

    input_path = Path(args.input)
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    data = parse_input(payload)
    result = build_report(data)

    Path(args.output).write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    if args.markdown:
        Path(args.markdown).write_text(result["markdown_report"], encoding="utf-8")


if __name__ == "__main__":
    main()
