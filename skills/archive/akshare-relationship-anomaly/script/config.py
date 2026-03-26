from __future__ import annotations
# ===== AkShare开源数据支持（新增） =====
from skillsChoice.common.unified_data_api import (
    get_data_api,
    get_index_quote,
)
# ====================================

DEFAULT_PRICE_LOOKBACK = 60
DEFAULT_VOLUME_LOOKBACK = 20
DEFAULT_TOP_N_UNIVERSE = 100
DEFAULT_SINGLE_START = "20250101"
DEFAULT_SINGLE_END = "20250301"

RISK_LEVELS = [
    (85, "极高"),
    (70, "高"),
    (45, "中"),
    (0, "低"),
]
