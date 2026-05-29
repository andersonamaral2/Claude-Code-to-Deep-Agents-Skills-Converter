# Conversor Universal de SKILL.md — Claude Code · Deep Agents · Codex · Qwen Code · Cursor

<p align="center">
  <img src="assets/og-banner-v2.2.png" alt="Conversor Universal de SKILL.md — Claude Code, Deep Agents, Codex, Qwen Code, Cursor" width="100%">
</p>

Converte **qualquer** SKILL.md entre **Claude Code, Deep Agents CLI, Codex CLI, Qwen Code e Cursor** — preservando 100% do conhecimento de domínio e adaptando a interface de execução de cada alvo. Todas as direções são suportadas, além de preview dry-run e processamento em lote.

> **English?** [Read in English](/README.md)
>
> **Primeira vez aqui?** O [FAQ](docs/FAQ.pt.md) antecipa as perguntas mais comuns (preciso disso, fidelidade, diferenças por ferramenta).

## Formatos suportados

| Formato | Dir. de skills (usuário) | Tier de conversão |
|---------|--------------------------|-------------------|
| **Claude Code** | `~/.claude/skills/<nome>/SKILL.md` | — (formato hub) |
| **Deep Agents CLI** | `~/.deepagents/agent/skills/<nome>/SKILL.md` | Tier B (ferramentas tipadas) |
| **Codex CLI** | `~/.codex/skills/<nome>/SKILL.md` | Tier A (remap leve) |
| **Qwen Code** | `~/.qwen/skills/<nome>/SKILL.md` | Tier A (remap leve) |
| **Cursor** | `~/.cursor/skills/<nome>/SKILL.md` | Tier A (remap leve) |

