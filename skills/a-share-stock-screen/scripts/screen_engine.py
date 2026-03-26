# -*- coding: utf-8 -*-
"""A-share stock screening engine using cn-stock-data unified layer.

Usage:
    python screen_engine.py --min-roe 15 --max-pe 30 --min-profit-growth 20 --top 20
    python screen_engine.py --strategy value --top 20
    python screen_engine.py --strategy growth --top 20
"""
import sys
import adata
import argparse
import json
import os
import subprocess

CN_STOCK_DATA = os.path.join(
    os.environ.get(
        "SKILLS_ROOT",
        os.path.expanduser("~/.claude/skills")),
    "cn-stock-data/scripts/cn_stock_data.py")


def run_cmd(args_list):
    """Run cn_stock_data.py and return parsed JSON."""
    cmd = [sys.executable, CN_STOCK_DATA] + args_list
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None


def get_all_finance(codes):
    """Get financial data for a list of codes."""
    results = {}
    for code in codes:
        data = run_cmd(["finance", "--code", code])
        if data and data.get("ok") and data["data"]:
            results[code] = data["data"][-1]  # latest period
    return results


def screen(min_roe=0, max_pe=9999, min_profit_growth=-9999,
            max_debt_ratio=100, min_gross_margin=0, top=20):
    """Screen stocks by financial criteria."""
    # Get stock list via adata
    try:
        sys.path.insert(0, os.path.dirname(CN_STOCK_DATA))

        all_stocks = adata.stock.info.all_code()
        if all_stocks is None or all_stocks.empty:
            print(json.dumps(
                {"ok": False, "error": "Failed to get stock list"}))
            return
    except Exception as e:
        print(json.dumps({"ok": False, "error": f"adata not available: {e}"}))
        return

    # Filter to A-shares only (6xxxx=SH, 0xxxx/3xxxx=SZ)
    codes = all_stocks["stock_code"].tolist()
    a_share_codes = [
        c for c in codes if c.startswith(
            ("6", "0", "3")) and len(c) == 6]

    # Sample if too many (full market scan is slow)
    if len(a_share_codes) > 200:
        # Get major index constituents as a representative sample
        try:
            # CSI 300 + CSI 500
            hs300 = adata.stock.info.index_constituent(index_code="000300")
            zz500 = adata.stock.info.index_constituent(index_code="000905")
            sample_codes = set()
            if hs300 is not None and not hs300.empty:
                sample_codes.update(hs300["stock_code"].tolist())
            if zz500 is not None and not zz500.empty:
                sample_codes.update(zz500["stock_code"].tolist())
            if sample_codes:
                a_share_codes = list(sample_codes)
        except Exception:
            a_share_codes = a_share_codes[:300]  # fallback: first 300

    # Fetch finance data
    candidates = []
    for code in a_share_codes:
        data = run_cmd(["finance", "--code", code])
        if not data or not data.get("ok") or not data["data"]:
            continue
        latest = data["data"][-1]

        roe = latest.get("roe_wtd")
        gross_margin = latest.get("gross_margin")
        net_profit_yoy = latest.get("net_profit_yoy_gr")
        debt_ratio = latest.get("asset_liab_ratio")

        # Apply filters
        try:
            if roe is not None and float(roe) < min_roe:
                continue
            if gross_margin is not None and float(
                    gross_margin) < min_gross_margin:
                continue
            if net_profit_yoy is not None and float(
                    net_profit_yoy) < min_profit_growth:
                continue
            if debt_ratio is not None and float(debt_ratio) > max_debt_ratio:
                continue
        except (ValueError, TypeError):
            continue

        candidates.append({
            "code": code,
            "roe": roe,
            "gross_margin": gross_margin,
            "net_margin": latest.get("net_margin"),
            "net_profit_yoy": net_profit_yoy,
            "total_rev_yoy": latest.get("total_rev_yoy_gr"),
            "asset_liab_ratio": debt_ratio,
            "basic_eps": latest.get("basic_eps"),
        })

    # Sort by ROE descending
    candidates.sort(key=lambda x: float(x.get("roe") or 0), reverse=True)
    candidates = candidates[:top]

    print(json.dumps({
        "ok": True,
        "count": len(candidates),
        "screened_from": len(a_share_codes),
        "filters": {
            "min_roe": min_roe,
            "max_pe": max_pe,
            "min_profit_growth": min_profit_growth,
            "max_debt_ratio": max_debt_ratio,
        },
        "data": candidates,
    }, ensure_ascii=False, indent=2, default=str))


def main():
    parser = argparse.ArgumentParser(description="A-share stock screener")
    parser.add_argument("--min-roe", type=float, default=15)
    parser.add_argument("--max-pe", type=float, default=30)
    parser.add_argument("--min-profit-growth", type=float, default=20)
    parser.add_argument("--max-debt-ratio", type=float, default=60)
    parser.add_argument("--min-gross-margin", type=float, default=0)
    parser.add_argument("--top", type=int, default=20)
    parser.add_argument(
        "--strategy",
        choices=[
            "value",
            "growth",
            "dividend",
            "northbound"],
        help="Use preset strategy")
    args = parser.parse_args()

    if args.strategy == "value":
        screen(min_roe=15, max_pe=20, min_profit_growth=10, max_debt_ratio=50,
                min_gross_margin=30, top=args.top)
    elif args.strategy == "growth":
        screen(
            min_roe=12,
            max_pe=9999,
            min_profit_growth=30,
            max_debt_ratio=60,
            top=args.top)
    elif args.strategy == "dividend":
        screen(
            min_roe=10,
            max_pe=15,
            min_profit_growth=-9999,
            max_debt_ratio=50,
            top=args.top)
    else:
        screen(min_roe=args.min_roe, max_pe=args.max_pe,
                min_profit_growth=args.min_profit_growth,
                max_debt_ratio=args.max_debt_ratio,
                min_gross_margin=args.min_gross_margin,
                top=args.top)


if __name__ == "__main__":
    main()
