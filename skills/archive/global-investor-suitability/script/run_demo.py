from __future__ import annotations

from suitability_checker import InvestorProfile, check_suitability
import argparse

import json


def main() -> None:
    parser = argparse.ArgumentParser(description="Run listed company suitability demo")
    parser.add_argument("--symbol", required=True, help="e.g. 688981")
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


if __name__ == "__main__":
    main()
