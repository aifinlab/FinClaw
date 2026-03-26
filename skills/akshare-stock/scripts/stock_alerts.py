#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票异常波动预警 - 基于AkShare
用于FinClaw自动监控系统
"""

import pandas as pd
import sys
from datetime import datetime, timedelta
import akshare as ak
import argparse
import json


def check_price_alerts(watchlist=None):
    """
    检查股票价格异常波动

    Args:
        watchlist: 监控股票列表，如 ['000001', '600519']

    Returns:
        dict: 预警信息
    """
    if watchlist is None:
        # 默认监控部分热门股票
        watchlist = [
            '000001',  # 平安银行
            '000002',  # 万科A
            '000858',  # 五粮液
            '002230',  # 科大讯飞
            '002594',  # 比亚迪
            '300750',  # 宁德时代
            '600000',  # 浦发银行
            '600009',  # 上海机场
            '600016',  # 民生银行
            '600028',  # 中国石化
            '600030',  # 中信证券
            '600031',  # 三一重工
            '600036',  # 招商银行
            '600048',  # 保利发展
            '600104',  # 上汽集团
            '600276',  # 恒瑞医药
            '600309',  # 万华化学
            '600519',  # 贵州茅台
            '600585',  # 海螺水泥
            '600588',  # 用友网络
            '600690',  # 海尔智家
            '600745',  # 闻泰科技
            '600809',  # 山西汾酒
            '600887',  # 伊利股份
            '601012',  # 隆基绿能
            '601088',  # 中国神华
            '601166',  # 兴业银行
            '601318',  # 中国平安
            '601398',  # 工商银行
            '601628',  # 中国人寿
            '601668',  # 中国建筑
            '601857',  # 中国石油
            '601888',  # 中国中免
            '601899',  # 紫金矿业
            '603288',  # 海天味业
            '603501',  # 韦尔股份
            '603986',  # 兆易创新
            '688008',  # 澜起科技
            '688009',  # 中国通号
            '688012',  # 中微公司
            '688036',  # 传音控股
            '688111',  # 金山办公
            '688981',  # 中芯国际
        ]

    alerts = []

    try:
        # 获取当日行情
        df = ak.stock_zh_a_spot_em()

        for code in watchlist:
            try:
                # 查找股票数据
                stock_data = df[df['代码'] == code]
                if stock_data.empty:
                    continue

                row = stock_data.iloc[0]
                name = row['名称']
                change_pct = float(row['涨跌幅']) if pd.notna(row['涨跌幅']) else 0
                volume_ratio = float(
    row['量比']) if '量比' in row and pd.notna(
        row['量比']) else 0

                # 涨跌停检测
                if change_pct >= 9.5:
                    alerts.append({
                        'code': code,
                        'name': name,
                        'type': '涨停',
                        'change_pct': round(change_pct, 2),
                        'message': f"{name}({code}) 涨停，涨幅 {change_pct:.2f}%"
                    })
                elif change_pct <= -9.5:
                    alerts.append({
                        'code': code,
                        'name': name,
                        'type': '跌停',
                        'change_pct': round(change_pct, 2),
                        'message': f"{name}({code}) 跌停，跌幅 {change_pct:.2f}%"
                    })

                # 大幅波动检测 (>5%)
                elif abs(change_pct) >= 5:
                    direction = '大涨' if change_pct > 0 else '大跌'
                    alerts.append({
                        'code': code,
                        'name': name,
                        'type': direction,
                        'change_pct': round(change_pct, 2),
                        'message': f"{name}({code}) {direction} {abs(change_pct):.2f}%"
                    })

                # 放量检测 (量比>3)
                elif volume_ratio >= 3:
                    alerts.append({
                        'code': code,
                        'name': name,
                        'type': '放量',
                        'volume_ratio': round(volume_ratio, 2),
                        'change_pct': round(change_pct, 2),
                        'message': f"{name}({code}) 放量，量比 {volume_ratio:.2f}，涨跌 {change_pct:.2f}%"
                    })

            except Exception as e:
                continue

        return {
            'status': 'success',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_checked': len(watchlist),
            'alerts_count': len(alerts),
            'alerts': alerts
        }

    except Exception as e:
        return {
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }


def main():
    """主函数 - CLI入口"""



    parser = argparse.ArgumentParser(description='股票异常波动监控')
    parser.add_argument('--codes', type=str, help='股票代码列表，逗号分隔')
    parser.add_argument(
    '--output',
    type=str,
    default='json',
        help='输出格式: json/text')

    args = parser.parse_args()

    watchlist = None
    if args.codes:
        watchlist = [c.strip() for c in args.codes.split(',')]

    result = check_price_alerts(watchlist)

    if args.output == 'json':
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"\n===== 股票异常波动监控 =====")
        print(f"时间: {result['timestamp']}")
        print(f"监控数量: {result.get('total_checked', 0)}")
        print(f"预警数量: {result.get('alerts_count', 0)}")

        if result.get('alerts'):
            print("\n预警详情:")
            for alert in result['alerts']:
                print(f"  [{alert['type']}] {alert['message']}")
        else:
            print("\n暂无异常波动")

if __name__ == '__main__':
    main()
