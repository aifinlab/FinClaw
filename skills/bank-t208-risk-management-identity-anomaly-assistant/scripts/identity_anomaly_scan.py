from dataclasses import dataclass
from typing import Dict, List
import argparse
import csv
import json


@dataclass
class IdentityRecord:
    customer_id: str
    id_number: str
    id_expiry: str
    change_count: int
    biometric_fail: int
    device_count: int
    address_match: str
    contact_match: str


DEFAULT_THRESHOLDS = {
    "change_count": 2,
    "biometric_fail": 3,
    "device_count": 3,
}


def parse_int(value: str) -> int:
    if value is None or value == "":
        return 0
    return int(float(value))


def load_records(path: str) -> List[IdentityRecord]:
    records: List[IdentityRecord] = []
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            records.append(
                IdentityRecord(
                    customer_id=row.get("customer_id", "").strip(),
                    id_number=row.get("id_number", "").strip(),
                    id_expiry=row.get("id_expiry", "").strip(),
                    change_count=parse_int(row.get("change_count")),
                    biometric_fail=parse_int(row.get("biometric_fail")),
                    device_count=parse_int(row.get("device_count")),
                    address_match=row.get("address_match", "").strip(),
                    contact_match=row.get("contact_match", "").strip(),
                )
            )
    return records


def evaluate_record(record: IdentityRecord, thresholds: Dict[str, int]) -> Dict[str, object]:
    signals: List[str] = []
    score = 0

    if record.change_count >= thresholds["change_count"]:
        score += 2
        signals.append("身份信息变更频繁")

    if record.biometric_fail >= thresholds["biometric_fail"]:
        score += 2
        signals.append("生物识别失败次数偏高")

    if record.device_count >= thresholds["device_count"]:
        score += 1
        signals.append("登录设备数量偏多")

    if record.address_match == "N":
        score += 1
        signals.append("地址一致性异常")

    if record.contact_match == "N":
        score += 1
        signals.append("联系方式一致性异常")

    if score >= 5:
        severity = "高"
    elif score >= 3:
        severity = "中"
    else:
        severity = "低"

    return {
        "customer_id": record.customer_id,
        "score": score,
        "severity": severity,
        "signals": signals,
        "change_count": record.change_count,
        "biometric_fail": record.biometric_fail,
        "device_count": record.device_count,
    }


def build_report(records: List[IdentityRecord], thresholds: Dict[str, int]) -> Dict[str, object]:
    signals = [evaluate_record(record, thresholds) for record in records]
    summary = {"高": 0, "中": 0, "低": 0}
    for signal in signals:
        summary[signal["severity"]] += 1
    return {"summary": summary, "signals": signals}


def parse_thresholds(path: str) -> Dict[str, int]:
    if not path:
        return DEFAULT_THRESHOLDS
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)
    thresholds = DEFAULT_THRESHOLDS.copy()
    thresholds.update({k: int(v) for k, v in data.items() if k in thresholds})
    return thresholds


def main() -> None:
    parser = argparse.ArgumentParser(description="客户身份异常识别")
    parser.add_argument("--input", required=True, help="身份异常CSV数据")
    parser.add_argument("--thresholds", help="阈值JSON配置")
    parser.add_argument("--output", required=True, help="输出JSON")
    args = parser.parse_args()

    records = load_records(args.input)
    thresholds = parse_thresholds(args.thresholds)
    report = build_report(records, thresholds)

    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
