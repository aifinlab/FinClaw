#!/usr/bin/env python3
# Volatility calculator from a price series CSV.
import argparse
import csv
import math
import statistics
from datetime import datetime


def parse_date(value):
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y%m%d"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    raise ValueError(f"Unsupported date format: {value}")


def load_prices(path, date_col, price_col):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if date_col not in reader.fieldnames or price_col not in reader.fieldnames:
            raise SystemExit("Missing required columns in input CSV.")
        for row in reader:
            date_val = row.get(date_col)
            price_val = row.get(price_col)
            if not date_val or not price_val:
                continue
            rows.append((parse_date(date_val.strip()), float(price_val)))
    rows.sort(key=lambda x: x[0])
    return rows


def main():
    parser = argparse.ArgumentParser(description="Calculate volatility from price series.")
    parser.add_argument("--input", required=True, help="Input CSV file with date and price.")
    parser.add_argument("--date-col", default="date", help="Date column name.")
    parser.add_argument("--price-col", default="price", help="Price column name.")
    parser.add_argument("--annualization", type=float, default=252, help="Annualization factor.")
    args = parser.parse_args()

    rows = load_prices(args.input, args.date_col, args.price_col)
    if len(rows) < 2:
        raise SystemExit("Not enough data to compute volatility.")

    log_returns = []
    for idx in range(1, len(rows)):
        prev_price = rows[idx - 1][1]
        curr_price = rows[idx][1]
        if prev_price <= 0 or curr_price <= 0:
            continue
        log_returns.append(math.log(curr_price / prev_price))

    if len(log_returns) < 2:
        raise SystemExit("Not enough return observations.")

    period_vol = statistics.stdev(log_returns)
    annual_vol = period_vol * math.sqrt(args.annualization)

    print(f"observations: {len(log_returns)}")
    print(f"period_volatility: {period_vol:.6f}")
    print(f"annualized_volatility: {annual_vol:.6f}")


if __name__ == "__main__":
    main()
