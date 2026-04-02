# Claude Code ↔ Deep Agents Skill Converter

> Bidirectional converter between SKILL.md formats for Claude Code and Deep Agents CLI — preserving 100% of domain knowledge while adapting the execution interface.

> Conversor bidirecional entre formatos SKILL.md do Claude Code e Deep Agents CLI — preservando 100% do conhecimento de dominio e adaptando a interface de execucao.

---

## Languages / Idiomas

- [English](/README.en.md)
- [Portugues](/README.pt.md)

---

## Repository Structure

- `README.md` - This file (navigation hub)
- `README.en.md` - Full documentation in English
- `README.pt.md` - Documentacao completa em Portugues
- `SKILL.en.md` - Skill definition for Deep Agents CLI (English)
- `SKILL.pt.md` - Definicao da skill para Deep Agents CLI (Portugues)
- `install.sh` - One-command installer for Deep Agents CLI
- `CHANGELOG.md` - Version history
- `CONTRIBUTING.md` - Contribution guidelines
- `LICENSE` - MIT License

---

## Quick Start / Inicio Rapido

### Install / Instalar
```bash
curl -fsSL https://raw.githubusercontent.com/andersonamaral2/Claude-Code-to-Deep-Agents-Skills-Converter/main/install.sh | bash
```

### Use / Usar
```bash
deepagents -y
> Convert this Claude Code skill to Deep Agents
```

> Auto-detects your locale (EN/PT). See full install options in [English](/README.en.md#installation) or [Portugues](/README.pt.md#instalação).

---

## What's New in v2.0

- **Bidirectional conversion** — Now converts Deep Agents → Claude Code too
- **Dry-run / preview mode** — See the diff before saving
- **Batch conversion** — Convert multiple skills at once
- **Inline command detection** — Catches backtick-wrapped commands inside sentences
- **Environment variables handling** — Explicit verification and `.env` support
- **Conditional / platform-specific flows** — OS detection via shell conditionals
- **MCP custom tools** — Handles `mcp__server__tool` call conversions
- **Claude Code Agent/hooks/thinking** — Maps Agent tool, hooks, and extended thinking
- **YAML frontmatter** — Adds Deep Agents skill metadata with version compatibility
- **Executable validation** — Grep-based lint checklist replaces "verify mentally"
- **10 Golden Rules** (up from 6)

---

## What This Does / O Que Isso Faz

Claude Code and Deep Agents CLI are both agents with filesystem and shell access, but they speak different "languages". This converter handles the translation automatically — in both directions.

O Claude Code e o Deep Agents CLI sao ambos agentes com acesso a filesystem e shell, mas falam "linguas" diferentes. Este conversor faz essa traducao automaticamente — nas duas direcoes.

---

## License / Licenca

MIT - See [LICENSE](LICENSE) for details.
