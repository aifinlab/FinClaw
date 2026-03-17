# 外部集成 Skills

本目录包含从 SkillHub/ClawHub 集成的外部 Skills，与 FinClaw 核心功能形成互补。

## 方案一：数据增强层

### 1. Stock Analysis（美股/加密货币）
- **来源**: ClawHub
- **功能**: 雅虎财经深度分析、投资组合管理、预警盯盘
- **安装**: `clawhub install stock-analysis`

### 2. Tavily Web Search（智能搜索）
- **来源**: SkillHub
- **功能**: AI优化网络搜索，专为AI代理设计
- **安装**: `clawhub install tavily-web-search`

### 3. Summarize（内容摘要）
- **来源**: SkillHub  
- **功能**: 总结网页/PDF/图片/音频/视频
- **安装**: `clawhub install summarize`

### 4. Firecrawl Search（网页爬取）
- **来源**: SkillHub
- **功能**: 网页搜索、提取、抓取
- **安装**: `clawhub install firecrawl-search`

## 使用方法

```bash
# 安装所有方案一技能
./install-scheme1.sh

# 或单独安装
clawhub install stock-analysis
```

## 方案二：投研工具链

### 集成的 Skills

| Skill | 下载量 | 功能 | 投研价值 |
|:---|:---:|:---|:---|
| **Technical Analyst** | 5.4k | 股票/加密货币技术分析工具 | 图表模式识别、趋势分析 |
| **Polymarket** | 4.8万 | 预测市场查询、赔率追踪 | 市场情绪指标、事件预期 |
| **YouTube Watcher** | 2.0万 | 抓取YouTube字幕、视频总结 | 财经视频快速消化 |

### 使用场景

#### 场景1：技术分析增强
```bash
# 自动识别图表模式
technical-analyst --chart 600519.png --patterns "头肩顶,双底,三角形"

# 与FinClaw技术指标结合
finclaw.js tech 600519 --output chart.png
technical-analyst --chart chart.png --analysis detailed
```

#### 场景2：预测市场情绪
```bash
# 查询美联储降息预期
polymarket --topic "Fed Rate Cut 2025" --odds-change 7d

# 查询重要事件预期
polymarket --search "比特币ETF批准" --timeline

# 生成市场情绪报告
finclaw.js sentiment --polymarket-data market_odds.json
```

#### 场景3：财经视频速读
```bash
# 抓取分析师视频观点
youtube-watcher --url "https://youtube.com/watch?v=xxx" --transcript

# 生成视频摘要
summarize --video transcript.txt --output summary.md

# 提取投资观点
finclaw.js extract --text summary.md --type "investment_thesis"
```

### 安装
```bash
./install-scheme2.sh
```

## 方案三：基础设施

### 集成的 Skills

| Skill | 下载量 | 功能 | 基础设施价值 |
|:---|:---:|:---|:---|
| **SQL Toolkit** | 6.4k | 数据库调试、备份、优化、查询 | 金融数据本地存储与管理 |
| **Ontology** | 9.1万 | 类型化知识图谱、实体关联 | 金融知识图谱构建 |
| **Proactive Agent** | 4.7万 | WAL协议、自主定时任务 | 任务调度与状态管理 |

### 使用场景

#### 场景1：本地金融数据库管理
```bash
# 创建金融数据本地数据库
sql-toolkit --create-db finclaw_data

# 自动备份每日数据
sql-toolkit --backup --schedule daily --retention 30d

# 优化查询性能
sql-toolkit --optimize --table stock_quotes
```

#### 场景2：金融知识图谱构建
```bash
# 创建股票实体
ontology --create-entity stock --properties code,name,sector

# 建立关联关系
ontology --relate-stock-to-sector --stock 600519 --sector "白酒"
ontology --relate-competitor --stock1 600519 --stock2 000858

# 查询产业链
ontology --query "宁德时代上游供应商"
```

#### 场景3：智能任务调度
```bash
# 创建自主监控任务
proactive-agent --create-task "daily_market_scan" \
    --schedule "0 9 * * 1-5" \
    --action "finclaw.js macro"

# 状态持久化（WAL协议）
proactive-agent --enable-wal --task daily_market_scan
```

### 安装
```bash
./install-scheme3.sh
```
