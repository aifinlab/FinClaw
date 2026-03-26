import sys
import json
from pathlib import Path
from shared.corporate_credit_skill_engine import build_packet, load_input, render_markdown  # noqa: E402
import argparse


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def validate_input(data: dict) -> dict:
    """验证输入参数"""
    if not isinstance(data, dict):
        raise ValueError("输入必须是字典类型")

    required_fields = []  # 添加必填字段
    for field in required_fields:
        if field not in data:
            raise ValueError(f"缺少必填字段: {field}")

    return data


def main() -> None:

    parser = argparse.ArgumentParser(
        description="Run t132 supply-chain due diligence skill.")
    parser.add_argument("--input", required=True, help="Input JSON path")
    parser.add_argument("--output", help="Optional output path")
    parser.add_argument(
        "--format",
        choices=[
            "json",
            "markdown"],
        default="markdown")
    args = parser.parse_args()

    packet = build_packet(load_input(Path(args.input)), "t132")
    content = json.dumps(
        packet,
        ensure_ascii=False,
        indent=2) if args.format == "json" else render_markdown(packet)
    if args.output:
        Path(args.output).write_text(content, encoding="utf-8")
    else:
        print(content)


if __name__ == "__main__":
    main()
