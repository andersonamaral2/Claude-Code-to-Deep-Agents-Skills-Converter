#!/bin/bash
# ============================================================================
# Claude Code ↔ Deep Agents Skill Converter — Installer v2.1
# ============================================================================
#
# Works in two modes:
#
#   STANDALONE (curl | bash) — downloads the skill directly from GitHub:
#     curl -fsSL https://raw.githubusercontent.com/andersonamaral2/Claude-Code-to-Deep-Agents-Skills-Converter/main/install.sh | bash
#
#   LOCAL (from cloned repo) — uses the local SKILL files:
#     git clone https://github.com/andersonamaral2/Claude-Code-to-Deep-Agents-Skills-Converter.git
#     cd Claude-Code-to-Deep-Agents-Skills-Converter
#     ./install.sh
#
# Options:
#   --agent NAME    Install for a specific agent (default: "agent")
#   --lang en|pt    Force language (default: auto-detect from $LANG)
#   --uninstall     Remove the installed skill
#   --help          Show this help
#
# ============================================================================

set -euo pipefail

# --- Config ---
SKILL_NAME="skill-converter"
AGENT_NAME="agent"
FORCE_LANG=""
UNINSTALL=false
GITHUB_RAW="https://raw.githubusercontent.com/andersonamaral2/Claude-Code-to-Deep-Agents-Skills-Converter/main"
GITHUB_REPO="https://github.com/andersonamaral2/Claude-Code-to-Deep-Agents-Skills-Converter"

# --- Colors ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# --- Detect mode ---
# If SKILL.en.md exists next to this script, we're in LOCAL mode.
# If piped via curl or SKILL.en.md is missing, we're in STANDALONE mode.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}" 2>/dev/null)" && pwd 2>/dev/null || echo "")"
if [ -n "$SCRIPT_DIR" ] && [ -f "$SCRIPT_DIR/SKILL.en.md" ]; then
    MODE="local"
else
    MODE="standalone"
fi

# --- Functions ---

print_banner() {
    echo ""
    echo -e "${CYAN}  ╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}  ║${NC}  ${BOLD}Claude Code ↔ Deep Agents Skill Converter${NC}                ${CYAN}║${NC}"
    echo -e "${CYAN}  ║${NC}  Installer v2.1                                           ${CYAN}║${NC}"
    echo -e "${CYAN}  ╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_help() {
    echo "Usage:"
    echo ""
    echo "  ${BOLD}Standalone (no git clone needed):${NC}"
    echo "    curl -fsSL $GITHUB_RAW/install.sh | bash"
    echo "    curl -fsSL $GITHUB_RAW/install.sh | bash -s -- --lang pt"
    echo ""
    echo "  ${BOLD}From cloned repo:${NC}"
    echo "    ./install.sh"
    echo "    ./install.sh --lang pt"
    echo "    ./install.sh --agent myagent"
    echo ""
    echo "Options:"
    echo "  --agent NAME    Agent identifier (default: agent)"
    echo "  --lang en|pt    Force language (default: auto-detect from \$LANG)"
    echo "  --uninstall     Remove the installed skill"
    echo "  --help          Show this help"
    echo ""
}

detect_language() {
    if [ -n "$FORCE_LANG" ]; then
        echo "$FORCE_LANG"
        return
    fi
    local lang_pref="${LANG:-en}"
    if echo "$lang_pref" | grep -qi "^pt"; then
        echo "pt"
    else
        echo "en"
    fi
}

download_skill() {
    local url="$1"
    local dest="$2"
    if command -v curl &>/dev/null; then
        curl -fsSL "$url" -o "$dest"
    elif command -v wget &>/dev/null; then
        wget -qO "$dest" "$url"
    else
        echo -e "${RED}Error: neither curl nor wget found. Cannot download.${NC}"
        exit 1
    fi
}

build_skill_file() {
    local source_file="$1"
    local target_file="$2"

    # Write frontmatter
    cat > "$target_file" <<'FRONTMATTER'
---
name: skill-converter
description: "Converts any SKILL.md between Claude Code and Deep Agents CLI formats — preserving 100% of domain knowledge while adapting the execution interface. Supports forward, reverse, dry-run, and batch conversion."
metadata:
  converter-version: "2.1"
  deep-agents-compat: ">=0.0.34"
  source-repo: "https://github.com/andersonamaral2/Claude-Code-to-Deep-Agents-Skills-Converter"
---

FRONTMATTER

    # Append skill content, stripping any existing frontmatter
    if head -1 "$source_file" | grep -q '^---'; then
        awk 'BEGIN{skip=1} /^---$/{count++; if(count==2){skip=0; next}} !skip{print}' "$source_file" >> "$target_file"
    else
        cat "$source_file" >> "$target_file"
    fi
}

# --- Parse arguments ---
while [[ $# -gt 0 ]]; do
    case $1 in
        --agent)
            AGENT_NAME="$2"
            shift 2
            ;;
        --lang)
            FORCE_LANG="$2"
            if [[ "$FORCE_LANG" != "en" && "$FORCE_LANG" != "pt" ]]; then
                echo -e "${RED}Error: --lang must be 'en' or 'pt'${NC}"
                exit 1
            fi
            shift 2
            ;;
        --uninstall)
            UNINSTALL=true
            shift
            ;;
        --help|-h)
            print_help
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Run with --help for usage."
            exit 1
            ;;
    esac
