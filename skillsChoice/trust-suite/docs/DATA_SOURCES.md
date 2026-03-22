# 信托数据对接层设计

## 数据源优先级

| 优先级 | 数据源 | 数据类型 | 获取方式 | 需要授权 |
|:---:|:---|:---|:---:|:---:|
| 1 | AkShare | 信托发行、收益率、基础统计 | API调用 | 否 |
| 2 | 用益信托网 | 产品详情、收益率排行 | 爬虫抓取 | 否 |
| 3 | **同花顺iFinD API** | 深度数据（财务、行业指数、公司行情） | API调用 | **是** |
| 4 | 中国信托登记 | 行业统计数据 | 公开报告解析 | 否 |

## 同花顺iFinD API

### 接入方式
- **接口类型**: REST API
- **认证方式**: Bearer Token
- **Base URL**: `https://ft.10jqka.com.cn/api/v1`
- **需要的Token**: THS_ACCESS_TOKEN

### 可用接口
- `real_time_quotation` - 实时行情
- `basic_data_service` - 财务数据
- `date_sequence` - 历史序列数据
- `edb_service` - 经济数据库

### 信托相关数据
- 信托母上市公司财务数据（ROE、净利润等）
- 多元金融板块指数（信托行业代理）
- 头部信托公司股价行情

### 配置方式
```bash
export THS_ACCESS_TOKEN="your_token_here"
```

## 数据分类

### 1. 产品数据
- 信托产品基本信息
- 收益率数据
- 发行规模
- 期限结构

### 2. 市场数据
- 行业发行统计
- 收益率走势
- 产品类型分布
- 区域分布

### 3. 机构数据
- 信托公司排名
- 管理规模
- 产品发行能力

## 统一接口设计

```python
class TrustDataProvider:
    def get_products(filters) -> List[TrustProduct]
    def get_yield_curve() -> DataFrame
    def get_issuance_stats() -> Dict
    def get_company_rankings() -> DataFrame
    def get_market_overview() -> Dict
```
