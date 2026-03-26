# FinClaw × 外部 Skills 集成指南

## 方案一：数据增强层

### 集成架构

```
FinClaw/
├── skills/
│   ├── akshare-stock/      # A股数据（已有）
│   ├── akshare-fund/       # 基金数据（已有）
│   ├── yfinance-global/    # 全球数据（已有）
│   └── external/           # 外部集成Skills（新增）
│       ├── stock-analysis/     # 美股/加密货币
│       ├── tavily-web-search/  # 智能搜索
│       ├── summarize/          # 内容摘要
│       └── firecrawl-search/   # 网页爬取
```

---

## 🎯 使用场景与示例

### 场景1：全球资产配置分析

**需求**: 用户持有A股+美股+加密货币，需要统一分析

```bash
# 1. A股部分（FinClaw原生）
cd skills/akshare-stock/scripts
python stock_quote_tx.py 600519    # 茅台

# 2. 美股部分（外部Skill）
stock-analysis --ticker AAPL,MSFT,TSLA --portfolio us_stocks

# 3. 加密货币部分（外部Skill）
stock-analysis --crypto BTC,ETH,SOL --portfolio crypto

# 4. 综合报告
finclaw-portfolio --combine china,us,crypto --output report.pdf
```

---

### 场景2：研报自动搜集与摘要

**需求**: 自动搜集最新研报并生成摘要

```bash
# 1. 搜索最新研报（外部Skill）
tavily-search "茅台 研报 2025 业绩预测" --limit 10 --format json > reports.json

# 2. 下载研报PDF（外部Skill）
firecrawl-search --url-list reports.json --download --output ./reports/

# 3. 生成摘要（外部Skill）
for pdf in ./reports/*.pdf; do
    summarize --file "$pdf" --output "${pdf%.pdf}_summary.txt"
done

# 4. 整合分析（FinClaw Agent）
node finclaw.js research --summaries ./reports/*_summary.txt
```

---

### 场景3：财经新闻实时监控

**需求**: 监控特定股票的最新新闻并预警

```bash
# 1. 设置监控关键词
KEYWORDS="宁德时代 锂电池 订单"

# 2. 定时搜索（外部Skill）
tavily-search "$KEYWORDS" --freshness day --limit 5 > news_today.json

# 3. 摘要提取（外部Skill）
summarize --json news_today.json --output news_summary.md

# 4. 情绪分析（FinClaw原生）
cd skills/sentiment-xueqiu/scripts
python sentiment_analyze.py --text news_summary.md

# 5. 触发预警（如果负面）
node finclaw.js alert --condition "sentiment < -0.5"
```

---

### 场景4：竞争对手动态监控

**需求**: 监控竞争对手的官网动态、新闻、财报

```bash
# 1. 爬取对手官网（外部Skill）
firecrawl-search --urls "https://competitor1.com/news" \
                 --urls "https://competitor2.com/press" \
                 --schedule daily \
                 --output ./competitor/

# 2. 提取关键信息（外部Skill）
summarize --dir ./competitor/ --pattern "产品|财报|合作" > intel.txt

# 3. 生成竞争分析报告（FinClaw Agent）
node finclaw.js competitor --data intel.txt --company "竞争对手"
```

---

## ⚙️ 配置文件

创建 `external/.env` 配置API密钥：

```bash
# Tavily API (免费版每月1000次)
TAVILY_API_KEY=tvly-your-key

# Firecrawl API
FIRECRAWL_API_KEY=fc-your-key

# Stock Analysis (通常免费)
YAHOO_FINANCE_ENABLED=true
```

---

## 🔗 与 FinClaw Agent 集成

修改 `finclaw/agents/` 中的Agent，添加外部Skill调用：

### 示例：research-agent.js 增强

```javascript
// 原有代码：获取A股数据
const chinaData = await getChinaStockData(code);

// 新增：获取美股数据（外部Skill）
const usData = await execSkill('stock-analysis', ['--ticker', code, '--json']);

// 新增：搜索相关新闻（外部Skill）
const news = await execSkill('tavily-search', [code, '--limit', '5']);

// 新增：生成摘要（外部Skill）
const summary = await execSkill('summarize', ['--text', news, '--max-length', '200']);

// 整合输出
return {
    china: chinaData,
    us: usData,
    news: summary
};
```

---

## 📊 数据流图

