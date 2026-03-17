---
name: akshare-relationship-anomaly
description: 用于基于AkShare数据的关联关系异常检测场景。适用于金融工作中的基础任务单元。
---

# AKShare A股关系网络异常识别 Skill

## Skill 名称
A股关系网络异常识别（a-share-relationship-network-anomaly）

## 数据来源
本 Skill 使用 AKShare 提供的 A 股公开数据接口构建“股票—营业部—高管/人员—公告事件”关系网络，并对关系网络中的异常活跃、异常聚集和异常共振进行识别。

当前实现主要使用以下 AKShare 接口（以 AKShare 官方文档为准）：

1. `stock_zh_a_spot_em`
   - 用途：获取 A 股股票列表与实时基础信息，用于初始化股票池。
2. `stock_zh_a_hist`
   - 用途：获取个股历史行情，用于计算收益率、振幅、成交量放大倍数、波动异常等市场行为特征。
3. `stock_lhb_detail_em`
   - 用途：获取龙虎榜明细数据，用于构建“股票—营业部”关系边，识别席位共现与异常集中。
4. `stock_lhb_stock_statistic_em`
   - 用途：获取个股龙虎榜统计信息，用于评估某只股票在观察窗口内的异常上榜频率。
5. `stock_share_hold_change_sse`
   - 用途：获取董监高及相关人员持股变动数据，用于构建“股票—人员”关系边，并识别异常窗口内的人员动作。
6. `stock_zh_a_disclosure_relation_cninfo`
   - 用途：获取信息披露调研/关系类公告，用于构建“股票—公告事件”关系边，辅助判断异常网络是否伴随公告密集披露。

> 说明：AKShare 官方中文文档提供股票数据接口总入口、数据字典与安装说明；AKShare 官方 GitHub 仓库采用 MIT License。citeturn249491search0turn249491search1turn648997search0turn648997search2turn648997search3

## 功能
本 Skill 面向 A 股“关系网络异常识别”场景，提供以下能力：

### 1. 构建多层关系网络
将以下实体建模为图网络中的节点：
- 股票节点
- 营业部节点
- 人员节点（董监高及相关人员）
- 公告事件节点

将以下关系建模为边：
- 股票 ↔ 营业部：来自龙虎榜席位明细
- 股票 ↔ 人员：来自董监高及相关人员持股变动
- 股票 ↔ 公告事件：来自信息披露调研/关系类公告

### 2. 识别四类异常

#### A. 营业部共现异常
若同一批营业部在较短窗口内反复出现在同一只或多只股票的龙虎榜中，则识别为“营业部共现异常”。

#### B. 网络扩散异常
若多个股票通过相同营业部形成高密度连边，且在窗口内同时出现价格/成交量异常，则识别为“网络扩散异常”。

#### C. 人员动作共振异常
若异常交易网络发生前后，相关股票伴随董监高及相关人员持股变动，则提高风险等级。

#### D. 公告密集共振异常
若异常网络窗口内同时出现调研/关系公告密集披露，则标记为“公告共振异常”。

### 3. 输出风险评分与解释
输出：
- 综合风险分数（0-100）
- 风险等级（低 / 中 / 高 / 极高）
- 异常标签列表
- 关键证据摘要
- 网络指标摘要（节点数、边数、度中心性、席位集中度等）

### 4. 生成可复核结果
Skill 支持导出：
- 风险明细 CSV
- 图边表 CSV
- 图节点表 CSV
- JSON 风险报告

## 使用示例

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 单股票扫描
```bash
python script/cli.py single \
  --symbol 000001 \
  --start-date 20250101 \
  --end-date 20250301 \
  --output-dir output/single_000001
```

### 3. 多股票扫描
```bash
python script/cli.py batch \
  --symbols 000001,600000,300750 \
  --start-date 20250101 \
  --end-date 20250301 \
  --output-dir output/batch_scan
```

### 4. 自动从 A 股股票池筛选后扫描
```bash
python script/cli.py universe \
  --limit 100 \
  --start-date 20250101 \
  --end-date 20250301 \
  --output-dir output/universe_scan
```

### 5. Python 调用
```python
from script.pipeline import run_single_symbol_scan

result = run_single_symbol_scan(
    symbol="000001",
    start_date="20250101",
    end_date="20250301",
    output_dir="output/demo"
)

print(result["risk_level"])
print(result["risk_score"])
print(result["signals"])
```

## 交易说明
1. 本 Skill 仅基于公开数据做关系网络异常识别，不构成买卖建议。
2. “异常”并不等于“违规”，仅表示该股票在观察窗口内出现了值得进一步研究的结构性信号。
3. 龙虎榜、公告、人员变动等数据存在发布时间差、缺失值或口径差异，实盘使用前应进行二次核验。
4. 建议将本 Skill 用作：
   - 风险排雷
   - 事件驱动研究辅助
   - 异常个股初筛
   - 合规/风控预警前置筛查
5. 不建议将单一分数直接作为自动交易触发条件，应与基本面、公告原文、盘口行为和成交结构联合判断。

## License
本 Skill 示例代码采用 MIT License 发布。

同时请注意：
- 上游数据接口库 AKShare 官方仓库采用 MIT License。citeturn648997search0turn648997search2
- 实际抓取到的数据来自各公开站点与交易所/资讯平台，其数据使用应遵守对应数据源网站条款与适用法律法规。citeturn249491search0turn249491search1
