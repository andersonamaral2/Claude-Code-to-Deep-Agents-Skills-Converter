---
name: skill-converter
description: "Converts any SKILL.md between Claude Code and Deep Agents CLI formats — preserving 100% of domain knowledge while adapting the execution interface. Supports forward, reverse, dry-run, and batch conversion."
metadata:
  converter-version: "2.0"
  deep-agents-compat: ">=0.0.34"
  source-repo: "https://github.com/andersonamaral2/Claude-Code-to-Deep-Agents-Skills-Converter"
---

# Skill: Claude Code ↔ Deep Agents Skill Converter

> Converts any SKILL.md between Claude Code and Deep Agents CLI formats — preserving 100% of domain knowledge while adapting the execution interface. Supports forward conversion (Claude Code → Deep Agents), reverse conversion (Deep Agents → Claude Code), dry-run preview, and batch processing.

---

## When to use

This skill is triggered when the user asks something like:

- "Convert this Claude Code skill to Deep Agents"
- "Convert this Deep Agents skill to Claude Code"
- "Adapt this SKILL.md to work with Deep Agents"
- "Port this skill from Claude Code to Deep Agents"
- "I have a Claude Code skill, I want to use it in Deep Agents"
- "Preview the conversion without saving" / "Dry-run"
- "Convert all skills in this folder"
- Or when the user provides a SKILL.md file and asks to "convert", "adapt", "port", "migrate"

---

## Context: Why conversion is needed

Claude Code and Deep Agents CLI share the same philosophy (agent with filesystem + shell access), but differ in the **execution interface**:

| Concept | Claude Code | Deep Agents CLI |
|---------|-------------|-----------------|
| Create file | Implicit (the LLM just "writes") | Explicit `write_file` tool |
| Edit file | Implicit | Explicit `edit_file` tool (search/replace) |
| Read file | Implicit | Explicit `read_file` tool |
| Run shell | Native `bash` in sandbox | `execute` tool (with HITL or `-y`) |
| Navigate filesystem | Implicit `ls`, `cat`, `find` | Typed `ls`, `glob`, `grep` tools |
| Planning | Implicit LLM reasoning | Explicit `write_todos` tool |
| Subtasks | `Agent` tool (sub-processes) | `task` tool (isolated sub-agents) |
| Memory | `CLAUDE.md` + `.claude/` memories | `AGENTS.md` + `/memories/` (persistent) |
| Skills | `.claude/` commands / slash commands | `~/.deepagents/<agent>/skills/<name>/SKILL.md` |
| HTTP requests | `curl` via bash | Native `http_request` tool |
| Web search | Not native | `web_search` tool (via Tavily) |
| MCP servers | `.claude/mcp.json` | `.deepagents/mcp.json` (same JSON format) |
| MCP tool calls | `mcp__server__tool_name` | Dynamic MCP tools (same protocol, auto-loaded) |
| Human approval | Automatic in sandbox | HITL by default, `-y` for auto-approve |
| Context window | Large (200k tokens) | Model-dependent + auto-compaction |
| Hooks / automation | `settings.json` hooks (pre/post) | Not native (use `execute` with shell scripts) |
| Extended thinking | Native `thinking` blocks | Model-dependent (pass-through if supported) |
| Environment variables | Available in sandbox `$VAR` | Available locally; use `.env` or `execute` to export |
| Skill metadata | No frontmatter | YAML frontmatter (`name`, `description`, `allowed-tools`) |

---

## Conversion Modes

### Mode A — Forward: Claude Code → Deep Agents (default)

Follow the full procedure below (Steps 0–8).

### Mode B — Reverse: Deep Agents → Claude Code

