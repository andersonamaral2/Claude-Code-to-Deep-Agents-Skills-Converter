#!/usr/bin/env bash
#
# validate-conversion.sh — validate a converted SKILL.md against a target format.
#
# Part of the Universal SKILL.md Converter.
# Repo: https://github.com/andersonamaral2/Claude-Code-to-Deep-Agents-Skills-Converter
#
# Usage:
#   scripts/validate-conversion.sh --target <codex|cursor|qwen|deepagents|claude> <path>
#
#   <path> may be either a skill directory (containing SKILL.md) or a SKILL.md file.
#
# Exit codes: 0 = valid, 1 = validation errors, 2 = usage error.
#
# The checks here mirror the rules each target CLI enforces (e.g. Codex's own
# quick_validate.py: name hyphen-case <=64, description <=1024 and no angle
# brackets, restricted frontmatter keys). It is intentionally dependency-light
# (pure bash + grep/sed) so it runs in CI without extra tooling.

set -euo pipefail

TARGET=""
TARGET_PATH=""

usage() {
  echo "Usage: $0 --target <codex|cursor|qwen|deepagents|claude> <path-to-skill-dir-or-SKILL.md>" >&2
  exit 2
}

while [ $# -gt 0 ]; do
  case "$1" in
    --target) TARGET="${2:-}"; shift 2 ;;
    -h|--help) usage ;;
    *) TARGET_PATH="$1"; shift ;;
  esac
done

[ -n "$TARGET" ] || usage
[ -n "$TARGET_PATH" ] || usage

# Resolve the SKILL.md file from a directory or direct file path.
if [ -d "$TARGET_PATH" ]; then
  FILE="$TARGET_PATH/SKILL.md"
elif [ -f "$TARGET_PATH" ]; then
  FILE="$TARGET_PATH"
else
  echo "ERROR: path not found: $TARGET_PATH" >&2
  exit 2
fi

if [ ! -f "$FILE" ]; then
  echo "ERROR: SKILL.md not found at: $FILE" >&2
  exit 2
fi

ERRORS=0
WARNINGS=0

err()  { echo "  [ERROR] $1";   ERRORS=$((ERRORS + 1)); }
warn() { echo "  [WARN]  $1";   WARNINGS=$((WARNINGS + 1)); }
ok()   { echo "  [OK]    $1"; }

echo "=== Validating $FILE (target: $TARGET) ==="

# --- Extract YAML frontmatter (between the first two '---' lines) -------------
FRONTMATTER=""
if head -1 "$FILE" | grep -q '^---[[:space:]]*$'; then
  FRONTMATTER="$(sed -n '2,/^---[[:space:]]*$/p' "$FILE" | sed '$d')"
fi

# Helper: read a top-level scalar frontmatter field value (strips quotes).
fm_field() {
  printf '%s\n' "$FRONTMATTER" \
    | grep -E "^$1:[[:space:]]*" \
    | head -1 \
    | sed -E "s/^$1:[[:space:]]*//; s/^[\"']//; s/[\"' ]*$//"
}

# --- Common checks: frontmatter required for every SKILL.md target ------------
needs_frontmatter() {
  case "$TARGET" in
    claude) return 1 ;;   # Claude Code skills do not require YAML frontmatter
    *)       return 0 ;;
  esac
}

if needs_frontmatter; then
  if [ -z "$FRONTMATTER" ]; then
    err "no YAML frontmatter found (target '$TARGET' requires it)"
  else
    ok "YAML frontmatter present"
    NAME="$(fm_field name)"
    DESC="$(fm_field description)"
    [ -n "$NAME" ] || err "frontmatter missing required 'name'"
    [ -n "$DESC" ] || err "frontmatter missing required 'description'"

    # name rules shared by Codex/Cursor/Qwen skills (hyphen-case, <=64).
    if [ -n "$NAME" ]; then
      if ! printf '%s' "$NAME" | grep -qE '^[a-z0-9-]+$'; then
        err "name '$NAME' must be hyphen-case (lowercase letters, digits, hyphens)"
      elif printf '%s' "$NAME" | grep -qE '(^-|-$|--)'; then
        err "name '$NAME' cannot start/end with a hyphen or contain '--'"
      elif [ "${#NAME}" -gt 64 ]; then
        err "name is too long (${#NAME} chars, max 64)"
      else
        ok "name '$NAME' is well-formed"
      fi
    fi

    # description length (<=1024) shared across targets.
    if [ -n "$DESC" ] && [ "${#DESC}" -gt 1024 ]; then
      err "description is too long (${#DESC} chars, max 1024)"
    fi
  fi
