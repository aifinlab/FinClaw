# -*- coding: utf-8 -*-
"""Stock code format converter for unified cn-stock-data layer."""


def parse_code(code: str) -> dict:
    """Parse any stock code format into a unified dict.

    Supported inputs:
      SH600519, SZ000001, HK00700, AAPL.O, BABA.N  (unified format)
      sh600519, sz000001  (ashare format)
      600519, 000001  (bare digits, auto-detect market)
      000001.XSHG, 000001.XSHE  (joinquant format)

    Returns: {"unified": "SH600519", "market": "SH", "bare": "600519"}
    """
    code = code.strip()

    # JoinQuant format
    if '.XSHG' in code:
        bare = code.replace('.XSHG', '')
        return {"unified": f"SH{bare}", "market": "SH", "bare": bare}
    if '.XSHE' in code:
        bare = code.replace('.XSHE', '')
        return {"unified": f"SZ{bare}", "market": "SZ", "bare": bare}

    # US/HK with dot suffix (AAPL.O, BABA.N)
    if '.' in code and not code[0].isdigit():
        return {"unified": code.upper(), "market": "US", "bare": code.upper()}

    upper = code.upper()

    # Already prefixed: SH600519, SZ000001, HK00700
    if upper.startswith('SH'):
        bare = upper[2:]
        return {"unified": upper, "market": "SH", "bare": bare}
    if upper.startswith('SZ'):
        bare = upper[2:]
        return {"unified": upper, "market": "SZ", "bare": bare}
    if upper.startswith('HK'):
        bare = upper[2:]
        return {"unified": upper, "market": "HK", "bare": bare}

    # Bare digits: auto-detect market
    if code.isdigit():
        if code.startswith('6') or code.startswith('9'):
            return {"unified": f"SH{code}", "market": "SH", "bare": code}
        elif code.startswith('0') or code.startswith('3') or code.startswith('2'):
            return {"unified": f"SZ{code}", "market": "SZ", "bare": code}

    # Fallback: treat as-is (unknown format)
    return {"unified": upper, "market": "UNKNOWN", "bare": code}


def to_akshare(code: str) -> str:
    """Convert to akshare format: bare digits '600519'."""
    return parse_code(code)["bare"]


def to_efinance(code: str) -> str:
    """Convert to efinance format: bare digits '600519'."""
    return parse_code(code)["bare"]


def to_adata(code: str) -> str:
    """Convert to adata format: bare digits '600519'."""
    return parse_code(code)["bare"]


def to_ashare(code: str) -> str:
    """Convert to ashare format: lowercase prefix 'sh600519'."""
    info = parse_code(code)
    if info["market"] in ("SH", "SZ"):
        return info["market"].lower() + info["bare"]
    return info["bare"]


def to_snowball(code: str) -> str:
    """Convert to pysnowball format.

    A-shares: SH600519, SZ000001 (prefix required)
    HK: bare digits 00700 (no HK prefix)
    US: AAPL.O as-is
    """
    info = parse_code(code)
    if info["market"] == "HK":
        return info["bare"]  # pysnowball HK uses bare "00700"
    return info["unified"]


def is_cross_market(code: str) -> bool:
    """Check if code is HK or US (cross-market)."""
    info = parse_code(code)
    return info["market"] in ("HK", "US")
