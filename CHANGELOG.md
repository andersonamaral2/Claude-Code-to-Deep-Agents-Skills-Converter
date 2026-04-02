# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

[2.1.0]: https://github.com/andersonamaral2/Claude-Code-to-Deep-Agents-Skills-Converter/releases/tag/v2.1.0
[2.0.0]: https://github.com/andersonamaral2/Claude-Code-to-Deep-Agents-Skills-Converter/releases/tag/v2.0.0
[1.0.0]: https://github.com/andersonamaral2/Claude-Code-to-Deep-Agents-Skills-Converter/releases/tag/v1.0.0
