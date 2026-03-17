# -*- coding: utf-8 -*-
"""Smart routing + fallback executor for cn-stock-data unified layer."""
import sys
import traceback
from code_converter import parse_code, is_cross_market
from adapters import EfinanceAdapter, AkshareAdapter, AdataAdapter, SnowballAdapter, AshareAdapter

# ── Priority chains per data type ─────────────────────────────────────
ROUTE_CONFIG = {
    "kline": ["efinance", "akshare", "adata", "ashare", "snowball"],
    "quote": ["efinance", "adata", "snowball"],
    "fund_flow": ["efinance", "adata", "snowball"],
    "finance": ["adata", "akshare", "snowball"],
    "north_flow": ["adata"],  # NOTE: 北向资金明细自2024-08下半年起停止实时披露，数据可能全为0
    "macro": ["akshare"],
}

# Cross-market (HK/US) always routes to snowball
CROSS_MARKET_ROUTE = {
    "kline": ["snowball"],
    "quote": ["snowball"],
    "fund_flow": ["snowball"],
    "finance": ["snowball"],
}

# ── Adapter registry ─────────────────────────────────────────────────
ADAPTERS = {
    "efinance": EfinanceAdapter,
    "akshare": AkshareAdapter,
    "adata": AdataAdapter,
    "snowball": SnowballAdapter,
    "ashare": AshareAdapter,
}

_adapter_cache = {}


def _get_adapter(name: str):
    if name not in _adapter_cache:
        cls = ADAPTERS.get(name)
        if cls and cls.is_available():
            _adapter_cache[name] = cls()
        else:
            _adapter_cache[name] = None
    return _adapter_cache[name]


def get_available_sources() -> dict:
    """Return {name: bool} availability status for all sources."""
    result = {}
    for name, cls in ADAPTERS.items():
        result[name] = cls.is_available()
    return result


def _get_route(data_type: str, code: str = None) -> list:
    """Get priority chain for data type, considering cross-market."""
    if code and is_cross_market(code):
        return CROSS_MARKET_ROUTE.get(data_type, ["snowball"])
    return ROUTE_CONFIG.get(data_type, [])


def execute_with_fallback(data_type: str, method_name: str, code: str = None,
                          force_source: str = None, **kwargs) -> dict:
    """Execute a data fetch with smart routing and auto-fallback.

    Returns unified result dict:
    {
        "ok": bool,
        "source": str,
        "fallback_used": bool,
        "code": str,
        "data_type": str,
        "count": int,
        "data": list[dict],
        "error": str (only if ok=False)
    }
    """
    unified_code = parse_code(code)["unified"] if code else None
    errors = []

    if force_source:
        chain = [force_source]
    else:
        chain = _get_route(data_type, code)

    first_source = chain[0] if chain else None

    for source_name in chain:
        adapter = _get_adapter(source_name)
        if adapter is None:
            errors.append(f"{source_name}: not available (library not installed)")
            continue

        method = getattr(adapter, method_name, None)
        if method is None:
            errors.append(f"{source_name}: method {method_name} not supported")
            continue

        try:
            # Build call kwargs
            call_kwargs = dict(kwargs)
            if code and "code" not in call_kwargs and "codes" not in call_kwargs:
                call_kwargs["code"] = code

            df = method(**call_kwargs)
            if df is None or df.empty:
                errors.append(f"{source_name}: returned empty data")
                continue

            records = df.to_dict(orient="records")
            return {
                "ok": True,
                "source": source_name,
                "fallback_used": source_name != first_source,
                "code": unified_code,
                "data_type": data_type,
                "count": len(records),
                "data": records,
            }
        except Exception as e:
            errors.append(f"{source_name}: {type(e).__name__}: {e}")
            continue

    return {
        "ok": False,
        "source": None,
        "fallback_used": True,
        "code": unified_code,
        "data_type": data_type,
        "count": 0,
        "data": [],
        "error": "; ".join(errors),
    }
