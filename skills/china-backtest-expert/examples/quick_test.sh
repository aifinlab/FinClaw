#!/bin/bash
# 快速测试脚本

echo "🦞 China Backtest Expert 快速测试"
echo "================================"

cd "$(dirname "$0")/.."

# 生成示例数据
echo ""
echo "1. 生成示例数据..."
python examples/sample_strategy.py

# 运行质量检查
echo ""
echo "2. 运行质量门禁检查..."
python scripts/quality_gate.py \
  --backtest-result examples/sample_backtest_data.csv \
  --config examples/quality_config.yaml \
  --output-format text

echo ""
echo "3. 生成JSON格式报告..."
python scripts/quality_gate.py \
  --backtest-result examples/sample_backtest_data.csv \
  --config examples/quality_config.yaml \
  --output-format json \
  --report test_report.json

echo ""
echo "✅ 测试完成！"
echo "报告已保存至: test_report.json"
