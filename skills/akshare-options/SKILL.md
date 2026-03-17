# AkShare 期权数据 Skill

基于 AkShare 的期权数据获取工具，覆盖ETF期权、股指期权的行情、隐含波动率、希腊字母等。

## 数据源
- **AkShare**: https://www.akshare.xyz
- **上交所**: 50ETF/300ETF/500ETF期权
- **深交所**: 创业板ETF/深证100ETF期权
- **中金所**: 沪深300股指期权/中证1000股指期权

## 核心功能

| 脚本 | 功能 | 命令 |
|:---|:---|:---|
| `option_quote.py` | 期权行情数据 | `python option_quote.py 50ETF` |
| `option_volatility.py` | 隐含波动率分析 | `python option_volatility.py` |
| `option_greeks.py` | 希腊字母监控 | `python option_greeks.py` |
| `option_pcr.py` | PCR情绪指标 | `python option_pcr.py` |
| `option_chain.py` | 期权链分析 | `python option_chain.py 300ETF` |

## 支持的期权品种

| 品种 | 代码 | 交易所 |
|:---|:---|:---|
| 华夏上证50ETF期权 | 50ETF | 上交所 |
| 华泰柏瑞沪深300ETF期权 | 300ETF | 上交所 |
| 南方中证500ETF期权 | 500ETF | 上交所 |
| 华夏科创50ETF期权 | 科创板50 | 上交所 |
| 嘉实沪深300ETF期权 | 沪深300ETF | 深交所 |
| 创业板ETF期权 | 创业板ETF | 深交所 |
| 沪深300股指期权 | IO | 中金所 |
| 中证1000股指期权 | MO | 中金所 |

## 快速开始

```bash
# 安装依赖
pip install akshare pandas

# 获取50ETF期权行情
python scripts/option_quote.py 50ETF

# 获取隐含波动率
python scripts/option_volatility.py

# 获取PCR指标
python scripts/option_pcr.py
```

## 数据说明

### 隐含波动率(IV)
- 反映市场对未来波动率的预期
- IV高位：市场恐慌，期权价格贵
- IV低位：市场平静，期权价格便宜

### PCR(Put-Call Ratio)
- PCR > 1：看跌情绪浓厚，可能见底
- PCR < 0.7：看涨情绪浓厚，可能见顶

### 希腊字母
- Delta：标的价格变动对期权价格的影响
- Gamma：Delta的变化速度
- Theta：时间衰减
- Vega：波动率变化的影响

## 许可证
MIT
