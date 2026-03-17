#!/usr/bin/env python3
# Simple financial ratio calculator.
import argparse
import csv
import sys


def safe_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def safe_div(numerator, denominator):
    if numerator is None or denominator in (None, 0):
        return ""
    return numerator / denominator


def main():
    parser = argparse.ArgumentParser(description="Calculate common financial ratios from a CSV.")
    parser.add_argument("--input", required=True, help="Input CSV file with financial fields.")
    parser.add_argument("--output", help="Output CSV file for ratios.")
    args = parser.parse_args()

    with open(args.input, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise SystemExit("Input CSV has no header.")
        rows = list(reader)

    output_rows = []
    for row in rows:
        revenue = safe_float(row.get("revenue"))
        gross_profit = safe_float(row.get("gross_profit"))
        net_income = safe_float(row.get("net_income"))
        total_assets = safe_float(row.get("total_assets"))
        total_liabilities = safe_float(row.get("total_liabilities"))
        equity = safe_float(row.get("equity"))
        current_assets = safe_float(row.get("current_assets"))
        current_liabilities = safe_float(row.get("current_liabilities"))
        inventory = safe_float(row.get("inventory"))
        cash = safe_float(row.get("cash"))
        operating_cashflow = safe_float(row.get("operating_cashflow"))

        row["gross_margin"] = safe_div(gross_profit, revenue)
        row["net_margin"] = safe_div(net_income, revenue)
        row["roa"] = safe_div(net_income, total_assets)
        row["roe"] = safe_div(net_income, equity)
        row["debt_ratio"] = safe_div(total_liabilities, total_assets)
        row["current_ratio"] = safe_div(current_assets, current_liabilities)
        row["quick_ratio"] = safe_div(
            (current_assets - inventory) if current_assets is not None and inventory is not None else None,
            current_liabilities,
        )
        row["cash_ratio"] = safe_div(cash, current_liabilities)
        row["ocf_to_net_income"] = safe_div(operating_cashflow, net_income)
        output_rows.append(row)

    fieldnames = list(output_rows[0].keys()) if output_rows else (reader.fieldnames or [])
    if args.output:
        with open(args.output, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(output_rows)
        print(f"Saved ratios to {args.output}")
    else:
        out = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
        out.writeheader()
        out.writerows(output_rows)


if __name__ == "__main__":
    main()
