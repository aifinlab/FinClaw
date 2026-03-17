from __future__ import annotations

import argparse
import json
from pathlib import Path

from fetch_data import fetch_financial_statements, resolve_company
from risk_model import build_overdue_risk_report


def main():
    parser = argparse.ArgumentParser(description='使用 AkShare 财报数据进行企业逾期风险识别')
    parser.add_argument('--company', default='荣盛发展', help='企业名称或 6 位股票代码，如 荣盛发展 / 002146')
    parser.add_argument('--output', default='output/report.json', help='输出 JSON 文件路径')
    args = parser.parse_args()

    profile = resolve_company(args.company)
    balance, profit, cashflow = fetch_financial_statements(profile.market_symbol)
    report = build_overdue_risk_report(balance, profit, cashflow)
    report['company'] = {
        'name': profile.name,
        'code': profile.code,
        'market_symbol': profile.market_symbol,
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')

    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f'\n报告已写入: {output_path.resolve()}')


if __name__ == '__main__':
    main()