```
用户请求
    ↓
FinClaw Router
    ↓
┌─────────────────┬─────────────────┐
↓                 ↓                 ↓
A股 Skills    美股/加密 Skills    搜索/摘要 Skills
(AkShare)     (Stock Analysis)   (Tavily/Summarize)
    ↓                 ↓                 ↓
    └─────────────────┴─────────────────┘
                      ↓
              FinClaw Agent 整合
                      ↓
              统一报告输出
```

---

## 🚀 快速开始

```bash
# 1. 进入外部Skills目录
cd finclaw/skills/external

# 2. 运行安装脚本
./install-scheme1.sh

# 3. 配置API密钥
cp .env.example .env
# 编辑 .env 填入你的密钥

# 4. 测试集成
./test-integration.sh
```

---

## 📈 效果对比

| 功能 | 集成前 | 集成后 |
|:---|:---|:---|
| 股票覆盖 | A股/港股 | A股/港股/**美股/加密货币** |
| 新闻获取 | 手动搜索 | **自动搜索+摘要** |
| 研报处理 | 手动下载 | **自动爬取+AI摘要** |
| 监控范围 | 价格/财务 | 价格/财务/**舆情/竞品** |

---

## 📝 下一步

- 方案二：投研工具链（Technical Analyst + Polymarket + YouTube Watcher）
- 方案三：基础设施（SQL Toolkit + Ontology + Proactive Agent）

---

## 方案二：投研工具链

### 集成的 Skills

| Skill | 下载量 | 功能 | 投研价值 |
|:---|:---:|:---|:---|
| **Technical Analyst** | 5.4k | 股票/加密货币技术分析工具 | 图表模式识别、趋势分析 |
| **Polymarket** | 4.8万 | 预测市场查询、赔率追踪 | 市场情绪指标、事件预期 |
| **YouTube Watcher** | 2.0万 | 抓取YouTube字幕、视频总结 | 财经视频快速消化 |

---

### 🎯 使用场景与示例

#### 场景5：AI图表模式识别

**需求**: 自动识别K线图中的技术形态

```bash
# 1. 生成股票K线图（FinClaw原生）
cd skills/akshare-stock/scripts
python stock_chart.py --code 600519 --period 6m --output moutai.png

# 2. AI识别图表模式（外部Skill）
technical-analyst --chart moutai.png \
    --patterns "head_and_shoulders,double_bottom,triangle,flag" \
    --confidence 0.8

# 3. 生成技术分析报告
finclaw.js tech-report --code 600519 --ai-patterns patterns.json
```

**输出示例**:
```json
{
  "patterns_found": [
    {"pattern": "ascending_triangle", "confidence": 0.87, "target_price": 1850},
    {"pattern": "bull_flag", "confidence": 0.72, "target_price": 1820}
  ],
  "recommendation": " bullish_breakout_expected"
}
```

---

#### 场景6：预测市场情绪监控

**需求**: 通过预测市场赔率判断宏观事件预期

```bash
# 1. 查询美联储降息概率
polymarket --market "fed-rate-cut-march-2025" --odds --history 30d

# 2. 查询重要政策事件
polymarket --search "China stimulus 2025" --volume --trending

# 3. 行业特定事件
polymarket --category crypto --market "bitcoin-etf-approval" --timeline

# 4. 生成市场情绪指数
python << 'PYEOF'
import json
# 计算Polymarket情绪得分
odds_data = json.load(open('polymarket_data.json'))
bullish_score = sum([m['yes_odds'] * m['volume'] for m in odds_data]) / sum([m['volume'] for m in odds_data])
print(f"预测市场情绪得分: {bullish_score:.2f}")
PYEOF

# 5. 整合到FinClaw监控
finclaw.js macro-sentiment --polymarket-score 0.65 --alert-threshold 0.3
```

**价值**: 传统舆情监控的补充，用真金白银押注的"真实预期"

---

#### 场景7：分析师视频观点提取

**需求**: 快速消化YouTube财经分析师视频

```bash
# 1. 获取视频字幕（外部Skill）
youtube-watcher --url "https://youtube.com/watch?v=analyst_review_2025" \
    --transcript --language zh,en \
    --output transcript.txt

# 2. 提取关键观点（外部Skill）
summarize --file transcript.txt \
    --extract "投资观点|推荐股票|目标价|风险提示" \
    --output key_points.md

# 3. 结构化分析
python << 'PYEOF'
import re

content = open('key_points.md').read()

# 提取推荐股票
tickers = re.findall(r'推荐[：:]?\s*([A-Z]{1,6})', content)
# 提取目标价
targets = re.findall(r'目标价[：:]?\s*(\d+)', content)
# 提取评级
ratings = re.findall(r'评级[：:]?\s*(买入|持有|卖出)', content)

print("分析师观点摘要:")
print(f"推荐标的: {tickers}")
print(f"目标价: {targets}")
print(f"评级: {ratings}")
PYEOF

# 4. 验证分析师历史准确率
finclaw.js analyst-track --name "分析师A" --history 1y

# 5. 生成观点对比报告
finclaw.js consensus --sources youtube_reviews --stock 600519
```

**适用**: 财报季分析师密集点评期

---

#### 场景8：产业链视频调研

**需求**: 通过行业专家视频了解产业链动态

```bash
# 1. 批量获取行业视频
for url in $(cat industry_videos.txt); do
    youtube-watcher --url "$url" --transcript --output "transcripts/$(basename $url).txt"
done

# 2. 提取产业链信息
cat transcripts/*.txt | summarize \
    --extract "上下游|产能|价格|订单|库存" \
    --output industry_intel.md

# 3. 与FinClaw产业链数据结合
cd skills/akshare-industry/scripts
python industry_chain.py --sector battery --output chain_data.json

# 4. 交叉验证
python << 'PYEOF'
# 对比视频调研数据与官方数据
video_intel = parse_intel('industry_intel.md')
official_data = json.load(open('chain_data.json'))

# 识别差异点
differences = compare_and_flag(video_intel, official_data)
print("⚠️  需要进一步验证的信息:")
for diff in differences:
    print(f"  - {diff['item']}: 视频说{diff['video']}, 官方数据{diff['official']}")
PYEOF

# 5. 生成调研报告
finclaw.js research --type industry --data merged_intel.json
```

**适用**: 新兴行业（如固态电池、人形机器人）的快速调研

---

## ⚙️ 配置

### Technical Analyst
```bash
# 通常无需API Key
# 可选：配置深度学习模型
TECH_ANALYST_MODEL=advanced  # basic|advanced
TECH_ANALYST_CONFIDENCE=0.75  # 最小置信度
```

### Polymarket
```bash
# 无需API Key，数据公开
# 可选：配置关注的分类
POLYMARKET_WATCHLIST="crypto,politics,finance"
POLYMARKET_ALERT_VOLUME=100000  # 交易量阈值
```

### YouTube Watcher
```bash
# 需要YouTube API Key（免费额度足够）
YOUTUBE_API_KEY=your-api-key
# 或无需Key但功能受限
YOUTUBE_API_KEY=none
```

---

## 🔗 与FinClaw Agent集成

### research-agent.js 增强

```javascript
// 原有：基本面分析
const fundamental = await analyzeFundamentals(code);

// 新增：AI图表分析
const chartPath = await generateChart(code, '6m');
const aiPatterns = await execSkill('technical-analyst', [
    '--chart', chartPath,
    '--patterns', 'all',
    '--json'
]);

// 新增：市场情绪
const marketSentiment = await execSkill('polymarket', [
    '--search', code,
    '--category', 'finance',
    '--odds'
]);

// 整合报告
return {
    ...fundamental,
    technical: {
        patterns: aiPatterns,
        chart: chartPath
    },
    sentiment: marketSentiment
};
```

---

## 📊 数据流图

```
┌─────────────────────────────────────────────────────────────┐
│                        投研工作流程                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │ K线图生成    │───→│ AI模式识别   │───→│ 技术信号     │  │
│  │ (FinClaw)    │    │ (Tech Analyst)│    │ 生成         │  │
│  └──────────────┘    └──────────────┘    └──────┬───────┘  │
│                                                  │          │
│  ┌──────────────┐    ┌──────────────┐           │          │
│  │ 预测市场     │───→│ 情绪指标     │───────────┤          │
│  │ (Polymarket) │    │ 计算         │           │          │
│  └──────────────┘    └──────────────┘           │          │
│                                                  ↓          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │ 视频抓取     │───→│ 观点提取     │───→│ 分析师共识   │  │
│  │ (YouTube)    │    │ (Summarize)  │    │ 生成         │  │
│  └──────────────┘    └──────────────┘    └──────┬───────┘  │
│                                                  │          │
│                                                  ↓          │
│                                         ┌──────────────┐   │
│                                         │ 综合投研报告 │   │
│                                         │ (FinClaw)    │   │
│                                         └──────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 快速开始

```bash
# 1. 安装方案二技能
cd finclaw/skills/external
./install-scheme2.sh

# 2. 配置（可选）
echo "YOUTUBE_API_KEY=your-key" >> .env

# 3. 测试
# 技术分析师
finclaw.js chart 600519 --output chart.png
technical-analyst --chart chart.png

# 预测市场情绪
polymarket --market "fed-rate-cut" --odds

# 视频分析
youtube-watcher --url "https://youtube.com/watch?v=xxx" --transcript | summarize
```

---

## 📈 效果对比

| 能力 | 方案一+二之前 | 方案一+二之后 |
|:---|:---|:---|
| 技术分析 | 指标计算 | 指标计算 + **AI图表模式识别** |
| 市场情绪 | 雪球/微博 | + **预测市场真金白银预期** |
| 信息来源 | 文字研报 | + **视频分析师观点** |
| 研究深度 | 量化数据 | + **AI辅助定性分析** |

---

## 📝 下一步

- 方案三：基础设施（SQL Toolkit + Ontology + Proactive Agent）

---

## 方案三：基础设施

### 集成的 Skills

| Skill | 下载量 | 功能 | 基础设施价值 |
|:---|:---:|:---|:---|
| **SQL Toolkit** | 6.4k | 数据库调试、备份、优化、查询 | 金融数据本地存储与管理 |
| **Ontology** | 9.1万 | 类型化知识图谱、实体关联 | 金融知识图谱构建 |
| **Proactive Agent** | 4.7万 | WAL协议、自主定时任务 | 任务调度与状态管理 |

---

### 🎯 使用场景与示例

#### 场景9：本地金融数据仓库搭建

**需求**: 建立本地金融数据库，支持高效查询和备份

```bash
# 1. 创建金融数据库（外部Skill）
sql-toolkit --create-database finclaw_db --type sqlite --path ./data/

# 2. 创建表结构
sql-toolkit --execute --database finclaw_db << 'SQL'
CREATE TABLE stock_quotes (
    code VARCHAR(10) PRIMARY KEY,
    name VARCHAR(50),
    price DECIMAL(10,2),
    change_pct DECIMAL(5,2),
    volume BIGINT,
    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE fund_nav (
    code VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100),
    nav DECIMAL(10,4),
    accum_nav DECIMAL(10,4),
    update_date DATE
);

CREATE TABLE macro_indicators (
    indicator VARCHAR(50) PRIMARY KEY,
    value DECIMAL(10,4),
    period VARCHAR(20),
    update_time TIMESTAMP
);
SQL

# 3. 从FinClaw导入数据
cd skills/akshare-stock/scripts
python stock_quote_tx.py 600519 --json | \
    sql-toolkit --import --database finclaw_db --table stock_quotes

# 4. 设置自动备份
sql-toolkit --schedule-backup \
    --database finclaw_db \
    --frequency daily \
    --time "02:00" \
    --retention 30

# 5. 查询示例
sql-toolkit --query --database finclaw_db "
SELECT * FROM stock_quotes 
WHERE change_pct > 5 
ORDER BY volume DESC 
LIMIT 20
"
```

**优势**:
- 避免重复调用API（节省配额）
- 本地查询速度快
- 历史数据可追溯
- 支持复杂SQL分析

---

#### 场景10：金融知识图谱构建

**需求**: 构建股票、行业、概念之间的关联知识图谱

```bash
# 1. 创建本体模型（外部Skill）
ontology --create-schema finance_kg --define '
{
  "entities": {
    "stock": {
      "properties": ["code", "name", "sector", "market_cap"],
      "relations": ["belongs_to", "competes_with", "supplies_to"]
    },
    "sector": {
      "properties": ["name", "index_code"],
      "relations": ["includes", "upstream_of", "downstream_of"]
    },
    "concept": {
      "properties": ["name", "hot_rank"],
      "relations": ["related_to"]
    },
    "fund": {
      "properties": ["code", "name", "manager", "scale"],
      "relations": ["holds", "invests_in"]
    }
  }
}'

# 2. 批量导入股票数据
for code in 600519 000858 002304 000568; do
    stock_info=$(python stock_quote_tx.py $code --json)
    ontology --create-entity stock \
        --id $code \
        --properties "$stock_info" \
        --schema finance_kg
done

# 3. 建立行业关联
ontology --create-relation \
    --from stock:600519 \
    --to sector:liquor \
    --type belongs_to

# 4. 建立竞争关系
ontology --create-relation \
    --from stock:600519 \
    --to stock:000858 \
    --type competes_with \
    --properties '{"similarity": 0.85}'

# 5. 查询产业链
ontology --query --schema finance_kg "
MATCH (s:stock)-[:supplies_to]->(:sector)-[:downstream_of]->(d:sector)
WHERE s.code = '300750'
RETURN d.name as downstream_sector
"

# 6. 推理潜在关联
ontology --infer --schema finance_kg \
    --type "共同供应商" \
    --entities stock:600519,stock:000858
```

**应用场景**:
- 产业链上下游分析
- 板块联动效应研究
- 基金持仓穿透分析
- 概念热点传导路径

---

#### 场景11：智能任务调度与状态管理

**需求**: 复杂的定时任务依赖管理和故障恢复

```bash
# 1. 创建任务工作流（外部Skill）
proactive-agent --create-workflow market_monitor \
    --definition '
{
  "tasks": [
    {
      "name": "pre_market_scan",
      "schedule": "0 8 * * 1-5",
      "command": "finclaw.js macro --market us,asia",
      "on_success": "market_alert_check",
      "on_failure": "notify_admin"
    },
    {
      "name": "market_alert_check",
      "command": "finclaw.js alert --run",
      "on_alert": "send_notification",
      "on_no_alert": "midday_update"
    },
    {
      "name": "midday_update",
      "schedule": "0 11,14 * * 1-5",
      "command": "finclaw.js market-midday",
      "parallel": ["fund_flow", "sector_rotation"]
    },
    {
      "name": "post_market",
      "schedule": "35 15 * * 1-5",
      "command": "finclaw.js lhb --daily",
      "dependencies": ["close_quotes_sync"]
    }
  ],
  "recovery": {
    "max_retries": 3,
    "retry_delay": "5m",
    "fallback": "manual_review"
  }
}'

# 2. 启用WAL（Write-Ahead Logging）
proactive-agent --enable-wal \
    --workflow market_monitor \
    --checkpoint-interval 1h

# 3. 任务状态查询
proactive-agent --status --workflow market_monitor

# 4. 手动触发
proactive-agent --trigger --workflow market_monitor --task pre_market_scan

# 5. 故障恢复（如果服务重启）
proactive-agent --recover --workflow market_monitor --from-checkpoint
```

**特性**:
- 任务依赖自动处理
- 失败自动重试
- 状态持久化（WAL）
- 故障后从断点恢复

---

#### 场景12：三位一体整合应用

**需求**: 数据库 + 知识图谱 + 智能调度 联合使用

```bash
# 场景：构建智能化的产业链监控系统

# 1. 初始化数据库（SQL Toolkit）
sql-toolkit --create-database supply_chain_db

# 2. 创建知识图谱本体（Ontology）
ontology --create-schema supply_chain --define '
{
  "entities": {
    "company": ["name", "sector", "market_cap"],
    "product": ["name", "category", "price"],
    "raw_material": ["name", "price_index"]
  },
  "relations": {
    "produces": ["company", "product", "capacity"],
    "consumes": ["company", "raw_material", "volume"],
    "supplies": ["company", "company", "material"]
  }
}'

# 3. 设置定时任务（Proactive Agent）
proactive-agent --create-workflow supply_chain_monitor --definition '
{
  "schedule": "0 */4 * * *",
  "steps": [
    {
      "name": "fetch_data",
      "action": "scrape_supply_chain_data",
      "output": "raw_data"
    },
    {
      "name": "update_database",
      "action": "sql-toolkit --import",
      "input": "raw_data",
      "output": "db_status"
    },
    {
      "name": "update_knowledge_graph",
      "action": "ontology --batch-update",
      "input": "raw_data",
      "condition": "db_status == success"
    },
    {
      "name": "detect_anomalies",
      "action": "analyze_price_changes",
      "output": "alerts"
    },
    {
      "name": "generate_report",
      "action": "finclaw.js report --supply-chain",
      "input": "alerts",
      "output": "report.pdf"
    }
  ],
  "wal": true,
  "notification": "feishu://kimi-claw"
}'

