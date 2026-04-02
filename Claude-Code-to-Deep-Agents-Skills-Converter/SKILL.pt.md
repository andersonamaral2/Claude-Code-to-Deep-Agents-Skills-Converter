# Skill: Claude Code → Deep Agents Skill Converter

> Converte qualquer SKILL.md escrita para o Claude Code em uma versão totalmente compatível com o Deep Agents CLI, preservando 100% do conhecimento de domínio e adaptando a interface de execução.

---

## Quando usar

Esta skill é ativada quando o usuário pedir algo como:

- "Converta essa skill do Claude Code para Deep Agents"
- "Adapte esse SKILL.md para funcionar no Deep Agents"
- "Transforme essa skill de Claude Code em Deep Agents"
- "Tenho uma skill do Claude Code, quero usar no Deep Agents"
- Ou quando o usuário fornecer um arquivo SKILL.md e pedir para "converter", "adaptar", "portar", "migrar"

---

## Contexto: Por que a conversão é necessária

O Claude Code e o Deep Agents CLI compartilham a mesma filosofia (agente com acesso a filesystem + shell), mas diferem na **interface de execução**:

| Conceito | Claude Code | Deep Agents CLI |
|----------|-------------|-----------------|
| Criar arquivo | Implícito (o LLM "escreve") | `write_file` tool explícita |
| Editar arquivo | Implícito | `edit_file` tool (search/replace) |
| Ler arquivo | Implícito | `read_file` tool |
| Executar shell | `bash` nativo no sandbox | `execute` tool (com HITL ou `-y`) |
| Navegar filesystem | `ls`, `cat`, `find` implícitos | `ls`, `glob`, `grep` tools tipadas |
| Planejamento | Raciocínio implícito do LLM | `write_todos` tool explícita |
| Sub-tarefas | Não disponível nativamente | `task` tool (sub-agents isolados) |
| Memória | `CLAUDE.md` (por sessão) | `AGENTS.md` + `/memories/` (persistente) |
| Skills | Não nativo | `~/.deepagents/<agent>/skills/<nome>/SKILL.md` |
| HTTP requests | `curl` via bash | `http_request` tool nativa |
| Web search | Não nativo | `web_search` tool (via Tavily) |
| MCP servers | `.claude/mcp.json` | `.deepagents/mcp.json` |
| Aprovação humana | Automática no sandbox | HITL por padrão, `-y` para auto-approve |
| Context window | Grande (200k tokens) | Depende do modelo + auto-compaction |

---

## Procedimento de Conversão

Ao receber uma skill do Claude Code, siga estes passos **na ordem exata**:

### Passo 0 — Planejar via `write_todos`

```
- [ ] 1. Ler e analisar a skill original do Claude Code
- [ ] 2. Identificar todos os padrões de execução implícitos
- [ ] 3. Mapear cada padrão para a tool equivalente do Deep Agents
- [ ] 4. Reescrever a skill com instruções explícitas de tools
- [ ] 5. Adicionar seções obrigatórias do Deep Agents
- [ ] 6. Validar a skill convertida
- [ ] 7. Salvar via write_file
```

### Passo 1 — Ler a skill original

Use `read_file` para ler o SKILL.md fornecido pelo usuário. Se o usuário colou o conteúdo no chat, pule este passo.

### Passo 2 — Identificar padrões implícitos

Escaneie o texto procurando estes padrões do Claude Code que precisam de tradução:

#### 2a. Criação de arquivos

**Detectar frases como:**
- "Crie o arquivo X"
- "Escreva em X.py"
- "O arquivo deve conter..."
- "Gere o seguinte código em..."
- "Salve como..."
- Blocos de código com path no comentário (`# arquivo: src/main.py`)

**Converter para:**
```
Use `write_file` para criar `{path}`:
```

#### 2b. Edição de arquivos

**Detectar frases como:**
- "Edite o arquivo X"
- "Modifique a função Y"
- "Adicione ao arquivo..."
- "Substitua X por Y"
- "No arquivo X, troque..."

**Converter para:**
```
Use `edit_file` para modificar `{path}` (search/replace):
  - old: {trecho_original}
  - new: {trecho_novo}
```

#### 2c. Execução de comandos

