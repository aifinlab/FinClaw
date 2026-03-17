# -*- coding: utf-8 -*-
from .efinance_adapter import EfinanceAdapter
from .akshare_adapter import AkshareAdapter
from .adata_adapter import AdataAdapter
from .snowball_adapter import SnowballAdapter
from .ashare_adapter import AshareAdapter

__all__ = [
    "EfinanceAdapter", "AkshareAdapter", "AdataAdapter",
    "SnowballAdapter", "AshareAdapter",
]
