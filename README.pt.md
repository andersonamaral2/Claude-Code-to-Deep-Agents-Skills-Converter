# Claude Code ↔ Deep Agents Skill Converter

Converte **qualquer** SKILL.md entre os formatos Claude Code e Deep Agents CLI — preservando 100% do conhecimento de domínio e adaptando a interface de execução. Agora com conversão bidirecional, preview dry-run e processamento em lote.

---

## Por que isso existe?

O Claude Code e o Deep Agents CLI são ambos agentes com acesso a filesystem e shell, mas falam "línguas" diferentes:

- **Claude Code** opera com bash implícito — ele simplesmente "escreve" arquivos e "roda" comandos sem precisar declarar qual tool está usando.
- **Deep Agents CLI** opera com tools tipadas e explícitas — `write_file`, `execute`, `edit_file`, `task`, etc.

Uma skill perfeita para o Claude Code **não funciona** no Deep Agents porque o agente não sabe traduzir "crie o arquivo X" para "use a tool `write_file` para criar X". Este conversor faz essa tradução automaticamente — nas duas direções.

---

## Novidades na v2.0

| Feature | Descrição |
|---------|-----------|
| Conversão bidirecional | Suporte Deep Agents → Claude Code |
| Dry-run / preview | Veja o diff antes de salvar |
| Conversão em lote | Converta todas as skills de um diretório de uma vez |
| Detecção de comandos inline | Captura `npm install` dentro de frases, não só blocos de código |
| Variáveis de ambiente | Verificação explícita e suporte a `.env` |
| Fluxos condicionais | Detecção de SO e disponibilidade de ferramentas via shell |
| Tools MCP customizadas | Converte chamadas `mcp__server__tool` |
| Agent/hooks/thinking | Mapeia Agent tool, hooks e extended thinking do Claude Code |
| Frontmatter YAML | Metadados da skill com compatibilidade de versão |
| Validação executável | Checklist baseado em grep substitui "verificar mentalmente" |
| 10 Regras de Ouro | Subiu de 6, cobrindo comandos inline, env vars, condicionais e validação |

---

## Instalação

### Opção A — Skill global (disponível em qualquer sessão)

```bash
# Criar o diretório da skill
mkdir -p ~/.deepagents/agent/skills/skill-converter

# Copiar a skill
cp SKILL.pt.md ~/.deepagents/agent/skills/skill-converter/SKILL.md
```

### Opção B — Skill local (escopo do projeto)

```bash
# Na raiz do projeto onde você vai trabalhar
mkdir -p .deepagents/skills/skill-converter
cp SKILL.pt.md .deepagents/skills/skill-converter/SKILL.md
```

### Verificar instalação

```bash
# Listar skills disponíveis
ls ~/.deepagents/agent/skills/
# Deve mostrar: skill-converter/

# Ou, se instalou localmente:
ls .deepagents/skills/
```

---

## Como usar

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

Veja os arquivos SKILL para um **exemplo real completo** (API Express.js com JWT auth, Docker, env vars) mostrando todas as 8 transformações aplicadas.

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
