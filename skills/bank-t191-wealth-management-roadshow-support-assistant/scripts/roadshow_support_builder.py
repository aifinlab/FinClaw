"""路演支持材料生成脚本

将结构化输入转为标准化路演支持材料（Markdown）。

使用方式:
  python roadshow_support_builder.py --input input.json --output output.md

输入字段参考 SKILL.md 中的说明。
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


PLACEHOLDER = "【待补充】"


@dataclass
class ClientProfile:
    level: str = PLACEHOLDER
    risk_level: str = PLACEHOLDER
    horizon: str = PLACEHOLDER
    liquidity: str = PLACEHOLDER


@dataclass
class ProductItem:
    name: str
    category: str = PLACEHOLDER
    highlights: List[str] = field(default_factory=list)
    risk_level: str = PLACEHOLDER
    suitability: str = PLACEHOLDER


@dataclass
class MarketView:
    summary: str = PLACEHOLDER
    source: str = PLACEHOLDER
    valid_until: str = PLACEHOLDER


@dataclass
class ComplianceInfo:
    forbidden: List[str] = field(default_factory=list)
    required: List[str] = field(default_factory=list)
    channel_limits: List[str] = field(default_factory=list)


@dataclass
class RoadshowInput:
    client_profile: ClientProfile = field(default_factory=ClientProfile)
    client_goal: str = PLACEHOLDER
    products: List[ProductItem] = field(default_factory=list)
    market_view: MarketView = field(default_factory=MarketView)
    compliance: ComplianceInfo = field(default_factory=ComplianceInfo)
    follow_up: List[str] = field(default_factory=list)
    scene: str = PLACEHOLDER


def _ensure_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    return [str(value)]


def parse_input(payload: Dict[str, Any]) -> RoadshowInput:
    client = payload.get("client", {})
    profile_data = client.get("profile", {}) if isinstance(client, dict) else {}
    profile = ClientProfile(
        level=profile_data.get("level", PLACEHOLDER) or PLACEHOLDER,
        risk_level=profile_data.get("risk_level", PLACEHOLDER) or PLACEHOLDER,
        horizon=profile_data.get("horizon", PLACEHOLDER) or PLACEHOLDER,
        liquidity=profile_data.get("liquidity", PLACEHOLDER) or PLACEHOLDER,
    )

    market = payload.get("market_view", {})
    market_view = MarketView(
        summary=market.get("summary", PLACEHOLDER) or PLACEHOLDER,
        source=market.get("source", PLACEHOLDER) or PLACEHOLDER,
        valid_until=market.get("valid_until", PLACEHOLDER) or PLACEHOLDER,
    )

    compliance_data = payload.get("compliance", {})
    compliance = ComplianceInfo(
        forbidden=_ensure_list(compliance_data.get("forbidden")),
        required=_ensure_list(compliance_data.get("required")),
        channel_limits=_ensure_list(compliance_data.get("channel_limits")),
    )

    products_payload = payload.get("products", [])
    products: List[ProductItem] = []
    for item in products_payload if isinstance(products_payload, list) else []:
        if not isinstance(item, dict):
            continue
        products.append(
            ProductItem(
                name=str(item.get("name", PLACEHOLDER) or PLACEHOLDER),
                category=str(item.get("category", PLACEHOLDER) or PLACEHOLDER),
                highlights=_ensure_list(item.get("highlights")),
                risk_level=str(item.get("risk_level", PLACEHOLDER) or PLACEHOLDER),
                suitability=str(item.get("suitability", PLACEHOLDER) or PLACEHOLDER),
            )
        )

    follow_up = _ensure_list(payload.get("follow_up"))

    return RoadshowInput(
        client_profile=profile,
        client_goal=str(payload.get("client", {}).get("goal", PLACEHOLDER) or PLACEHOLDER),
        products=products,
        market_view=market_view,
        compliance=compliance,
        follow_up=follow_up,
        scene=str(payload.get("scene", PLACEHOLDER) or PLACEHOLDER),
    )


def format_section(title: str, lines: Iterable[str]) -> str:
    content = "\n".join(f"- {line}" for line in lines if line.strip())
    if not content:
        content = f"- {PLACEHOLDER}"
    return f"## {title}\n{content}\n"


def build_markdown(data: RoadshowInput) -> str:
    header = [
        "# 路演支持材料",
        f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"适用场景：{data.scene}",
        "",
    ]

    profile_lines = [
        f"客户层级：{data.client_profile.level}",
        f"风险偏好：{data.client_profile.risk_level}",
        f"投资期限：{data.client_profile.horizon}",
        f"流动性要求：{data.client_profile.liquidity}",
        f"本次目标：{data.client_goal}",
    ]

    market_lines = [
        f"观点摘要：{data.market_view.summary}",
        f"观点来源：{data.market_view.source}",
        f"有效期限：{data.market_view.valid_until}",
    ]

    product_lines: List[str] = []
    for product in data.products:
        highlights = "、".join(product.highlights) if product.highlights else PLACEHOLDER
        product_lines.append(
            f"{product.name}（{product.category}）/ 风险等级：{product.risk_level} / 适当性：{product.suitability} / 卖点：{highlights}"
        )

    compliance_lines = []
    if data.compliance.required:
        compliance_lines.append("必须提示：" + "；".join(data.compliance.required))
    if data.compliance.forbidden:
        compliance_lines.append("禁用表述：" + "；".join(data.compliance.forbidden))
    if data.compliance.channel_limits:
        compliance_lines.append("渠道限制：" + "；".join(data.compliance.channel_limits))

    follow_up_lines = data.follow_up or [PLACEHOLDER]

    output = "\n".join(header)
    output += format_section("客户概况与目标", profile_lines)
    output += format_section("市场观点", market_lines)
    output += format_section("产品要点", product_lines)
    output += format_section("沟通主线建议", [
        "开场：回顾客户关注点与路演目标",
        "现状：说明市场背景与观点依据",
        "配置逻辑：解释产品与需求的匹配关系",
        "风险提示：强调波动、期限与适当性要求",
        "下一步：确认资料、安排后续沟通",
    ])
    output += format_section("风险提示与合规提醒", compliance_lines)
    output += format_section("常见追问与回应", [
        "如果市场继续波动？——强调分散配置与持有期限的重要性",
        "收益能否保证？——明确不承诺收益，说明风险收益特征",
        "后续如何跟进？——明确资料补充与回访节奏",
    ])
    output += format_section("后续跟进", follow_up_lines)

    return output.strip() + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成路演支持材料")
    parser.add_argument("--input", required=True, help="输入 JSON 文件路径")
    parser.add_argument("--output", required=True, help="输出 Markdown 文件路径")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)

    payload = json.loads(input_path.read_text(encoding="utf-8"))
    data = parse_input(payload)
    output_path.write_text(build_markdown(data), encoding="utf-8")


if __name__ == "__main__":
    main()
