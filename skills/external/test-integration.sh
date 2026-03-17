#!/bin/bash
# FinClaw 外部 Skills 集成测试

echo "=================================="
echo "FinClaw 外部 Skills 集成测试"
echo "=================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

check_skill() {
    local skill=$1
    local command=$2
    
    echo -n "检测 $skill ... "
    if command -v $command > /dev/null 2>&1; then
        echo -e "${GREEN}✓ 已安装${NC}"
        return 0
    else
        echo -e "${RED}✗ 未安装${NC}"
        return 1
    fi
}

echo "📋 检测已安装的 Skills:"
echo ""

# 方案一：数据增强层
echo "【方案一：数据增强层】"
SKILLS_1=(
    "stock-analysis:stock-analysis"
    "tavily-web-search:tavily-search"
    "summarize:summarize"
    "firecrawl-search:firecrawl"
)

installed_1=0
for skill_info in "${SKILLS_1[@]}"; do
    IFS=':' read -r name cmd <<< "$skill_info"
    if check_skill "$name" "$cmd"; then
        ((installed_1++))
    fi
done

echo ""
echo "方案一: ${installed_1}/4 Skills"
echo ""

# 方案二：投研工具链
echo "【方案二：投研工具链】"
SKILLS_2=(
    "technical-analyst:technical-analyst"
    "polymarket:polymarket"
    "youtube-watcher:youtube-watcher"
)

installed_2=0
for skill_info in "${SKILLS_2[@]}"; do
    IFS=':' read -r name cmd <<< "$skill_info"
    if check_skill "$name" "$cmd"; then
        ((installed_2++))
    fi
done

echo ""
echo "方案二: ${installed_2}/3 Skills"
echo ""

# 方案三：基础设施
echo "【方案三：基础设施】"
SKILLS_3=(
    "sql-toolkit:sql-toolkit"
    "ontology:ontology"
    "proactive-agent:proactive-agent"
)

installed_3=0
for skill_info in "${SKILLS_3[@]}"; do
    IFS=':' read -r name cmd <<< "$skill_info"
    if check_skill "$name" "$cmd"; then
        ((installed_3++))
    fi
done

echo ""
echo "方案三: ${installed_3}/3 Skills"
echo ""

# 总计
total=$((installed_1 + installed_2 + installed_3))
echo "=================================="
echo -e "总计: ${total}/10 Skills 已安装"
echo "=================================="
echo ""

if [ $total -eq 0 ]; then
    echo -e "${YELLOW}提示: 尚未安装任何外部 Skills${NC}"
    echo ""
    echo "安装方案一: ./install-scheme1.sh"
    echo "安装方案二: ./install-scheme2.sh"
    echo "安装方案三: ./install-scheme3.sh"
elif [ $total -lt 10 ]; then
    echo -e "${YELLOW}提示: 部分 Skills 未安装${NC}"
    echo ""
    [ $installed_1 -lt 4 ] && echo "安装方案一: ./install-scheme1.sh"
    [ $installed_2 -lt 3 ] && echo "安装方案二: ./install-scheme2.sh"
    [ $installed_3 -lt 3 ] && echo "安装方案三: ./install-scheme3.sh"
else
    echo -e "${GREEN}✓ 所有外部 Skills 已就绪！${NC}"
    echo ""
    echo "FinClaw 生态: 50个原生 + 10个外部 = 60个 Skills"
fi

echo ""
echo "详细使用说明: cat INTEGRATION.md"
