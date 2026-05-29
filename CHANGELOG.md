# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Express.js full-stack conversion example** (closes #1): `examples/claude-code-sample-3/SKILL.md` → `examples/deep-agents-output-3/SKILL.md` — a real-world Express + JWT + PostgreSQL + Docker Compose skill with layered middleware and env-var handling, fully converted with all T1–T8 transformations. Wired into the CI example validator and listed in README EN/PT.
- **MCP tool conversion example** (closes #3): Example 12 added to `SKILL.en.md` and `SKILL.pt.md` (in sync) showing `.claude/mcp.json` → `.deepagents/mcp.json`, preserved `mcp__server__tool` calls, token verification, and the `--trust-project-mcp` note (plus pointers to the Codex/Qwen/Cursor MCP config locations).
- **`install.sh --target <deepagents|claude|codex|qwen|cursor>`** — install the converter skill into any of the five CLIs' skill directories (defaults to Deep Agents). The Deep Agents CLI check is now skipped for other targets, and the verify/quick-start output is target-aware. Injected frontmatter updated to the universal v2.2 description (angle-bracket-free, so it passes Codex's validator).
- **CI hardening** in `lint.yml`: a **gitleaks secret-scan** job (scans the working tree, fails on any finding) and an **EN/PT parity** job (heading-count check for SKILL and README pairs — closes issue #4). The installer job also asserts an invalid `--target` is rejected.
- **Qwen Code converter** (bidirectional, Tier A), verified against Qwen Code 0.17.0 bundled skills: `.qwen/skills/<name>/SKILL.md`, frontmatter `name`/`description` + optional `allowedTools` (snake_case YAML list), `argument-hint`, `when_to_use`, `paths`, `disable-model-invocation`, `priority`. Key step is the snake_case tool-name remap (`Read`→`read_file`, `Bash`→`run_shell_command`, …). `CLAUDE.md`→`QWEN.md`.
- `examples/qwen-output/python-fastapi-todo-app/SKILL.md` — FastAPI Todo sample converted to a Qwen Code skill, modeled on Qwen's own bundled skills.
- `validate-conversion.sh`: Qwen target checks folder==name (convention) and flags Claude-style tool names in `allowedTools`. CI validates the Qwen example.
- **Cursor converter** (bidirectional, Tier A): `.cursor/skills/<name>/SKILL.md` with the skill `name` matching its parent folder; frontmatter `name`/`description` + optional `paths`/`disable-model-invocation`/`metadata` (no `allowed-tools`). Documents Cursor's legacy reading of `.claude/skills/`/`.codex/skills/` and flags sub-agents as non-portable.
- `examples/cursor-output/python-fastapi-todo-app/SKILL.md` — FastAPI Todo sample converted to Cursor format (folder named to match `name`).
- `validate-conversion.sh`: Cursor target now checks `name` == parent folder and warns on `allowed-tools`. CI validates the Cursor example.

## [2.2.0] - 2026-05-29

### Added

- **Universal multi-format conversion.** The converter now targets five ecosystems in any direction: Claude Code, Deep Agents CLI, Codex CLI, Qwen Code, and Cursor.
- **Cross-format reference matrix** in `SKILL.en.md` / `SKILL.pt.md` mapping skill paths, frontmatter fields, memory files, tool names, MCP config, and command arguments across all five formats.
- **Source/target format detection** via fingerprints, and a **two-tier model**: Tier A (light remap for the natural-language SKILL.md targets — Codex/Qwen/Cursor) and Tier B (the existing heavy Claude Code ↔ Deep Agents T1–T8 translation).
- **Codex CLI converter** (bidirectional), verified against Codex CLI 0.98.0: `$CODEX_HOME/skills` layout, strict frontmatter allow-list (`name`, `description`, `license`, `allowed-tools`, `metadata`), and the no-`<`/`>`-in-description rule.
- `examples/codex-output/SKILL.md` — full before/after of the FastAPI Todo sample converted to Codex format (passes Codex's bundled `quick_validate.py`).
- `scripts/validate-conversion.sh` — dependency-light, multi-target conversion validator (Codex rules implemented; Cursor/Qwen/Deep Agents/Claude targets scaffolded). Wired into CI.

### Changed

- Skill renamed in spirit to **Universal SKILL.md Converter** (skill `name` stays `skill-converter` for install compatibility); `converter-version` bumped to `2.2`.
- `.github/workflows/lint.yml` now validates the Codex example with `validate-conversion.sh`.
- Golden Rules reorganized into Universal rules + Tier B additions.

## [2.1.0] - 2026-04-02

### Added

- `install.sh` — self-contained installer that works in two modes:
  - **Standalone**: `curl -fsSL .../install.sh | bash` (no git clone needed)
  - **Local**: `./install.sh` from cloned repo
- Auto-detects locale (`$LANG`) and picks English or Portuguese skill
- `--agent NAME` flag for multi-agent setups
- `--lang en|pt` flag to force language
- `--uninstall` flag for clean removal
- Deep Agents self-install option: `deepagents -y -S all -n "Run: curl ... | bash"`
- YAML frontmatter added to SKILL.en.md and SKILL.pt.md source files
- Complete before/after conversion examples with full T1-T8 transformations (FastAPI Todo App, Docker Monitoring Stack)

### Changed

- README.md, README.en.md, README.pt.md rewritten with 4 installation methods (A: curl one-liner, B: clone+install, C: Deep Agents self-install, D: manual)
- Examples in `examples/deep-agents-output/` and `examples/deep-agents-output-2/` rewritten to demonstrate all 8 mandatory transformations
- Fixed CLAUDE.md → AGENTS.md semantic replacement in example 2

## [2.0.0] - 2026-04-02

### Added

- Bidirectional conversion: Deep Agents → Claude Code (reverse conversion)
- Dry-run / preview mode: see diff before saving
- Batch conversion: convert multiple skills at once via sub-agents
- Inline command detection: catches backtick-wrapped commands inside sentences
- Environment variables and secrets handling with verification scripts
- Conditional / platform-specific flow conversion (shell case/if blocks)
- MCP custom tool call conversion handling
- Claude Code Agent tool → Deep Agents `task` mapping
- Claude Code hooks (settings.json) → shell scripts conversion
- Extended thinking / reasoning blocks handling
- YAML frontmatter with skill metadata and version compatibility
- Executable validation checklist (grep-based, replaces "verify mentally")
- Full real-world conversion example (Express.js API with JWT, Docker, env vars)
- 5 new conversion examples (inline commands, env vars, conditionals, Agent tool, full app)
- 4 new Golden Rules (inline commands, env vars, conditionals, validation)
- Compatibility section in README with Deep Agents CLI version info

### Changed

- T1 (Execution Context) now emphasizes listing only used tools
- T3 (Prerequisites) now includes environment variable checks
- T8 (Troubleshooting) now includes env var and context window sections
- Semantic replacement table expanded with Agent tool, hooks, and MCP entries
- Pattern detection expanded from 6 categories (2a-2f) to 12 (2a-2l)
- Conversion procedure expanded from 7 steps to 8 steps
- Golden Rules expanded from 6 to 10

## [1.0.0] - 2026-04-02

### Added

- Bilingual skill converter (English & Portuguese)
- 8 mandatory transformations (T1-T8) for Claude Code to Deep Agents conversion
- Automatic semantic replacements for tools, paths, and conventions
- Support for global and local skill installation
- 4 usage methods: file-based, paste, direct registration, and non-interactive
- Complete documentation in English (`README.en.md`, `SKILL.en.md`)
- Complete documentation in Portuguese (`README.pt.md`, `SKILL.pt.md`)

[2.2.0]: https://github.com/andersonamaral2/Claude-Code-to-Deep-Agents-Skills-Converter/releases/tag/v2.2.0
[2.1.0]: https://github.com/andersonamaral2/Claude-Code-to-Deep-Agents-Skills-Converter/releases/tag/v2.1.0
[2.0.0]: https://github.com/andersonamaral2/Claude-Code-to-Deep-Agents-Skills-Converter/releases/tag/v2.0.0
[1.0.0]: https://github.com/andersonamaral2/Claude-Code-to-Deep-Agents-Skills-Converter/releases/tag/v1.0.0
