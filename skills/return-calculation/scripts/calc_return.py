#!/usr/bin/env python3
# Simple return calculator from a price series CSV.
from datetime import datetime
import argparse
import csv
import math


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
    parser = argparse.ArgumentParser(description="Calculate simple/log returns from price series.")
    parser.add_argument("--input", required=True, help="Input CSV file with date and price.")
    parser.add_argument("--date-col", default="date", help="Date column name.")
    parser.add_argument("--price-col", default="price", help="Price column name.")
    parser.add_argument("--start-date", help="Start date (YYYY-MM-DD).")
    parser.add_argument("--end-date", help="End date (YYYY-MM-DD).")
    args = parser.parse_args()

    rows = load_prices(args.input, args.date_col, args.price_col)
    if args.start_date:
        start = parse_date(args.start_date)
        rows = [row for row in rows if row[0] >= start]
    if args.end_date:
        end = parse_date(args.end_date)
        rows = [row for row in rows if row[0] <= end]

    if len(rows) < 2:
        raise SystemExit("Not enough data to compute return.")

    start_date, start_price = rows[0]
    end_date, end_price = rows[-1]
    simple_return = end_price / start_price - 1
    log_return = math.log(end_price / start_price)

    days = (end_date - start_date).days
    annualized_return = ""
    if days > 0:
        annualized_return = (end_price / start_price) ** (365 / days) - 1

    print(f"start_date: {start_date.date()}")
    print(f"end_date: {end_date.date()}")
    print(f"simple_return: {simple_return:.6f}")
    print(f"log_return: {log_return:.6f}")
    if annualized_return != "":
        print(f"annualized_return: {annualized_return:.6f}")


if __name__ == "__main__":
    main()
