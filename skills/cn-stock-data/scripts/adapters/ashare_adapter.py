# -*- coding: utf-8 -*-
"""ashare adapter for cn-stock-data unified layer (lightweight Sina+Tencent)."""
import os
import sys
import pandas as pd
from field_mapper import KLINE_FIELDS, map_fields
from code_converter import to_ashare
from Ashare import get_price
from Ashare import get_price
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


class AshareAdapter:
    name = "ashare"

    @staticmethod
    def is_available():
            # Ashare.py lives in the same scripts/ directory
            scripts_dir = os.path.dirname(os.path.dirname(__file__))
            sys.path.insert(0, scripts_dir)

            return True