#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
催化剂日历工具
用于生成催化剂日历、跟踪事件、提醒重要时点
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional


class CatalystCalendar:
    """催化剂日历管理器"""
    
    # 催化剂类型
    CATALYST_TYPES = {
        'earnings': '财报',
        'product': '产品',
        'policy': '政策',
        'ma': '并购重组',
        'order': '订单',
        'capacity': '产能',
        'equity': '股权',
        'other': '其他'
    }
    
    # 确定性等级
    CERTAINTY_LEVELS = {
        'high': '高确定性',
        'mid': '中确定性',
        'low': '低确定性'
    }
    
    # 预期影响
    IMPACT_LEVELS = {
        'positive': '正面',
        'neutral': '中性',
        'negative': '负面'
    }
    
    def __init__(self):
        self.events = []
    
    def add_event(self, date: str, company: str, event: str, 
                  event_type: str = 'other', certainty: str = 'mid',
                  impact: str = 'positive', description: str = '') -> Dict:
        """
        添加催化剂事件
        
        Args:
            date: 日期 (YYYY-MM-DD)
            company: 公司名称
            event: 事件名称
            event_type: 事件类型
            certainty: 确定性等级
            impact: 预期影响
            description: 事件描述
            
        Returns:
            添加的事件信息
        """
        event_data = {
            'id': len(self.events) + 1,
            'date': date,
            'company': company,
            'event': event,
            'event_type': event_type,
            'event_type_cn': self.CATALYST_TYPES.get(event_type, '其他'),
            'certainty': certainty,
            'certainty_cn': self.CERTAINTY_LEVELS.get(certainty, '中确定性'),
            'impact': impact,
            'impact_cn': self.IMPACT_LEVELS.get(impact, '中性'),
            'description': description,
            'status': 'pending'
        }
        
        self.events.append(event_data)
        return event_data
    
    def get_events_by_date_range(self, start_date: str, end_date: str) -> List[Dict]:
        """
        获取日期范围内的事件
        
        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            
        Returns:
            事件列表
        """
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        filtered = []
        for event in self.events:
            event_date = datetime.strptime(event['date'], '%Y-%m-%d')
            if start <= event_date <= end:
                filtered.append(event)
        
        # 按日期排序
        filtered.sort(key=lambda x: x['date'])
        return filtered
    
    def get_events_by_company(self, company: str) -> List[Dict]:
        """
        获取指定公司的事件
        
        Args:
            company: 公司名称
            
        Returns:
            事件列表
        """
        return [e for e in self.events if company in e['company']]
    
    def get_events_by_type(self, event_type: str) -> List[Dict]:
        """
        获取指定类型的事件
        
        Args:
            event_type: 事件类型
            
        Returns:
            事件列表
        """
        return [e for e in self.events if e['event_type'] == event_type]
    
    def get_upcoming_events(self, days: int = 30) -> List[Dict]:
        """
        获取未来 N 天内的事件
        
        Args:
            days: 天数
            
        Returns:
            即将发生的事件列表
        """
        today = datetime.now()
        end_date = today + timedelta(days=days)
        
        return self.get_events_by_date_range(
            today.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )
    
    def generate_calendar_table(self, start_date: str, end_date: str) -> str:
        """
        生成催化剂日历表格（Markdown 格式）
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            Markdown 表格字符串
        """
        events = self.get_events_by_date_range(start_date, end_date)
        
        if not events:
            return "暂无催化剂事件"
        
        # 表头
        header = "| 日期 | 公司 | 事件 | 类型 | 确定性 | 影响 |\n"
        separator = "|------|------|------|------|--------|------|\n"
        
        # 数据行
        rows = []
        for event in events:
            row = f"| {event['date']} | {event['company']} | {event['event']} | {event['event_type_cn']} | {event['certainty_cn']} | {event['impact_cn']} |\n"
            rows.append(row)
        
        return header + separator + "".join(rows)
    
    def generate_company_catalyst_list(self, company: str) -> str:
        """
        生成公司催化剂列表
        
        Args:
            company: 公司名称
            
        Returns:
            催化剂列表（Markdown 格式）
        """
        events = self.get_events_by_company(company)
        
        if not events:
            return f"{company} 暂无催化剂事件"
        
        output = f"## 【{company}】催化剂跟踪\n\n"
        
        for event in events:
            status_icon = '🟢' if event['status'] == 'completed' else '🟡'
            output += f"### {status_icon} {event['event']}\n"
            output += f"- 日期：{event['date']}\n"
            output += f"- 类型：{event['event_type_cn']}\n"
            output += f"- 确定性：{event['certainty_cn']}\n"
            output += f"- 预期影响：{event['impact_cn']}\n"
            if event['description']:
                output += f"- 描述：{event['description']}\n"
            output += "\n"
        
        return output
    
    def update_event_status(self, event_id: int, status: str) -> bool:
        """
        更新事件状态
        
        Args:
            event_id: 事件 ID
            status: 新状态 (pending/completed/cancelled)
            
        Returns:
            是否更新成功
        """
        for event in self.events:
            if event['id'] == event_id:
                event['status'] = status
                return True
        return False
    
    def export_to_json(self) -> str:
        """
        导出为 JSON 格式
        
        Returns:
            JSON 字符串
        """
        return json.dumps(self.events, ensure_ascii=False, indent=2)


def main():
    """测试函数"""
    calendar = CatalystCalendar()
    
    # 添加测试事件
    calendar.add_event('2024-03-20', '贵州茅台', '2023 年年报发布', 'earnings', 'high', 'positive')
    calendar.add_event('2024-03-25', '宁德时代', '麒麟电池发布会', 'product', 'high', 'positive')
    calendar.add_event('2024-04-01', '光伏行业', '行业政策发布', 'policy', 'mid', 'positive')
    calendar.add_event('2024-04-10', '某公司', '大股东减持', 'equity', 'high', 'negative')
    
    # 生成日历表格
    print("催化剂日历:")
    print(calendar.generate_calendar_table('2024-03-01', '2024-04-30'))
    
    # 获取即将发生的事件
    print("\n即将发生的催化剂:")
    upcoming = calendar.get_upcoming_events(30)
    for event in upcoming:
        print(f"- {event['date']}: {event['company']} - {event['event']}")


if __name__ == "__main__":
    main()
