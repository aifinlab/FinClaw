#!/usr/bin/env python3
"""
Search funds by name or code (using Tencent Suggest API).

Usage:
    python fund_search_tx.py <keyword>

Example:
    python fund_search_tx.py 白酒
    python fund_search_tx.py 300ETF
    python fund_search_tx.py 512800
"""

import json
import requests
import sys
import traceback


def search_funds_tx(keyword):
    """使用腾讯财经API搜索基金"""
    try:
        # Tencent suggest API
        url = "https://smartbox.gtimg.cn/s3/"
        params = {
            'v': '2',
            'q': keyword,
            't': 'all'
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }

        resp = requests.get(url, params=params, headers=headers, timeout=10)

        # Decode unicode escapes
        data = resp.text.encode('utf-8').decode('unicode_escape')

        if not data or 'v_hint="' not in data:
            print(f"[INFO] No results for '{keyword}'")
            sys.exit(0)

        # Parse Tencent suggest format
        content = data.split('v_hint="')[1].split('"')[0]
        if not content:
            print(f"[INFO] No results for '{keyword}'")
            sys.exit(0)

        # Format: market~code~name~pinyin~type (items separated by ^)
        funds = []
        items = content.split('^')

        print(f"\n🔍 Fund search results for '{keyword}':")
        print(f"{'='*70}")
        print(f"  {'No.':<4} {'Code':<8} {'Name':<20} {'Type':<10} {'Market':<8}")
        print(f"  {'-'*70}")

        for idx, item in enumerate(items[:20], 1):
            parts = item.split('~')
            if len(parts) >= 3:
                market = parts[0]
                code = parts[1]
                name = parts[2]
                fund_type = parts[4] if len(parts) > 4 else 'Unknown'

                # Filter for funds (ETF, LOF, FJ, etc.)
                if code.isdigit() and len(code) == 6:
                    fund_types = ['ETF', 'LOF', 'FJ', 'FOF', 'QDII', 'GP-A', 'GP-B']
                    if any(ft in fund_type for ft in fund_types) or keyword.isdigit():
                        print(f"  {idx:<4} {code:<8} {name:<20} {fund_type:<10} {market:<8}")
                        funds.append({
                            "index": idx,
                            "code": code,
                            "name": name,
                            "market": market,
                            "type": fund_type
                        })

        if not funds:
            print(f"  [INFO] No fund results found for '{keyword}'")

        # Print JSON for parsing
        print(f"\n##SEARCH_META##")
        print(json.dumps({
            "keyword": keyword,
            "total": len(funds),
            "results": funds
        }, ensure_ascii=False))

    except Exception as e:
        print(f"[ERROR] Failed to search funds: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python fund_search_tx.py <keyword>")
        print("Example: python fund_search_tx.py 白酒")
        print("         python fund_search_tx.py 300ETF")
        sys.exit(1)

    keyword = sys.argv[1]
    search_funds_tx(keyword)