Os cinco agora usam um formato `SKILL.md` em linguagem natural quase idêntico, então converter
para Codex, Qwen Code e Cursor é basicamente **remapear frontmatter + caminhos + config MCP**
(Tier A). O Deep Agents usa ferramentas tipadas e explícitas (`write_file`, `execute`, `task`),
então recebe a tradução mais pesada (**Tier B**). O mapeamento completo está na
[matriz de referência entre formatos](/SKILL.pt.md#matriz-de-referência-entre-formatos) dentro da skill.

---

## Por que isso existe?

Agentes de código compartilham cada vez mais a mesma ideia de `SKILL.md` — uma pasta com um
`SKILL.md` que ensina um procedimento ao agente — mas diferem nos detalhes que fazem a skill
realmente carregar e rodar:

- **Regras de frontmatter** diferem (o Codex proíbe `<`/`>` na description e só aceita cinco
  chaves; o Qwen usa `allowedTools` em camelCase; skills do Cursor usam `paths`).
- **Locais dos arquivos** diferem (`~/.codex/skills`, `~/.qwen/skills`, `~/.cursor/skills`, …).
- **Arquivos de memória** diferem (`CLAUDE.md` vs `AGENTS.md` vs `QWEN.md`).
- **Deep Agents** vai além: usa ferramentas tipadas e explícitas (`write_file`, `execute`,
  `task`), então "crie o arquivo X" implícito precisa virar "use `write_file` para criar X".

Uma skill feita para uma ferramenta não carrega direito em outra até esses detalhes serem
remapeados. Este conversor faz essa tradução automaticamente — **em todas as direções** —
preservando 100% do conhecimento de domínio.

---

## Novidades na v2.2

| Recurso | Descrição |
|---------|-----------|
| 3 novos alvos | **Codex CLI**, **Qwen Code** e **Cursor** — todos bidirecionais |
| Matriz entre formatos | Uma tabela mapeando caminhos, frontmatter, ferramentas e config MCP dos 5 formatos |
| Detecção de origem/destino | Infere as duas pontas por impressões digitais e escolhe o tier de conversão |
| Modelo de 2 níveis | Tier A (remap leve para alvos SKILL.md) · Tier B (tradução pesada Deep Agents) |
| Validador multi-alvo | `scripts/validate-conversion.sh` aplica as regras reais de frontmatter/caminho/ferramenta de cada CLI |
| `install.sh --target` | Instala o conversor em qualquer uma das 5 CLIs |
| Verificado nas CLIs reais | Formatos confirmados no Codex 0.98.0 e Qwen Code 0.17.0 instalados, não só na doc |
| Novos exemplos | FastAPI nos 4 formatos · Express + JWT + PostgreSQL + Docker · conversão de servidor/tools MCP |
| CI endurecido | **Secret-scan (gitleaks)** + **paridade EN/PT** obrigatórios em todo PR |

> Procurando a lista de recursos da v2.1 (Claude Code ↔ Deep Agents)? Veja o [CHANGELOG](CHANGELOG.md).

---

## Instalação

### Opção A — Uma linha (recomendado)

Sem precisar de git clone — basta rodar:

```bash
curl -fsSL https://raw.githubusercontent.com/andersonamaral2/Claude-Code-to-Deep-Agents-Skills-Converter/main/install.sh | bash
```

Pronto. O instalador baixa a skill do GitHub, adiciona frontmatter YAML, e registra no Deep Agents CLI. Detecta automaticamente seu idioma e escolhe Português ou Inglês.

**Com opções:**
```bash
# Forçar Português
curl -fsSL .../install.sh | bash -s -- --lang pt

# Instalar para um agente específico
curl -fsSL .../install.sh | bash -s -- --agent meuagente

# Instalar a skill conversora em outra CLI (Deep Agents é o padrão)
curl -fsSL .../install.sh | bash -s -- --target codex
curl -fsSL .../install.sh | bash -s -- --target cursor
curl -fsSL .../install.sh | bash -s -- --target qwen
curl -fsSL .../install.sh | bash -s -- --target claude
```

O `--target` escolhe o diretório de skills de destino: `~/.deepagents/<agente>/skills`
(padrão), `~/.claude/skills`, `$CODEX_HOME/skills`, `~/.qwen/skills` ou `~/.cursor/skills`.
Para Codex, ele também roda o validador que vem com o Codex quando disponível.

### Opção B — Clone + install

Se quiser o repositório completo (exemplos, docs, contribuição):

```bash
git clone https://github.com/andersonamaral2/Claude-Code-to-Deep-Agents-Skills-Converter.git
cd Claude-Code-to-Deep-Agents-Skills-Converter
./install.sh
```

Do repositório clonado você também tem:
```bash
./install.sh --agent meuagente   # Instalar para um agente específico
./install.sh --lang pt           # Forçar Português
./install.sh --uninstall         # Remover a skill
```

### Opção C — Deixe o Deep Agents instalar para você

Peça ao próprio agente para buscar e instalar:

```bash
deepagents -y -S "all" -n "Run: curl -fsSL https://raw.githubusercontent.com/andersonamaral2/Claude-Code-to-Deep-Agents-Skills-Converter/main/install.sh | bash"
```

### Opção D — Instalação manual

Se preferir controle total:

```bash
# Global (disponível em toda sessão)
mkdir -p ~/.deepagents/agent/skills/skill-converter
cp SKILL.pt.md ~/.deepagents/agent/skills/skill-converter/SKILL.md

# Ou escopo do projeto
mkdir -p .deepagents/skills/skill-converter
cp SKILL.pt.md .deepagents/skills/skill-converter/SKILL.md
```

> **Nota:** Instalação manual não injeta frontmatter YAML. A skill funciona mas `deepagents skills list` pode mostrar um aviso. Use o instalador para um setup limpo.

### Verificar instalação

```bash
deepagents skills list
# Deve mostrar: skill-converter
```

### Desinstalar

```bash
# Do repositório clonado:
./install.sh --uninstall

# Ou manualmente:
rm -rf ~/.deepagents/agent/skills/skill-converter
```

---

## Como usar

Depois de instalar o skill-converter, inicie o Deep Agents e diga **o que converter** e **onde salvar**. Você fornece a skill de origem de duas formas:

1. **Por caminho de arquivo** — aponte para um SKILL.md no disco (o agente lê o arquivo)
2. **Colando o conteúdo** — cole o conteúdo da skill direto no chat

Todos os exemplos abaixo assumem que o conversor já está instalado (`deepagents skills list` mostra `skill-converter`).

### Método 1 — Converter Claude Code → Deep Agents (de arquivo)

```bash
deepagents -y

> Leia o arquivo ~/skills-claude-code/devops-audit/SKILL.md e converta
> essa skill do Claude Code para Deep Agents. Salve como devops-audit-deepagents/SKILL.md
```

### Método 2 — Converter Deep Agents → Claude Code

```bash
deepagents -y

> Converta essa skill do Deep Agents de volta para o formato Claude Code:
> Leia ~/deepagents-skills/minha-skill/SKILL.md e converta para Claude Code.
> Salve como minha-skill-claude-code/SKILL.md
```

### Método 2b — Converter Claude Code → Codex (Tier A)

```bash
deepagents -y

> Leia ~/.claude/skills/minha-skill/SKILL.md e converta para o formato Codex.
> Salve como ~/.codex/skills/minha-skill/SKILL.md
```

O conversor mantém a prosa das instruções, adiciona frontmatter válido para Codex (`name` em
hyphen-case, `description` sem `<`/`>`) e remapeia `CLAUDE.md` → `AGENTS.md`. Valide o resultado com:

```bash
# o validador do próprio conversor
scripts/validate-conversion.sh --target codex ~/.codex/skills/minha-skill
# e o validador que vem com o Codex, se instalado
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py ~/.codex/skills/minha-skill
```

### Método 2c — Converter Claude Code → Cursor (Tier A)

```bash
deepagents -y

> Leia ~/.claude/skills/minha-skill/SKILL.md e converta para uma skill do Cursor.
> Salve como ~/.cursor/skills/minha-skill/SKILL.md
```

O Cursor exige que o `name` da skill **seja igual ao nome da pasta**, descarta `allowed-tools`
e lê o `AGENTS.md` para contexto do projeto. Valide com:

```bash
scripts/validate-conversion.sh --target cursor ~/.cursor/skills/minha-skill
```

> **Atenção:** o Cursor também lê `.claude/skills/` nativamente como caminho legado, então uma
> skill existente do Claude Code frequentemente funciona no Cursor sem conversão alguma — a
> conversão só te dá um layout nativo limpo com `paths`/`disable-model-invocation`.

### Método 2d — Converter Claude Code → Qwen Code (Tier A)

```bash
deepagents -y

> Leia ~/.claude/skills/minha-skill/SKILL.md e converta para uma skill do Qwen Code.
> Salve como ~/.qwen/skills/minha-skill/SKILL.md
```

O passo-chave é o **remap de nomes de ferramentas**: `allowed-tools: Read, Write, Edit, Bash`
do Claude vira `allowedTools: [read_file, write_file, edit, run_shell_command]` do Qwen (lista
YAML snake_case). `CLAUDE.md` → `QWEN.md`. Valide com:

```bash
scripts/validate-conversion.sh --target qwen ~/.qwen/skills/minha-skill
```

### Método 3 — Dry-run / Preview (sem salvar)

```bash
deepagents -y

> Mostre o preview da conversão de ~/minha-skill/SKILL.md de Claude Code para Deep Agents.
> Não salve ainda, só me mostre o diff.
```

### Método 4 — Conversão em lote (batch)

```bash
deepagents -y

> Converta todas as skills Claude Code em ~/claude-skills/ para formato Deep Agents.
> Salve cada uma em ~/deepagents-skills/{nome}/SKILL.md
```

### Método 5 — Converter e já registrar como skill

```bash
deepagents -y

> Leia ~/minha-skill-claude-code/SKILL.md, converta de Claude Code para Deep Agents,
> e salve direto em ~/.deepagents/agent/skills/minha-skill/SKILL.md
```

### Método 6 — Conversão não-interativa (one-shot)

```bash
deepagents -n -y \
  "Leia o arquivo ./SKILL-claude-code.md e converta de Claude Code para Deep Agents. \
   Salve como ./SKILL-deepagents.md"
```

### Método 7 — Colar a skill direto no chat

Sem precisar de arquivo — cole o conteúdo diretamente:

```bash
deepagents -y

> Converta essa skill do Claude Code para Deep Agents e salve como ./convertida/SKILL.md:
>
> # Skill: Meu App
> Crie o arquivo src/main.py:
> ...
```

---

## O que a conversão faz

A skill aplica **8 transformações obrigatórias** (T1-T8):

| # | Transformação | O que adiciona |
|---|---------------|----------------|
| T1 | Header de contexto | Tabela mapeando tools ao uso na skill (apenas tools usadas) |
| T2 | Plano de execução | Checklist para `write_todos` com todos os steps |
| T3 | Pré-requisitos | Verificação de ferramentas + env vars via `execute` |
| T4 | Criação explícita | Todo "crie o arquivo" vira `write_file` explícito |
| T5 | Testes inline | Após cada arquivo criado, teste via `execute` |
| T6 | Sub-agents | Fluxos multi-item convertidos para `task` paralelo |
| T7 | Guia de uso | 3 modos de uso (interativo, one-shot, CI/CD) |
| T8 | Troubleshooting | Problemas comuns baseados nas dependências |

Além disso, trata estes **padrões adicionais**:

| Padrão | Conversão |
|--------|-----------|
| Comandos inline (`rode \`npm install\``) | Extraídos para blocos `execute` explícitos |
| Variáveis de ambiente / secrets | Script de verificação + suporte `.env` |
| Condicional / específico por plataforma | Blocos shell `case`/`if` via `execute` |
| Agent tool do Claude Code | Sub-agents via `task` |
| Hooks do Claude Code (settings.json) | Shell scripts + documentação no AGENTS.md |
| Extended thinking | Pass-through dependente do modelo |
| Tools MCP customizadas (`mcp__*`) | Mesmas tools, config em `.deepagents/mcp.json` |
| Frontmatter YAML | Adicionado com metadados e versão de compatibilidade |

E faz **substituições semânticas** automáticas:

| Claude Code | Deep Agents |
|-------------|-------------|
| `CLAUDE.md` | `AGENTS.md` |
| `.claude/` | `.deepagents/` |
| bash implícito | `execute` explícito |
| escrita implícita | `write_file` explícito |
| edição implícita | `edit_file` explícito |
| leitura implícita | `read_file` explícito |
| curl via bash | `http_request` ou `execute` |
| loop sequencial | `task` para sub-agents |
| Agent tool | tool `task` |

---

## Exemplo real: antes e depois

### Antes (Claude Code)

```markdown
# Skill: Gerador de API REST

Crie o arquivo `src/app.py`:

```python
from flask import Flask
app = Flask(__name__)
```

Instale as dependências:

```bash
pip install flask
```

Teste:

```bash
python src/app.py
```
```

### Depois (Deep Agents)

```markdown
---
name: rest-api-generator
description: "Gera uma API REST Flask com setup básico"
metadata:
  converted-from: claude-code
  converter-version: "2.0"
  deep-agents-compat: ">=0.0.34"
---

# Skill: Gerador de API REST

## Contexto de Execução
| Tool | Uso nesta skill |
|------|----------------|
| `write_file` | Criar arquivos do projeto Flask |
| `execute` | Instalar dependências e testar |

## Plano de Execução (use com `write_todos`)
- [ ] 1. Verificar Python 3.11+
- [ ] 2. Criar estrutura de diretórios
- [ ] 3. Criar src/app.py
- [ ] 4. Instalar dependências
- [ ] 5. Testar

## Verificação de Pré-requisitos
Use `execute`:
```bash
python3 --version
```

Use `write_file` para criar `src/app.py`:
```python
from flask import Flask
app = Flask(__name__)
```

Teste via `execute`:
```bash
python -c "from src.app import app; print('OK')"
```

Instale dependências via `execute`:
```bash
pip install flask
```

Teste completo via `execute`:
```bash
python src/app.py &
curl http://localhost:5000
kill %1
```
```

Veja o diretório `examples/` para **conversões completas antes/depois** mostrando todas as 8 transformações aplicadas:

- **FastAPI Todo App** (`claude-code-sample` → `deep-agents-output`) — também convertido para os formatos Codex, Cursor e Qwen (`codex-output`, `cursor-output`, `qwen-output`).
- **Docker Monitoring Stack** (`claude-code-sample-2` → `deep-agents-output-2`).
- **API Express.js com JWT + PostgreSQL + Docker** (`claude-code-sample-3` → `deep-agents-output-3`) — uma conversão real com JWT auth, múltiplas camadas de middleware, banco relacional e dev local containerizado.

---

## Estrutura de diretórios

Após a instalação, seu setup fica assim:

```
~/.deepagents/
  └── agent/
      ├── AGENTS.md
      ├── memories/
      └── skills/
          ├── skill-converter/          <- este conversor
          │   └── SKILL.md
          ├── devops-audit/             <- exemplo de skill convertida
          │   └── SKILL.md
          └── outra-skill-convertida/   <- quantas quiser
              └── SKILL.md
```

---

## Dicas

**Use `-y` durante a conversão.** O conversor faz várias operações de `read_file` e `write_file` — o auto-approve evita ficar parando a cada uma.

**Modelo recomendado.** Modelos com context window grande (128k+) funcionam melhor porque a skill original + as regras de conversão + a saída ocupam bastante espaço. Kimi K2.5, Claude Sonnet/Opus, GPT-4o são boas opções.

**Validação automatizada.** Após converter, a skill roda um script de validação baseado em grep que verifica seções faltantes, padrões não convertidos e referências antigas. Sem mais verificação manual.

**Skills muito grandes (>500 linhas).** Se a skill original for enorme, considere pedir ao conversor para dividir em sub-skills. O Deep Agents suporta múltiplos SKILL.md na mesma pasta de skill.

**Processamento em lote.** Converta um diretório inteiro de skills de uma vez. Cada conversão roda em um sub-agent paralelo para mais velocidade.

---

## Limitações

- O conversor não executa a skill — ele apenas adapta o documento para que o Deep Agents CLI consiga executá-la.
- Skills que dependem de features exclusivas do sandbox do Claude Code (como acesso a portas de rede específicas) podem precisar de ajustes manuais no ambiente local.
- A qualidade da conversão depende do modelo LLM que está rodando o Deep Agents CLI.
- A conversão reversa (Deep Agents → Claude Code) remove referências explícitas a tools, o que pode perder alguma precisão em edge cases.

---

## Compatibilidade

- **Deep Agents CLI**: v0.0.34+ (testado)
- **Python**: 3.11+ (requisito do Deep Agents)
- **Formato de skill**: Frontmatter YAML com campos `name`, `description`, `metadata`

---

## Licença

MIT — use, adapte e distribua como quiser. Veja [LICENSE](LICENSE).
