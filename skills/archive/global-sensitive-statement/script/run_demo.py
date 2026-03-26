from __future__ import annotations

from legal_rules import DEFAULT_COMPANY

from pathlib import Path
from sensitive_statement_detector import SensitiveStatementDetector, save_json, save_markdown

DEMO_TEXT = """
立讯精密工业股份有限公司2025年半年度业绩预告显示：
预计2025年1月1日至2025年6月30日归属于上市公司股东的净利润为647,539.54万元至674,520.36万元，比上年同期增长20%至25%。
本期业绩预告的相关财务数据未经注册会计师审计。
公司就业绩预告有关事项与年报审计会计师事务所进行了初步沟通，双方不存在分歧。
预告期内，关税壁垒等非经济因素持续冲击全球产业链分工格局，国际经贸环境的不确定性显著增强。
公司作为全球高端精密制造领域的领军企业，在复杂多变的外部环境中展现出卓越的抗风险能力，通过深化垂直整合战略强化技术护城河。
本次业绩预告是公司财务部门初步测算的结果，具体财务数据以公司披露的2025年半年度报告为准。敬请广大投资者谨慎决策，注意投资风险。
""".strip()


def main() -> None:
    out_dir = Path("demo_output")
    out_dir.mkdir(exist_ok=True)

    input_path = out_dir / "sample_public_text.txt"
    input_path.write_text(DEMO_TEXT, encoding="utf-8")

    detector = SensitiveStatementDetector()
    findings = detector.detect(DEMO_TEXT)
    summary = detector.summarize(findings)

    save_json(findings, summary, out_dir / "report.json")
    save_markdown(findings, summary, out_dir / "report.md")

    print(f"示例企业: {DEFAULT_COMPANY['name']} ({DEFAULT_COMPANY['ticker']})")
    print(f"分析文本: {input_path}")
    print(f"JSON报告: {out_dir / 'report.json'}")
    print(f"Markdown报告: {out_dir / 'report.md'}")
    print(summary)


if __name__ == "__main__":
    main()
