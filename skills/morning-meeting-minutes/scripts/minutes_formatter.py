#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
晨会纪要格式化工具
用于格式化晨会纪要、提取要点、生成待办
"""

from datetime import datetime
from typing import Dict, List, Optional
import json


class MinutesFormatter:
    """晨会纪要格式化器"""

    # 市场指数名称
    INDEX_NAMES = {
        'sh': '上证指数',
        'sz': '深证成指',
        'cyb': '创业板指',
        'hs300': '沪深 300',
        'zz500': '中证 500'
    }

    @staticmethod
    def format_market_summary(data: Dict) -> str:
        """
        格式化市场概览

        Args:
            data: 市场数据字典

        Returns:
            格式化文本
        """
        output = "## 一、市场概览\n\n"

        # 指数表现
        indices = data.get('indices', [])
        if indices:
            output += "### 指数表现\n"
            for idx in indices:
                name = idx.get('name', '')
                change = idx.get('change', 0)
                change_str = f"{change:+.2f}%"
                output += f"- {name}: {change_str}\n"
            output += "\n"

        # 成交量
        volume = data.get('volume', 0)
        if volume:
            output += f"### 成交量\n- 两市成交：{volume}亿元\n\n"

        # 资金流向
        north = data.get('north_flow', 0)
        if north:
            direction = '流入' if north > 0 else '流出'
            output += f"### 资金流向\n- 北向资金：{direction}{abs(north)}亿元\n\n"

        # 热点板块
        sectors = data.get('hot_sectors', [])
        if sectors:
            output += "### 热点板块\n"
            for sector in sectors:
                output += f"- {sector}\n"

        return output

    @staticmethod
    def format_viewpoint(sector: str, view: str, logic: str, targets: List[str]) -> str:
        """
        格式化行业观点

        Args:
            sector: 行业名称
            view: 核心观点
            logic: 逻辑
            targets: 推荐标的

        Returns:
            格式化文本
        """
        output = f"### {sector}\n"
        output += f"- **观点**: {view}\n"
        output += f"- **逻辑**: {logic}\n"
        if targets:
            output += f"- **标的**: {', '.join(targets)}\n"
        return output

    @staticmethod
    def format_company_comment(company: str, event: str, comment: str, rating: str) -> str:
        """
        格式化工厂点评

        Args:
            company: 公司名称
            event: 事件
            comment: 点评
            rating: 评级

        Returns:
            格式化文本
        """
        output = f"### {company}\n"
        output += f"- **事件**: {event}\n"
        output += f"- **点评**: {comment}\n"
        output += f"- **评级**: {rating}\n"
        return output

    @staticmethod
    def generate_recommendation_table(recommendations: List[Dict]) -> str:
        """
        生成重点推荐表格

        Args:
            recommendations: 推荐列表

        Returns:
            Markdown 表格
        """
        if not recommendations:
            return "暂无推荐"

        header = "| 标的 | 逻辑 | 目标价 | 催化剂 |\n"
        separator = "|------|------|--------|----------|\n"

        rows = []
        for rec in recommendations:
            row = f"| {rec.get('name', '')} | {rec.get('logic', '')} | {rec.get('target', '')} | {rec.get('catalyst', '')} |\n"
            rows.append(row)

        return header + separator + "".join(rows)

    @staticmethod
    def generate_todo_list(todos: List[Dict]) -> str:
        """
        生成待办事项列表

        Args:
            todos: 待办列表

        Returns:
            格式化文本
        """
        if not todos:
            return "暂无待办"

        output = ""
        for todo in todos:
            checked = "✓" if todo.get('done', False) else " "
            output += f"- [{checked}] {todo.get('task', '')}"
            if todo.get('assignee'):
                output += f" - @{todo['assignee']}"
            if todo.get('deadline'):
                output += f" (截止：{todo['deadline']})"
            output += "\n"

        return output

    @staticmethod
    def generate_full_minutes(data: Dict) -> str:
        """
        生成完整晨会纪要

        Args:
            data: 纪要数据字典

        Returns:
            完整纪要文本
        """
        output = f"# 【晨会纪要】{data.get('date', datetime.now().strftime('%Y-%m-%d'))}\n\n"

        # 市场概览
        if 'market' in data:
            output += MinutesFormatter.format_market_summary(data['market'])
            output += "\n"

        # 宏观与政策
        if 'macro' in data:
            output += "## 二、宏观与政策\n\n"
            for item in data['macro']:
                output += f"- {item}\n"
            output += "\n"

        # 行业观点
        if 'views' in data:
            output += "## 三、行业观点\n\n"
            for view in data['views']:
                output += MinutesFormatter.format_viewpoint(
                    view.get('sector', ''),
                    view.get('view', ''),
                    view.get('logic', ''),
                    view.get('targets', [])
                )
                output += "\n"

        # 公司点评
        if 'comments' in data:
            output += "## 四、公司点评\n\n"
            for comment in data['comments']:
                output += MinutesFormatter.format_company_comment(
                    comment.get('company', ''),
                    comment.get('event', ''),
                    comment.get('comment', ''),
                    comment.get('rating', '')
                )
                output += "\n"

        # 重点推荐
        if 'recommendations' in data:
            output += "## 五、重点推荐\n\n"
            output += MinutesFormatter.generate_recommendation_table(data['recommendations'])
            output += "\n"

        # 待办事项
        if 'todos' in data:
            output += "## 六、待办事项\n\n"
            output += MinutesFormatter.generate_todo_list(data['todos'])
            output += "\n"

        # 明日关注
        if 'watchlist' in data:
            output += "## 七、明日关注\n\n"
            for item in data['watchlist']:
                output += f"- {item}\n"

        # 落款
        output += f"\n---\n整理：{data.get('editor', '')}  发送：{datetime.now().strftime('%H:%M')}\n"

        return output


def main():
    """测试函数"""
    # 测试数据
    test_data = {
        'date': '2024-03-14',
        'market': {
            'indices': [
                {'name': '上证指数', 'change': 0.5},
                {'name': '深证成指', 'change': 0.8},
                {'name': '创业板指', 'change': 1.2}
            ],
            'volume': 9500,
            'north_flow': 50,
            'hot_sectors': ['AI', '新能源', '医药']
        },
        'views': [
            {
                'sector': 'AI',
                'view': '大模型持续迭代，应用落地加速',
                'logic': '技术突破 + 商业化进展',
                'targets': ['科大讯飞', '海康威视']
            }
        ],
        'recommendations': [
            {'name': '贵州茅台', 'logic': '高端酒需求稳定', 'target': '2000 元', 'catalyst': '年报'}
        ],
        'todos': [
            {'task': '完成 XX 公司调研', 'assignee': '张三', 'deadline': '2024-03-15'}
        ],
        'watchlist': ['美国 CPI 数据', '美联储议息会议'],
        'editor': '李四'
    }

    # 生成完整纪要
    minutes = MinutesFormatter.generate_full_minutes(test_data)
    print(minutes)


if __name__ == "__main__":
    main()
