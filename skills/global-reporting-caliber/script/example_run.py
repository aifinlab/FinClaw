from __future__ import annotations

from company_validator import ListedCompanyReportingValidator


if __name__ == "__main__":
    validator = ListedCompanyReportingValidator()
    result = validator.run(
        company_name="贵州茅台",
        stock_code="600519",
        keyword="关联交易",
        limit=3,
    )
    print(result["validation"]["summary"])
