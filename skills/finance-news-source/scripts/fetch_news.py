#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Finance News Pro - 财经新闻抓取核心脚本
从多个财经源抓取实时新闻，输出结构化 JSON
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import re


# ============== 数据源配置 ==============

SOURCES = {
    # 快讯类（实时）
    "cls": {
        "name": "财联社",
        "url": "https://www.cls.cn/telegraph",
        "type": "fast",
        "cache_minutes": 5
    },
    "wallstreet": {
        "name": "华尔街见闻",
        "url": "https://www.wallstreetcn.com/live",
        "type": "fast",
        "cache_minutes": 5
    },
    "eastmoney": {
        "name": "东方财富",
        "url": "https://news.eastmoney.com/kx/",
        "type": "fast",
        "cache_minutes": 10
    },
    "xueqiu": {
        "name": "雪球",
        "url": "https://xueqiu.com/hots",
        "type": "fast",
        "cache_minutes": 10
    },
    
    # 深度类（分析）
    "caixin": {
        "name": "财新",
        "url": "https://www.caixin.com/",
        "type": "deep",
        "cache_minutes": 60
    },
    "yicai": {
        "name": "第一财经",
        "url": "https://www.yicai.com/",
        "type": "deep",
        "cache_minutes": 60
    },
    "jiemian": {
        "name": "界面新闻",
        "url": "https://www.jiemian.com/",
        "type": "deep",
        "cache_minutes": 60
    },
    "latepost": {
        "name": "晚点 LatePost",
        "url": "https://www.postlate.cn/",
        "type": "deep",
        "cache_minutes": 120
    },
    
    # 宏观/政策
    "pbc": {
        "name": "央行官网",
        "url": "http://www.pbc.gov.cn/",
        "type": "policy",
        "cache_minutes": 1440
    },
    "csrc": {
        "name": "证监会",
        "url": "http://www.csrc.gov.cn/",
        "type": "policy",
        "cache_minutes": 1440
    },
    
    # 港美股
    "futunn": {
        "name": "富途牛牛",
        "url": "https://www.futunn.com/learn",
        "type": "us_hk",
        "cache_minutes": 30
    },
    "seekingalpha": {
        "name": "Seeking Alpha",
        "url": "https://seekingalpha.com/",
        "type": "us_hk",
        "cache_minutes": 30
    }
}


# ============== 个股映射表 ==============