See the [Reverse Conversion](#reverse-conversion-deep-agents--claude-code) section at the end.

### Mode C — Dry-run / Preview

When the user asks for a preview or dry-run:

1. Perform the full conversion in memory.
2. Instead of saving via `write_file`, display a **diff-style comparison**:
   - Show sections side-by-side or as unified diff.
   - Highlight what was added (T1–T8 sections), what was replaced (semantic swaps), and what was preserved.
3. Ask the user to confirm before saving.

```
Example output:
━━━ CONVERSION PREVIEW ━━━
+ Added: Execution Context header (T1)
+ Added: Execution Plan with 7 steps (T2)
+ Added: Prerequisites check for: node, docker (T3)
~ Replaced: 12 implicit file creations → write_file (T4)
~ Replaced: 8 bash blocks → execute (T4)
+ Added: 12 inline tests after write_file (T5)
+ Added: 3 task delegations for parallel flows (T6)
+ Added: Usage guide with 3 modes (T7)
+ Added: Troubleshooting section (T8)
= Preserved: 100% domain knowledge (tables, code, formulas)
━━━ Size: 340 lines → 520 lines (+53%) ━━━
Save to {path}? [y/n]
```

### Mode D — Batch conversion

When the user asks to convert multiple skills at once:

1. Use `glob` to find all SKILL.md files in the specified directory.
2. For each skill found, use `task` to delegate the conversion to a sub-agent:
   ```
   task("Convert the Claude Code skill at {path} to Deep Agents format.
         Save the result to {output_path}. Follow the skill-converter SKILL.md procedure.")
   ```
3. After all sub-agents finish, generate a summary report:
   ```
   ━━━ BATCH CONVERSION REPORT ━━━
   ✓ skills/devops-audit/SKILL.md → converted (280 → 410 lines)
   ✓ skills/api-generator/SKILL.md → converted (150 → 230 lines)
   ✗ skills/broken-skill/SKILL.md → FAILED: no actionable content found
   ━━━ 2/3 successful ━━━
   ```

---

## Forward Conversion Procedure (Claude Code → Deep Agents)

When receiving a Claude Code skill, follow these steps **in exact order**:

### Step 0 — Plan via `write_todos`

```
- [ ] 1. Read and analyze the original Claude Code skill
- [ ] 2. Identify all implicit execution patterns (including inline commands)
- [ ] 3. Map each pattern to the equivalent Deep Agents tool
- [ ] 4. Rewrite the skill with explicit tool instructions
- [ ] 5. Add mandatory Deep Agents sections (T1–T8)
- [ ] 6. Handle special cases (env vars, conditionals, MCP, hooks)
- [ ] 7. Add YAML frontmatter with metadata
- [ ] 8. Validate the converted skill (executable checklist)
- [ ] 9. Save via write_file (or show preview if dry-run)
```

### Step 1 — Read the original skill

Use `read_file` to read the SKILL.md provided by the user. If the user pasted the content in the chat, skip this step.

### Step 2 — Identify implicit patterns

Scan the text looking for these Claude Code patterns that need translation:

#### 2a. File creation

**Detect phrases like:**
- "Create the file X"
- "Write to X.py"
- "The file should contain..."
- "Generate the following code in..."
- "Save as..."
- Code blocks with path in comment (`# file: src/main.py`)

**Convert to:**
```
Use `write_file` to create `{path}`:
```

#### 2b. File editing

**Detect phrases like:**
- "Edit the file X"
- "Modify the function Y"
- "Add to the file..."
- "Replace X with Y"
- "In file X, change..."

**Convert to:**
```
Use `edit_file` to modify `{path}` (search/replace):
  - old: {original_text}
  - new: {new_text}
```

#### 2c. Command execution (block AND inline)

**Detect code blocks:**
- Bare ```bash blocks without file context
- "Run: `command`"
- "Execute `command`"

**Also detect inline commands (IMPORTANT — easily missed):**
- "run `npm install` and then..."
- "use `pip install flask` to install"
- "after running `docker build .`..."
- Any backtick-wrapped command inside a sentence that is not a file path or variable name

**How to tell inline commands apart from code references:**
- If the backtick content starts with a known CLI (`npm`, `pip`, `docker`, `git`, `curl`, `make`, `pytest`, `cargo`, etc.) → it's a command → convert.
- If it's a function/variable name like `main()` or `$CONFIG_PATH` → it's a reference → leave it.

**Convert to:**
```
Use `execute` to run:
```bash
{command}
```
```

#### 2d. Reading and inspection

**Detect phrases like:**
- "Read the file X"
- "Check the contents of..."
- "Inspect..."
- "Verify the file exists"
- "List files in..."
- "Search for X in the files"

**Convert to:**
```
Use `read_file` to read `{path}`
Use `ls` to list `{dir}`
Use `glob` to search `{pattern}`
Use `grep` to search `{text}` in `{path}`
```

#### 2e. HTTP requests

**Detect phrases like:**
- "Make a request to..."
- "Call the API..."
- "Use `curl` to..."
- "POST/GET/PUT to URL..."

**Convert to:**
```
Use `http_request` to call `{url}`:
  - method: {GET|POST|PUT|DELETE}
  - headers: {headers}
  - body: {body}

# OR, if the command is complex with pipes/auth:
Use `execute` to run:
```bash
curl -X POST ...
```
```

#### 2f. Complex multi-step flows

**Detect phrases like:**
- "For each item, do..."
- "Repeat for all..."
- "Process in parallel..."
- "Run for each repository..."

**Convert to:**
```
Use `task` to delegate each iteration to a sub-agent with isolated context:
  - Instruction: "{subtask description for item N}"
```

#### 2g. Claude Code Agent sub-processes

**Detect phrases like:**
- "Use the Agent tool to..."
- "Launch a sub-agent for..."
- "Delegate to a background agent..."
- References to `subagent_type`, `isolation: "worktree"`

**Convert to:**
```
Use `task` to delegate to a sub-agent:
  - Instruction: "{task description}"

Note: Deep Agents `task` provides isolated context similar to Claude Code's Agent tool.
Worktree isolation is not natively supported — use `execute` with `git worktree` commands
if branch isolation is needed.
```

#### 2h. Hooks and automation

**Detect phrases like:**
- "Configure a hook in settings.json..."
- "Add a pre-commit hook..."
- "Set up automation that runs when..."
- References to `settings.json` hooks, `user-prompt-submit-hook`, etc.

**Convert to:**
```
Deep Agents CLI does not have native hooks. Convert to shell scripts executed via `execute`:

Use `write_file` to create `scripts/{hook_name}.sh`:
```bash
#!/bin/bash
{hook_logic}
```

Use `execute` to make it executable:
```bash
chmod +x scripts/{hook_name}.sh
```

Add a note in AGENTS.md: "Run `scripts/{hook_name}.sh` before/after {event}."
```

#### 2i. Extended thinking / reasoning blocks

**Detect phrases like:**
- "Use extended thinking to reason about..."
- References to `thinking` blocks or `budget_tokens`

**Convert to:**
```
Note: Extended thinking is model-dependent in Deep Agents CLI.
If the underlying model supports reasoning tokens, they work automatically.
No explicit conversion needed — remove any thinking-specific configuration
and let the model handle reasoning natively.
```

#### 2j. Environment variables and secrets

**Detect phrases like:**
- "Set `$API_KEY` to..."
- "Export the token: `export TOKEN=...`"
- "The `.env` file should contain..."
- "Use the environment variable `$DATABASE_URL`"
- References to secrets, tokens, API keys in the sandbox

**Convert to:**
```
## Environment Setup

Before execution, verify required environment variables via `execute`:
```bash
# Check required variables
for var in {VAR1} {VAR2} {VAR3}; do
  if [ -z "${!var}" ]; then
    echo "ERROR: $var is not set"
    exit 1
  fi
done
echo "All environment variables OK"
```

If using a `.env` file, load it via `execute`:
```bash
set -a && source .env && set +a
```

**Security note:** Never hardcode secrets in the SKILL.md.
Use environment variables or a `.env` file (added to `.gitignore`).
```

#### 2k. Conditional / platform-specific flows

**Detect phrases like:**
- "If the system is macOS, do X; if Linux, do Y"
- "For Windows users..."
- "If Docker is available, use containers; otherwise..."
- "When running in CI..."

**Convert to:**
```
### Platform-specific execution

Use `execute` to detect the platform and branch accordingly:
```bash
OS=$(uname -s)
case "$OS" in
  Darwin) {macOS_command} ;;
  Linux)  {linux_command} ;;
  *)      echo "Unsupported OS: $OS"; exit 1 ;;
esac
```

For tool availability checks:
```bash
if command -v docker &>/dev/null; then
  {docker_path}
else
  {fallback_path}
fi
```
```

#### 2l. MCP custom tool calls

**Detect phrases like:**
- "Use the MCP tool `mcp__server__action`..."
- "Call `mcp__slack__send_message`..."
- References to `.claude/mcp.json` server configurations
- Any tool call starting with `mcp__`

**Convert to:**
```
## MCP Tool Integration

Deep Agents CLI loads MCP tools automatically from `.deepagents/mcp.json`.
The same MCP servers and tools are available — only the config path changes.

1. Use `write_file` to create `.deepagents/mcp.json`:
```json
{original .claude/mcp.json content}
```

2. MCP tool calls work the same way in Deep Agents. If the original skill calls
   `mcp__server__action`, the same tool is available after loading the MCP config.
   
   For project-level MCP servers, the user must approve them on first use
   (or use `--trust-project-mcp` to skip approval).
```

### Step 3 — Apply the 8 Mandatory Transformations

Every converted skill **MUST** contain these 8 transformations:

#### T1 — Execution context header

Add right after the skill title and description. **Only include tools actually used by the skill** — do not pad with unused tools:

```markdown
## Execution Context

This skill runs inside **Deep Agents CLI** (v0.0.34+). Available tools:

| Tool | Usage in this skill |
|------|---------------------|
| `{tool}` | {specific usage description} |

> **Only list tools this skill actually uses.** Remove all rows that don't apply.

**Critical execution rules:**
1. Always start by creating the plan via `write_todos`.
2. Create files one by one via `write_file` — never try to generate everything at once.
3. Test each module via `execute` immediately after creating it.
4. Use `task` to delegate long or parallel subtasks to sub-agents.
```

#### T2 — Execution plan

Add section with checklist for `write_todos`. Extract the logical steps from the original skill and convert to checklist:

```markdown
## Execution Plan (use with `write_todos`)

When receiving the request, run `write_todos` with:

- [ ] 1. {step extracted from original skill}
- [ ] 2. {step extracted from original skill}
- [ ] ...
- [ ] N. Test complete flow
```

#### T3 — Prerequisites check

If the skill depends on external tools (gh CLI, aws CLI, docker, node, etc.) or environment variables, add:

```markdown
## Prerequisites Check

Before creating any files, use `execute` to verify:

```bash
# Tools
{tool} --version

# Environment variables (if applicable)
[ -z "$REQUIRED_VAR" ] && echo "ERROR: REQUIRED_VAR not set" && exit 1
```

If not installed, install via `execute`:

```bash
{installation command}
```
```

#### T4 — Explicit file creation instructions

Every time the original skill mentions "create file X", the converted version must say:

```markdown
Use `write_file` to create `{path}`:
```

Followed by the file content.

#### T5 — Explicit test instructions

After each module/file created, add:

```markdown
Test via `execute`:
```bash
python -c "from {module} import {func}; print('OK')"
```
```

Or equivalent for the skill's language.

#### T6 — Sub-agents for parallelism

If the skill involves processing multiple items (repos, files, endpoints, etc.), add:

```markdown
### Parallel execution via sub-agents

To process multiple {items}, use `task` for each:

The main agent lists the {items} via `execute`, then for each item
creates a sub-agent via `task` with specific instructions and isolated context.
```

#### T7 — Deep Agents CLI usage guide

Add final section with usage modes:

```markdown
## Usage with Deep Agents CLI

### Mode 1 — Build (one-shot)
```bash
deepagents -y "Create {what the skill builds} following the {name} skill"
```

### Mode 2 — Interactive
```bash
deepagents
> {natural command that activates the skill}
```

### Mode 3 — Non-interactive (CI/CD)
```bash
deepagents -n -y -S "{allowed commands}" "{instruction}"
```
```

#### T8 — Troubleshooting section

Add section with common problems based on the skill's dependencies:

```markdown
## Troubleshooting

### {Tool X} not found
```bash
# Check:
{tool} --version
# Install:
{installation command}
```

### Environment variable not set
```bash
# Check what's missing:
env | grep EXPECTED_PREFIX
# Set it:
export VAR_NAME="value"
# Or load from .env:
set -a && source .env && set +a
```

### Sub-agent can't access project modules
```bash
# Sub-agent runs in isolated context. Instruct it to:
cd /path/to/project && {command}
```

### Context window overflow
```
Use /compact to force compaction before continuing.
Consider splitting the task with `task` sub-agents.
```
```

### Step 4 — Add YAML frontmatter

Every converted skill should include Deep Agents-compatible frontmatter:

```yaml
---
name: {skill-name-kebab-case}
description: "{One-line description, max 1024 chars — this is used for skill discovery}"
metadata:
  converted-from: claude-code
  converter-version: "2.0"
  deep-agents-compat: ">=0.0.34"
---
```

### Step 5 — Claude Code → Deep Agents reference replacements

Perform semantic find/replace across the text:

| Find (Claude Code) | Replace (Deep Agents) |
|---------------------|----------------------|
| "CLAUDE.md" | "AGENTS.md" |
| ".claude/" | ".deepagents/" |
| ".claude/mcp.json" | ".deepagents/mcp.json" |
| "Claude Code" (as executor) | "Deep Agents CLI" |
| "sandbox" | "local environment (with HITL)" |
| "bash tool" / "native bash" | "`execute` tool" |
| "write the file" (implicit) | "use `write_file` to create" |
| "edit the file" (implicit) | "use `edit_file` to modify" |
| "read the file" (implicit) | "use `read_file` to read" |
| "Agent tool" / "sub-agent" | "`task` tool" |
| "settings.json hooks" | "shell scripts via `execute`" |
| `mcp__server__tool` calls | Same tool name (verify MCP config exists) |

### Step 6 — Preserve 100% of domain knowledge

**CRITICAL:** The conversion is about the *execution interface*, not the *technical content*. Preserve in full:

- All reference tables (metrics, scores, thresholds, regex, etc.)
- All implementation code blocks
- All formulas and calculations
- All output templates and formats
- All business rules and edge cases
- All architecture diagrams
- All infrastructure configurations
- All examples and samples

**Never summarize, simplify, or omit technical content.** The converted skill must be equal to or larger than the original.

### Step 7 — Validate the converted skill (executable checklist)

Before saving, run this validation via `execute`. This replaces the old "verify mentally" approach:

```bash
FILE="{path_to_converted_skill}"

echo "=== SKILL CONVERSION VALIDATION ==="
ERRORS=0

# Check mandatory sections exist
for section in "Execution Context" "Execution Plan" "Prerequisites" "Usage with Deep Agents" "Troubleshooting"; do
  if ! grep -q "$section" "$FILE"; then
    echo "MISSING: $section section"
    ERRORS=$((ERRORS + 1))
  fi
done

# Check for unconverted implicit patterns
for pattern in "create the file" "write the file" "edit the file" "read the file" "run the command" "execute the command"; do
  COUNT=$(grep -ic "$pattern" "$FILE" || true)
  WF_COUNT=$(grep -c "write_file\|edit_file\|read_file\|execute" "$FILE" || true)
  if [ "$COUNT" -gt 0 ]; then
    echo "WARNING: Found '$pattern' $COUNT time(s) — verify each has explicit tool reference"
  fi
done

# Check for orphan bash blocks (no execute reference nearby)
BASH_BLOCKS=$(grep -c '```bash' "$FILE" || true)
EXECUTE_REFS=$(grep -c '`execute`' "$FILE" || true)
if [ "$BASH_BLOCKS" -gt "$EXECUTE_REFS" ]; then
  echo "WARNING: $BASH_BLOCKS bash blocks but only $EXECUTE_REFS execute references"
fi

# Check frontmatter exists
if ! head -1 "$FILE" | grep -q '^---'; then
  echo "MISSING: YAML frontmatter"
  ERRORS=$((ERRORS + 1))
fi

# Check old references
for old_ref in "CLAUDE.md" ".claude/" "sandbox"; do
  if grep -q "$old_ref" "$FILE"; then
    echo "WARNING: Found unconverted reference '$old_ref'"
  fi
done

echo "=== VALIDATION COMPLETE: $ERRORS errors ==="
```

If errors > 0, fix them before saving.

### Step 8 — Save

Use `write_file` to save the converted skill:

```bash
# Suggested path — user can choose another:
write_file("{skill-name}/SKILL.md", converted_content)
```

---

## Conversion Examples

### Example 1: Implicit bash command

**Original (Claude Code):**
```markdown
Install the dependencies:
```bash
pip install langchain boto3
```
```

**Converted (Deep Agents):**
```markdown
Install the dependencies via `execute`:
```bash
pip install langchain boto3
```
```

### Example 2: Implicit file creation

**Original (Claude Code):**
```markdown
Create the file `src/main.py` with the following content:

```python
def main():
    print("Hello")
```
```

**Converted (Deep Agents):**
```markdown
Use `write_file` to create `src/main.py`:

```python
def main():
    print("Hello")
```

Test via `execute`:
```bash
python -c "from src.main import main; main()"
```
```

### Example 3: Editing an existing file

**Original (Claude Code):**
```markdown
In `config.py`, add `DEBUG = True` after the imports line.
```

**Converted (Deep Agents):**
```markdown
Use `edit_file` to modify `config.py`:
  - Find: `import os`
  - Replace with: `import os\n\nDEBUG = True`
```

### Example 4: Multi-item flow

**Original (Claude Code):**
```markdown
For each repository in the organization, run the audit and generate the report.
```

**Converted (Deep Agents):**
```markdown
List the repositories via `execute`:
```bash
gh repo list {org} --limit 50 --json name
```

For each repository, use `task` to delegate to a sub-agent:
```
task("Audit the repository {org}/{repo}. Run: cd project && python audit.py {repo}")
```

Each sub-agent runs in isolated context without polluting the main context window.
```

### Example 5: References to CLAUDE.md

**Original (Claude Code):**
```markdown
Add the project conventions to `CLAUDE.md` at the root.
```

**Converted (Deep Agents):**
```markdown
Add the project conventions to `AGENTS.md` at the root (equivalent to Claude Code's CLAUDE.md).

Alternatively, save as persistent memory via `/remember "convention: ..."` in the interactive session.
```

### Example 6: curl/HTTP via bash

**Original (Claude Code):**
```markdown
Test the API:
```bash
curl -X POST https://api.example.com/data -H "Authorization: Bearer $TOKEN" -d '{"key": "value"}'
```
```

**Converted (Deep Agents):**
```markdown
Test the API via `http_request`:
  - URL: `https://api.example.com/data`
  - Method: POST
  - Headers: `{"Authorization": "Bearer $TOKEN"}`
  - Body: `{"key": "value"}`

Or, if you need pipes or shell processing, use `execute`:
```bash
curl -X POST https://api.example.com/data -H "Authorization: Bearer $TOKEN" -d '{"key": "value"}'
```
```

### Example 7: Inline commands (easily missed)

**Original (Claude Code):**
```markdown
After generating the models, run `npm run build` to compile and then use `npm test` to verify everything works.
```

**Converted (Deep Agents):**
```markdown
After generating the models, compile via `execute`:
```bash
npm run build
```

Then verify via `execute`:
```bash
npm test
```
```

### Example 8: Environment variables

**Original (Claude Code):**
```markdown
Set your OpenAI key: `export OPENAI_API_KEY=sk-...`
The script reads `$DATABASE_URL` from the environment.
```

**Converted (Deep Agents):**
```markdown
## Environment Setup

Verify required environment variables via `execute`:
```bash
for var in OPENAI_API_KEY DATABASE_URL; do
  if [ -z "${!var}" ]; then
    echo "ERROR: $var is not set"
    exit 1
  fi
done
echo "All environment variables OK"
```

If not already set, configure via `execute`:
```bash
export OPENAI_API_KEY="sk-..."   # Replace with your actual key
export DATABASE_URL="postgresql://..."
```

**Security note:** Never hardcode production secrets. Use a `.env` file added to `.gitignore`.
```

### Example 9: Conditional / platform-specific

**Original (Claude Code):**
```markdown
On macOS, install with `brew install redis`. On Linux, use `apt-get install redis-server`.
```

**Converted (Deep Agents):**
```markdown
Install Redis via `execute` (platform-aware):
```bash
OS=$(uname -s)
case "$OS" in
  Darwin) brew install redis ;;
  Linux)  sudo apt-get install -y redis-server ;;
  *)      echo "Unsupported OS: $OS"; exit 1 ;;
esac
```
```

### Example 10: Claude Code Agent tool

**Original (Claude Code):**
```markdown
Use the Agent tool to launch a background agent that runs the full test suite while you continue with the next task.
```

**Converted (Deep Agents):**
```markdown
Use `task` to delegate test execution to a sub-agent with isolated context:
```
task("Run the full test suite: cd /path/to/project && npm test. Report pass/fail summary.")
```

The sub-agent runs independently. Continue with the next task in the main agent.
```

### Example 11: Full real-world conversion (complete before/after)

**Original (Claude Code) — REST API scaffold skill:**
```markdown
# Skill: Express API Generator

Create a production-ready Express.js REST API with authentication.

## Prerequisites

Make sure Node.js 18+ and npm are installed. Also need Docker for the database.

## Steps

Create the project structure. Initialize with `npm init -y` and install dependencies:
`npm install express jsonwebtoken bcrypt pg dotenv`

Create the file `src/index.js`:
```javascript
const express = require('express');
const app = express();
app.use(express.json());

const authRouter = require('./routes/auth');
const usersRouter = require('./routes/users');

app.use('/auth', authRouter);
app.use('/users', usersRouter);

app.listen(process.env.PORT || 3000, () => {
  console.log('Server running');
});
```

Create `src/routes/auth.js` with JWT login and register routes.

Create `src/routes/users.js` with CRUD endpoints protected by auth middleware.

Create `.env` with:
```
PORT=3000
JWT_SECRET=your-secret-key
DATABASE_URL=postgresql://user:pass@localhost:5432/mydb
```

Start the database: `docker compose up -d`

Test the API:
```bash
curl -X POST http://localhost:3000/auth/register -H "Content-Type: application/json" -d '{"email":"test@test.com","password":"123456"}'
```

Add the project conventions to CLAUDE.md.
```

**Converted (Deep Agents):**
```markdown
---
name: express-api-generator
description: "Creates a production-ready Express.js REST API with JWT authentication, PostgreSQL, and Docker"
metadata:
  converted-from: claude-code
  converter-version: "2.0"
  deep-agents-compat: ">=0.0.34"
---

# Skill: Express API Generator

> Creates a production-ready Express.js REST API with authentication.

## Execution Context

This skill runs inside **Deep Agents CLI** (v0.0.34+). Available tools:

| Tool | Usage in this skill |
|------|---------------------|
| `write_file` | Create project files (index.js, routes, .env) |
| `execute` | Run npm, docker, curl, and validation commands |
| `edit_file` | Modify files if adjustments needed |
| `write_todos` | Plan the execution steps |

**Critical execution rules:**
1. Always start by creating the plan via `write_todos`.
2. Create files one by one via `write_file` — never try to generate everything at once.
3. Test each module via `execute` immediately after creating it.

## Execution Plan (use with `write_todos`)

- [ ] 1. Check prerequisites (Node.js 18+, npm, Docker)
- [ ] 2. Verify environment variables
- [ ] 3. Initialize project and install dependencies
- [ ] 4. Create src/index.js
- [ ] 5. Create src/routes/auth.js
- [ ] 6. Create src/routes/users.js
- [ ] 7. Create .env configuration
- [ ] 8. Start database via Docker
- [ ] 9. Test complete API flow

## Prerequisites Check

Use `execute` to verify:
```bash
node --version   # Requires 18+
npm --version
docker --version
docker compose version
```

## Environment Setup

Verify required environment variables via `execute`:
```bash
for var in JWT_SECRET DATABASE_URL; do
  if [ -z "${!var}" ]; then
    echo "WARNING: $var not set — will use defaults from .env"
  fi
done
```

## Implementation

Initialize the project via `execute`:
```bash
npm init -y
```

Install dependencies via `execute`:
```bash
npm install express jsonwebtoken bcrypt pg dotenv
```

Use `write_file` to create `src/index.js`:
```javascript
const express = require('express');
const app = express();
app.use(express.json());

const authRouter = require('./routes/auth');
const usersRouter = require('./routes/users');

app.use('/auth', authRouter);
app.use('/users', usersRouter);

app.listen(process.env.PORT || 3000, () => {
  console.log('Server running');
});
```

Test via `execute`:
```bash
node -e "require('./src/index.js')" &
sleep 2 && kill %1 && echo "OK: index.js loads without errors"
```

Use `write_file` to create `src/routes/auth.js` with JWT login and register routes.

Test via `execute`:
```bash
node -e "require('./src/routes/auth.js'); console.log('OK: auth routes loaded')"
```

Use `write_file` to create `src/routes/users.js` with CRUD endpoints protected by auth middleware.

Test via `execute`:
```bash
node -e "require('./src/routes/users.js'); console.log('OK: user routes loaded')"
```

Use `write_file` to create `.env`:
```
PORT=3000
JWT_SECRET=your-secret-key
DATABASE_URL=postgresql://user:pass@localhost:5432/mydb
```

**Security note:** This `.env` contains placeholder secrets. Replace with real values before production. Add `.env` to `.gitignore`.

Start the database via `execute`:
```bash
docker compose up -d
```

Test the full API via `execute`:
```bash
curl -s -X POST http://localhost:3000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"123456"}'
```

Add the project conventions to `AGENTS.md` at the root (equivalent to Claude Code's CLAUDE.md).

## Usage with Deep Agents CLI

### Mode 1 — Build (one-shot)
```bash
deepagents -y "Create an Express API with auth following the express-api-generator skill"
```

### Mode 2 — Interactive
```bash
deepagents
> Build me a REST API with JWT authentication
```

### Mode 3 — Non-interactive (CI/CD)
```bash
deepagents -n -y -S "npm,node,docker" "Generate Express API scaffold in ./api"
```

## Troubleshooting

### Node.js not found
```bash
node --version
# Install via nvm:
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
```

### Docker not running
```bash
docker info
# If not running:
sudo systemctl start docker
```

### Port 3000 already in use
```bash
lsof -i :3000
# Kill the process or change PORT in .env
```

### Context window overflow
```
Use /compact to force compaction before continuing.
Consider splitting route generation into `task` sub-agents.
```
```

---

## Special Cases

### Skills that use Docker

If the original skill builds containers, the conversion keeps Docker commands via `execute`, but adds a note:

```markdown
**Deep Agents Note:** Docker commands run via `execute` and require Docker
to be installed and accessible in the local environment. If using a remote sandbox
(Modal, Daytona), verify that Docker-in-Docker is enabled.
```

### Skills that use MCP servers

Convert configuration path and add approval note:

```markdown
# Claude Code: .claude/mcp.json
# Deep Agents: .deepagents/mcp.json (same JSON format)
# Also searched: project root .mcp.json

Use `write_file` to create `.deepagents/mcp.json`:
```json
{
  "mcpServers": {
    "{name}": {
      "command": "{cmd}",
      "args": [{args}]
    }
  }
}
```

Note: Project-level stdio MCP servers require user approval on first use.
Use `--trust-project-mcp` to skip approval. Remote servers (SSE/HTTP) are always allowed.
```

### Skills with MCP custom tool calls

If the skill references specific MCP tools (e.g., `mcp__slack__send_message`):

```markdown
MCP tools are auto-loaded in Deep Agents CLI from the MCP config.
The tool names and calling convention are identical. Ensure the MCP server
is configured in `.deepagents/mcp.json` before calling any MCP tools.
```

### Skills with large context window

If the original skill assumes 200k tokens (Claude Code default), add warning:

```markdown
**Deep Agents Note:** This skill was originally designed for 200k token context.
If using a model with smaller context, consider:
- Use `/compact` periodically to free space
- Use `task` to isolate subtasks in sub-agents
- Split execution into smaller steps
```

### Skills that generate many files

If the skill creates more than 10 files, add directory creation first:

```markdown
**Before creating the files**, create the directory structure via `execute`:
```bash
mkdir -p {dir1} {dir2} {dir3}
touch {dir1}/__init__.py {dir2}/__init__.py
```
```

### Skills with hooks or automation

```markdown
Claude Code hooks (settings.json) do not have a direct equivalent in Deep Agents CLI.
Convert hooks to shell scripts and document them in AGENTS.md as manual or CI-triggered steps.
```

### Skills with conditional / platform-specific logic

```markdown
Wrap platform-specific sections in shell conditionals via `execute`.
Use `uname -s` for OS detection, `command -v` for tool availability checks.
Do not leave bare "if macOS / if Linux" text — make it executable.
```

---

## Reverse Conversion: Deep Agents → Claude Code

When converting **from Deep Agents to Claude Code**, apply the inverse transformations:

### Reverse procedure

1. **Remove YAML frontmatter** — Claude Code skills don't use it.
2. **Remove T1 (Execution Context table)** — Claude Code doesn't need explicit tool listings.
3. **Remove T2 (Execution Plan)** — Claude Code uses implicit LLM reasoning.
4. **Simplify T3 (Prerequisites)** — Keep the checks but remove `execute` wrapper:
   ```markdown
   # Before: Use `execute` to verify: node --version
   # After:  Verify Node.js 18+ is installed: node --version
   ```
5. **De-explicit file operations:**
   | Deep Agents | Claude Code |
   |-------------|-------------|
   | `Use write_file to create X:` | `Create the file X:` |
   | `Use edit_file to modify X:` | `Edit X:` |
   | `Use read_file to read X` | `Read X` |
   | `Use execute to run:` | (just the ```bash block) |
   | `Use task to delegate:` | `Use the Agent tool to launch a sub-agent:` |
6. **Remove T5 (inline tests)** — Claude Code tests implicitly when needed.
7. **Convert references back:**
   | Deep Agents | Claude Code |
   |-------------|-------------|
   | `AGENTS.md` | `CLAUDE.md` |
   | `.deepagents/` | `.claude/` |
   | `Deep Agents CLI` | `Claude Code` |
   | `http_request` tool | `curl` via bash |
   | `web_search` tool | Not available (remove or note) |
8. **Simplify T7 (Usage)** — Replace with simple Claude Code invocation:
   ```markdown
   ## Usage
   Open Claude Code in the project directory and say: "{natural command}"
   ```
9. **Simplify T8 (Troubleshooting)** — Keep only truly useful entries, remove boilerplate.

### Reverse validation

Scan the converted skill for Deep Agents-specific terms that should not remain:
- `write_file`, `edit_file`, `read_file`, `execute`, `task`, `write_todos`
- `.deepagents/`, `AGENTS.md`
- `http_request`, `web_search`

---

## Converted Skill Structure

Every converted skill must follow this structure (in order):

```
1. --- YAML frontmatter ---                              ← Step 4
2. # Skill Title
3. > Description (blockquote)
4. ## Execution Context (tools table)                    ← T1
5. ## Execution Plan (write_todos checklist)             ← T2
6. ## Prerequisites Check                                ← T3
7. ## Environment Setup (if applicable)                  ← 2j
8. ## Architecture (preserve from original)
9. ## File Structure (with write_file instructions)      ← T4
10. ## Dependencies (with execute instructions)
11. ## [Technical sections from original, converted]      ← T4/T5/T6
12. ## Usage with Deep Agents CLI                         ← T7
13. ## Troubleshooting                                    ← T8
```

Sections 7–11 vary per skill. The important thing is that ALL technical sections go through the pattern conversion (Step 2) and the 8 transformations (Step 3).

---

## Golden Rules

1. **Never lose content.** The converted skill is ≥ original size.
2. **Never assume implicits.** Deep Agents CLI needs explicit instructions on which tool to use.
3. **Always start with `write_todos`.** The plan is the foundation of every Deep Agents execution.
4. **Test after every `write_file`.** The create → test → next pattern is unbreakable.
5. **Use `task` for parallelism.** If the skill processes N items, use N sub-agents.
6. **Preserve all domain knowledge.** Tables, regex, formulas, templates — everything.
7. **Catch inline commands.** Backtick-wrapped commands inside sentences need conversion too.
8. **Handle env vars explicitly.** Never assume variables are available — verify or document them.
9. **Make conditionals executable.** Platform checks become shell `case`/`if` blocks, not prose.
10. **Validate with the checklist.** Run the grep-based validation before saving.
