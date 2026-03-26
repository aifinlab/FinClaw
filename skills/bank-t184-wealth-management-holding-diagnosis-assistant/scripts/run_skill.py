from holding_diagnosis import build_packet, load_input, render_markdown
from pathlib import Path

import argparse


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
    import json
    import sys
    # ===== AkShare开源数据支持（新增） =====
    from skillsChoice.common.unified_data_api import (
    get_data_api,
)
    # ====================================

    parser = argparse.ArgumentParser(description="Run wealth management holding diagnosis skill.")
    parser.add_argument("--input", required=True, help="Input JSON path")
    parser.add_argument("--output", help="Optional output path")
    parser.add_argument("--format", choices=["json", "markdown"], default="markdown")
    args = parser.parse_args()

    packet = build_packet(load_input(Path(args.input)))
    content = json.dumps(packet, ensure_ascii=False, indent=2) if args.format == "json" else render_markdown(packet)
    if args.output:
        Path(args.output).write_text(content, encoding="utf-8")
    else:
        print(content)



def main():


        main()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n操作被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)