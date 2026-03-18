import argparse
import csv
import json
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class GraphEdge:
    source: str
    target: str
    relation: str
    weight: float


DEFAULT_THRESHOLDS = {
    "high_risk_degree": 3,
    "high_risk_weight": 0.6,
}


def parse_float(value: str) -> float:
    if value is None or value == "":
        return 0.0
    return float(value)


def load_edges(path: str) -> List[GraphEdge]:
    edges: List[GraphEdge] = []
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            edges.append(
                GraphEdge(
                    source=row.get("source", "").strip(),
                    target=row.get("target", "").strip(),
                    relation=row.get("relation", "").strip(),
                    weight=parse_float(row.get("weight")),
                )
            )
    return edges


def build_adjacency(edges: List[GraphEdge]) -> Dict[str, List[GraphEdge]]:
    adjacency: Dict[str, List[GraphEdge]] = defaultdict(list)
    for edge in edges:
        adjacency[edge.source].append(edge)
        adjacency[edge.target].append(edge)
    return adjacency


def compute_node_stats(edges: List[GraphEdge]) -> Dict[str, Dict[str, float]]:
    stats: Dict[str, Dict[str, float]] = defaultdict(lambda: {"degree": 0, "weight": 0.0})
    for edge in edges:
        stats[edge.source]["degree"] += 1
        stats[edge.target]["degree"] += 1
        stats[edge.source]["weight"] += edge.weight
        stats[edge.target]["weight"] += edge.weight
    return stats


def evaluate_nodes(stats: Dict[str, Dict[str, float]], thresholds: Dict[str, float]) -> List[Dict[str, object]]:
    results: List[Dict[str, object]] = []
    for node, values in stats.items():
        degree = values["degree"]
        weight = values["weight"]
        signals: List[str] = []
        score = 0

        if degree >= thresholds["high_risk_degree"]:
            score += 2
            signals.append("关联节点数量偏高")

        if weight >= thresholds["high_risk_weight"]:
            score += 2
            signals.append("关联强度偏高")

        if score >= 4:
            severity = "高"
        elif score >= 2:
            severity = "中"
        else:
            severity = "低"

        results.append(
            {
                "node": node,
                "degree": degree,
                "weight": round(weight, 2),
                "score": score,
                "severity": severity,
                "signals": signals,
            }
        )
    return results


def build_report(edges: List[GraphEdge], thresholds: Dict[str, float]) -> Dict[str, object]:
    stats = compute_node_stats(edges)
    signals = evaluate_nodes(stats, thresholds)
    summary = {"高": 0, "中": 0, "低": 0}
    for signal in signals:
        summary[signal["severity"]] += 1

    top_nodes = sorted(signals, key=lambda x: (-x["score"], -x["weight"]))[:10]

    return {
        "summary": summary,
        "top_nodes": top_nodes,
        "signals": signals,
        "edge_count": len(edges),
    }


def parse_thresholds(path: str) -> Dict[str, float]:
    if not path:
        return DEFAULT_THRESHOLDS
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)
    thresholds = DEFAULT_THRESHOLDS.copy()
    thresholds.update({k: float(v) for k, v in data.items() if k in thresholds})
    return thresholds


def main() -> None:
    parser = argparse.ArgumentParser(description="关联方图谱风险分析")
    parser.add_argument("--input", required=True, help="关系边CSV数据")
    parser.add_argument("--thresholds", help="阈值JSON配置")
    parser.add_argument("--output", required=True, help="输出JSON")
    args = parser.parse_args()

    edges = load_edges(args.input)
    thresholds = parse_thresholds(args.thresholds)
    report = build_report(edges, thresholds)

    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