fi

# --- Target-specific checks ---------------------------------------------------
case "$TARGET" in
  codex)
    # Codex's quick_validate.py forbids '<' and '>' in the description.
    if [ -n "${DESC:-}" ] && printf '%s' "$DESC" | grep -q '[<>]'; then
      err "description contains angle brackets (< or >) — Codex rejects these"
    fi
    # Codex allows only these frontmatter keys.
    if [ -n "$FRONTMATTER" ]; then
      while IFS= read -r key; do
        [ -n "$key" ] || continue
        case "$key" in
          name|description|license|allowed-tools|metadata) ;;
          *) warn "frontmatter key '$key' is not in Codex's allow-list (name, description, license, allowed-tools, metadata)" ;;
        esac
      done < <(printf '%s\n' "$FRONTMATTER" | grep -E '^[A-Za-z0-9_-]+:' | sed -E 's/:.*//')
    fi
    # Codex skills live in <name>/SKILL.md; warn on stale Claude/Deep Agents refs.
    grep -q 'CLAUDE\.md' "$FILE" && warn "stale reference 'CLAUDE.md' (Codex uses AGENTS.md)"
    grep -q '\.claude/'  "$FILE" && warn "stale reference '.claude/' (Codex uses .codex/ or ~/.codex/skills)"
    grep -qE '\bwrite_file\b|\bedit_file\b|\bexecute\b tool' "$FILE" && \
      warn "Deep Agents tool names present — Codex uses implicit shell/apply_patch, not write_file/execute"
    ;;
  cursor)
    # Cursor requires the skill 'name' to match its parent folder name.
    PARENT="$(basename "$(dirname "$FILE")")"
    if [ -n "${NAME:-}" ]; then
      if [ "$NAME" != "$PARENT" ]; then
        err "Cursor requires 'name' ('$NAME') to match the parent folder name ('$PARENT')"
      else
        ok "name matches parent folder ('$PARENT')"
      fi
    fi
    printf '%s\n' "$FRONTMATTER" | grep -qE '^allowed-tools:' && \
      warn "'allowed-tools' is not used by Cursor skills — safe to drop"
    grep -q 'CLAUDE\.md' "$FILE" && warn "stale reference 'CLAUDE.md' (Cursor uses AGENTS.md or .cursor/rules)"
    grep -q '\.claude/'  "$FILE" && warn "stale reference '.claude/' (Cursor reads .claude/skills as legacy but .cursor/skills is canonical)"
    ;;
  qwen)
    grep -q 'CLAUDE\.md' "$FILE" && warn "stale reference 'CLAUDE.md' (Qwen Code uses QWEN.md or AGENTS.md)"
    grep -q '\.claude/'  "$FILE" && warn "stale reference '.claude/' (Qwen Code uses .qwen/skills)"
    ;;
  deepagents)
    # Deep Agents conversions must be explicit about tools and sections.
    for section in "Execution Context" "Execution Plan" "Usage with Deep Agents"; do
      grep -q "$section" "$FILE" || warn "missing recommended Deep Agents section: $section"
    done
    grep -q 'CLAUDE\.md' "$FILE" && warn "stale reference 'CLAUDE.md' (Deep Agents uses AGENTS.md)"
    grep -q '\.claude/'  "$FILE" && warn "stale reference '.claude/' (Deep Agents uses .deepagents/)"
    ;;
  claude)
    # Reverse target: should NOT carry target-specific tool names / frontmatter noise.
    grep -q 'AGENTS\.md\|QWEN\.md' "$FILE" && warn "reference to AGENTS.md/QWEN.md remains (Claude Code uses CLAUDE.md)"
    grep -qE '\bwrite_file\b|\bedit_file\b|\bapply_patch\b' "$FILE" && \
      warn "explicit tool names remain (Claude Code uses implicit file operations)"
    ;;
  *)
    echo "ERROR: unknown target '$TARGET'" >&2
    exit 2
    ;;
esac

echo "=== Result: $ERRORS error(s), $WARNINGS warning(s) ==="
[ "$ERRORS" -eq 0 ]
