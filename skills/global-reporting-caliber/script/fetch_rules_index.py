"""Output the public source registry and built-in rule catalog."""
from __future__ import annotations

import json
from public_sources import build_default_source_registry
from rule_catalog import to_dict


def main() -> None:
    payload = {
        "public_sources": build_default_source_registry(),
        "rules": to_dict(),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
