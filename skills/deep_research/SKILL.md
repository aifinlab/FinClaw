---
name: deep_research
display_name: 深度研究
description: 深度研究能力，支持多源搜索、信息聚合、引用回溯、文档上传分析。适用于市场调研、竞品分析、学术研究、技术选型、金融投研等场景。支持上传 PDF/Excel/Word 等文档，自动转换并提取关键信息。
version: 1.2.0
author: system
tags: [research, search, analysis, investigation, report, survey, 调研, 研究, 分析, browser, automation, 舆情, sentiment, 口碑, 金融, finance, 投研, 股票, stock, 财报, 行业分析, 估值, investment, document, pdf, excel, 文档, 上传, 微信, wechat, 公众号]
allowed_tools: [web_search, read_url, wechat_article, create_document, browser_open, browser_snapshot, browser_click, browser_fill, browser_screenshot, browser_close, file_converter, mem_retain, mem_delete, mem_summarize, mem_pin, mem_list_blocks]
max_iterations: 30
timeout: 600
enabled: true
match_threshold: 0.65
priority: 10
---

## 能力概述

深度研究能力让你能够系统性地调研某个主题，通过多源搜索、信息聚合、交叉验证，生成结构化的研究报告。

**核心特点**：
- 每个结论都标注来源引用，确保可追溯性
- 自动评估来源可信度
- 支持多维度拆解复杂主题
- 交叉验证关键数据
- **支持文档上传**: 自动转换 PDF/Excel/Word 等文件为 Markdown

## 工作流程

### Phase 0: 文档预处理（如有上传）
当用户上传文档时，优先处理：
1. 检测附件类型（PDF/Excel/Word/CSV 等）
2. 使用 `file_converter` 工具转换为 Markdown
3. 提取关键信息并注入 Context
4. 对于财报等结构化数据，自动识别关键指标

> 详见 L3 资源：`resources/document_upload_guide.md`

### Phase 1: 需求澄清
与用户确认研究主题、深度、范围：
- 主题是什么？
- 需要多深入？（概览 / 深度分析）
- 有无特定关注点？
- 输出格式偏好？

### Phase 2: 查询拆解
将主题拆解为多个搜索子查询，确保覆盖：
- **概述**：{topic} overview / 概述
- **市场/规模**：{topic} market size / 市场规模
- **关键玩家**：{topic} key players companies / 主要厂商
- **技术趋势**：{topic} trends 2024 / 发展趋势
- **挑战问题**：{topic} challenges problems / 面临挑战
- **案例研究**：{topic} case studies / 典型案例

### Phase 3: 并行搜索
对每个子查询执行 web_search：
- 每个维度至少获取 3-5 个来源
- 优先选择权威来源
- 记录搜索时间（时效性）

### Phase 4: 内容提取
对搜索结果中的高相关性页面调用 read_url：
- 只读取 Top 相关性页面（避免 Context 爆炸）
- 优先官方网站、权威媒体
- 对长文本先摘要再存储

### Phase 4.5: 浏览器自动化（按需）
当遇到以下情况时，切换到浏览器操作：
- 动态 SPA 应用（read_url 返回空白）
- 需要登录的平台
- 反爬虫保护的网站
- 需要滚动/交互加载的内容

浏览器工作流：
1. `browser_open` 打开目标页面
2. `browser_snapshot` 获取页面结构（compact模式）
3. 根据需要执行 `browser_click`/`browser_fill`
4. `browser_screenshot` 记录关键帧
5. 提取信息后 `browser_close` 释放资源

> 详见 L3 资源：`resources/browser_automation.md`

### Phase 5: 信息聚合
- 去重相同信息
- 识别共识与分歧
- 评估来源可信度
- 整理关键数据点

### Phase 6: 结构化输出
生成研究报告，标注引用

### Phase 7: 用户确认
询问是否需要深入某个方向

## 工具使用

### web_search
**用途**：搜索网页信息

**参数**：
- `query`: 搜索查询（精确、具体）
- `num_results`: 结果数量（建议 5-10）

**最佳实践**：
- 查询要具体，避免泛泛而谈
- 多个维度分别搜索，而非一次搜全部
- 优先使用英文搜索（信息更丰富）
- 对于中文主题，中英文各搜一次

**示例**：
```
web_search(query="AI Agent market size 2024", num_results=5)
web_search(query="AI Agent 市场规模 2024", num_results=5)
```

### read_url
**用途**：提取网页完整内容

**参数**：
- `url`: 目标 URL

**最佳实践**：
- 只读取搜索结果中的高相关性页面
- 优先选择官方网站、权威媒体
- 对于长文本（>2000字），先摘要再存储

**示例**：
```
read_url(url="https://example.com/article")
```

### wechat_article
**用途**：提取微信公众号文章内容

**参数**：
- `url`: 微信公众号文章链接 (mp.weixin.qq.com)
- `format`: 输出格式，"markdown" (默认) 或 "html"
- `include_images`: 是否包含图片引用 (默认 true)

**最佳实践**：
- 当用户提供微信公众号链接时，使用此工具而不是 read_url
- 微信文章通常无法通过通用爬虫抓取
- 输出为干净的 Markdown 格式

