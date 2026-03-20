#!/usr/bin/env bash
set -euo pipefail

# FinClaw CLI Installer
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/aifinlab/FinClaw/main/install.sh | bash
#   curl -fsSL https://raw.githubusercontent.com/aifinlab/FinClaw/main/install.sh | bash -s -- --cli-only
#   curl -fsSL https://raw.githubusercontent.com/aifinlab/FinClaw/main/install.sh | bash -s -- --no-skills

CLI_ONLY=false
SKILLS_PREF="default"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --cli-only)  CLI_ONLY=true; shift ;;
    --no-skills) SKILLS_PREF="off"; shift ;;
    --with-skills) SKILLS_PREF="on"; shift ;;
    -h|--help)
      cat <<'USAGE'
Usage: install.sh [--cli-only] [--no-skills|--with-skills]

  --cli-only    只安装 CLI，跳过所有 Skills
  --no-skills   安装 CLI，但跳过默认 Skills（仍安装 finclaw workspace skill）
USAGE
      exit 0 ;;
    *) echo "Error: unknown argument: $1" >&2; exit 1 ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── 颜色输出 ──────────────────────────────────────────────────────────────────
_info()  { echo -e "\033[1;34m[FinClaw]\033[0m $*"; }
_ok()    { echo -e "\033[1;32m[FinClaw]\033[0m $*"; }
_warn()  { echo -e "\033[1;33m[FinClaw]\033[0m $*" >&2; }
_error() { echo -e "\033[1;31m[FinClaw]\033[0m $*" >&2; exit 1; }

# ── 检查 Python ───────────────────────────────────────────────────────────────
PYTHON=""
for cmd in python3 python; do
  if command -v "$cmd" &>/dev/null; then
    ver=$("$cmd" -c 'import sys; print(sys.version_info >= (3,8))' 2>/dev/null || echo "False")
    if [[ "$ver" == "True" ]]; then
      PYTHON="$cmd"
      break
    fi
  fi
done

[[ -z "$PYTHON" ]] && _error "需要 Python 3.8+，请先安装 Python。"
_info "使用 $PYTHON ($($PYTHON --version))"

# ── 安装 FinClaw CLI ──────────────────────────────────────────────────────────
_info "安装 FinClaw CLI..."
"$PYTHON" -m pip install --quiet --upgrade finskillshub

# 验证安装，修复 PATH
if ! command -v finclaw &>/dev/null; then
  USER_BIN="$($PYTHON -m site --user-base)/bin"
  export PATH="$PATH:$USER_BIN"
  if ! command -v finclaw &>/dev/null; then
    _warn "finclaw 命令未找到，请将以下路径加入 PATH：$USER_BIN"
  fi
fi

_ok "FinClaw CLI 安装完成 → $(finclaw --version 2>/dev/null || echo 'finclaw')"

# ── 安装 finclaw workspace skill ──────────────────────────────────────────────
# 把 finclaw.md 安装到 openclaw workspace，让 Agent 自动感知 finclaw 的存在
OPENCLAW_WORKSPACE="${OPENCLAW_WORKSPACE:-${HOME}/.openclaw/workspace}"
FINCLAW_SKILL_DIR="${OPENCLAW_WORKSPACE}/skills/finclaw"

install_workspace_skill() {
  local src=""

  # 优先用安装包里的 finclaw.md（离线安装场景）
  if [[ -f "${SCRIPT_DIR}/skill/finclaw.md" ]]; then
    src="${SCRIPT_DIR}/skill/finclaw.md"
  elif [[ -f "${SCRIPT_DIR}/finclaw.md" ]]; then
    src="${SCRIPT_DIR}/finclaw.md"
  else
    # 从 GitHub 下载
    local tmp_md
    tmp_md="$(mktemp)"
    if curl -fsSL \
        "https://raw.githubusercontent.com/aifinlab/FinClaw/main/finclaw.md" \
        -o "$tmp_md" 2>/dev/null; then
      src="$tmp_md"
    fi
  fi

  if [[ -z "$src" ]]; then
    _warn "无法获取 finclaw.md，跳过 workspace skill 安装。"
    return 0
  fi

  mkdir -p "${FINCLAW_SKILL_DIR}"
  cp "$src" "${FINCLAW_SKILL_DIR}/SKILL.md"
  _ok "workspace skill 已安装 → ${FINCLAW_SKILL_DIR}/SKILL.md"
}

install_workspace_skill

if [[ "$CLI_ONLY" == "true" ]]; then
  echo ""
  echo "  运行 'finclaw list' 查看可用 Skills"
  echo "  运行 'finclaw install <id>' 安装 Skill"
  exit 0
fi

# ── 安装默认 Skills ───────────────────────────────────────────────────────────
if [[ "$SKILLS_PREF" != "off" ]]; then
  DEFAULT_SKILLS=("akshare-stock" "akshare-fund")
  _info "安装默认 Skills: ${DEFAULT_SKILLS[*]}"
  finclaw install "${DEFAULT_SKILLS[@]}" \
    || _warn "部分默认 Skills 安装失败，可稍后手动运行 finclaw install。"
else
  _info "跳过默认 Skills 安装（--no-skills）"
fi

# ── 完成提示 ──────────────────────────────────────────────────────────────────
echo ""
_ok "FinClaw 安装完成！"
echo ""
echo "  finclaw list                  查看所有可用 Skills"
echo "  finclaw search 股票           搜索 Skills"
echo "  finclaw install akshare-stock 安装 Skill"
echo "  finclaw path                  查看 Skills 存储路径"
echo ""
echo "  workspace skill: ${FINCLAW_SKILL_DIR}/SKILL.md"
echo "  建议重启 Agent 以加载 FinClaw 能力。"
