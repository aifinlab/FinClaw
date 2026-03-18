from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
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


def build_industry_weights(holdings_rows, mapping_rows):
    mapping = {}
    for row in mapping_rows:
        code = (row.get('代码') or row.get('code') or '').strip()
        industry = (row.get('行业') or row.get('industry') or '未分类').strip() or '未分类'
        if code:
            mapping[code] = industry

    result = defaultdict(float)
    details = []
    for row in holdings_rows:
        code = (row.get('代码') or row.get('code') or '').strip()
        name = (row.get('名称') or row.get('name') or '').strip()
        weight = to_float(row.get('权重') or row.get('weight') or 0)
        industry = mapping.get(code, '未分类')
        result[industry] += weight
        details.append({'代码': code, '名称': name, '行业': industry, '权重': round(weight, 6)})

    industry_rows = [
        {'行业': k, '行业权重': round(v, 6)} for k, v in sorted(result.items(), key=lambda x: x[1], reverse=True)
    ]
    return {'行业权重汇总': industry_rows, '明细': details}


def main():
    if len(sys.argv) < 3:
        print('用法: python industry_weight_mapper.py 持仓.csv 行业映射.csv [输出.json]')
        sys.exit(1)

    holdings_path = sys.argv[1]
    mapping_path = sys.argv[2]
    output_path = sys.argv[3] if len(sys.argv) > 3 else None

    holdings_rows = read_csv(holdings_path)
    mapping_rows = read_csv(mapping_path)
    result = build_industry_weights(holdings_rows, mapping_rows)

    text = json.dumps(result, ensure_ascii=False, indent=2)
    if output_path:
        Path(output_path).write_text(text, encoding='utf-8')
    else:
        print(text)


if __name__ == '__main__':
    main()
