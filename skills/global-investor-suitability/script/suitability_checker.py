from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional

from fetch_public_data import CompanyProfile, fetch_company_profile


LAW_LIBRARY: Dict[str, Dict[str, object]] = {
    "GENERAL": {
        "source": "中国证监会《证券期货投资者适当性管理办法》",
        "principles": [
            "经营机构应了解投资者信息、评估风险承受能力并给出适当性匹配意见。",
            "普通投资者与专业投资者适用不同的保护强度。",
        ],
        "url": "https://www.csrc.gov.cn/csrc/c106256/c1653849/content.shtml",
    },
    "STAR": {
        "source": "上海证券交易所科创板投资者适当性规则摘要",
        "min_assets_20d": 500000,
        "min_trading_months": 24,
        "requires_risk_disclosure": True,
        "risk_level_hint": "high",
        "url": "https://one.sse.com.cn/onething/gptz/",
        "rules": [
            "个人投资者参与科创板股票交易，申请权限开通前20个交易日证券账户及资金账户内资产日均不低于人民币50万元。",
            "参与证券交易24个月以上。",
            "首次委托买入前应签署风险揭示书。",
        ],
    },
    "ChiNext": {
        "source": "深圳证券交易所创业板投资者适当性管理实施办法（2020年修订）",
        "min_assets_20d": 100000,
        "min_trading_months": 24,
        "requires_risk_disclosure": True,
        "risk_level_hint": "medium",
        "url": "https://docs.static.szse.cn/www/disclosure/notice/general/W020200427839935354879.pdf",
        "rules": [
            "新申请开通创业板交易权限的个人投资者，权限开通前20个交易日证券账户及资金账户内资产日均应不低于人民币10万元。",
            "参与证券交易24个月以上。",
            "首次参与创业板交易应签署风险揭示书。",
        ],
    },
    "Main Board": {
        "source": "中国证监会适当性管理办法 + 交易所风险揭示要求",
        "min_assets_20d": 0,
        "min_trading_months": 0,
        "requires_risk_disclosure": True,
        "risk_level_hint": "low",
        "url": "https://www.csrc.gov.cn/csrc/c106256/c1653849/content.shtml",
        "rules": [
            "主板普通股票通常不设置与科创板/创业板相同的权限资产门槛。",
            "经营机构仍需完成投资者分类、风险测评、风险揭示和适当性匹配。",
        ],
    },
    "BSE": {
        "source": "北交所公开规则口径（部署前建议人工复核最新官方规则）",
        "min_assets_20d": 500000,
        "min_trading_months": 24,
        "requires_risk_disclosure": True,
        "risk_level_hint": "high",
        "url": "https://www.bse.cn/",
        "rules": [
            "北交所股票交易通常要求投资者满足合格投资者门槛并完成风险揭示。",
            "如用于生产环境，应核对最新北交所投资者适当性规则。",
        ],
    },
}


@dataclass
class InvestorProfile:
    investor_type: str = "individual"
    avg_assets_20d: float = 0.0
    trading_experience_months: int = 0
    signed_risk_disclosure: bool = False
    risk_tolerance: str = "medium"
    is_professional_investor: bool = False


@dataclass
class SuitabilityResult:
    status: str
    company: Dict[str, object]
    investor_profile: Dict[str, object]
    unmet_conditions: List[str]
    matched_rules: List[str]
    warnings: List[str]
    legal_basis: List[Dict[str, str]]

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


RISK_ORDER = {"low": 1, "medium": 2, "high": 3}


def check_suitability(symbol: str, investor: InvestorProfile) -> SuitabilityResult:
    company: CompanyProfile = fetch_company_profile(symbol)
    board_rule = LAW_LIBRARY.get(company.board, LAW_LIBRARY["GENERAL"])

    unmet: List[str] = []
    warnings: List[str] = []
    matched_rules = list(board_rule.get("rules", []))
    legal_basis = [
        {
            "name": str(LAW_LIBRARY["GENERAL"]["source"]),
            "url": str(LAW_LIBRARY["GENERAL"]["url"]),
        },
        {
            "name": str(board_rule.get("source", "")),
            "url": str(board_rule.get("url", "")),
        },
    ]

    if investor.investor_type not in {"individual", "institution"}:
        unmet.append("investor_type 仅支持 individual 或 institution")

    if investor.investor_type == "individual" and not investor.is_professional_investor:
        min_assets = float(board_rule.get("min_assets_20d", 0))
        min_months = int(board_rule.get("min_trading_months", 0))
        require_disclosure = bool(board_rule.get("requires_risk_disclosure", False))
        target_risk = str(board_rule.get("risk_level_hint", "medium"))

        if investor.avg_assets_20d < min_assets:
            unmet.append(
                f"20个交易日日均资产不足：当前 {investor.avg_assets_20d:.0f} 元，要求至少 {min_assets:.0f} 元"
            )
        if investor.trading_experience_months < min_months:
            unmet.append(
                f"证券交易经验不足：当前 {investor.trading_experience_months} 个月，要求至少 {min_months} 个月"
            )
        if require_disclosure and not investor.signed_risk_disclosure:
            unmet.append("尚未签署风险揭示书")
        if RISK_ORDER.get(investor.risk_tolerance, 0) < RISK_ORDER.get(target_risk, 0):
            warnings.append(
                f"投资者风险承受能力为 {investor.risk_tolerance}，低于该板块典型风险提示级别 {target_risk}"
            )
    else:
        warnings.append("机构/专业投资者情形适用更细的内部制度与经纪业务规则，建议人工复核。")

    if unmet:
        status = "FAIL"
    elif warnings:
        status = "REVIEW"
    else:
        status = "PASS"

    return SuitabilityResult(
        status=status,
        company=company.to_dict(),
        investor_profile=asdict(investor),
        unmet_conditions=unmet,
        matched_rules=matched_rules,
        warnings=warnings,
        legal_basis=legal_basis,
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Check stock investor suitability")
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--investor-type", default="individual")
    parser.add_argument("--avg-assets-20d", type=float, default=0)
    parser.add_argument("--trading-experience-months", type=int, default=0)
    parser.add_argument("--signed-risk-disclosure", default="false")
    parser.add_argument("--risk-tolerance", default="medium")
    parser.add_argument("--is-professional-investor", default="false")
    args = parser.parse_args()

    investor = InvestorProfile(
        investor_type=args.investor_type,
        avg_assets_20d=args.avg_assets_20d,
        trading_experience_months=args.trading_experience_months,
        signed_risk_disclosure=str(args.signed_risk_disclosure).lower() == "true",
        risk_tolerance=args.risk_tolerance,
        is_professional_investor=str(args.is_professional_investor).lower() == "true",
    )
    result = check_suitability(args.symbol, investor)
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
