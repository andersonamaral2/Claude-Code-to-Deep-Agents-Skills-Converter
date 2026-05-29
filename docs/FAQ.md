# FAQ — Universal SKILL.md Converter

Common questions about what this tool does, how it converts, and where it's verified.
Portuguese version: [FAQ.pt.md](FAQ.pt.md).

---

## Do I even need this?

### Cursor already reads `.claude/skills/` — why convert at all?

For **Claude Code → Cursor**, often you don't need to: Cursor reads `.claude/skills/` (and
`.codex/skills/`) as legacy paths, so an existing skill frequently just works. Converting buys
you two things: a clean native `.cursor/skills/` layout, and access to Cursor-only frontmatter
like `paths` and `disable-model-invocation`.

The bigger wins are the directions Cursor does **not** auto-handle — Claude Code ↔ **Codex**
(strict frontmatter rules), ↔ **Qwen Code** (camelCase `allowedTools` with snake_case tool
names), and ↔ **Deep Agents** (typed, explicit tools).

### They're all converging on `SKILL.md` — won't this be obsolete soon?

The *file* is converging; the *rules around it* are not — and that's the whole problem. Same
filename, but:

- Codex forbids `<`/`>` in the description and allows only five frontmatter keys.
- Qwen wants `allowedTools` in camelCase with snake_case tool names.
- Cursor requires `name` to match the folder and doesn't use `allowed-tools`.
- The memory file (`CLAUDE.md` vs `AGENTS.md` vs `QWEN.md`) and MCP config differ per tool.

Until those converge too, "just copy the file" silently breaks. If they fully converge, great —
this becomes a thin validator, which is still useful.

### Isn't this just find-and-replace? Why a skill / LLM?

For the three natural-language targets it's deliberately close to that — we call it **Tier A**:
remap frontmatter keys, paths, the memory file, and MCP config. That mechanical part is real,
and `scripts/validate-conversion.sh` enforces each CLI's rules deterministically in plain bash.

The model matters for the messy bits — deriving a valid `name`/`description`, rewriting a
description that contains `<`/`>` for Codex, preserving 100% of the domain prose — and for
**Tier B** (Claude Code ↔ Deep Agents), where implicit "create the file" must become explicit
`write_file` / `execute` / `task` calls. That part is not regex-able.

---

## Conversion fidelity & correctness

### Did you actually verify converted skills load in each tool?

Partially, and the scope matters. We verified the **formats and validators against the
installed binaries**:

- **Codex 0.98.0** discovers skills under `$CODEX_HOME/skills` and ships
  `skill-creator/scripts/quick_validate.py`, which restricts frontmatter to
  `{name, description, license, allowed-tools, metadata}`, requires `name` to match
  `^[a-z0-9-]+$` (≤64 chars), and **rejects `<`/`>` in the description** (≤1024 chars). The
  Codex example passes that validator.
- **Qwen Code 0.17.0** — the example is modeled on Qwen's own bundled skills (`qc-helper`,
  `review`), so it is valid by construction.

What we did **not** do is a live end-to-end agent run in every tool (Codex auth was expired
during testing; Qwen needs an interactive session). So: format-validated and validator-checked,
not "watched the agent execute it in all four." Live-run evidence will be added over time.

### Does bidirectional / round-trip conversion lose information?

Domain knowledge (code, tables, steps, formulas) is preserved in both directions — that's the
hard invariant. The *envelope* isn't always loss-free: e.g. Deep Agents → Claude Code drops the
explicit tool annotations (they're implicit in Claude Code), and a target that lacks a given
field has nowhere to put it. Those losses are noted, never hidden.

### How does it handle sub-agents, hooks, and extended thinking?

It **flags non-portable features instead of silently dropping them**. Cursor has no skill-level
sub-agents, so a skill that fans work out to `Task` gets a note that those steps run
sequentially there; Codex/Qwen keep `task`. Claude Code hooks (`settings.json`) and
extended-thinking blocks get the same treatment: a visible note rather than a skill that looks
complete but isn't.

### How does it handle MCP servers?

It remaps both the **path** and the **format**, and preserves the `mcp__server__tool` call
names unchanged:

- Claude Code `.claude/mcp.json` → Deep Agents `.deepagents/mcp.json` (same JSON schema)
- → Codex `[mcp_servers.*]` in `config.toml`
- → Qwen Code `mcpServers` in `settings.json`
- → Cursor `.cursor/mcp.json`

See **Example 12** in `SKILL.en.md` for a full before/after, including the
`--trust-project-mcp` note for first-use approval of project-level stdio servers.

---

## Per-tool specifics

### What exactly differs between the targets?

The full mapping lives in the
[cross-format reference matrix](../SKILL.en.md#cross-format-reference-matrix). Summary:

| Concept | Claude Code | Deep Agents | Codex | Qwen Code | Cursor |
|---------|-------------|-------------|-------|-----------|--------|
| Skill dir (user) | `~/.claude/skills/` | `~/.deepagents/agent/skills/` | `~/.codex/skills/` | `~/.qwen/skills/` | `~/.cursor/skills/` |
| Memory file | `CLAUDE.md` | `AGENTS.md` | `AGENTS.md` | `QWEN.md` | `AGENTS.md` / Rules |
| Tools | implicit | typed (`write_file`…) | implicit (`apply_patch`) | snake_case (`read_file`…) | implicit |
| `name` rule | hyphen-case | hyphen-case | hyphen-case ≤64 | unicode slug | `name` == folder |

### Why is Deep Agents the "odd one out"?

The other four run natural-language skills (the agent infers when to read/write/run). Deep
Agents CLI uses typed, explicit tools — `write_file`, `edit_file`, `execute`, `task`,
`write_todos` — so "create the file X" must be rewritten to "use `write_file` to create X",
with inline tests after each step. That heavier translation is the **Tier B** path the project
started with.

---

## Project

### License? Commercial use?

MIT — use, fork, adapt, and ship it.

### Why bilingual (EN/PT)?

The maintainer is Brazilian and wanted the Portuguese-speaking dev community covered too. Docs,
the skill, and this FAQ all ship in both languages, and an EN/PT parity check runs in CI.

### How do you keep up as these CLIs change their formats?

The format facts are pinned to **specific verified versions** (Codex 0.98.0, Qwen Code 0.17.0)
and documented as such, and `scripts/validate-conversion.sh` encodes each CLI's real rules so
drift surfaces as a failing check. When a CLI changes, the matrix and validator are updated
against the new installed binary — not against possibly-stale docs.

### How do I install and use it?

One-liner (defaults to Deep Agents; use `--target` for another CLI):

```bash
curl -fsSL https://raw.githubusercontent.com/andersonamaral2/Claude-Code-to-Deep-Agents-Skills-Converter/main/install.sh | bash
```

Full instructions, all install methods, and usage examples are in the
[README](../README.md).
