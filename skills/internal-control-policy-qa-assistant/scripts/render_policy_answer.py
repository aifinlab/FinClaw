from __future__ import annotations

import json
import sys
from typing import Any, Dict

TEMPLATE = """# 制度问答答复\n\n## 问题\n{question}\n\n## 适用依据\n{basis}\n\n## 结论（{confidence_level}）\n{conclusion}\n\n## 解释说明\n{explanation}\n\n## 例外与补充条件\n{exceptions}\n\n## 执行建议\n{actions}\n\n## 升级确认建议\n{escalation}\n\n## 风险提示\n{risk_notice}\n"""


def render(data: Dict[str, Any]) -> str:
    return TEMPLATE.format(
        question=data.get("question", "未提供"),
        basis=data.get("basis", "待补充"),
        confidence_level=data.get("confidence_level", "C级"),
        conclusion=data.get("conclusion", "待判断"),
        explanation=data.get("explanation", "待补充"),
        exceptions=data.get("exceptions", "如存在例外情形，请补充说明。"),
        actions=data.get("actions", "建议先补充制度依据后再答复。"),
        escalation=data.get("escalation", "如涉及冲突、版本不明或重大例外，请升级确认。"),
        risk_notice=data.get("risk_notice", "本答复仅供内部制度理解参考，不替代正式制度解释。"),
    )


def main() -> None:
    payload = json.load(sys.stdin)
    sys.stdout.write(render(payload))


if __name__ == "__main__":
    main()
