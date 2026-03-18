#!/bin/bash
echo "=============================================="
echo "FinClaw 行情数据源测试"
echo "=============================================="

echo -e "\n1. A股指数 - 上证指数:"
python3 scripts/quote.py 000001 2>&1 | head -12

echo -e "\n2. A股 - 五粮液(深市):"
python3 scripts/quote.py 000858 2>&1 | head -12

echo -e "\n3. 港股 - 腾讯控股:"
python3 scripts/quote.py 00700 2>&1 | head -12

echo -e "\n4. 美股 - 苹果(AAPL):"
python3 scripts/quote.py AAPL 2>&1 | head -12

echo -e "\n5. 美股 - 特斯拉(TSLA):"
python3 scripts/quote.py TSLA 2>&1 | head -12

echo -e "\n6. 美股 - 英伟达(NVDA):"
python3 scripts/quote.py NVDA 2>&1 | head -12

echo -e "\n=============================================="
echo "测试完成"
echo "=============================================="
