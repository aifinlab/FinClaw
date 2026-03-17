# Backtrader 策略回测 Skill

基于 Backtrader 的量化策略回测框架。

## 依赖
- **Backtrader**: https://www.backtrader.com
- **AkShare**: 数据获取

## 核心功能

| 脚本 | 功能 | 命令 |
|:---|:---|:---|
| `backtest_sma.py` | 双均线策略 | `python backtest_sma.py 600519` |
| `backtest_macd.py` | MACD策略 | `python backtest_macd.py 600519` |
| `backtest_boll.py` | 布林带策略 | `python backtest_boll.py 600519` |
| `backtest_report.py` | 绩效分析 | `python backtest_report.py` |

## 绩效指标

| 指标 | 说明 |
|:---|:---|
| 总收益率 | 策略总收益 |
| 年化收益率 | 年化后的收益率 |
| 夏普比率 | 风险调整收益 |
| 最大回撤 | 最大亏损幅度 |
| 胜率 | 盈利交易占比 |

## 快速开始

```bash
# 安装依赖
pip install backtrader akshare

# 双均线回测
python scripts/backtest_sma.py 600519

# MACD回测
python scripts/backtest_macd.py 600519

# 绩效报告
python scripts/backtest_report.py
```

## 许可证
MIT