# 4. 启动监控
proactive-agent --start --workflow supply_chain_monitor

# 5. 查询知识图谱获取洞察
ontology --query --schema supply_chain "
MATCH (c:company)-[:supplies]->(t:company)
WHERE c.sector = '锂矿' AND t.sector = '电池'
RETURN c.name, t.name, 
       avg_price_change(c, 7d) as supplier_impact,
       avg_price_change(t, 7d) as downstream_impact
ORDER BY supplier_impact DESC
"

# 6. 保存到数据库供后续分析
sql-toolkit --execute --database supply_chain_db "
INSERT INTO price_alerts (date, supplier, downstream, correlation)
VALUES (CURRENT_DATE, 'supplier_A', 'battery_B', 0.85)
"
```

**价值**:
- 数据存储结构化
- 知识关联可视化
- 任务执行自动化
- 故障恢复可靠化

---

## ⚙️ 配置

### SQL Toolkit
```bash
# 数据库配置
SQL_TOOLKIT_DEFAULT_DB=sqlite  # sqlite|postgres|mysql
SQL_TOOLKIT_BACKUP_DIR=./backups
SQL_TOOLKIT_QUERY_TIMEOUT=30s
```

### Ontology
```bash
# 知识图谱配置
ONTOLOGY_DEFAULT_SCHEMA=finance_kg
ONTOLOGY_STORAGE=graphdb  # graphdb|neo4j|memory
ONTOLOGY_INFERENCE=true   # 启用推理引擎
```

### Proactive Agent
```bash
# 任务调度配置
PROACTIVE_WAL_DIR=./wal
PROACTIVE_CHECKPOINT_INTERVAL=1h
PROACTIVE_MAX_RETRIES=3
PROACTIVE_NOTIFICATION_CHANNEL=feishu
```

---

## 📊 三位一体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    FinClaw 基础设施层                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Proactive Agent (调度层)                │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │   │
│  │  │ 定时任务    │  │ 依赖管理    │  │ 故障恢复    │  │   │
│  │  │ Schedule    │  │ Dependency  │  │ Recovery    │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  │   │
│  │  ┌─────────────────────────────────────────────────┐  │   │
│  │  │         WAL (Write-Ahead Logging)               │  │   │
│  │  └─────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────┘   │
│                           │                                 │
│           ┌───────────────┼───────────────┐                 │
│           ▼               ▼               ▼                 │
│  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐    │
│  │  SQL Toolkit  │ │   Ontology    │ │   FinClaw     │    │
│  │   (数据层)    │ │  (知识层)     │ │   (业务层)    │    │
│  │               │ │               │ │               │    │
│  │  stock_quotes │ │  股票实体     │ │  股票分析     │    │
│  │  fund_nav     │ │  行业关联     │ │  基金研究     │    │
│  │  macro_data   │ │  概念图谱     │ │  宏观监控     │    │
│  └───────────────┘ └───────────────┘ └───────────────┘    │
│           │               │               │                 │
│           └───────────────┴───────────────┘                 │
│                           │                                 │
│                           ▼                                 │
│                  ┌─────────────────┐                        │
│                  │   统一输出层    │                        │
│                  │  CLI/Web/消息   │                        │
│                  └─────────────────┘                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 快速开始

```bash
# 1. 安装方案三技能
cd finclaw/skills/external
./install-scheme3.sh

