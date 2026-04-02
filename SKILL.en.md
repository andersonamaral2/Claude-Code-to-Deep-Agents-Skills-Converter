# Skill: Claude Code → Deep Agents Skill Converter

> Converts any SKILL.md written for Claude Code into a fully compatible Deep Agents CLI version, preserving 100% of the domain knowledge while adapting the execution interface.

---

## When to use

This skill is triggered when the user asks something like:

- "Convert this Claude Code skill to Deep Agents"
- "Adapt this SKILL.md to work with Deep Agents"
- "Port this skill from Claude Code to Deep Agents"
- "I have a Claude Code skill, I want to use it in Deep Agents"
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
| Subtasks | Not natively available | `task` tool (isolated sub-agents) |
| Memory | `CLAUDE.md` (per session) | `AGENTS.md` + `/memories/` (persistent) |
| Skills | Not native | `~/.deepagents/<agent>/skills/<name>/SKILL.md` |
| HTTP requests | `curl` via bash | Native `http_request` tool |
| Web search | Not native | `web_search` tool (via Tavily) |
| MCP servers | `.claude/mcp.json` | `.deepagents/mcp.json` |
| Human approval | Automatic in sandbox | HITL by default, `-y` for auto-approve |
| Context window | Large (200k tokens) | Model-dependent + auto-compaction |

---

## Conversion Procedure

When receiving a Claude Code skill, follow these steps **in exact order**:

### Step 0 — Plan via `write_todos`

```
- [ ] 1. Read and analyze the original Claude Code skill
- [ ] 2. Identify all implicit execution patterns
- [ ] 3. Map each pattern to the equivalent Deep Agents tool
- [ ] 4. Rewrite the skill with explicit tool instructions
- [ ] 5. Add mandatory Deep Agents sections
- [ ] 6. Validate the converted skill
- [ ] 7. Save via write_file
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

#### 2c. Command execution

**Detect phrases like:**
- "Run: `command`"
- "Execute `command`"
- "In the terminal: `command`"
- Bare ```bash blocks without file context
- "Install with `pip install ...`"
- "Test with `pytest`"

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

### Step 3 — Apply the 8 Mandatory Transformations

Every converted skill **MUST** contain these 8 transformations:

#### T1 — Execution context header

Add right after the skill title and description:

```markdown
## Execution Context

This skill runs inside **Deep Agents CLI**. Available tools:

| Tool | Usage in this skill |
|------|---------------------|
| `execute` | {describe specific usage} |
| `write_file` | {describe specific usage} |
| `edit_file` | {describe specific usage} |
| `read_file` | {describe specific usage} |
| `ls` / `glob` / `grep` | {describe specific usage} |
| `task` | {describe specific usage} |
| `write_todos` | {describe specific usage} |
| `http_request` | {describe specific usage} |
| `web_search` | {describe specific usage} |

**Critical execution rules:**
1. Always start by creating the plan via `write_todos`.
2. Create files one by one via `write_file` — never try to generate everything at once.
3. Test each module via `execute` immediately after creating it.
4. Use `task` to delegate long or parallel subtasks to sub-agents.
```

Fill the "Usage in this skill" column by analyzing the actual skill content. Remove rows for tools that don't apply to the specific skill.

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

If the skill depends on external tools (gh CLI, aws CLI, docker, node, etc.), add:

```markdown
## Prerequisites Check

Before creating any files, use `execute` to verify:

```bash
{tool} --version
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

### Sub-agent can't access project modules
```bash
# Sub-agent runs in isolated context. Instruct it to:
cd /path/to/project && {command}
```

### Context window overflow
```
Use /compact to force compaction before continuing
```
```

### Step 4 — Claude Code → Deep Agents reference replacements

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

### Step 5 — Preserve 100% of domain knowledge

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

### Step 6 — Validate the converted skill

Before saving, mentally verify:

```
✓ Has execution context header with tools table?
✓ Has execution plan for write_todos?
✓ Has prerequisites check?
✓ Every file creation uses "write_file" explicitly?
✓ Every shell command uses "execute" explicitly?
✓ Every edit uses "edit_file" explicitly?
✓ Every read uses "read_file" explicitly?
✓ Parallel flows use "task" for sub-agents?
✓ Has Deep Agents CLI usage guide?
✓ Has troubleshooting section?
✓ ALL domain knowledge preserved?
✓ No tables, formulas, regex, or templates omitted?
✓ References to "CLAUDE.md" replaced with "AGENTS.md"?
✓ References to ".claude/" replaced with ".deepagents/"?
```

### Step 7 — Save

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

Convert configuration references:

```markdown
# Claude Code: .claude/mcp.json
# Deep Agents: .deepagents/mcp.json (same JSON format)

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

---

## Converted Skill Structure

Every converted skill must follow this structure (in order):

```
1. # Skill Title
2. > Description (blockquote)
3. ## Execution Context (tools table)                  ← T1
4. ## Execution Plan (write_todos checklist)            ← T2
5. ## Prerequisites Check                               ← T3
6. ## Architecture (preserve from original)
7. ## File Structure (with write_file instructions)     ← T4
8. ## Dependencies (with execute instructions)
9. ## [Technical sections from original, converted]     ← T4/T5/T6
10. ## Usage with Deep Agents CLI                        ← T7
11. ## Troubleshooting                                   ← T8
```

Sections 6-9 vary per skill. The important thing is that ALL technical sections go through the pattern conversion (Step 2) and the 8 transformations (Step 3).

---

## Golden Rules

1. **Never lose content.** The converted skill is ≥ original size.
2. **Never assume implicits.** Deep Agents CLI needs explicit instructions on which tool to use.
3. **Always start with `write_todos`.** The plan is the foundation of every Deep Agents execution.
4. **Test after every `write_file`.** The create → test → next pattern is unbreakable.
5. **Use `task` for parallelism.** If the skill processes N items, use N sub-agents.
6. **Preserve all domain knowledge.** Tables, regex, formulas, templates — everything.
