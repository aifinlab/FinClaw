#!/usr/bin/env python3
"""测试同花顺API可用性"""
import sys
sys.path.insert(0, '/root/.openclaw/workspace/finclaw/skills/fund-suite/data')

from ths_fund_adapter import ThsFundAdapter

adapter = ThsFundAdapter()
print(f"Token存在: {bool(adapter.access_token)}")
print(f"Token前20位: {adapter.access_token[:20]}...")
print(f"iFinD可用: {adapter.is_available()}")