**示例**：
```python
wechat_article(url="https://mp.weixin.qq.com/s/xxxxx")
wechat_article(url="https://mp.weixin.qq.com/s/xxxxx", format="html")
```

### create_document
**用途**：创建研究报告

**参数**：
- `title`: 报告标题
- `content`: Markdown 格式内容
- `format`: 输出格式（markdown）

### file_converter
**用途**：将上传文件转换为 Markdown

**参数**：
- `file_path`: 文件路径（绝对或相对）
- `extract_images`: 是否提取图片描述（默认 false）

**支持格式**：
- **办公文档**: PDF, DOCX, PPTX, XLSX, XLS
- **结构化数据**: CSV, JSON, XML
- **文本**: TXT, MD, HTML
- **图片**: JPG, PNG (需 Vision LLM)
- **压缩包**: ZIP (递归处理)

**示例**：
```python
file_converter(file_path="/workspace/uploads/2024Q3_财报.xlsx")
file_converter(file_path="/workspace/uploads/行业报告_2024.pdf")
```

> 详见 L3 资源：`resources/document_upload_guide.md`

### browser_* 系列（浏览器自动化）

基于 agent-browser 的 Snapshot + Refs 机制，相比传统 Playwright 节省 93%+ tokens。

**browser_open**: 打开网页
```python
browser_open(url="https://example.com")
# 返回: {"title": "...", "url": "..."}
```

**browser_snapshot**: 获取页面结构快照（核心）
```python
browser_snapshot(interactive_only=True, compact=True)
# 返回压缩的 Markdown 格式，约 500-2000 tokens
# - @e1 [搜索框] type=input
# - @e2 [按钮] type=button
```

**browser_click**: 点击元素
```python
browser_click(ref="@e1")  # 使用 snapshot 返回的 Ref ID
```

**browser_fill**: 填充输入框
```python
browser_fill(ref="@e1", text="搜索关键词")
```

**browser_screenshot**: 截取关键帧
```python
browser_screenshot(path="/workspace/screenshots/step1.png")
```

**browser_close**: 关闭浏览器
```python
browser_close()
```

> 详细用法参见 L3 资源：`resources/browser_automation.md`

## 最佳实践

### 1. Read-then-Summarize
对于长文本（>2000字）：
1. 先用小模型摘要
2. 摘要放入 Context
3. 原文存储到文件系统

### 2. 引用回溯
每个关键结论必须标注引用：
- 格式：`[1]`、`[2]`
- 在文末列出完整引用信息
- 引用格式：`[编号] 标题 - 来源域名 (可信度)`

### 3. 来源可信度评分
| 来源类型 | 评分 |
|---------|------|
| 官方网站/政府机构 | ★★★★★ |
| 知名媒体/研究机构 | ★★★★ |
| 专业博客/技术文档 | ★★★ |
| 社交媒体/论坛 | ★★ |
| 未知来源 | ★ |

### 4. 交叉验证
- 关键数据至少 2 个来源确认
- 存在分歧时明确标注
- 不同来源的数据范围要说明

### 5. 时效性标注
- 注明搜索日期
- 对于快速变化的领域，提醒用户数据可能过时

## 输出格式

```markdown
# [研究主题] 深度研究报告

> 研究日期：YYYY-MM-DD
> 研究深度：[概览/深度分析]

## 摘要
3-5 句话概括核心发现，包含最重要的数据点。

## 目录
- 1. 概述
- 2. 市场规模与趋势
- 3. 主要玩家
- 4. 技术分析
- 5. 挑战与机遇
- 6. 结论与建议

## 1. 概述
简要介绍主题背景...[1]

## 2. 市场规模与趋势
### 2.1 市场规模
具体数据...[2][3]

### 2.2 增长趋势
分析内容...[4]

## 3. 主要玩家
| 公司 | 产品 | 特点 |
|------|------|------|
| ... | ... | ... |

## 4. 技术分析
技术细节...[5]

## 5. 挑战与机遇
### 5.1 主要挑战
- 挑战1...[6]
- 挑战2...

### 5.2 机遇
- 机遇1...

## 6. 结论与建议
总结性内容...

---

## 参考来源
[1] 标题 - example.com (★★★★)
[2] 标题 - research.org (★★★★★)
[3] 标题 - news.com (★★★★)
...

## 数据说明
- 本报告数据采集于 YYYY-MM-DD
- 部分数据存在来源差异，已在文中标注
- 对于快速变化的领域，建议定期更新
```

## 注意事项

1. **避免 Context 爆炸**
   - 不要一次性搜索太多 query
   - 长文本先摘要
   - 只提取关键信息入 Context

2. **语言策略**
   - 优先使用英文搜索（信息更丰富）
   - 对于中文主题，中英文各搜一次
   - 输出语言与用户输入保持一致

3. **时效性处理**
   - 对于时效性强的内容，注明搜索日期
   - 提醒用户数据可能变化

4. **不确定性处理**
   - 明确标注"据多个来源显示"/"部分来源认为"
   - 存在争议时两方观点都呈现
   - 避免过度断言

5. **隐私与版权**
   - 不搜索个人隐私信息
   - 引用内容要标注来源
   - 大段引用需注明"引自"
