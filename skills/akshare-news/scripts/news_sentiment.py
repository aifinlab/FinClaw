#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新闻情感分析 - AkShare
分析财经新闻的情感倾向
"""

import akshare as ak
import sys
import re

# 定义情感词典
POSITIVE_WORDS = [
    '上涨', '大涨', '涨停', '新高', '突破', '利好', '预增', '扭亏', '增长', '提升',
    '超预期', '订单', '中标', '回购', '增持', '分红', '扩张', '盈利', '盈利增长',
    '看好', '推荐', '买入', '增持评级', '目标价上调', '业绩大增', '战略合作',
    '技术突破', '创新', '领先', '优势', '龙头', '独角兽', '并购', '重组', '资产注入'
]

NEGATIVE_WORDS = [
    '下跌', '大跌', '跌停', '新低', '跌破', '利空', '预减', '亏损', '下降', '下滑',
    '不及预期', '减持', '解禁', '处罚', '诉讼', '违规', '风险', '暴雷', '裁员',
    '看空', '卖出', '减持评级', '目标价下调', '业绩下滑', '债务危机', '资金链',
    '停产', '亏损扩大', '退市', 'ST', '警告', '调查', '冻结', '质押', '违约'
]

def analyze_sentiment(text):
    """
    分析文本情感倾向
    返回: score(正数=积极, 负数=消极, 0=中性), label(标签)
    """
    pos_count = sum(1 for word in POSITIVE_WORDS if word in text)
    neg_count = sum(1 for word in NEGATIVE_WORDS if word in text)
    
    score = pos_count - neg_count
    
    if score > 0:
        label = "🟢 积极"
    elif score < 0:
        label = "🔴 消极"
    else:
        label = "➡️ 中性"
    
    return score, label, pos_count, neg_count

def get_stock_news_sentiment(stock="600519"):
    """获取个股新闻情感分析"""
    try:
        df = ak.stock_news_em()
        
        # 分析每条新闻的情感
        sentiments = []
        for i, row in df.head(50).iterrows():
            title = row.get('标题', '')
            score, label, pos, neg = analyze_sentiment(title)
            sentiments.append({
                '标题': title,
                '情感得分': score,
                '情感标签': label,
                '正向词': pos,
                '负向词': neg,
                '来源': row.get('来源', 'N/A'),
                '时间': row.get('时间', 'N/A')
            })
        
        return sentiments
    except Exception as e:
        print(f"情感分析失败: {e}")
        return []

def format_sentiment_report(stock):
    """格式化情感分析报告"""
    print("=" * 80)
    print(f"📊 新闻情感分析 | {stock}")
    print("=" * 80)
    
    sentiments = get_stock_news_sentiment(stock)
    if sentiments:
        # 统计
        pos_count = sum(1 for s in sentiments if s['情感得分'] > 0)
        neg_count = sum(1 for s in sentiments if s['情感得分'] < 0)
        neu_count = sum(1 for s in sentiments if s['情感得分'] == 0)
        
        print(f"\n📈 情感统计 (分析{len(sentiments)}条新闻):")
        print("-" * 80)
        print(f"   🟢 积极: {pos_count}条 ({pos_count/len(sentiments)*100:.1f}%)")
        print(f"   🔴 消极: {neg_count}条 ({neg_count/len(sentiments)*100:.1f}%)")
        print(f"   ➡️ 中性: {neu_count}条 ({neu_count/len(sentiments)*100:.1f}%)")
        
        # 整体判断
        if pos_count > neg_count * 2:
            overall = "🟢🟢🟢 强烈积极"
        elif pos_count > neg_count:
            overall = "🟢🟢 积极偏多"
        elif neg_count > pos_count * 2:
            overall = "🔴🔴🔴 强烈消极"
        elif neg_count > pos_count:
            overall = "🔴🔴 消极偏多"
        else:
            overall = "➡️ 情绪中性"
        
        print(f"\n💡 整体情绪: {overall}")
        
        # 具体新闻
        print("\n📰 详细分析:")
        print("-" * 80)
        for s in sentiments[:10]:
            print(f"\n{s['情感标签']} 得分:{s['情感得分']:+d}")
            print(f"   {s['标题']}")
            print(f"   来源: {s['来源']} | 时间: {s['时间']}")
    else:
        print("未获取到数据")
    
    print("\n" + "=" * 80)

def show_usage():
    """显示用法"""
    print("\n📋 用法:")
    print("   python news_sentiment.py <股票代码>")
    print("\n示例:")
    print("   python news_sentiment.py 600519")
    print("   python news_sentiment.py 300750")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        stock = sys.argv[1]
        format_sentiment_report(stock)
    else:
        format_sentiment_report("600519")
        show_usage()
