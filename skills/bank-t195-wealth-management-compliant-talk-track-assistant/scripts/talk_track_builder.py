"""财富管理合规话术生成器

功能：
- 读取结构化输入（JSON）
- 生成沟通主线、话术片段、风险提示、待核验事项

使用：
python scripts/talk_track_builder.py --input input.json --output output.json
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import argparse
import json


def validate_input(data: dict) -> dict:
    """验证输入参数"""
    if not isinstance(data, dict):
        raise ValueError("输入必须是字典类型")

    required_fields = []  # 添加必填字段
    for field in required_fields:
        if field not in data:
            raise ValueError(f"缺少必填字段: {field}")

    return data




@dataclass
class ClientProfile:
    name: str
    risk_level: str
    goals: List[str]
    horizon: str
    liquidity: str
    holdings_summary: str


@dataclass
class ProductInfo:
    name: str
    risk_level: str
    tenor: str
    asset_type: str
    fee: str
    key_risks: List[str]


@dataclass
class MarketContext:
    date: str
    source: str
    summary: str


@dataclass
class ComplianceContext:
    prohibited_phrases: List[str] = field(default_factory=list)
    mandatory_disclosures: List[str] = field(default_factory=list)
    suitability_notes: List[str] = field(default_factory=list)


@dataclass
class TalkTrackInput:
    client: ClientProfile
    products: List[ProductInfo]
    market: MarketContext
    scenario: str
    objective: str
    compliance: ComplianceContext
    missing_info: List[str] = field(default_factory=list)


def load_input(path: Path) -> TalkTrackInput:
    data = json.loads(path.read_text(encoding="utf-8"))

    client = ClientProfile(**data["client"])
    products = [ProductInfo(**item) for item in data.get("products", [])]
    market = MarketContext(**data["market"])
    compliance = ComplianceContext(**data.get("compliance", {}))

    return TalkTrackInput(
        client=client,
        products=products,
        market=market,
        scenario=data.get("scenario", "客户陪伴"),
        objective=data.get("objective", "解释持仓与下一步动作"),
        compliance=compliance,
        missing_info=data.get("missing_info", []),
    )


def build_mainline(talk_input: TalkTrackInput) -> List[str]:
    client = talk_input.client
    market = talk_input.market
    mainline = [
        f"开场：感谢{client.name}的关注，先对当前市场情况做简要说明。",
        f"事实说明：截至{market.date}，{market.summary}（来源：{market.source}）。",
        f"客户目标回顾：关注{', '.join(client.goals)}，期限{client.horizon}，流动性要求为{client.liquidity}。",
        f"持仓解释：当前持仓概览为{client.holdings_summary}，风险承受能力为{client.risk_level}。",
    ]
    return mainline


def build_recommendation(talk_input: TalkTrackInput) -> List[str]:
    if not talk_input.products:
        return ["建议：当前缺少可用产品信息，优先补充产品池与适当性匹配结果。"]

    recommendation = ["建议：结合适当性与期限约束，以下为可讨论的产品方向："]
    for product in talk_input.products:
        recommendation.append(
            f"- {product.name}（风险等级{product.risk_level}，期限{product.tenor}，资产类型{product.asset_type}，费用{product.fee}）"
        )
    recommendation.append("建议以客户风险承受能力为前提，逐一确认产品风险提示与认购适当性。")
    return recommendation


def build_risk_disclosures(talk_input: TalkTrackInput) -> List[str]:
    disclosures = ["风险提示："]
    for note in talk_input.compliance.mandatory_disclosures:
        disclosures.append(f"- {note}")

    if not talk_input.compliance.mandatory_disclosures:
        disclosures.append("- 本次沟通仅作信息交流，不构成收益承诺或产品保证。")
    return disclosures


def build_follow_up(talk_input: TalkTrackInput) -> List[str]:
    follow_up = [
        "下一步：",
        "- 若客户认可方向，补充适当性核验与产品材料确认。",
        "- 约定回访时间，跟进客户疑问与市场变化。",
    ]
    return follow_up


def build_missing_info(missing_info: List[str]) -> List[str]:
    if not missing_info:
        return []
    return ["待补充信息："] + [f"- {item}" for item in missing_info]


def build_output(talk_input: TalkTrackInput) -> Dict[str, List[str]]:
    return {
        "mainline": build_mainline(talk_input),
        "recommendation": build_recommendation(talk_input),
        "risk_disclosures": build_risk_disclosures(talk_input),
        "follow_up": build_follow_up(talk_input),
        "missing_info": build_missing_info(talk_input.missing_info),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="财富管理合规话术生成器")
    parser.add_argument("--input", required=True, help="输入JSON路径")
    parser.add_argument("--output", required=True, help="输出JSON路径")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)

    talk_input = load_input(input_path)
    output = build_output(talk_input)
    output["generated_at"] = datetime.now().isoformat(timespec="seconds")

    output_path.write_text(
        json.dumps(output, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
