#!/usr/bin/env python3
"""
A股聪明钱/主力行为量化识别脚本
Smart Money Detector for A-Share Market

计算指标: 大单净流入占比、OBV、A/D Line、MFI
识别模式: 吸筹(accumulation)、出货(distribution)、洗盘(washout)、拉升(markup)

Usage:
    python smart_money_detector.py --flow flow.json --kline kline.json [--days 20]
"""

import argparse
import json
import sys
import numpy as np
import pandas as pd


def load_data(flow_path: str, kline_path: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """加载资金流向和K线 JSON 数据"""
    with open(flow_path, "r", encoding="utf-8") as f:
        flow_raw = json.load(f)
    with open(kline_path, "r", encoding="utf-8") as f:
        kline_raw = json.load(f)

    # 兼容 list 或 dict(带 data key) 格式
    if isinstance(flow_raw, dict):
        flow_raw = flow_raw.get("data", flow_raw.get("items", [flow_raw]))
    if isinstance(kline_raw, dict):
        kline_raw = kline_raw.get("data", kline_raw.get("items", [kline_raw]))

    flow_df = pd.DataFrame(flow_raw)
    kline_df = pd.DataFrame(kline_raw)

    # 统一日期列名
    for col in ["date", "trade_date", "日期"]:
        if col in flow_df.columns:
            flow_df.rename(columns={col: "date"}, inplace=True)
            break
    for col in ["date", "trade_date", "日期"]:
        if col in kline_df.columns:
            kline_df.rename(columns={col: "date"}, inplace=True)
            break

    flow_df["date"] = pd.to_datetime(flow_df["date"])
    kline_df["date"] = pd.to_datetime(kline_df["date"])

    return flow_df, kline_df


def calc_large_order_ratio(flow_df: pd.DataFrame) -> pd.Series:
    """计算大单净流入占比 (%)"""
    # 尝试多种字段名
    net_col = None
    for col in ["大单净流入", "large_net_inflow", "big_net_inflow", "主力净流入"]:
        if col in flow_df.columns:
            net_col = col
            break
    amount_col = None
    for col in ["总成交额", "total_amount", "amount", "成交额"]:
        if col in flow_df.columns:
            amount_col = col
            break

    if net_col is None or amount_col is None:
        # fallback: 返回全零
        return pd.Series(np.zeros(len(flow_df)), index=flow_df.index, name="large_order_ratio")

    net = pd.to_numeric(flow_df[net_col], errors="coerce").fillna(0)
    amt = pd.to_numeric(flow_df[amount_col], errors="coerce").replace(0, np.nan)
    ratio = (net / amt * 100).fillna(0)
    ratio.name = "large_order_ratio"
    return ratio


def calc_obv(kline_df: pd.DataFrame) -> pd.Series:
    """计算 OBV (On Balance Volume)"""
    close = pd.to_numeric(kline_df["close"], errors="coerce")
    volume = pd.to_numeric(kline_df["volume"], errors="coerce").fillna(0)

    direction = np.sign(close.diff()).fillna(0)
    obv = (direction * volume).cumsum()
    obv.name = "obv"
    return obv


def calc_ad_line(kline_df: pd.DataFrame) -> pd.Series:
    """计算 Accumulation/Distribution Line"""
    high = pd.to_numeric(kline_df["high"], errors="coerce")
    low = pd.to_numeric(kline_df["low"], errors="coerce")
    close = pd.to_numeric(kline_df["close"], errors="coerce")
    volume = pd.to_numeric(kline_df["volume"], errors="coerce").fillna(0)

    hl_range = high - low
    # 避免除零
    hl_range = hl_range.replace(0, np.nan)
    clv = ((close - low) - (high - close)) / hl_range
    clv = clv.fillna(0)
    ad = (clv * volume).cumsum()
    ad.name = "ad_line"
    return ad


def calc_mfi(kline_df: pd.DataFrame, period: int = 14) -> pd.Series:
    """计算 MFI (Money Flow Index)"""
    high = pd.to_numeric(kline_df["high"], errors="coerce")
    low = pd.to_numeric(kline_df["low"], errors="coerce")
    close = pd.to_numeric(kline_df["close"], errors="coerce")
    volume = pd.to_numeric(kline_df["volume"], errors="coerce").fillna(0)

    typical_price = (high + low + close) / 3
    raw_money_flow = typical_price * volume

    tp_diff = typical_price.diff()
    pos_flow = raw_money_flow.where(tp_diff > 0, 0)
    neg_flow = raw_money_flow.where(tp_diff < 0, 0)

    pos_sum = pos_flow.rolling(window=period, min_periods=1).sum()
    neg_sum = neg_flow.rolling(window=period, min_periods=1).sum()

    money_ratio = pos_sum / neg_sum.replace(0, np.nan)
    mfi = 100 - 100 / (1 + money_ratio)
    mfi = mfi.fillna(50)
    mfi.name = "mfi"
    return mfi


def detect_trend(series: pd.Series, window: int = 5) -> str:
    """判断序列趋势: rising / falling / flat"""
    if len(series) < window:
        return "flat"
    recent = series.tail(window).values
    slope = np.polyfit(range(len(recent)), recent, 1)[0]
    std = np.std(recent) if np.std(recent) > 0 else 1
    normalized = slope / std
    if normalized > 0.3:
        return "rising"
    elif normalized < -0.3:
        return "falling"
    return "flat"


def score_pattern(indicators: dict) -> dict:
    """
    根据多指标综合评分，识别主力行为模式
    返回: {pattern, confidence, scores, evidence}
    """
    scores = {
        "accumulation": 0.0,  # 吸筹
        "distribution": 0.0,  # 出货
        "washout": 0.0,       # 洗盘
        "markup": 0.0,        # 拉升
    }
    evidence = {k: [] for k in scores}

    price_trend = indicators["price_trend"]
    obv_trend = indicators["obv_trend"]
    ad_trend = indicators["ad_trend"]
    avg_ratio = indicators["avg_large_order_ratio"]
    latest_mfi = indicators["latest_mfi"]
    volume_trend = indicators["volume_trend"]
    ratio_trend = indicators["ratio_trend"]

    # --- 吸筹 accumulation ---
    if price_trend in ("flat", "falling") and obv_trend == "rising":
        scores["accumulation"] += 30
        evidence["accumulation"].append("OBV上升但价格未涨(量价背离)")
    if price_trend in ("flat", "falling") and ad_trend == "rising":
        scores["accumulation"] += 25
        evidence["accumulation"].append("AD线上升但价格横盘/下跌")
    if 0 < avg_ratio <= 5:
        scores["accumulation"] += 15
        evidence["accumulation"].append(f"大单温和净流入({avg_ratio:.1f}%)")
    if latest_mfi < 30:
        scores["accumulation"] += 15
        evidence["accumulation"].append(f"MFI低位({latest_mfi:.0f}),资金枯竭区")
    if volume_trend == "falling":
        scores["accumulation"] += 15
        evidence["accumulation"].append("成交量萎缩(筹码锁定)")

    # --- 出货 distribution ---
    if price_trend in ("flat", "rising") and obv_trend == "falling":
        scores["distribution"] += 30
        evidence["distribution"].append("OBV下降但价格未跌(顶部背离)")
    if price_trend in ("flat", "rising") and ad_trend == "falling":
        scores["distribution"] += 25
        evidence["distribution"].append("AD线下降但价格仍在高位")
    if avg_ratio < -2:
        scores["distribution"] += 20
        evidence["distribution"].append(f"大单持续净流出({avg_ratio:.1f}%)")
    if latest_mfi > 80:
        scores["distribution"] += 15
        evidence["distribution"].append(f"MFI高位({latest_mfi:.0f}),超买区")
    if volume_trend == "rising" and price_trend == "flat":
        scores["distribution"] += 10
        evidence["distribution"].append("高位放量滞涨")

    # --- 洗盘 washout ---
    if price_trend == "falling" and volume_trend == "falling":
        scores["washout"] += 25
        evidence["washout"].append("缩量下跌(抛压有限)")
    if price_trend == "falling" and obv_trend in ("flat", "rising"):
        scores["washout"] += 25
        evidence["washout"].append("价跌但OBV未明显下降")
    if -2 <= avg_ratio <= 2 and price_trend == "falling":
        scores["washout"] += 20
        evidence["washout"].append(f"下跌中大单流出占比小({avg_ratio:.1f}%)")
    if ratio_trend == "rising" and price_trend == "falling":
        scores["washout"] += 15
        evidence["washout"].append("价格下跌但大单占比回升")

    # --- 拉升 markup ---
    if price_trend == "rising" and volume_trend == "rising":
        scores["markup"] += 25
        evidence["markup"].append("量价齐升")
    if price_trend == "rising" and obv_trend == "rising":
        scores["markup"] += 20
        evidence["markup"].append("OBV同步上升,趋势确认")
    if avg_ratio > 5:
        scores["markup"] += 25
        evidence["markup"].append(f"大单强劲流入({avg_ratio:.1f}%)")
    if 50 < latest_mfi < 80:
        scores["markup"] += 10
        evidence["markup"].append(f"MFI适中({latest_mfi:.0f}),尚未超买")
    if ad_trend == "rising" and price_trend == "rising":
        scores["markup"] += 20
        evidence["markup"].append("AD线随价格同步上升")

    # 找到最高分模式
    best = max(scores, key=scores.get)
    max_score = scores[best]
    confidence = min(max_score, 100)

    # 如果最高分太低，判定为无明显模式
    if confidence < 20:
        best = "neutral"
        evidence["neutral"] = ["各项指标无明显方向性"]

    pattern_names = {
        "accumulation": "吸筹",
        "distribution": "出货",
        "washout": "洗盘",
        "markup": "拉升",
        "neutral": "无明显主力行为",
    }

    return {
        "pattern": best,
        "pattern_cn": pattern_names.get(best, best),
        "confidence": round(confidence, 1),
        "all_scores": {k: round(v, 1) for k, v in scores.items()},
        "evidence": evidence.get(best, []),
    }


def analyze(flow_df: pd.DataFrame, kline_df: pd.DataFrame, days: int = 20) -> dict:
    """主分析函数"""
    # 按日期排序并截取分析窗口
    kline_df = kline_df.sort_values("date").tail(days).reset_index(drop=True)
    flow_df = flow_df.sort_values("date").tail(days).reset_index(drop=True)

    # 计算指标
    large_ratio = calc_large_order_ratio(flow_df)
    obv = calc_obv(kline_df)
    ad = calc_ad_line(kline_df)
    mfi = calc_mfi(kline_df)

    close = pd.to_numeric(kline_df["close"], errors="coerce")
    volume = pd.to_numeric(kline_df["volume"], errors="coerce").fillna(0)

    # 趋势判断
    indicators = {
        "price_trend": detect_trend(close),
        "obv_trend": detect_trend(obv),
        "ad_trend": detect_trend(ad),
        "volume_trend": detect_trend(volume),
        "ratio_trend": detect_trend(large_ratio),
        "avg_large_order_ratio": float(large_ratio.mean()),
        "latest_mfi": float(mfi.iloc[-1]) if len(mfi) > 0 else 50.0,
    }

    # 模式识别
    result = score_pattern(indicators)

    # 汇总输出
    output = {
        "analysis_window": days,
        "data_points": len(kline_df),
        "indicators": {
            "large_order_ratio": {
                "mean": round(float(large_ratio.mean()), 2),
                "latest": round(float(large_ratio.iloc[-1]), 2) if len(large_ratio) > 0 else 0,
                "trend": indicators["ratio_trend"],
            },
            "obv": {
                "trend": indicators["obv_trend"],
                "latest": round(float(obv.iloc[-1]), 0) if len(obv) > 0 else 0,
            },
            "ad_line": {
                "trend": indicators["ad_trend"],
                "latest": round(float(ad.iloc[-1]), 0) if len(ad) > 0 else 0,
            },
            "mfi": {
                "value": round(indicators["latest_mfi"], 1),
                "zone": "超买" if indicators["latest_mfi"] > 80 else "超卖" if indicators["latest_mfi"] < 20 else "正常",
            },
        },
        "price_trend": indicators["price_trend"],
        "volume_trend": indicators["volume_trend"],
        "pattern": result["pattern"],
        "pattern_cn": result["pattern_cn"],
        "confidence": result["confidence"],
        "all_scores": result["all_scores"],
        "evidence": result["evidence"],
    }

    return output


def main():
    parser = argparse.ArgumentParser(description="A股聪明钱/主力行为量化识别")
    parser.add_argument("--flow", required=True, help="资金流向 JSON 文件路径")
    parser.add_argument("--kline", required=True, help="K线数据 JSON 文件路径")
    parser.add_argument("--days", type=int, default=20, help="分析窗口天数 (默认20)")
    args = parser.parse_args()

    try:
        flow_df, kline_df = load_data(args.flow, args.kline)
    except Exception as e:
        print(json.dumps({"error": f"数据加载失败: {e}"}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)

    result = analyze(flow_df, kline_df, args.days)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
