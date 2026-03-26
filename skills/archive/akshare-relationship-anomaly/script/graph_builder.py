from .data_loader import DataBundle

from __future__ import annotations

from typing import Dict, Tuple
import networkx as nx

import pandas as pd


def build_relationship_graph(bundle: DataBundle) -> Tuple[nx.Graph, Dict[str, int]]:
    graph = nx.Graph()
    stock_node = f"stock:{bundle.symbol}"
    graph.add_node(stock_node, node_type="stock", symbol=bundle.symbol)

    edge_counter = {
        "broker_edges": 0,
        "person_edges": 0,
        "disclosure_edges": 0,
    }

    _add_broker_edges(graph, stock_node, bundle.lhb_detail, edge_counter)
    _add_person_edges(graph, stock_node, bundle.hold_change, edge_counter)
    _add_disclosure_edges(graph, stock_node, bundle.disclosure, edge_counter)

    return graph, edge_counter


def _add_broker_edges(graph: nx.Graph, stock_node: str, df: pd.DataFrame, edge_counter: Dict[str, int]) -> None:
    if df.empty:
        return

    broker_col = _find_first_existing(df, ["营业部名称", "营业部", "买方营业部", "卖方营业部", "解读"])
    amount_col = _find_first_existing(df, ["买入金额", "卖出金额", "成交金额", "净买额", "金额"])
    date_col = _find_first_existing(df, ["上榜日", "日期", "交易日期"])

    if broker_col is None:
        return

    for _, row in df.iterrows():
        broker = str(row.get(broker_col, "")).strip()
        if not broker or broker == "nan":
            continue
        broker_node = f"broker:{broker}"
        graph.add_node(broker_node, node_type="broker", name=broker)
        graph.add_edge(
            stock_node,
            broker_node,
            edge_type="lhb",
            event_date=str(row.get(date_col, "")) if date_col else "",
            amount=float(pd.to_numeric(row.get(amount_col, 0), errors="coerce") or 0),
        )
        edge_counter["broker_edges"] += 1


def _add_person_edges(graph: nx.Graph, stock_node: str, df: pd.DataFrame, edge_counter: Dict[str, int]) -> None:
    if df.empty:
        return

    person_col = _find_first_existing(df, ["姓名", "人员姓名"])
    role_col = _find_first_existing(df, ["职务", "职务名称"])
    delta_col = _find_first_existing(df, ["变动数", "持股变动数"])
    reason_col = _find_first_existing(df, ["变动原因", "原因"])
    date_col = _find_first_existing(df, ["变动日期", "填报日期", "日期"])

    if person_col is None:
        return

    for _, row in df.iterrows():
        person = str(row.get(person_col, "")).strip()
        if not person or person == "nan":
            continue
        person_node = f"person:{person}"
        graph.add_node(person_node, node_type="person", name=person, role=str(row.get(role_col, "")))
        graph.add_edge(
            stock_node,
            person_node,
            edge_type="hold_change",
            event_date=str(row.get(date_col, "")) if date_col else "",
            delta=float(pd.to_numeric(row.get(delta_col, 0), errors="coerce") or 0),
            reason=str(row.get(reason_col, "")) if reason_col else "",
        )
        edge_counter["person_edges"] += 1


def _add_disclosure_edges(graph: nx.Graph, stock_node: str, df: pd.DataFrame, edge_counter: Dict[str, int]) -> None:
    if df.empty:
        return

    title_col = _find_first_existing(df, ["公告标题", "标题", "公告名称"])
    date_col = _find_first_existing(df, ["公告时间", "日期", "时间"])
    link_col = _find_first_existing(df, ["公告链接", "链接", "url"])

    if title_col is None:
        return

    for idx, row in df.iterrows():
        title = str(row.get(title_col, "")).strip()
        if not title or title == "nan":
            title = f"公告_{idx}"
        event_node = f"event:{title[:80]}:{idx}"
        graph.add_node(
            event_node,
            node_type="disclosure",
            title=title,
            event_date=str(row.get(date_col, "")) if date_col else "",
            url=str(row.get(link_col, "")) if link_col else "",
        )
        graph.add_edge(stock_node, event_node, edge_type="disclosure")
        edge_counter["disclosure_edges"] += 1


def graph_summary(graph: nx.Graph) -> dict:
    if graph.number_of_nodes() == 0:
        return {
            "nodes": 0,
            "edges": 0,
            "density": 0.0,
            "max_degree": 0,
            "stock_degree": 0,
        }

    degrees = dict(graph.degree())
    stock_degree = 0
    for node, attrs in graph.nodes(data=True):
        if attrs.get("node_type") == "stock":
            stock_degree = degrees.get(node, 0)
            break

    density = nx.density(graph) if graph.number_of_nodes() > 1 else 0.0

    return {
        "nodes": graph.number_of_nodes(),
        "edges": graph.number_of_edges(),
        "density": round(density, 6),
        "max_degree": max(degrees.values()) if degrees else 0,
        "stock_degree": stock_degree,
    }


def export_graph_tables(graph: nx.Graph) -> tuple[pd.DataFrame, pd.DataFrame]:
    nodes = []
    for node, attrs in graph.nodes(data=True):
        row = {"node_id": node}
        row.update(attrs)
        nodes.append(row)
    edges = []
    for source, target, attrs in graph.edges(data=True):
        row = {"source": source, "target": target}
        row.update(attrs)
        edges.append(row)
    return pd.DataFrame(nodes), pd.DataFrame(edges)


def _find_first_existing(df: pd.DataFrame, candidates: list[str]) -> str | None:
    for col in candidates:
        if col in df.columns:
            return col
    return None