**Detectar frases como:**
- "Execute: `comando`"
- "Rode `comando`"
- "No terminal: `comando`"
- Blocos ```bash sem contexto de arquivo
- "Instale com `pip install ...`"
- "Teste com `pytest`"

**Converter para:**
```
Use `execute` para rodar:
```bash
{comando}
```
```

#### 2d. Leitura e inspeção

**Detectar frases como:**
- "Leia o arquivo X"
- "Verifique o conteúdo de..."
- "Inspecione..."
- "Confira se o arquivo existe"
- "Liste os arquivos em..."
- "Busque por X nos arquivos"

**Converter para:**
```
Use `read_file` para ler `{path}`
Use `ls` para listar `{dir}`
Use `glob` para buscar `{pattern}`
Use `grep` para procurar `{texto}` em `{path}`
```

#### 2e. Requisições HTTP

**Detectar frases como:**
- "Faça uma requisição para..."
- "Chame a API..."
- "Use `curl` para..."
- "POST/GET/PUT para URL..."

**Converter para:**
```
Use `http_request` para chamar `{url}`:
  - method: {GET|POST|PUT|DELETE}
  - headers: {headers}
  - body: {body}

# OU, se for um comando complexo com pipes/auth:
Use `execute` para rodar:
```bash
curl -X POST ...
```
```

#### 2f. Fluxos multi-step complexos

**Detectar frases como:**
- "Para cada item, faça..."
- "Repita para todos os..."
- "Processe em paralelo..."
- "Execute para cada repositório..."

**Converter para:**
```
Use `task` para delegar cada iteração a um sub-agent com contexto isolado:
  - Instrução: "{descrição da subtarefa para o item N}"
```

### Passo 3 — Aplicar as 8 Transformações Obrigatórias

Toda skill convertida **DEVE** conter estas 8 transformações:

#### T1 — Header de contexto de execução

Adicionar logo após o título e descrição da skill:

```markdown
## Contexto de Execução

Esta skill roda dentro do **Deep Agents CLI**. Tools disponíveis:

| Tool | Uso nesta skill |
|------|----------------|
| `execute` | {descrever uso específico} |
| `write_file` | {descrever uso específico} |
| `edit_file` | {descrever uso específico} |
| `read_file` | {descrever uso específico} |
| `ls` / `glob` / `grep` | {descrever uso específico} |
| `task` | {descrever uso específico} |
| `write_todos` | {descrever uso específico} |
| `http_request` | {descrever uso específico} |
| `web_search` | {descrever uso específico} |

**Regras críticas de execução:**
1. Sempre comece criando o plano via `write_todos`.
2. Crie arquivos um a um via `write_file` — nunca tente gerar tudo de uma vez.
3. Teste cada módulo via `execute` imediatamente após criá-lo.
4. Use `task` para delegar subtarefas longas ou paralelas a sub-agents.
```

Preencha a coluna "Uso nesta skill" analisando o conteúdo real da skill. Remova linhas de tools que não se aplicam à skill específica.

#### T2 — Plano de execução

Adicionar seção com checklist para `write_todos`. Extraia os passos lógicos da skill original e converta em checklist:

```markdown
## Plano de Execução (use com `write_todos`)

Ao receber o pedido, execute `write_todos` com:

- [ ] 1. {passo extraído da skill original}
- [ ] 2. {passo extraído da skill original}
- [ ] ...
- [ ] N. Testar fluxo completo
```

#### T3 — Verificação de pré-requisitos

Se a skill depende de ferramentas externas (gh CLI, aws CLI, docker, node, etc.), adicionar:

```markdown
## Verificação de Pré-requisitos

Antes de criar qualquer arquivo, use `execute` para verificar:

```bash
{ferramenta} --version
```

Se não estiver instalado, instale via `execute`:

```bash
{comando de instalação}
```
```

#### T4 — Instruções explícitas de criação de arquivo

Toda vez que a skill original menciona "crie o arquivo X", na versão convertida deve aparecer:

```markdown
Use `write_file` para criar `{path}`:
```

Seguido do conteúdo do arquivo.

#### T5 — Instruções explícitas de teste

Após cada módulo/arquivo criado, adicionar:

```markdown
Teste via `execute`:
```bash
python -c "from {modulo} import {func}; print('OK')"
```
```

Ou equivalente para a linguagem da skill.

#### T6 — Uso de sub-agents para paralelismo

Se a skill envolve processar múltiplos itens (repos, arquivos, endpoints, etc.), adicionar:

```markdown
### Execução paralela via sub-agents

Para processar múltiplos {itens}, use `task` para cada um:

O agente principal lista os {itens} via `execute`, depois para cada item
cria um sub-agent via `task` com instrução específica e contexto isolado.
```

#### T7 — Guia de uso com Deep Agents CLI

Adicionar seção final com os modos de uso:

```markdown
## Guia de Uso com Deep Agents CLI

### Modo 1 — Construção (one-shot)
```bash
deepagents -y "Crie {o que a skill constrói} seguindo a skill {nome}"
```

### Modo 2 — Execução interativa
```bash
deepagents
> {comando natural que ativa a skill}
```

