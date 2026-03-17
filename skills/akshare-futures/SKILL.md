# AkShare 期货数据 Skill

基于 AkShare 的期货数据获取工具，覆盖商品期货、股指期货、持仓量、龙虎榜等。

## 数据源
- **AkShare**: https://www.akshare.xyz
- **新浪财经**: 实时行情
- **东方财富**: 历史数据

## 核心功能

| 脚本 | 功能 | 命令 |
|:---|:---|:---|
| `futures_quote.py` | 期货实时行情 | `python futures_quote.py RB0` |
| `futures_hist.py` | 期货历史数据 | `python futures_hist.py M0` |
| `futures_hold.py` | 持仓量龙虎榜 | `python futures_hold.py OI2501` |
| `futures_main.py` | 主力合约切换 | `python futures_main.py shfe` |
| `futures_board.py` | 期货板块监控 | `python futures_board.py` |
| `futures_spread.py` | 期现价差分析 | `python futures_spread.py RB` |
| `futures_global.py` | 外盘期货行情 | `python futures_global.py` |

## 支持的交易所

| 交易所 | 代码 | 主要品种 |
|:---|:---|:---|
| 上海期货交易所 | SHFE | 铜、铝、螺纹钢、黄金、原油 |
| 大连商品交易所 | DCE | 豆粕、铁矿石、棕榈油、玉米 |
| 郑州商品交易所 | ZCE | PTA、甲醇、白糖、棉花 |
| 中国金融期货交易所 | CFFEX | 沪深300、上证50、中证500、国债 |
| 上海国际能源交易中心 | INE | 原油期货 |

## 快速开始

```bash
# 安装依赖
pip install akshare pandas

# 获取螺纹钢主力行情
python scripts/futures_quote.py RB0

# 获取持仓龙虎榜
python scripts/futures_hold.py OI2501

# 获取期货板块监控
python scripts/futures_board.py
```

## 数据字段说明

### 实时行情
- `symbol`: 合约代码
- `name`: 合约名称
- `price`: 最新价
- `change`: 涨跌额
- `change_pct`: 涨跌幅(%)
- `volume`: 成交量
- `open_interest`: 持仓量

### 持仓龙虎榜
- `rank`: 排名
- `broker`: 期货公司
- `volume`: 成交量
- `volume_change`: 成交量增减
- `long_position`: 多头持仓
- `short_position`: 空头持仓

## 期现价差

监控期货价格与现货价格的价差，识别套利机会：
- **正价差**: 期货 > 现货（远期溢价）
- **逆价差**: 期货 < 现货（远期贴水）

## 许可证
MIT
