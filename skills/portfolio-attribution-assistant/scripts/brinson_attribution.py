from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


def read_csv(path: str):
    with open(path, 'r', encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def to_float(value, default=0.0):
    try:
        if value is None or value == '':
            return default
        return float(value)
    except Exception:
        return default


def index_by_industry(rows):
    data = {}
    for row in rows:
        industry = (row.get('行业') or row.get('industry') or '').strip()
        if not industry:
            continue
        data[industry] = {
            '组合权重': to_float(row.get('组合权重') or row.get('portfolio_weight') or 0),
            '基准权重': to_float(row.get('基准权重') or row.get('benchmark_weight') or 0),
            '组合收益': to_float(row.get('组合收益') or row.get('portfolio_return') or 0),
            '基准收益': to_float(row.get('基准收益') or row.get('benchmark_return') or 0),
        }
    return data


def brinson_single_period(rows):
    data = index_by_industry(rows)
    industries = sorted(data.keys())
    results = []
    total_alloc = 0.0
    total_select = 0.0
    total_interact = 0.0

    for ind in industries:
        d = data[ind]
        pw = d['组合权重']
        bw = d['基准权重']
        pr = d['组合收益']
        br = d['基准收益']

        allocation = (pw - bw) * br
        selection = bw * (pr - br)
        interaction = (pw - bw) * (pr - br)
        total = allocation + selection + interaction

        total_alloc += allocation
        total_select += selection
        total_interact += interaction

        results.append({
            '行业': ind,
            '组合权重': round(pw, 6),
            '基准权重': round(bw, 6),
            '组合收益': round(pr, 6),
            '基准收益': round(br, 6),
            '配置贡献': round(allocation, 6),
            '选股贡献': round(selection, 6),
            '交互贡献': round(interaction, 6),
            '总贡献': round(total, 6),
        })

    results.sort(key=lambda x: x['总贡献'], reverse=True)
    return {
        '行业归因结果': results,
        '汇总': {
            '配置贡献合计': round(total_alloc, 6),
            '选股贡献合计': round(total_select, 6),
            '交互贡献合计': round(total_interact, 6),
            '超额收益近似合计': round(total_alloc + total_select + total_interact, 6),
        }
    }


def main():
    if len(sys.argv) < 2:
        print('用法: python brinson_attribution.py 行业归因输入.csv [输出.json]')
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    rows = read_csv(input_path)
    result = brinson_single_period(rows)

    text = json.dumps(result, ensure_ascii=False, indent=2)
    if output_path:
        Path(output_path).write_text(text, encoding='utf-8')
    else:
        print(text)


if __name__ == '__main__':
    main()
