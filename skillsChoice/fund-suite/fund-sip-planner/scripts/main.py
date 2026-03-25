#!/usr/bin/env python3
"""基金定投计划 - 入口文件"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fund_sip_planner import main
if __name__ == "__main__":
    main()