# 2. 配置
echo "SQL_TOOLKIT_DEFAULT_DB=sqlite" >> .env

# 3. 初始化数据库
sql-toolkit --create-database finclaw_db

# 4. 创建知识图谱
ontology --create-schema finance_kg --load-defaults

# 5. 启动智能监控
proactive-agent --create-workflow market_monitor --from-file workflow.json
proactive-agent --start --workflow market_monitor
```

---

## 📈 三大方案完整能力

| 能力维度 | 方案一 | 方案二 | 方案三 | 合计 |
|:---|:---:|:---:|:---:|:---:|
| **数据获取** | 美股/加密货币/搜索/摘要/爬取 | AI图表/预测市场/视频 | 本地数据库 | 全渠道覆盖 |
| **分析能力** | 全球资产 | 技术形态/市场情绪 | 知识图谱推理 | 多维度分析 |
| **信息来源** | 网页/研报 | 视频/预测市场 | 结构化数据 | 全类型覆盖 |
| **基础设施** | - | - | 数据库/图谱/调度 | 企业级架构 |

**总计**: 10个外部 Skills + 50个原生 Skills = **60个 Skills** 生态

---

## 🎉 集成完成

所有三个方案已完成集成：
- ✅ 方案一：数据增强层（4个Skills）
- ✅ 方案二：投研工具链（3个Skills）
- ✅ 方案三：基础设施（3个Skills）

详细文档：`external/INTEGRATION.md`