STOCK_MAPPING = {
    # A 股
    "宁德时代": {"code": "300750.SZ", "market": "A", "sector": "新能源"},
    "比亚迪": {"code": "002594.SZ", "market": "A", "sector": "新能源"},
    "贵州茅台": {"code": "600519.SH", "market": "A", "sector": "消费"},
    "五粮液": {"code": "000858.SZ", "market": "A", "sector": "消费"},
    "招商银行": {"code": "600036.SH", "market": "A", "sector": "金融"},
    "工商银行": {"code": "601398.SH", "market": "A", "sector": "金融"},
    "平安银行": {"code": "000001.SZ", "market": "A", "sector": "金融"},
    "中国平安": {"code": "601318.SH", "market": "A", "sector": "金融"},
    "中信证券": {"code": "600030.SH", "market": "A", "sector": "金融"},
    "东方财富": {"code": "300059.SZ", "market": "A", "sector": "金融"},
    "隆基绿能": {"code": "601012.SH", "market": "A", "sector": "新能源"},
    "阳光电源": {"code": "300274.SZ", "market": "A", "sector": "新能源"},
    "迈瑞医疗": {"code": "300760.SZ", "market": "A", "sector": "医疗"},
    "恒瑞医药": {"code": "600276.SH", "market": "A", "sector": "医疗"},
    "药明康德": {"code": "603259.SH", "market": "A", "sector": "医疗"},
    "中芯国际": {"code": "688981.SH", "market": "A", "sector": "芯片"},
    "海康威视": {"code": "002415.SZ", "market": "A", "sector": "科技"},
    "立讯精密": {"code": "002475.SZ", "market": "A", "sector": "科技"},
    "工业富联": {"code": "601138.SH", "market": "A", "sector": "科技"},
    "中科曙光": {"code": "603019.SH", "market": "A", "sector": "算力"},
    "浪潮信息": {"code": "000977.SZ", "market": "A", "sector": "算力"},
    
    # 港股
    "腾讯": {"code": "0700.HK", "market": "HK", "sector": "科技"},
    "腾讯控股": {"code": "0700.HK", "market": "HK", "sector": "科技"},
    "阿里巴巴": {"code": "9988.HK", "market": "HK", "sector": "科技"},
    "美团": {"code": "3690.HK", "market": "HK", "sector": "科技"},
    "小米": {"code": "1810.HK", "market": "HK", "sector": "科技"},
    "小米集团": {"code": "1810.HK", "market": "HK", "sector": "科技"},
    "京东": {"code": "9618.HK", "market": "HK", "sector": "科技"},
    "百度": {"code": "9888.HK", "market": "HK", "sector": "科技"},
    "网易": {"code": "9999.HK", "market": "HK", "sector": "科技"},
    "快手": {"code": "1024.HK", "market": "HK", "sector": "科技"},
    "比亚迪股份": {"code": "1211.HK", "market": "HK", "sector": "新能源"},
    "理想汽车": {"code": "2015.HK", "market": "HK", "sector": "新能源"},
    "小鹏汽车": {"code": "9868.HK", "market": "HK", "sector": "新能源"},
    "蔚来": {"code": "9866.HK", "market": "HK", "sector": "新能源"},
    "汇丰控股": {"code": "0005.HK", "market": "HK", "sector": "金融"},
    "友邦保险": {"code": "1299.HK", "market": "HK", "sector": "金融"},
    "港交所": {"code": "0388.HK", "market": "HK", "sector": "金融"},
    
    # 美股
    "苹果": {"code": "AAPL", "market": "US", "sector": "科技"},
    "微软": {"code": "MSFT", "market": "US", "sector": "科技"},
    "谷歌": {"code": "GOOGL", "market": "US", "sector": "科技"},
    "亚马逊": {"code": "AMZN", "market": "US", "sector": "科技"},
    "英伟达": {"code": "NVDA", "market": "US", "sector": "芯片"},
    "特斯拉": {"code": "TSLA", "market": "US", "sector": "新能源"},
    "Meta": {"code": "META", "market": "US", "sector": "科技"},
    "脸书": {"code": "META", "market": "US", "sector": "科技"},
    "推特": {"code": "TWTR", "market": "US", "sector": "科技"},
    "X": {"code": "TWTR", "market": "US", "sector": "科技"},
    "英特尔": {"code": "INTC", "market": "US", "sector": "芯片"},
    "AMD": {"code": "AMD", "market": "US", "sector": "芯片"},
    "高通": {"code": "QCOM", "market": "US", "sector": "芯片"},
    "博通": {"code": "AVGO", "market": "US", "sector": "芯片"},
    "台积电": {"code": "TSM", "market": "US", "sector": "芯片"},
    "三星": {"code": "005930.KS", "market": "KR", "sector": "芯片"},
    "巴菲特": {"code": "BRK.A", "market": "US", "sector": "金融"},
    "伯克希尔": {"code": "BRK.A", "market": "US", "sector": "金融"},
    "高盛": {"code": "GS", "market": "US", "sector": "金融"},
    "摩根士丹利": {"code": "MS", "market": "US", "sector": "金融"},
    "摩根大通": {"code": "JPM", "market": "US", "sector": "金融"},
    "花旗": {"code": "C", "market": "US", "sector": "金融"},
    "美联储": {"code": "FED", "market": "US", "sector": "宏观"},
}


# ============== 情感分析关键词 ==============

POSITIVE_KEYWORDS = [
    "利好", "上涨", "突破", "超预期", "增长", "盈利", "收益", "分红",
    "回购", "增持", "签约", "订单", "合作", "获批", "通过", "获奖",
    "创新", "领先", "第一", "龙头", "垄断", "稀缺", "独家", "专利",
    "补贴", "扶持", "政策", "放宽", "松绑", "鼓励", "支持", "促进",
    "重组", "并购", "注入", "分拆", "上市", "IPO", "定增", "配股",
    "涨价", "提价", "供不应求", "产能", "扩张", "投产", "达产",
    "技术突破", "产品发布", "新品", "迭代", "升级", "优化", "效率提升"
]

NEGATIVE_KEYWORDS = [
    "利空", "下跌", "暴跌", "崩盘", "亏损", "暴雷", "违约", "退市",
    "减持", "质押", "冻结", "查封", "处罚", "调查", "立案", "问询",
    "诉讼", "纠纷", "仲裁", "赔偿", "罚款", "警告", "谴责", "黑名单",
    "限制", "禁令", "制裁", "打压", "收紧", "调控", "限购", "限产",
    "降价", "跌价", "滞销", "库存", "积压", "产能过剩", "供过于求",
    "裁员", "倒闭", "破产", "清算", "重组失败", "终止", "取消", "延期",
    "事故", "爆炸", "泄漏", "污染", "安全", "质量", "召回", "缺陷"
]


def generate_id(text: str) -> str:
    """生成新闻唯一 ID"""
    return hashlib.md5(text.encode()).hexdigest()[:12]


