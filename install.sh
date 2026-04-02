#!/bin/bash
# ============================================================================
# Claude Code ↔ Deep Agents Skill Converter — Installer
# ============================================================================
#
# Installs the skill-converter skill into Deep Agents CLI so it's available
# globally via `deepagents skills list`.
#
# Usage:
#   ./install.sh                  # Install for default agent ("agent")
#   ./install.sh --agent myagent  # Install for a specific agent
#   ./install.sh --uninstall      # Remove the installed skill
#
# One-liner (clone + install):
#   git clone https://github.com/andersonamaral2/Claude-Code-to-Deep-Agents-Skills-Converter.git && cd Claude-Code-to-Deep-Agents-Skills-Converter && ./install.sh
#
# ============================================================================

set -euo pipefail

SKILL_NAME="skill-converter"
AGENT_NAME="agent"
UNINSTALL=false
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

print_banner() {
    echo -e "${CYAN}"
    echo "  ╔══════════════════════════════════════════════════════════╗"
    echo "  ║   Claude Code ↔ Deep Agents Skill Converter            ║"
    echo "  ║   Installer v2.0                                       ║"
    echo "  ╚══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --agent)
            AGENT_NAME="$2"
            shift 2
            ;;
        --uninstall)
            UNINSTALL=true
            shift
            ;;
        --help|-h)
            echo "Usage: ./install.sh [--agent NAME] [--uninstall]"
            echo ""
            echo "Options:"
            echo "  --agent NAME    Agent identifier (default: agent)"
            echo "  --uninstall     Remove the installed skill"
            echo "  --help          Show this help"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
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
        echo -e "${GREEN}Uninstalled ${SKILL_NAME} (removed symlink)${NC}"
    elif [ -d "$TARGET_DIR" ]; then
        rm -rf "$TARGET_DIR"
        echo -e "${GREEN}Uninstalled ${SKILL_NAME} (removed directory)${NC}"
    else
        echo -e "${YELLOW}Skill ${SKILL_NAME} is not installed for agent '${AGENT_NAME}'${NC}"
    fi
    exit 0
fi

# --- Install ---
print_banner

# Check Deep Agents CLI
if ! command -v deepagents &>/dev/null; then
    echo -e "${RED}Error: deepagents CLI not found.${NC}"
    echo "Install it first: pip install deepagents-cli"
    exit 1
fi

echo -e "${GREEN}✓${NC} Deep Agents CLI found: $(deepagents -v 2>&1 | head -1)"

# Check that SKILL.en.md exists in the repo
if [ ! -f "$REPO_DIR/SKILL.en.md" ]; then
    echo -e "${RED}Error: SKILL.en.md not found in $REPO_DIR${NC}"
    echo "Make sure you're running this from the cloned repository."
    exit 1
fi

# Detect language
LANG_PREF="${LANG:-en}"
if echo "$LANG_PREF" | grep -qi "^pt"; then
    SKILL_SOURCE="$REPO_DIR/SKILL.pt.md"
    echo -e "${CYAN}→${NC} Detected Portuguese locale, using SKILL.pt.md"
else
    SKILL_SOURCE="$REPO_DIR/SKILL.en.md"
    echo -e "${CYAN}→${NC} Using SKILL.en.md (English)"
fi

# Create skills directory if needed
mkdir -p "$SKILLS_DIR"

# Remove old installation if exists
if [ -L "$TARGET_DIR" ] || [ -d "$TARGET_DIR" ]; then
    echo -e "${YELLOW}→${NC} Removing previous installation..."
    rm -rf "$TARGET_DIR"
fi

# Create skill directory and install
mkdir -p "$TARGET_DIR"

# Build the SKILL.md with proper YAML frontmatter
cat > "$TARGET_DIR/SKILL.md" <<FRONTMATTER
---
name: skill-converter
description: "Converts any SKILL.md between Claude Code and Deep Agents CLI formats — preserving 100% of domain knowledge while adapting the execution interface. Supports forward, reverse, dry-run, and batch conversion."
metadata:
  converted-from: claude-code
  converter-version: "2.0"
  deep-agents-compat: ">=0.0.34"
  source-repo: "https://github.com/andersonamaral2/Claude-Code-to-Deep-Agents-Skills-Converter"
---

FRONTMATTER

# Append the actual skill content (skip any existing frontmatter if present)
if head -1 "$SKILL_SOURCE" | grep -q '^---'; then
    # Has frontmatter — skip it
    awk 'BEGIN{skip=1} /^---$/{count++; if(count==2){skip=0; next}} !skip{print}' "$SKILL_SOURCE" >> "$TARGET_DIR/SKILL.md"
else
    # No frontmatter — append as-is
    cat "$SKILL_SOURCE" >> "$TARGET_DIR/SKILL.md"
fi

echo -e "${GREEN}✓${NC} Skill installed to: ${TARGET_DIR}/SKILL.md"

# Verify it shows up
echo ""
echo -e "${CYAN}Verifying installation...${NC}"
if deepagents skills info "$SKILL_NAME" --agent "$AGENT_NAME" 2>&1 | grep -qi "skill-converter\|converter"; then
    echo -e "${GREEN}✓${NC} Skill '${SKILL_NAME}' is registered and visible!"
else
    echo -e "${GREEN}✓${NC} Skill installed. Run 'deepagents skills list' to verify."
fi

echo ""
echo -e "${GREEN}Installation complete!${NC}"
echo ""
echo "Usage:"
echo "  deepagents -y \"Convert this Claude Code skill to Deep Agents: <paste or path>\""
echo "  deepagents    (then ask to convert a skill interactively)"
echo ""
echo "To uninstall:"
echo "  ./install.sh --uninstall"
echo ""
