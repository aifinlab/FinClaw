from __future__ import annotations

import json
from typing import Any, Dict, List


def _pick(data: Dict[str, Any], keys: List[str], default: Any = None) -> Any:
    for key in keys:
        if key in data and data[key] not in (None, ""):
            return data[key]
    return default


def normalize_application(raw: Dict[str, Any]) -> Dict[str, Any]:
    normalized = {
        "申请人基础信息": {
            "姓名": _pick(raw, ["姓名", "申请人姓名", "name"]),
            "年龄": _pick(raw, ["年龄", "age"]),
            "婚姻状况": _pick(raw, ["婚姻状况", "marital_status"]),
            "户籍": _pick(raw, ["户籍", "hukou"]),
            "居住地": _pick(raw, ["居住地", "residence"]),
        },
        "申请信息": {
            "产品类型": _pick(raw, ["产品类型", "loan_type"]),
            "申请金额": _pick(raw, ["申请金额", "amount"]),
            "申请期限": _pick(raw, ["申请期限", "term"]),
            "申请用途": _pick(raw, ["申请用途", "purpose"]),
            "担保方式": _pick(raw, ["担保方式", "guarantee"]),
        },
        "职业收入信息": {
            "单位": _pick(raw, ["单位", "工作单位", "employer"]),
            "岗位": _pick(raw, ["岗位", "职位", "position"]),
            "工作年限": _pick(raw, ["工作年限", "employment_years"]),
            "月收入": _pick(raw, ["月收入", "monthly_income"]),
            "收入来源": _pick(raw, ["收入来源", "income_source"]),
        },
        "资产负债信息": {
            "房产": _pick(raw, ["房产", "property_assets"], []),
            "车辆": _pick(raw, ["车辆", "car_assets"], []),
            "存款投资": _pick(raw, ["存款投资", "financial_assets"], []),
            "现有贷款": _pick(raw, ["现有贷款", "existing_loans"], []),
            "信用卡负债": _pick(raw, ["信用卡负债", "credit_card_debt"]),
        },
        "征信信息": {
            "逾期情况": _pick(raw, ["逾期情况", "overdue_info"]),
            "查询次数": _pick(raw, ["查询次数", "query_count"]),
            "授信使用率": _pick(raw, ["授信使用率", "utilization_rate"]),
        },
        "辅助材料": _pick(raw, ["辅助材料", "documents"], {}),
    }
    return normalized


if __name__ == "__main__":
    sample = {
        "姓名": "张三",
        "年龄": 33,
        "产品类型": "个人消费贷",
        "申请金额": 300000,
        "申请期限": "36个月",
        "申请用途": "家装",
        "单位": "某科技公司",
        "岗位": "产品经理",
        "月收入": 28000,
        "查询次数": 5,
    }
    print(json.dumps(normalize_application(sample), ensure_ascii=False, indent=2))
