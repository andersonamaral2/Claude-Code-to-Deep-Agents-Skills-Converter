# Claude Code → Deep Agents Skill Converter

Convert **any** SKILL.md written for Claude Code into a Deep Agents CLI compatible version — preserving 100% of the domain knowledge while adapting the execution interface.

---

## Why does this exist?

Claude Code and Deep Agents CLI are both agents with filesystem and shell access, but they speak different "languages":

- **Claude Code** operates with implicit bash — it simply "writes" files and "runs" commands without declaring which tool it's using.
- **Deep Agents CLI** operates with typed, explicit tools — `write_file`, `execute`, `edit_file`, `task`, etc.

A skill that works perfectly in Claude Code **won't work** in Deep Agents because the agent can't translate "create file X" into "use the `write_file` tool to create X". This converter handles that translation automatically.

---

## Installation

### Option A — Global skill (available in every session)

```bash
# Create the skill directory
mkdir -p ~/.deepagents/agent/skills/skill-converter

# Copy the SKILL.md
cp SKILL.md ~/.deepagents/agent/skills/skill-converter/SKILL.md
```

### Option B — Local skill (project-scoped)

```bash
# At the root of the project where you'll work
mkdir -p .deepagents/skills/skill-converter
cp SKILL.md .deepagents/skills/skill-converter/SKILL.md
```

### Verify installation

```bash
# List available skills
ls ~/.deepagents/agent/skills/
# Should show: skill-converter/

# Or, if installed locally:
ls .deepagents/skills/
```

---

## Usage

### Method 1 — Convert a skill from a file

```bash
# 1. Place the Claude Code SKILL.md anywhere accessible
#    Example: ~/claude-code-skills/devops-audit/SKILL.md

# 2. Start Deep Agents CLI
deepagents -y

# 3. Request the conversion
> Read the file ~/claude-code-skills/devops-audit/SKILL.md and convert
> this Claude Code skill to Deep Agents. Save as devops-audit-deepagents/SKILL.md
```

### Method 2 — Convert a skill by pasting content

```bash
# 1. Start Deep Agents CLI
deepagents

# 2. Paste the skill content and request conversion
> Convert this Claude Code skill to Deep Agents:
>
> [paste the SKILL.md content here]
```

### Method 3 — Convert and register as a Deep Agents skill directly

```bash
deepagents -y

> Read ~/my-claude-code-skill/SKILL.md, convert from Claude Code to Deep Agents,
> and save directly to ~/.deepagents/agent/skills/my-skill/SKILL.md
```

After that, the converted skill is permanently available:

```bash
# In any future session:
deepagents
> Build the project following the my-skill skill
```

### Method 4 — Non-interactive conversion (one-shot)

```bash
deepagents -n -y \
  "Read the file ./SKILL-claude-code.md and convert from Claude Code to Deep Agents. \
   Save as ./SKILL-deepagents.md"
```

---

## What the conversion does

The skill applies **8 mandatory transformations** (T1-T8):

| # | Transformation | What it adds |
|---|----------------|--------------|
| T1 | Execution context header | Table mapping Deep Agents tools to skill usage |
| T2 | Execution plan | Checklist for `write_todos` with all steps |
| T3 | Prerequisites | External tool verification via `execute` |
| T4 | Explicit creation | Every "create the file" becomes explicit `write_file` |
| T5 | Inline tests | After each file created, test via `execute` |
| T6 | Sub-agents | Multi-item flows converted to parallel `task` calls |
| T7 | Usage guide | 3 usage modes (interactive, one-shot, CI/CD) |
| T8 | Troubleshooting | Common issues based on dependencies |

And performs automatic **semantic replacements**:

| Claude Code | Deep Agents |
|-------------|-------------|
| `CLAUDE.md` | `AGENTS.md` |
| `.claude/` | `.deepagents/` |
| Implicit bash | Explicit `execute` |
| Implicit writing | Explicit `write_file` |
| Implicit editing | Explicit `edit_file` |
| Implicit reading | Explicit `read_file` |
| curl via bash | `http_request` or `execute` |
| Sequential loop | `task` for sub-agents |

---

## Real example: before and after

### Before (Claude Code)

```markdown
# Skill: REST API Generator

Create the file `src/app.py`:

```python
from flask import Flask
app = Flask(__name__)
```

Install the dependencies:

```bash
pip install flask
```

Test:

```bash
python src/app.py
```
```

### After (Deep Agents)

```markdown
# Skill: REST API Generator

## Execution Context
| Tool | Usage in this skill |
|------|---------------------|
| `write_file` | Create Flask project files |
| `execute` | Install dependencies and run tests |

## Execution Plan (use with `write_todos`)
- [ ] 1. Check Python 3.11+
- [ ] 2. Create directory structure
- [ ] 3. Create src/app.py
- [ ] 4. Install dependencies
- [ ] 5. Test

## Prerequisites Check
Use `execute`:
```bash
python3 --version
```

Use `write_file` to create `src/app.py`:
```python
from flask import Flask
app = Flask(__name__)
```

Test via `execute`:
```bash
python -c "from src.app import app; print('OK')"
```

Install dependencies via `execute`:
```bash
pip install flask
```

Full test via `execute`:
```bash
python src/app.py &
curl http://localhost:5000
kill %1
```
```

---

## Directory structure

After installation, your setup looks like this:

```
~/.deepagents/
  └── agent/
      ├── AGENTS.md
      ├── memories/
      └── skills/
          ├── skill-converter/             ← this converter
          │   └── SKILL.md
          ├── devops-audit/                ← example converted skill
          │   └── SKILL.md
          └── another-converted-skill/     ← as many as you want
              └── SKILL.md
```

---

## Tips

**Use `-y` during conversion.** The converter performs multiple `read_file` and `write_file` operations — auto-approve prevents stopping at each one.

**Recommended models.** Models with large context windows (128k+) work best because the original skill + conversion rules + output take up significant space. Kimi K2.5, Claude Sonnet/Opus, and GPT-4o are good choices.

**Quick validation.** After converting, open the generated SKILL.md and search for words like "create", "write", "run", "execute" without the explicit mention of the corresponding tool (`write_file`, `execute`, etc.). If you find any, the conversion is incomplete.

**Very large skills (>500 lines).** If the original skill is huge, consider asking the converter to split it into sub-skills. Deep Agents supports multiple SKILL.md files in the same skill folder.

---

## Limitations

- The converter does not execute the skill — it only adapts the document so that Deep Agents CLI can execute it.
- Skills that depend on features exclusive to Claude Code's sandbox (such as access to specific network ports) may need manual adjustments in the local environment.
- Conversion quality depends on the LLM model running the Deep Agents CLI.

---

## License

MIT — use, adapt, and distribute as you wish.
