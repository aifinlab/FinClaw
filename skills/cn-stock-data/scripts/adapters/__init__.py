# -*- coding: utf-8 -*-
from .adata_adapter import AdataAdapter
from .akshare_adapter import AkshareAdapter
from .ashare_adapter import AshareAdapter
from .efinance_adapter import EfinanceAdapter
from .snowball_adapter import SnowballAdapter

__all__ = [
    "EfinanceAdapter", "AkshareAdapter", "AdataAdapter",
    "SnowballAdapter", "AshareAdapter",
]
