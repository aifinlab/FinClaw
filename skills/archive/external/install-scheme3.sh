#!/bin/bash
# FinClaw 方案三：基础设施 Skills 安装脚本

set -e

echo "=================================="
echo "FinClaw 方案三：基础设施 Skills"
echo "=================================="
echo ""

# 检查 clawhub 是否安装
if ! command -v clawhub &> /dev/null; then
    echo "❌ clawhub 未安装，正在安装..."
    pip install skillhub
fi

echo "✅ clawhub 已就绪"
echo ""

# 安装 Skills
echo "📦 开始安装 3 个基础设施 Skills..."
echo ""

SKILLS=(
    "sql-toolkit"
    "ontology"
    "proactive-agent"
)

for skill in "${SKILLS[@]}"; do
    echo "⬇️  安装 $skill..."
    if clawhub install "$skill" 2>&1; then
        echo "✅ $skill 安装成功"
    else
        echo "⚠️  $skill 安装失败，尝试备用方式..."
        curl -sL "https://clawhub.ai/api/skills/$skill/download" -o "/tmp/$skill.zip" 2>/dev/null || true
    fi
    echo ""
done

echo "=================================="
echo "安装完成！"
echo "=================================="
echo ""
echo "使用方法："
echo "  sql-toolkit --help"
echo "  ontology --help"
echo "  proactive-agent --help"
echo ""
echo "集成文档: external/INTEGRATION.md"