### Modo 3 — Não-interativo (CI/CD)
```bash
deepagents -n -y -S "{comandos permitidos}" "{instrução}"
```
```

#### T8 — Seção de troubleshooting

Adicionar seção com problemas comuns baseados nas dependências da skill:

```markdown
## Troubleshooting

### {Ferramenta X} não encontrada
```bash
# Verificar:
{ferramenta} --version
# Instalar:
{comando de instalação}
```

### Sub-agent não acessa módulos do projeto
```bash
# O sub-agent roda em contexto isolado. Instruí-lo a:
cd /path/to/projeto && {comando}
```

### Context window estourando
```
Use /compact para forçar compactação antes de continuar
```
```

### Passo 4 — Transformações de referência Claude Code → Deep Agents

Fazer find/replace semântico no texto:

| Encontrar (Claude Code) | Substituir (Deep Agents) |
|--------------------------|--------------------------|
| "CLAUDE.md" | "AGENTS.md" |
| ".claude/" | ".deepagents/" |
| ".claude/mcp.json" | ".deepagents/mcp.json" |
| "Claude Code" (como executor) | "Deep Agents CLI" |
| "sandbox" | "ambiente local (com HITL)" |
| "bash tool" / "bash nativo" | "tool `execute`" |
| "escreva o arquivo" (implícito) | "use `write_file` para criar" |
| "edite o arquivo" (implícito) | "use `edit_file` para modificar" |
| "leia o arquivo" (implícito) | "use `read_file` para ler" |

### Passo 5 — Preservar 100% do conhecimento de domínio

**CRÍTICO:** A conversão é sobre a *interface de execução*, não sobre o *conteúdo técnico*. Preserve integralmente:

- Todas as tabelas de referência (métricas, scores, thresholds, regex, etc.)
- Todos os blocos de código de implementação
- Todas as fórmulas e cálculos
- Todos os templates e formatos de saída
- Todas as regras de negócio e edge cases
- Todos os diagramas de arquitetura
- Todas as configurações de infraestrutura
- Todos os exemplos e amostras

**Nunca resumir, simplificar ou omitir conteúdo técnico.** A skill convertida deve ter tamanho igual ou maior que a original.

### Passo 6 — Validar a skill convertida

Antes de salvar, verificar mentalmente:

```
✓ Tem header de contexto de execução com tabela de tools?
✓ Tem plano de execução para write_todos?
✓ Tem verificação de pré-requisitos?
✓ Toda criação de arquivo usa "write_file" explicitamente?
✓ Todo comando shell usa "execute" explicitamente?
✓ Toda edição usa "edit_file" explicitamente?
✓ Toda leitura usa "read_file" explicitamente?
✓ Fluxos paralelos usam "task" para sub-agents?
✓ Tem guia de uso com Deep Agents CLI?
✓ Tem seção de troubleshooting?
✓ TODO o conhecimento de domínio foi preservado?
✓ Nenhuma tabela, fórmula, regex ou template foi omitido?
✓ Referências a "CLAUDE.md" foram trocadas por "AGENTS.md"?
✓ Referências a ".claude/" foram trocadas por ".deepagents/"?
```

### Passo 7 — Salvar

Use `write_file` para salvar a skill convertida:

```bash
# Path sugerido — o usuário pode escolher outro:
write_file("{nome-da-skill}/SKILL.md", conteudo_convertido)
```

---

## Exemplos de Conversão

### Exemplo 1: Comando bash implícito

**Original (Claude Code):**
```markdown
Instale as dependências:
```bash
pip install langchain boto3
```
```

**Convertido (Deep Agents):**
```markdown
Instale as dependências via `execute`:
```bash
pip install langchain boto3
```
```

### Exemplo 2: Criação de arquivo implícita

**Original (Claude Code):**
```markdown
Crie o arquivo `src/main.py` com o seguinte conteúdo:

```python
def main():
    print("Hello")
```
```

**Convertido (Deep Agents):**
```markdown
Use `write_file` para criar `src/main.py`:

```python
def main():
    print("Hello")
```

Teste via `execute`:
```bash
python -c "from src.main import main; main()"
```
```

### Exemplo 3: Edição de arquivo existente

**Original (Claude Code):**
```markdown
No arquivo `config.py`, adicione a variável `DEBUG = True` após a linha de imports.
```

**Convertido (Deep Agents):**
```markdown
Use `edit_file` para modificar `config.py`:
  - Buscar: `import os`
  - Substituir por: `import os\n\nDEBUG = True`
```

### Exemplo 4: Fluxo multi-item

**Original (Claude Code):**
```markdown
Para cada repositório da organização, execute a auditoria e gere o relatório.
```

**Convertido (Deep Agents):**
```markdown
Liste os repositórios via `execute`:
```bash
gh repo list {org} --limit 50 --json name
```