def extract_stocks(text: str) -> List[Dict]:
    """从文本中提取相关股票"""
    stocks = []
    seen = set()
    
    for name, info in STOCK_MAPPING.items():
        if name in text and info["code"] not in seen:
            stocks.append({
                "name": name,
                "code": info["code"],
                "market": info["market"],
                "sector": info["sector"]
            })
            seen.add(info["code"])
    
    return stocks


def analyze_sentiment(text: str) -> str:
    """分析新闻情感：利好/利空/中性"""
    text_lower = text.lower()
    
    positive_count = sum(1 for kw in POSITIVE_KEYWORDS if kw in text_lower)
    negative_count = sum(1 for kw in NEGATIVE_KEYWORDS if kw in text_lower)
    
    if positive_count > negative_count + 1:
        return "positive"
    elif negative_count > positive_count + 1:
        return "negative"
    else:
        return "neutral"


def assess_impact_level(text: str) -> str:
    """评估影响级别：市场级/行业级/公司级"""
    market_keywords = ["央行", "美联储", "财政部", "国务院", "GDP", "CPI", "利率", "降准", "降息", "战争", "贸易"]
    sector_keywords = ["行业", "板块", "产业", "新能源", "芯片", "科技", "金融", "地产", "消费", "医疗"]
    
    text_lower = text.lower()
    
    if any(kw in text_lower for kw in market_keywords):
        return "market"
    elif any(kw in text_lower for kw in sector_keywords):
        return "sector"
    else:
        return "company"


def get_operation_advice(sentiment: str, impact: str) -> str:
    """根据情感和影響给出操作建议"""
    if sentiment == "positive":
        if impact == "market":
            return "关注"
        elif impact == "sector":
            return "关注相关板块"
        else:
            return "关注"
    elif sentiment == "negative":
        if impact == "market":
            return "谨慎"
        elif impact == "sector":
            return "谨慎/回避"
        else:
            return "谨慎"
    else:
        return "观望"


def fetch_cls_news(browser, limit: int = 15) -> List[Dict]:
    """抓取财联社电报"""
    news_list = []
    
    # 这里使用浏览器工具抓取
    # 实际实现需要调用 browser 工具
    # 这里返回模拟数据结构
    
    return news_list


def fetch_wallstreet_news(browser, limit: int = 15) -> List[Dict]:
    """抓取华尔街见闻快讯"""
    news_list = []
    return news_list


def fetch_news(source: str, browser=None, limit: int = 15) -> List[Dict]:
    """
    抓取指定源新闻
    
    Args:
        source: 源 key
        browser: 浏览器实例
        limit: 最大数量
    
    Returns:
        新闻列表
    """
    if source not in SOURCES:
        print(f"未知源：{source}")
        return []
    
    source_info = SOURCES[source]
    
    # 根据源类型选择抓取函数
    if source == "cls":
        return fetch_cls_news(browser, limit)
    elif source == "wallstreet":
        return fetch_wallstreet_news(browser, limit)
    # ... 其他源
    
    return []


def process_news(news_list: List[Dict]) -> List[Dict]:
    """
    处理新闻：添加情感分析、股票关联等
    
    Args:
        news_list: 原始新闻列表
    
    Returns:
        处理后的新闻列表
    """
    processed = []
    
    for news in news_list:
        # 情感分析
        sentiment = analyze_sentiment(news.get("title", "") + news.get("content", ""))
        
        # 影响评估
        impact = assess_impact_level(news.get("title", "") + news.get("content", ""))
        
        # 股票关联
        stocks = extract_stocks(news.get("title", "") + news.get("content", ""))
        
        # 操作建议
        advice = get_operation_advice(sentiment, impact)
        
        processed.append({
            **news,
            "sentiment": sentiment,
            "impact_level": impact,
            "related_stocks": stocks,
            "operation_advice": advice
        })
    
    return processed


def save_to_cache(data: List[Dict], source: str, outdir: Path):
    """保存到缓存"""
    cache_dir = outdir / "cache" / datetime.now().strftime("%Y-%m-%d")
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    cache_file = cache_dir / f"{source}.json"
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"缓存已保存：{cache_file}")


def save_report(report: str, date: str, suffix: str, outdir: Path):
    """保存报告"""
    report_dir = outdir / "reports" / date[:7]
    report_dir.mkdir(parents=True, exist_ok=True)
    
    report_file = report_dir / f"{date}_{suffix}.md"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"报告已保存：{report_file}")
    return report_file