done

SKILLS_DIR="$HOME/.deepagents/${AGENT_NAME}/skills"
TARGET_DIR="${SKILLS_DIR}/${SKILL_NAME}"

# --- Uninstall ---
if [ "$UNINSTALL" = true ]; then
    if [ -L "$TARGET_DIR" ]; then
        rm "$TARGET_DIR"
        echo -e "${GREEN}✓ Uninstalled ${SKILL_NAME} (removed symlink)${NC}"
    elif [ -d "$TARGET_DIR" ]; then
        rm -rf "$TARGET_DIR"
        echo -e "${GREEN}✓ Uninstalled ${SKILL_NAME} (removed directory)${NC}"
    else
        echo -e "${YELLOW}Skill ${SKILL_NAME} is not installed for agent '${AGENT_NAME}'${NC}"
    fi
    exit 0
fi

# =====================
#   INSTALL
# =====================
print_banner

# Check Deep Agents CLI
if ! command -v deepagents &>/dev/null; then
    echo -e "${RED}Error: deepagents CLI not found.${NC}"
    echo ""
    echo "Install it first:"
    echo "  pip install deepagents-cli"
    echo ""
    exit 1
fi
echo -e "${GREEN}✓${NC} Deep Agents CLI found: $(deepagents -v 2>&1 | head -1)"

# Detect language
LANG_CODE=$(detect_language)
if [ "$LANG_CODE" = "pt" ]; then
    SKILL_FILENAME="SKILL.pt.md"
    echo -e "${CYAN}→${NC} Idioma: Português (SKILL.pt.md)"
else
    SKILL_FILENAME="SKILL.en.md"
    echo -e "${CYAN}→${NC} Language: English (SKILL.en.md)"
fi

# Create target directory
mkdir -p "$SKILLS_DIR"
if [ -L "$TARGET_DIR" ] || [ -d "$TARGET_DIR" ]; then
    echo -e "${YELLOW}→${NC} Removing previous installation..."
    rm -rf "$TARGET_DIR"
fi
mkdir -p "$TARGET_DIR"

# --- Fetch skill based on mode ---
if [ "$MODE" = "local" ]; then
    # LOCAL MODE: use file from cloned repo
    SKILL_SOURCE="$SCRIPT_DIR/$SKILL_FILENAME"
    if [ ! -f "$SKILL_SOURCE" ]; then
        echo -e "${RED}Error: $SKILL_FILENAME not found in $SCRIPT_DIR${NC}"
        exit 1
    fi
    echo -e "${CYAN}→${NC} Mode: local (using cloned repo)"
    build_skill_file "$SKILL_SOURCE" "$TARGET_DIR/SKILL.md"
else
    # STANDALONE MODE: download from GitHub
    echo -e "${CYAN}→${NC} Mode: standalone (downloading from GitHub)"
    TMPFILE=$(mktemp)
    trap 'rm -f "$TMPFILE"' EXIT

    echo -e "${CYAN}→${NC} Downloading $SKILL_FILENAME..."
    download_skill "$GITHUB_RAW/$SKILL_FILENAME" "$TMPFILE"

    if [ ! -s "$TMPFILE" ]; then
        echo -e "${RED}Error: Failed to download $SKILL_FILENAME${NC}"
        echo "Check your internet connection or try:"
        echo "  git clone $GITHUB_REPO && cd Claude-Code-to-Deep-Agents-Skills-Converter && ./install.sh"
        exit 1
    fi
    echo -e "${GREEN}✓${NC} Downloaded successfully"
    build_skill_file "$TMPFILE" "$TARGET_DIR/SKILL.md"
fi

# Count lines to show size
LINES=$(wc -l < "$TARGET_DIR/SKILL.md")
echo -e "${GREEN}✓${NC} Skill installed to: ${BOLD}${TARGET_DIR}/SKILL.md${NC} (${LINES} lines)"

# Verify
echo ""
echo -e "${CYAN}Verifying installation...${NC}"
if deepagents skills info "$SKILL_NAME" --agent "$AGENT_NAME" 2>&1 | grep -qi "skill-converter\|converter"; then
    echo -e "${GREEN}✓${NC} Skill '${BOLD}${SKILL_NAME}${NC}' is registered and visible in Deep Agents CLI!"
else
    echo -e "${GREEN}✓${NC} Skill installed. Run '${BOLD}deepagents skills list${NC}' to verify."
fi

# --- Success message ---
echo ""
echo -e "${GREEN}${BOLD}Installation complete!${NC}"
echo ""
echo -e "${BOLD}Quick start:${NC}"
echo "  deepagents -y"
echo "  > Convert this Claude Code skill to Deep Agents: <paste or path>"
echo ""
echo -e "${BOLD}Or non-interactive:${NC}"
echo "  deepagents -y -n \"Convert the Claude Code skill at ./my-skill/SKILL.md to Deep Agents format\""
echo ""
echo -e "${BOLD}Uninstall:${NC}"
if [ "$MODE" = "local" ]; then
    echo "  ./install.sh --uninstall"
else
    echo "  rm -rf $TARGET_DIR"
fi
echo ""
