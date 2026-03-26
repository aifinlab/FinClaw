from .data_loader import AkshareADataLoader

from .graph_builder import build_relationship_graph, export_graph_tables, graph_summary
from .reporting import write_outputs

from .scoring import compute_market_anomaly_features, score_risk

from __future__ import annotations
from pathlib import Path
from typing import Dict, List
import pandas as pd


def run_single_symbol_scan(symbol: str, start_date: str, end_date: str, output_dir: str) -> Dict[str, object]:
    loader = AkshareADataLoader()
    bundle = loader.load_symbol_bundle(symbol=symbol, start_date=start_date, end_date=end_date)

    graph, edge_counter = build_relationship_graph(bundle)
    graph_stats = graph_summary(graph)
    market_features = compute_market_anomaly_features(bundle.hist)
    risk_info = score_risk(
        market_features=market_features,
        graph_stats=graph_stats,
        edge_counter=edge_counter,
        lhb_stat=bundle.lhb_stat,
        hold_change=bundle.hold_change,
        disclosure=bundle.disclosure,
    )

    summary = {
        "symbol": symbol,
        "start_date": start_date,
        "end_date": end_date,
        **risk_info,
        **market_features,
        **graph_stats,
        **edge_counter,
        "evidence": build_evidence(bundle=bundle, market_features=market_features, graph_stats=graph_stats),
    }

    nodes_df, edges_df = export_graph_tables(graph)
    write_outputs(output_dir=output_dir, summary=summary, nodes_df=nodes_df, edges_df=edges_df)
    return summary


def run_batch_scan(symbols: List[str], start_date: str, end_date: str, output_dir: str) -> pd.DataFrame:
    results = []
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    for symbol in symbols:
        symbol_dir = out / symbol
        summary = run_single_symbol_scan(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            output_dir=str(symbol_dir),
        )
        results.append(summary)
    df = pd.DataFrame(results).sort_values("risk_score", ascending=False)
    df.to_csv(out / "batch_risk_ranking.csv", index=False, encoding="utf-8-sig")
    return df


def run_universe_scan(limit: int, start_date: str, end_date: str, output_dir: str) -> pd.DataFrame:
    loader = AkshareADataLoader()
    universe = loader.get_universe(limit=limit)
    if "代码" not in universe.columns:
        raise ValueError("未能从 AKShare 获取 A 股股票代码列。")
    symbols = universe["代码"].astype(str).str.zfill(6).tolist()
    return run_batch_scan(symbols=symbols, start_date=start_date, end_date=end_date, output_dir=output_dir)


def build_evidence(bundle, market_features: Dict[str, float], graph_stats: Dict[str, float]) -> str:
    parts = []
    if market_features.get("volume_ratio", 0) >= 2:
        parts.append(f"最近成交量为近20日均量的 {market_features['volume_ratio']:.2f} 倍")
    if market_features.get("return_z_proxy", 0) >= 2:
        parts.append(f"最近涨跌幅异常强度代理值为 {market_features['return_z_proxy']:.2f}")
    if not bundle.lhb_detail.empty:
        parts.append(f"观察期存在 {len(bundle.lhb_detail)} 条龙虎榜相关记录")
    if not bundle.hold_change.empty:
        parts.append(f"存在 {len(bundle.hold_change)} 条人员持股变动记录")
    if not bundle.disclosure.empty:
        parts.append(f"存在 {len(bundle.disclosure)} 条调研/关系披露记录")
    if graph_stats.get("stock_degree", 0) > 0:
        parts.append(f"股票节点关系度为 {graph_stats['stock_degree']}")
    return "；".join(parts) if parts else "观察期内未发现足够强的关系网络异常证据。"