# ============== 主函数 ==============

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="财经新闻抓取")
    parser.add_argument("--source", type=str, default="all",
                       help="数据源，逗号分隔 (cls,wallstreet,eastmoney,...)")
    parser.add_argument("--limit", type=int, default=15,
                       help="每源最大新闻数")
    parser.add_argument("--keyword", type=str, default="",
                       help="关键词过滤")
    parser.add_argument("--market", type=str, default="",
                       help="市场过滤 (A,HK,US)")
    parser.add_argument("--outdir", type=str, default="finance-news",
                       help="输出目录")
    parser.add_argument("--no-save", action="store_true",
                       help="不保存到文件")
    
    args = parser.parse_args()
    
    # 确定数据源
    if args.source == "all":
        sources = list(SOURCES.keys())
    else:
        sources = [s.strip() for s in args.source.split(",")]
    
    print(f"数据源：{sources}")
    print(f"每源限制：{args.limit} 条")
    
    # 抓取新闻
    all_news = []
    for source in sources:
        print(f"\n正在抓取：{SOURCES.get(source, {}).get('name', source)}...")
        news = fetch_news(source, limit=args.limit)
        all_news.extend(news)
        print(f"  抓取到 {len(news)} 条")
    
    # 处理新闻
    print("\n正在分析情感、关联股票...")
    processed_news = process_news(all_news)
    
    # 关键词过滤
    if args.keyword:
        keywords = [k.strip() for k in args.keyword.split(",")]
        filtered = []
        for news in processed_news:
            text = news.get("title", "") + news.get("content", "")
            if any(kw in text for kw in keywords):
                filtered.append(news)
        processed_news = filtered
        print(f"关键词过滤后：{len(filtered)} 条")
    
    # 市场过滤
    if args.market:
        filtered = []
        for news in processed_news:
            stocks = news.get("related_stocks", [])
            if not stocks or any(s["market"] == args.market for s in stocks):
                filtered.append(news)
        processed_news = filtered
        print(f"市场过滤后：{len(filtered)} 条")
    
    # 输出
    print(f"\n总计：{len(processed_news)} 条新闻")
    
    if not args.no_save:
        outdir = Path(args.outdir)
        date = datetime.now().strftime("%Y-%m-%d")
        
        # 保存缓存
        for source in sources:
            source_news = [n for n in processed_news if n.get("source") == source]
            if source_news:
                save_to_cache(source_news, source, outdir)
        
        # 生成并保存报告
        report = generate_report(processed_news, date)
        report_file = save_report(report, date, "briefing", outdir)
    
    # 输出 JSON
    print("\n" + "="*50)
    print(json.dumps(processed_news, ensure_ascii=False, indent=2))


def generate_report(news_list: List[Dict], date: str) -> str:
    """生成 Markdown 报告"""
    report = []
    report.append(f"# 📈 财经简报 - {date} {datetime.now().strftime('%H:%M')}")
    report.append("")
    
    # 头条焦点
    report.append("## 🔥 头条焦点")
    report.append("")
    
    for i, news in enumerate(news_list[:5], 1):
        sentiment_icon = {"positive": "🟢", "negative": "🔴", "neutral": "⚪"}[news.get("sentiment", "neutral")]
        sentiment_text = {"positive": "利好", "negative": "利空", "neutral": "中性"}[news.get("sentiment", "neutral")]
        
        report.append(f"### {i}. [{news.get('title', '无标题')}]({news.get('url', '#')}) {sentiment_icon}{sentiment_text}")
        report.append(f"- **来源**: {news.get('source_name', '未知')} | **时间**: {news.get('time', '未知')}")
        report.append(f"- **影响**: {news.get('impact_level', '未知')}")
        
        if news.get("related_stocks"):
            stocks_str = ", ".join([f"{s['name']}({s['code']})" for s in news["related_stocks"][:3]])
            report.append(f"- **相关股票**: {stocks_str}")
        
        report.append(f"- **摘要**: {news.get('summary', news.get('title', '无'))}")
        report.append(f"- **操作建议**: {news.get('operation_advice', '观望')}")
        report.append("")
    
    # 市场情绪统计
    positive_count = sum(1 for n in news_list if n.get("sentiment") == "positive")
    negative_count = sum(1 for n in news_list if n.get("sentiment") == "negative")
    neutral_count = sum(1 for n in news_list if n.get("sentiment") == "neutral")
    
    total = len(news_list) or 1
    report.append("## 📊 市场情绪")
    report.append(f"- 整体情绪：{'偏多' if positive_count > negative_count else '偏空'} ({positive_count*100//total}% 利好)")
    report.append(f"- 利好：{positive_count} 条 | 利空：{negative_count} 条 | 中性：{neutral_count} 条")
    
    return "\n".join(report)


if __name__ == "__main__":
    main()
