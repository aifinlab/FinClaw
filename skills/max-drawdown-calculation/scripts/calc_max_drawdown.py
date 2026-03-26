#!/usr/bin/env python3
# Maximum drawdown calculator from a price series CSV.
from datetime import datetime
import argparse
import csv


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
    parser = argparse.ArgumentParser(description="Calculate maximum drawdown from price series.")
    parser.add_argument("--input", required=True, help="Input CSV file with date and price.")
    parser.add_argument("--date-col", default="date", help="Date column name.")
    parser.add_argument("--price-col", default="price", help="Price column name.")
    args = parser.parse_args()

    rows = load_prices(args.input, args.date_col, args.price_col)
    if len(rows) < 2:
        raise SystemExit("Not enough data to compute drawdown.")

    peak_price = rows[0][1]
    peak_date = rows[0][0]
    max_drawdown = 0.0
    dd_start = peak_date
    dd_end = peak_date

    for date_val, price_val in rows:
        if price_val > peak_price:
            peak_price = price_val
            peak_date = date_val
        drawdown = (price_val - peak_price) / peak_price
        if drawdown < max_drawdown:
            max_drawdown = drawdown
            dd_start = peak_date
            dd_end = date_val

    print(f"max_drawdown: {max_drawdown:.6f}")
    print(f"start_date: {dd_start.date()}")
    print(f"end_date: {dd_end.date()}")


if __name__ == "__main__":
    main()
