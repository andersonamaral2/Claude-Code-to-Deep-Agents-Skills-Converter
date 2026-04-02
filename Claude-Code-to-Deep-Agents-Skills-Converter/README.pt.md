# Claude Code → Deep Agents Skill Converter

Converte **qualquer** SKILL.md escrita para o Claude Code em uma versão compatível com o Deep Agents CLI — preservando 100% do conhecimento de domínio e adaptando a interface de execução.

---

## Por que isso existe?

O Claude Code e o Deep Agents CLI são ambos agentes com acesso a filesystem e shell, mas falam "línguas" diferentes:

- **Claude Code** opera com bash implícito — ele simplesmente "escreve" arquivos e "roda" comandos sem precisar declarar qual tool está usando.
- **Deep Agents CLI** opera com tools tipadas e explícitas — `write_file`, `execute`, `edit_file`, `task`, etc.

Uma skill perfeita para o Claude Code **não funciona** no Deep Agents porque o agente não sabe traduzir "crie o arquivo X" para "use a tool `write_file` para criar X". Este conversor faz essa tradução automaticamente.

---

## Instalação

### Opção A — Skill global (disponível em qualquer sessão)

```bash
# Criar o diretório da skill
mkdir -p ~/.deepagents/agent/skills/skill-converter

# Copiar a skill
cp SKILL.md ~/.deepagents/agent/skills/skill-converter/SKILL.md
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

### Método 1 — Converter uma skill que está num arquivo

```bash
# 1. Coloque o SKILL.md do Claude Code em qualquer lugar acessível
#    Exemplo: ~/skills-claude-code/devops-audit/SKILL.md

# 2. Inicie o Deep Agents CLI
deepagents -y

# 3. Peça a conversão
> Leia o arquivo ~/skills-claude-code/devops-audit/SKILL.md e converta
> essa skill do Claude Code para Deep Agents. Salve como devops-audit-deepagents/SKILL.md
```

### Método 2 — Converter uma skill colando o conteúdo

```bash
# 1. Inicie o Deep Agents CLI
deepagents

# 2. Cole o conteúdo da skill e peça a conversão
> Converta essa skill do Claude Code para Deep Agents:
>
> [cole o conteúdo do SKILL.md aqui]
```

### Método 3 — Converter e já registrar como skill do Deep Agents

```bash
deepagents -y

> Leia ~/minha-skill-claude-code/SKILL.md, converta de Claude Code para Deep Agents,
> e salve direto em ~/.deepagents/agent/skills/minha-skill/SKILL.md
```

Depois disso, a skill convertida fica disponível permanentemente:

```bash
# Em qualquer sessão futura:
deepagents
> Crie o projeto seguindo a skill minha-skill
```

### Método 4 — Conversão não-interativa (one-shot)

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
| T1 | Header de contexto | Tabela mapeando tools do Deep Agents ao uso na skill |
| T2 | Plano de execução | Checklist para `write_todos` com todos os steps |
| T3 | Pré-requisitos | Verificação de ferramentas externas via `execute` |
| T4 | Criação explícita | Todo "crie o arquivo" vira `write_file` explícito |
| T5 | Testes inline | Após cada arquivo criado, teste via `execute` |
| T6 | Sub-agents | Fluxos multi-item convertidos para `task` paralelo |
| T7 | Guia de uso | 3 modos de uso (interativo, one-shot, CI/CD) |
| T8 | Troubleshooting | Problemas comuns baseados nas dependências |

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

---

## Estrutura de diretórios

Após a instalação, seu setup fica assim:

```
~/.deepagents/
  └── agent/
      ├── AGENTS.md
      ├── memories/
      └── skills/
          ├── skill-converter/          ← este conversor
          │   └── SKILL.md
          ├── devops-audit/             ← exemplo de skill convertida
          │   └── SKILL.md
          └── outra-skill-convertida/   ← quantas quiser
              └── SKILL.md
```

---

## Dicas

**Use `-y` durante a conversão.** O conversor faz várias operações de `read_file` e `write_file` — o auto-approve evita ficar parando a cada uma.

**Modelo recomendado.** Modelos com context window grande (128k+) funcionam melhor porque a skill original + as regras de conversão + a saída ocupam bastante espaço. Kimi K2.5, Claude Sonnet/Opus, GPT-4o são boas opções.

**Validação rápida.** Após converter, abra o SKILL.md gerado e busque por palavras como "crie", "escreva", "rode", "execute" sem a menção explícita da tool correspondente (`write_file`, `execute`, etc.). Se encontrar alguma, a conversão ficou incompleta.

**Skills muito grandes (>500 linhas).** Se a skill original for enorme, considere pedir ao conversor para dividir em sub-skills. O Deep Agents suporta múltiplos SKILL.md na mesma pasta de skill.

---

## Limitações

- O conversor não executa a skill — ele apenas adapta o documento para que o Deep Agents CLI consiga executá-la.
- Skills que dependem de features exclusivas do sandbox do Claude Code (como acesso a portas de rede específicas) podem precisar de ajustes manuais no ambiente local.
- A qualidade da conversão depende do modelo LLM que está rodando o Deep Agents CLI.

---

## Licença

MIT — use, adapte e distribua como quiser.
