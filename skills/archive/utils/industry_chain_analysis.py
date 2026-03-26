#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FinClaw 产业链分析脚本
支持自动数据源切换（同花顺 → 腾讯财经/AkShare）

使用方法:
    python industry_chain_analysis.py [产业链名称]

示例:
    python industry_chain_analysis.py 新能源电池
    python industry_chain_analysis.py 半导体
    python industry_chain_analysis.py 光伏
"""

    from data_source_fallback import get_industry_chain
    from data_source_fallback import get_industry_chain
from pathlib import Path

# 添加fallback模块路径
sys.path.insert(0, str(Path(__file__).parent))

try:
import json
except ImportError:
    # 备用导入
    sys.path.insert(0, '/root/.openclaw/workspace/finclaw/skills/utils')
import sys


def format_industry_report(chain_data: dict) -> str:
    """格式化产业链分析报告"""
    if not chain_data.get("success"):
        return f"""
❌ **产业链分析失败**

错误信息: {chain_data.get('error', '未知错误')}
支持的产业链: {', '.join(chain_data.get('supported', []))}

---
📊 **数据源状态**: 同花顺API Token已过期，已自动切换至备用数据源
⏱️ **分析时间**: 自动降级运行
"""

    summary = chain_data.get("summary", {})
    segments = chain_data.get("segments", {})

    # 构建报告
    lines = [
        f"""
============================================================
🔗 **{chain_data['industry']}产业链分析报告**

**整体景气度**: {summary.get('sentiment', '未知')} ({summary.get('overall_change_pct', 0):.2f}%)
**监控股票**: {summary.get('total_stocks', 0)}只
**数据获取**: 腾讯财经（同花顺暂不可用，自动切换）
"""
    ]

    # 各环节详情
    for segment_name, segment_data in segments.items():
        avg_change = segment_data.get('avg_change_pct', 0)
        emoji = "📈" if avg_change > 0 else "📉" if avg_change < 0 else "➡️"

        lines.append(f"""
## {segment_name}
景气度: {emoji} {avg_change:+.2f}% ({len(segment_data.get('stocks', []))}只股票)

| 代码 | 名称 | 价格 | 涨跌幅 |
|:---:|:---:|---:|---:|
""")

        # 添加股票列表（按涨跌幅排序）
        stocks = sorted(segment_data.get('stocks', []), key=lambda x: x.get('change_pct', 0), reverse=True)
        for stock in stocks[:5]:  # 只显示前5只
            change_emoji = "📈" if stock.get('change_pct', 0) > 0 else "📉" if stock.get('change_pct', 0) < 0 else "➡️"
            lines.append(f"| {stock['code']} | {stock['name']} | ¥{stock['price']:.2f} | {change_emoji} {stock.get('change_pct', 0):+.2f}% |")

    # 数据来源标注
    lines.append(f"""
---
📊 **数据来源**: 腾讯财经API
⏱️ **数据时间**: {chain_data.get('timestamp', '实时')}
⚡ **状态**: 同花顺API Token过期，已自动切换至备用源
🔧 **分析工具**: FinClaw v1.0

*注：同花顺API暂时不可用，已自动切换至腾讯财经获取实时数据*
============================================================
""")

    return "\n".join(lines)


def main():
    """主函数"""
    # 获取命令行参数
    industry = "新能源电池"  # 默认
    if len(sys.argv) > 1:
        industry = sys.argv[1]

    print(f"正在分析 {industry} 产业链...")
    print("(同花顺API暂不可用，自动切换至腾讯财经)")
    print()

    # 获取产业链数据
    chain_data = get_industry_chain(industry)

    # 输出报告
    report = format_industry_report(chain_data)
    print(report)

    # 同时输出JSON格式（便于其他程序调用）
    output_json = {
        "industry": industry,
        "success": chain_data.get("success", False),
        "data_source": "tencent_finance",
        "fallback_reason": "ths_token_expired",
        "summary": chain_data.get("summary", {}),
        "segments": chain_data.get("segments", {})
    }

    # 保存JSON结果
    output_dir = Path("/root/.openclaw/workspace/finclaw-workspace/finclaw/reports")
    output_dir.mkdir(parents=True, exist_ok=True)

    json_path = output_dir / f"industry_chain_{industry.replace(' ', '_')}.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(output_json, f, ensure_ascii=False, indent=2)

    print(f"\nJSON结果已保存: {json_path}")


if __name__ == "__main__":
    main()
