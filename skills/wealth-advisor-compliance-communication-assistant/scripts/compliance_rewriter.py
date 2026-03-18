from __future__ import annotations

import json
import sys

REPLACEMENTS = {
    "稳赚": "存在收益机会，但未来表现仍受市场变化影响",
    "稳拿": "有一定配置价值，但仍需结合风险承受能力综合判断",
    "肯定": "可能",
    "一定": "在特定条件下可能",
    "基本不会亏": "仍存在波动和回撤可能",
    "和存款差不多": "风险收益特征与存款不同，需要单独评估",
    "赶紧买": "如您有兴趣，可进一步了解并结合自身情况审慎判断",
}


def rewrite(text: str) -> str:
    out = text
    for src, dst in REPLACEMENTS.items():
        out = out.replace(src, dst)
    return out


def main() -> None:
    text = sys.stdin.read()
    result = {
        "原文": text,
        "改写后": rewrite(text),
        "提示": [
            "请人工再次核对产品要素与风险揭示是否完整。",
            "若涉及适当性判断，请补充客户风险等级与投资期限信息。",
        ],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