Para cada repositório, use `task` para delegar a um sub-agent:
```
task("Audite o repositório {org}/{repo}. Execute: cd projeto && python audit.py {repo}")
```

Cada sub-agent roda em contexto isolado, sem poluir a janela de contexto principal.
```

### Exemplo 5: Referências a CLAUDE.md

**Original (Claude Code):**
```markdown
Adicione as convenções do projeto ao `CLAUDE.md` na raiz.
```

**Convertido (Deep Agents):**
```markdown
Adicione as convenções do projeto ao `AGENTS.md` na raiz (equivalente ao CLAUDE.md do Claude Code).

Alternativamente, salve como memória persistente via `/remember "convenção: ..."` na sessão interativa.
```

### Exemplo 6: curl/HTTP via bash

**Original (Claude Code):**
```markdown
Teste a API:
```bash
curl -X POST https://api.exemplo.com/data -H "Authorization: Bearer $TOKEN" -d '{"key": "value"}'
```
```

**Convertido (Deep Agents):**
```markdown
Teste a API via `http_request`:
  - URL: `https://api.exemplo.com/data`
  - Method: POST
  - Headers: `{"Authorization": "Bearer $TOKEN"}`
  - Body: `{"key": "value"}`

Ou, se precisar de pipes ou processamento shell, use `execute`:
```bash
curl -X POST https://api.exemplo.com/data -H "Authorization: Bearer $TOKEN" -d '{"key": "value"}'
```
```

---

## Casos Especiais

### Skills que usam Docker

Se a skill original monta containers, a conversão mantém os comandos Docker via `execute`, mas adiciona nota:

```markdown
**Nota Deep Agents:** Comandos Docker rodam via `execute` e requerem que o Docker
esteja instalado e acessível no ambiente local. Se usando sandbox remoto
(Modal, Daytona), verifique se Docker-in-Docker está habilitado.
```

### Skills que usam MCP servers

Converter referências de configuração:

```markdown
# Claude Code: .claude/mcp.json
# Deep Agents: .deepagents/mcp.json (mesmo formato JSON)

Use `write_file` para criar `.deepagents/mcp.json`:
```json
{
  "mcpServers": {
    "{nome}": {
      "command": "{cmd}",
      "args": [{args}]
    }
  }
}
```
```

### Skills com context window grande

Se a skill original assume 200k tokens (Claude Code padrão), adicionar aviso:

```markdown
**Nota Deep Agents:** Esta skill foi originalmente projetada para contexto de 200k tokens.
Se estiver usando um modelo com contexto menor, considere:
- Usar `/compact` periodicamente para liberar espaço
- Usar `task` para isolar subtarefas em sub-agents
- Dividir a execução em etapas menores
```

### Skills que geram muitos arquivos

Se a skill cria mais de 10 arquivos, adicionar padrão de diretórios primeiro:

```markdown
**Antes de criar os arquivos**, crie a estrutura de diretórios via `execute`:
```bash
mkdir -p {dir1} {dir2} {dir3}
touch {dir1}/__init__.py {dir2}/__init__.py
```
```

---

## Estrutura Final da Skill Convertida

Toda skill convertida deve seguir esta estrutura (em ordem):

```
1. # Título da Skill
2. > Descrição (blockquote)
3. ## Contexto de Execução (tabela de tools)          ← T1
4. ## Plano de Execução (checklist write_todos)        ← T2
5. ## Verificação de Pré-requisitos                    ← T3
6. ## Arquitetura (preservar da original)
7. ## Estrutura de Arquivos (com instruções write_file) ← T4
8. ## Dependências (com instruções execute)
9. ## [Seções técnicas da original, convertidas]       ← T4/T5/T6
10. ## Guia de Uso com Deep Agents CLI                  ← T7
11. ## Troubleshooting                                  ← T8
```

As seções 6-9 variam conforme a skill. O importante é que TODAS as seções técnicas passem pela conversão de padrões (Passo 2) e pelas 8 transformações (Passo 3).

---

## Regras de Ouro

1. **Nunca perder conteúdo.** A skill convertida tem tamanho ≥ original.
2. **Nunca assumir implícitos.** O Deep Agents CLI precisa de instruções explícitas de qual tool usar.
3. **Sempre começar com `write_todos`.** O plano é o alicerce de toda execução no Deep Agents.
4. **Testar depois de cada `write_file`.** O padrão cria → testa → próximo é inquebrável.
5. **Usar `task` para paralelismo.** Se a skill processa N itens, N sub-agents.
6. **Preservar todo conhecimento de domínio.** Tabelas, regex, fórmulas, templates — tudo.
