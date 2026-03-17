#!/bin/bash
# FinClaw 方案一：数据增强层 Skills 安装脚本

set -e

echo "=================================="
echo "FinClaw 方案一：数据增强层 Skills"
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
echo "📦 开始安装 4 个 Skills..."
echo ""

SKILLS=(
    "stock-analysis"
    "tavily-web-search" 
    "summarize"
    "firecrawl-search"
)

for skill in "${SKILLS[@]}"; do
    echo "⬇️  安装 $skill..."
    if clawhub install "$skill" 2>&1; then
        echo "✅ $skill 安装成功"
    else
        echo "⚠️  $skill 安装失败，尝试备用方式..."
        # 备用：从 ClawHub 直接下载
        curl -sL "https://clawhub.ai/api/skills/$skill/download" -o "/tmp/$skill.zip" 2>/dev/null || true
    fi
    echo ""
done

echo "=================================="
echo "安装完成！"
echo "=================================="
echo ""
echo "使用方法："
echo "  stock-analysis --help"
echo "  tavily-search --help"
echo "  summarize --help"
echo "  firecrawl --help"
echo ""
echo "集成文档: external/INTEGRATION.md"
