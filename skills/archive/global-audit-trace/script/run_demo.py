from check_audit_trace import run as run_checks
from common import save_json

from fetch_company_profile import run as run_company
from fetch_regulations import run as run_regulations
from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def main() -> None:
    regulations = run_regulations(keyword_text="信息披露 审计 留痕 内部控制", max_items=5)
    save_json(regulations, str(DATA_DIR / "regulations.json"))

    company = run_company(
        company_name="上海悦心健康集团股份有限公司",
        stock_code="002162",
        annual_report_url="https://disc.static.szse.cn/disc/disk03/finalpage/2025-08-26/d139527a-8b5b-409a-b051-13c688736fec.PDF",
        company_site="https://www.cimic.com",
    )
    save_json(company, str(DATA_DIR / "company_profile.json"))

    result = run_checks(company, regulations)
    save_json(result, str(DATA_DIR / "audit_trace_result.json"))
    print("demo completed")
    print(f"result file: {DATA_DIR / 'audit_trace_result.json'}")


if __name__ == "__main__":
    main()
