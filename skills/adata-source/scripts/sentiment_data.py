#!/usr/bin/env python3
"""adata 情绪数据获取脚本：北向资金、热门排行"""
import sys
import json
import argparse
import adata
import pandas as pd


def _df_to_json(df, max_rows=None):
    if df is None or (isinstance(df, pd.DataFrame) and df.empty):
        return []
    if max_rows and len(df) > max_rows:
        df = df.head(max_rows)
    return json.loads(df.to_json(orient="records", force_ascii=False, date_format="iso"))


def north_flow():
    """北向资金历史数据（沪股通/深股通/合计）"""
    df = adata.sentiment.north.north_flow()
    return {"count": len(df), "data": _df_to_json(df)}


def north_flow_current():
    """北向资金当日实时"""
    try:
        df = adata.sentiment.north.north_flow_current()
        return {"count": len(df), "data": _df_to_json(df)}
    except Exception as e:
        return {"count": 0, "data": [], "warning": f"北向资金实时获取失败: {str(e)}"}


def north_flow_min():
    """北向资金分钟级数据"""
    try:
        df = adata.sentiment.north.north_flow_min()
        return {"count": len(df), "data": _df_to_json(df)}
    except Exception as e:
        return {"count": 0, "data": [], "warning": f"北向资金分钟数据获取失败: {str(e)}"}


def hot_rank():
    """东方财富热门股 TOP 100"""
    try:
        df = adata.sentiment.hot.pop_rank_100_east()
        return {"count": len(df), "data": _df_to_json(df)}
    except Exception as e:
        return {"count": 0, "data": [], "warning": f"热门排行获取失败: {str(e)}"}


def hot_rank_ths():
    """同花顺热门股 TOP 100"""
    try:
        df = adata.sentiment.hot.hot_rank_100_ths()
        return {"count": len(df), "data": _df_to_json(df)}
    except Exception as e:
        return {"count": 0, "data": [], "warning": f"同花顺热门排行获取失败: {str(e)}"}


def hot_concept():
    """同花顺热门概念 TOP 20"""
    try:
        df = adata.sentiment.hot.hot_concept_20_ths()
        return {"count": len(df), "data": _df_to_json(df)}
    except Exception as e:
        return {"count": 0, "data": [], "warning": f"热门概念获取失败: {str(e)}"}


def main():
    parser = argparse.ArgumentParser(description="adata 情绪数据")
    parser.add_argument("command", choices=[
        "north", "north_current", "north_min",
        "hot", "hot_ths", "hot_concept"
    ])
    args = parser.parse_args()

    try:
        cmd_map = {
            "north": north_flow,
            "north_current": north_flow_current,
            "north_min": north_flow_min,
            "hot": hot_rank,
            "hot_ths": hot_rank_ths,
            "hot_concept": hot_concept,
        }
        result = cmd_map[args.command]()
    except Exception as e:
        result = {"error": str(e)}

    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
