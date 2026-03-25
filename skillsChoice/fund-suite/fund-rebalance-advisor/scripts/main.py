#!/usr/bin/env python3
"""基金再平衡顾问 - 入口文件"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fund_rebalance_advisor_v2 import main
if __name__ == "__main__":
    main()
