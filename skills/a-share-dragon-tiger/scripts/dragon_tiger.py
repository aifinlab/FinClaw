#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股龙虎榜数据获取 - 简化版
用于盘后龙虎榜分析
"""

import sys
from datetime import datetime, timedelta
import akshare as ak
import argparse
import json


def get_today_billboard():
    """获取今日龙虎榜数据"""
    try:
        # 获取当日日期
        today = datetime.now().strftime('%Y%m%d')

        # 获取龙虎榜明细
        df = ak.stock_lhb_detail_em(start_date=today, end_date=today)

        if df.empty:
            return {
                'status': 'success',
                'message': '今日暂无龙虎榜数据',
                'date': today,
                'data': []
            }

        # 转换为JSON格式
        records = df.head(20).to_dict('records')

        # 简化字段
        simplified = []
        for record in records:
            simplified.append({
                'code': record.get('代码', ''),
                'name': record.get('名称', ''),
                'reason': record.get('上榜原因', ''),
                'close': record.get('收盘价', 0),
                'change_pct': record.get('涨跌幅', 0),
                'turnover': record.get('成交额', 0),
                'buy_amount': record.get('买入金额', 0),
                'sell_amount': record.get('卖出金额', 0),
                'net_amount': record.get('净额', 0),
            })

        return {
            'status': 'success',
            'date': today,
            'count': len(simplified),
            'data': simplified
        }

    except Exception as e:
        return {
            'status': 'error',
            'message': str(e),
            'date': datetime.now().strftime('%Y%m%d')
        }


def get_billboard_by_stock(code):
    """获取指定股票的龙虎榜历史"""
    try:
        # 获取近30日龙虎榜
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        df = ak.stock_lhb_detail_em(
            start_date=start_date.strftime('%Y%m%d'),
            end_date=end_date.strftime('%Y%m%d')
        )

        # 过滤指定股票
        stock_df = df[df['代码'] == code]

        if stock_df.empty:
            return {
                'status': 'success',
                'code': code,
                'message': '近30日无龙虎榜记录',
                'count': 0,
                'data': []
            }

        records = stock_df.to_dict('records')

        return {
            'status': 'success',
            'code': code,
            'count': len(records),
            'data': records
        }

    except Exception as e:
        return {
            'status': 'error',
            'code': code,
            'message': str(e)
        }


def main():
    """主函数"""



    parser = argparse.ArgumentParser(description='龙虎榜数据获取')
    parser.add_argument('--code', type=str, help='指定股票代码')
    parser.add_argument('--output', type=str, default='json', help='输出格式')

    args = parser.parse_args()

    if args.code:
        result = get_billboard_by_stock(args.code)
    else:
        result = get_today_billboard()

    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
