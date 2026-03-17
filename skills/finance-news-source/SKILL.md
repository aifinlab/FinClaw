---
name: finance-news-source
description: "财经新闻数据源，聚合12+中文财经网站的实时快讯和深度报道。提供结构化新闻抓取能力，覆盖快讯（财联社/华尔街见闻/东方财富/雪球）、深度（财新/第一财经/界面/晚点）、宏观政策（央行/证监会/统计局）、港美股（富途/老虎/SeekingAlpha）四大类源。当其他 skill 需要财经新闻数据输入时（如 a-share-morning-note、finance-news-analysis），作为数据源调用。与 cn-stock-data（行情/财务数据）互补，本 skill 专注新闻资讯数据。"
---

# 财经新闻数据源

## 定位

finance-news-source 是金融数据源体系中专注**新闻资讯**的数据层 skill，与 cn-stock-data（行情/财务）互补。它聚合 12+ 财经网站，输出结构化新闻 JSON，供上层分析 skill（如 finance-news-analysis、a-share-morning-note）消费。

本 skill 只负责**抓取和结构化**，不做情感分析、影响评估等分析工作。

## 数据源一览

### 快讯类（实时，缓存 5-10 分钟）

| 源 key | 名称 | URL | 特点 |
|--------|------|-----|------|
| cls | 财联社 | https://www.cls.cn/telegraph | 7x24 电报，最快 |
| wallstreet | 华尔街见闻 | https://www.wallstreetcn.com/live | 宏观+市场 |
| eastmoney | 东方财富 | https://news.eastmoney.com/kx/ | A 股聚焦 |
| xueqiu | 雪球 | https://xueqiu.com/hots | 社区热点 |

### 深度类（分析，缓存 1-2 小时）

| 源 key | 名称 | URL | 特点 |
|--------|------|-----|------|
| caixin | 财新 | https://www.caixin.com/ | 深度调查 |
| yicai | 第一财经 | https://www.yicai.com/ | 产业分析 |
| jiemian | 界面新闻 | https://www.jiemian.com/ | 商业报道 |
| latepost | 晚点 LatePost | https://www.postlate.cn/ | 科技商业 |

### 宏观政策类（官方，缓存 24 小时）

| 源 key | 名称 | URL | 特点 |
|--------|------|-----|------|
| pbc | 央行官网 | http://www.pbc.gov.cn/ | 货币政策 |
| csrc | 证监会 | http://www.csrc.gov.cn/ | 监管动态 |
| stats | 国家统计局 | http://www.stats.gov.cn/ | 经济数据 |

### 港美股类（缓存 30 分钟）

| 源 key | 名称 | URL | 特点 |
|--------|------|-----|------|
| futunn | 富途牛牛 | https://www.futunn.com/learn | 港美股资讯 |
| tiger | 老虎证券 | https://www.tigerbrokers.com/ | 美股分析 |
| seekingalpha | Seeking Alpha | https://seekingalpha.com/ | 美股深度 |

## 脚本用法

```bash
SCRIPTS="$SKILLS_ROOT/finance-news-source/scripts"

# 抓取所有源（默认每源15条）
python "$SCRIPTS/fetch_news.py" --source all --limit 15

# 指定源（逗号分隔）
python "$SCRIPTS/fetch_news.py" --source cls,wallstreet,eastmoney

# 按市场过滤
python "$SCRIPTS/fetch_news.py" --market A   # A 股相关
python "$SCRIPTS/fetch_news.py" --market HK  # 港股相关
python "$SCRIPTS/fetch_news.py" --market US  # 美股相关

# 关键词过滤
python "$SCRIPTS/fetch_news.py" --keyword "AI,算力,英伟达"

# 只抓快讯源（最快）
python "$SCRIPTS/fetch_news.py" --source cls,wallstreet --limit 10

# 不保存到文件，只输出 JSON
python "$SCRIPTS/fetch_news.py" --source cls --no-save
```

## 输出格式（JSON）

```json
{
  "ok": true,
  "source": "cls",
  "source_name": "财联社",
  "fetch_time": "2026-03-15T14:30:00",
  "count": 15,
  "news": [
    {
      "id": "a1b2c3d4e5f6",
      "title": "央行降准0.25个百分点",
      "content": "中国人民银行决定...",
      "url": "https://www.cls.cn/detail/...",
      "source": "cls",
      "source_name": "财联社",
      "time": "14:15",
      "date": "2026-03-15",
      "type": "fast"
    }
  ]
}
```

每条新闻包含：id（哈希去重）、title、content、url、source、source_name、time、date、type（fast/deep/policy/us_hk）。

## 个股映射表

内置 60+ 常见股票的名称→代码映射（A股/港股/美股），存储在 `scripts/config.json` 的 `stocks` 字段中。用于从新闻文本中识别提及的股票。

调用方可通过 `extract_stocks(text)` 函数提取文本中出现的股票：

```python
from fetch_news import extract_stocks
stocks = extract_stocks("宁德时代发布新电池技术，比亚迪也在跟进")
# [{"name": "宁德时代", "code": "300750.SZ", "market": "A", "sector": "新能源"}, ...]
```

## 关键词扩展表

`scripts/config.json` 的 `keywords` 字段存储行业关键词的自动扩展规则：

```json
{
  "AI": ["AI", "LLM", "GPT", "大模型", "人工智能", "算力", "GPU"],
  "新能源": ["新能源", "电动车", "电池", "锂电", "光伏", "风电", "储能"],
  "芯片": ["芯片", "半导体", "CPU", "GPU", "光刻机", "封装"]
}
```

搜索 "AI" 会自动扩展为搜索所有相关词。

## 缓存策略

| 源类型 | 缓存时间 | 说明 |
|--------|----------|------|
| fast（快讯） | 5 分钟 | 时效性最强 |
| deep（深度） | 60 分钟 | 内容变化慢 |
| policy（政策） | 24 小时 | 官方公告更新不频繁 |
| us_hk（港美股） | 30 分钟 | 交易时段更新 |

缓存存储在 `finance-news/cache/YYYY-MM-DD/` 目录下。

## 抓取方式

优先级从高到低：

1. **WebFetch 工具**：直接抓取网页内容，提取新闻列表（推荐，无额外依赖）
2. **RSS Feed**：部分源提供 RSS（财联社、华尔街见闻）
3. **Python requests + BeautifulSoup**：需安装额外依赖

脚本中各源的抓取函数为桩代码，实际使用时由调用方（通常是 LLM）通过 WebFetch 工具直接抓取对应 URL，再交给脚本中的 `process_raw_news()` 进行结构化。

## 与其他数据源的关系

| 数据源 skill | 覆盖范围 | 关系 |
|-------------|----------|------|
| cn-stock-data | 行情、财务、资金流 | 互补，本 skill 覆盖新闻 |
| akshare-finance | 行情、基本面 | 互补 |
| efinance-data | 行情、龙虎榜 | 互补 |
| adata-source | 行情、北向资金 | 互补 |
| pysnowball-data | 跨市场行情 | 互补 |
| ashare-data | 轻量行情 | 互补 |

## 依赖

```bash
# 基础（标准库即可）
python --version  # 需要 3.8+

# 可选增强
pip install requests beautifulsoup4  # 如果需要 Python 直接抓取
```
