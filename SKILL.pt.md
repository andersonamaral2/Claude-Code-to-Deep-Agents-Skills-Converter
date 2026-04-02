---
name: skill-converter
description: "Converte qualquer SKILL.md entre os formatos Claude Code e Deep Agents CLI — preservando 100% do conhecimento de dominio e adaptando a interface de execucao. Suporta conversao direta, reversa, dry-run e batch."
metadata:
  converter-version: "2.0"
  deep-agents-compat: ">=0.0.34"
  source-repo: "https://github.com/andersonamaral2/Claude-Code-to-Deep-Agents-Skills-Converter"
---

# Skill: Claude Code ↔ Deep Agents Skill Converter

> Converte qualquer SKILL.md entre os formatos Claude Code e Deep Agents CLI — preservando 100% do conhecimento de domínio e adaptando a interface de execução. Suporta conversão direta (Claude Code → Deep Agents), conversão reversa (Deep Agents → Claude Code), preview dry-run e processamento em lote.

---

## Quando usar

Esta skill é ativada quando o usuário pedir algo como:

- "Converta essa skill do Claude Code para Deep Agents"
- "Converta essa skill do Deep Agents para Claude Code"
- "Adapte esse SKILL.md para funcionar no Deep Agents"
- "Transforme essa skill de Claude Code em Deep Agents"
- "Tenho uma skill do Claude Code, quero usar no Deep Agents"
- "Mostre o preview da conversão sem salvar" / "Dry-run"
- "Converta todas as skills nessa pasta"
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
| Sub-tarefas | `Agent` tool (sub-processos) | `task` tool (sub-agents isolados) |
| Memória | `CLAUDE.md` + `.claude/` memórias | `AGENTS.md` + `/memories/` (persistente) |
| Skills | `.claude/` comandos / slash commands | `~/.deepagents/<agent>/skills/<nome>/SKILL.md` |
| HTTP requests | `curl` via bash | `http_request` tool nativa |
| Web search | Não nativo | `web_search` tool (via Tavily) |
| MCP servers | `.claude/mcp.json` | `.deepagents/mcp.json` (mesmo formato JSON) |
| Chamadas MCP custom | `mcp__server__tool_name` | Tools MCP dinâmicas (mesmo protocolo, auto-loaded) |
| Aprovação humana | Automática no sandbox | HITL por padrão, `-y` para auto-approve |
| Context window | Grande (200k tokens) | Depende do modelo + auto-compaction |
| Hooks / automação | `settings.json` hooks (pre/post) | Não nativo (usar `execute` com shell scripts) |
| Extended thinking | Blocos `thinking` nativos | Depende do modelo (pass-through se suportado) |
| Variáveis de ambiente | Disponíveis no sandbox `$VAR` | Disponíveis localmente; usar `.env` ou `execute` para export |
| Metadados da skill | Sem frontmatter | Frontmatter YAML (`name`, `description`, `allowed-tools`) |

---

## Modos de Conversão

### Modo A — Direto: Claude Code → Deep Agents (padrão)

Siga o procedimento completo abaixo (Passos 0–8).

### Modo B — Reverso: Deep Agents → Claude Code

Veja a seção [Conversão Reversa](#conversão-reversa-deep-agents--claude-code) no final.

### Modo C — Dry-run / Preview

Quando o usuário pedir preview ou dry-run:

1. Realize a conversão completa em memória.
2. Em vez de salvar via `write_file`, exiba uma **comparação estilo diff**:
   - Mostre seções lado a lado ou como diff unificado.
   - Destaque o que foi adicionado (T1–T8), substituído (trocas semânticas) e preservado.
3. Peça confirmação do usuário antes de salvar.

```
Exemplo de output:
━━━ PREVIEW DA CONVERSÃO ━━━
+ Adicionado: Header de Contexto de Execução (T1)
+ Adicionado: Plano de Execução com 7 passos (T2)
+ Adicionado: Verificação de pré-requisitos: node, docker (T3)
~ Substituído: 12 criações implícitas de arquivo → write_file (T4)
~ Substituído: 8 blocos bash → execute (T4)
+ Adicionado: 12 testes inline após write_file (T5)
+ Adicionado: 3 delegações via task para fluxos paralelos (T6)
+ Adicionado: Guia de uso com 3 modos (T7)
+ Adicionado: Seção de troubleshooting (T8)
= Preservado: 100% do conhecimento de domínio (tabelas, código, fórmulas)
━━━ Tamanho: 340 linhas → 520 linhas (+53%) ━━━
Salvar em {path}? [s/n]
```

### Modo D — Conversão em lote (batch)

Quando o usuário pedir para converter múltiplas skills de uma vez:

1. Use `glob` para encontrar todos os arquivos SKILL.md no diretório especificado.
2. Para cada skill encontrada, use `task` para delegar a conversão a um sub-agent:
   ```
   task("Converta a skill Claude Code em {path} para formato Deep Agents.
         Salve o resultado em {output_path}. Siga o procedimento do SKILL.md do skill-converter.")
   ```
3. Após todos os sub-agents finalizarem, gere um relatório resumido:
   ```
   ━━━ RELATÓRIO DE CONVERSÃO EM LOTE ━━━
   ✓ skills/devops-audit/SKILL.md → convertida (280 → 410 linhas)
   ✓ skills/api-generator/SKILL.md → convertida (150 → 230 linhas)
   ✗ skills/broken-skill/SKILL.md → FALHOU: nenhum conteúdo acionável encontrado
   ━━━ 2/3 bem-sucedidas ━━━
   ```

---

## Procedimento de Conversão Direta (Claude Code → Deep Agents)

Ao receber uma skill do Claude Code, siga estes passos **na ordem exata**:

### Passo 0 — Planejar via `write_todos`

```
- [ ] 1. Ler e analisar a skill original do Claude Code
- [ ] 2. Identificar todos os padrões de execução implícitos (incluindo comandos inline)
- [ ] 3. Mapear cada padrão para a tool equivalente do Deep Agents
- [ ] 4. Reescrever a skill com instruções explícitas de tools
- [ ] 5. Adicionar seções obrigatórias do Deep Agents (T1–T8)
- [ ] 6. Tratar casos especiais (env vars, condicionais, MCP, hooks)
- [ ] 7. Adicionar frontmatter YAML com metadados
- [ ] 8. Validar a skill convertida (checklist executável)
- [ ] 9. Salvar via write_file (ou mostrar preview se dry-run)
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

#### 2c. Execução de comandos (bloco E inline)

**Detectar blocos de código:**
- Blocos ```bash sem contexto de arquivo
- "Execute: `comando`"
- "Rode `comando`"

**Também detectar comandos inline (IMPORTANTE — facilmente ignorados):**
- "rode `npm install` e depois..."
- "use `pip install flask` para instalar"
- "após rodar `docker build .`..."
- Qualquer comando entre crases dentro de uma frase que não seja um path de arquivo ou nome de variável

**Como distinguir comandos inline de referências a código:**
- Se o conteúdo entre crases começa com um CLI conhecido (`npm`, `pip`, `docker`, `git`, `curl`, `make`, `pytest`, `cargo`, etc.) → é um comando → converter.
- Se é um nome de função/variável como `main()` ou `$CONFIG_PATH` → é uma referência → manter.

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

#### 2g. Sub-processos Agent do Claude Code

**Detectar frases como:**
- "Use a ferramenta Agent para..."
- "Lance um sub-agent para..."
- "Delegue a um agente em background..."
- Referências a `subagent_type`, `isolation: "worktree"`

**Converter para:**
```
Use `task` para delegar a um sub-agent:
  - Instrução: "{descrição da tarefa}"

Nota: O `task` do Deep Agents fornece contexto isolado similar ao Agent tool do Claude Code.
Isolamento via worktree não é suportado nativamente — use `execute` com comandos `git worktree`
se precisar de isolamento de branch.
```

#### 2h. Hooks e automação

**Detectar frases como:**
- "Configure um hook no settings.json..."
- "Adicione um hook de pre-commit..."
- "Configure uma automação que roda quando..."
- Referências a hooks do `settings.json`, `user-prompt-submit-hook`, etc.

**Converter para:**
```
O Deep Agents CLI não possui hooks nativos. Converta para shell scripts executados via `execute`:

Use `write_file` para criar `scripts/{nome_hook}.sh`:
```bash
#!/bin/bash
{lógica_do_hook}
```

Use `execute` para torná-lo executável:
```bash
chmod +x scripts/{nome_hook}.sh
```

Adicione uma nota no AGENTS.md: "Execute `scripts/{nome_hook}.sh` antes/depois de {evento}."
```

#### 2i. Extended thinking / blocos de raciocínio

**Detectar frases como:**
- "Use extended thinking para raciocinar sobre..."
- Referências a blocos `thinking` ou `budget_tokens`

**Converter para:**
```
Nota: Extended thinking depende do modelo no Deep Agents CLI.
Se o modelo subjacente suportar tokens de raciocínio, eles funcionam automaticamente.
Nenhuma conversão explícita necessária — remova configurações específicas de thinking
e deixe o modelo lidar com o raciocínio nativamente.
```

#### 2j. Variáveis de ambiente e secrets

**Detectar frases como:**
- "Defina `$API_KEY` como..."
- "Exporte o token: `export TOKEN=...`"
- "O arquivo `.env` deve conter..."
- "Use a variável de ambiente `$DATABASE_URL`"
- Referências a secrets, tokens, API keys no sandbox

**Converter para:**
```
## Configuração de Ambiente

Antes da execução, verifique as variáveis de ambiente necessárias via `execute`:
```bash
# Verificar variáveis obrigatórias
for var in {VAR1} {VAR2} {VAR3}; do
  if [ -z "${!var}" ]; then
    echo "ERRO: $var não está definida"
    exit 1
  fi
done
echo "Todas as variáveis de ambiente OK"
```

Se usar arquivo `.env`, carregue via `execute`:
```bash
set -a && source .env && set +a
```

**Nota de segurança:** Nunca coloque secrets diretamente no SKILL.md.
Use variáveis de ambiente ou arquivo `.env` (adicionado ao `.gitignore`).
```

#### 2k. Fluxos condicionais / específicos por plataforma

**Detectar frases como:**
- "Se o sistema for macOS, faça X; se Linux, faça Y"
- "Para usuários Windows..."
- "Se Docker estiver disponível, use containers; caso contrário..."
- "Quando rodando em CI..."

**Converter para:**
```
### Execução específica por plataforma

Use `execute` para detectar a plataforma e agir conforme:
```bash
OS=$(uname -s)
case "$OS" in
  Darwin) {comando_macOS} ;;
  Linux)  {comando_linux} ;;
  *)      echo "SO não suportado: $OS"; exit 1 ;;
esac
```

Para verificações de disponibilidade de ferramentas:
```bash
if command -v docker &>/dev/null; then
  {caminho_docker}
else
  {caminho_alternativo}
fi
```
```

#### 2l. Chamadas a tools MCP customizadas

**Detectar frases como:**
- "Use a tool MCP `mcp__server__action`..."
- "Chame `mcp__slack__send_message`..."
- Referências a configurações de servidores em `.claude/mcp.json`
- Qualquer chamada de tool começando com `mcp__`

**Converter para:**
```
## Integração com Tools MCP

O Deep Agents CLI carrega tools MCP automaticamente do `.deepagents/mcp.json`.
Os mesmos servidores e tools MCP estão disponíveis — só o caminho da config muda.

1. Use `write_file` para criar `.deepagents/mcp.json`:
```json
{conteúdo original do .claude/mcp.json}
```

2. As chamadas de tools MCP funcionam da mesma forma no Deep Agents. Se a skill original
   chama `mcp__server__action`, a mesma tool está disponível após carregar a config MCP.
   
   Para servidores MCP de projeto (stdio), o usuário precisa aprovar no primeiro uso
   (ou usar `--trust-project-mcp` para pular a aprovação).
```

### Passo 3 — Aplicar as 8 Transformações Obrigatórias

Toda skill convertida **DEVE** conter estas 8 transformações:

#### T1 — Header de contexto de execução

Adicionar logo após o título e descrição da skill. **Incluir apenas as tools que a skill realmente usa** — não preencher com tools não utilizadas:

```markdown
## Contexto de Execução

Esta skill roda dentro do **Deep Agents CLI** (v0.0.34+). Tools disponíveis:

| Tool | Uso nesta skill |
|------|----------------|
| `{tool}` | {descrição específica de uso} |

> **Liste apenas as tools que esta skill realmente usa.** Remova todas as linhas que não se aplicam.

**Regras críticas de execução:**
1. Sempre comece criando o plano via `write_todos`.
2. Crie arquivos um a um via `write_file` — nunca tente gerar tudo de uma vez.
3. Teste cada módulo via `execute` imediatamente após criá-lo.
4. Use `task` para delegar subtarefas longas ou paralelas a sub-agents.
```

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

Se a skill depende de ferramentas externas (gh CLI, aws CLI, docker, node, etc.) ou variáveis de ambiente, adicionar:

```markdown
## Verificação de Pré-requisitos

Antes de criar qualquer arquivo, use `execute` para verificar:

```bash
# Ferramentas
{ferramenta} --version

# Variáveis de ambiente (se aplicável)
[ -z "$VARIAVEL_OBRIGATORIA" ] && echo "ERRO: VARIAVEL_OBRIGATORIA não definida" && exit 1
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

### Variável de ambiente não definida
```bash
# Verificar o que falta:
env | grep PREFIXO_ESPERADO
# Definir:
export NOME_VAR="valor"
# Ou carregar do .env:
set -a && source .env && set +a
```

### Sub-agent não acessa módulos do projeto
```bash
# O sub-agent roda em contexto isolado. Instruí-lo a:
cd /path/to/projeto && {comando}
```

### Context window estourando
```
Use /compact para forçar compactação antes de continuar.
Considere dividir a tarefa com sub-agents via `task`.
```
```

### Passo 4 — Adicionar frontmatter YAML

Toda skill convertida deve incluir frontmatter compatível com Deep Agents:

```yaml
---
name: {nome-da-skill-kebab-case}
description: "{Descrição em uma linha, máx 1024 chars — usada para descoberta de skills}"
metadata:
  converted-from: claude-code
  converter-version: "2.0"
  deep-agents-compat: ">=0.0.34"
---
```

### Passo 5 — Transformações de referência Claude Code → Deep Agents

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
| "Agent tool" / "sub-agent" | "tool `task`" |
| "settings.json hooks" | "shell scripts via `execute`" |
| chamadas `mcp__server__tool` | Mesmo nome de tool (verificar se config MCP existe) |

### Passo 6 — Preservar 100% do conhecimento de domínio

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

### Passo 7 — Validar a skill convertida (checklist executável)

Antes de salvar, execute esta validação via `execute`. Isso substitui a antiga abordagem de "verificar mentalmente":

```bash
FILE="{path_da_skill_convertida}"

echo "=== VALIDAÇÃO DA CONVERSÃO DE SKILL ==="
ERRORS=0

# Verificar se seções obrigatórias existem
for section in "Contexto de Execução" "Plano de Execução" "Pré-requisitos" "Guia de Uso" "Troubleshooting"; do
  if ! grep -q "$section" "$FILE"; then
    echo "FALTANDO: seção $section"
    ERRORS=$((ERRORS + 1))
  fi
done

# Verificar padrões implícitos não convertidos
for pattern in "crie o arquivo" "escreva o arquivo" "edite o arquivo" "leia o arquivo" "rode o comando" "execute o comando"; do
  COUNT=$(grep -ic "$pattern" "$FILE" || true)
  if [ "$COUNT" -gt 0 ]; then
    echo "AVISO: Encontrado '$pattern' $COUNT vez(es) — verifique se cada um tem referência explícita à tool"
  fi
done

# Verificar blocos bash órfãos (sem referência a execute por perto)
BASH_BLOCKS=$(grep -c '```bash' "$FILE" || true)
EXECUTE_REFS=$(grep -c '`execute`' "$FILE" || true)
if [ "$BASH_BLOCKS" -gt "$EXECUTE_REFS" ]; then
  echo "AVISO: $BASH_BLOCKS blocos bash mas apenas $EXECUTE_REFS referências a execute"
fi

# Verificar se frontmatter existe
if ! head -1 "$FILE" | grep -q '^---'; then
  echo "FALTANDO: frontmatter YAML"
  ERRORS=$((ERRORS + 1))
fi

# Verificar referências antigas
for old_ref in "CLAUDE.md" ".claude/" "sandbox"; do
  if grep -q "$old_ref" "$FILE"; then
    echo "AVISO: Encontrada referência não convertida '$old_ref'"
  fi
done

echo "=== VALIDAÇÃO COMPLETA: $ERRORS erros ==="
```

Se erros > 0, corrija antes de salvar.

### Passo 8 — Salvar

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

### Exemplo 7: Comandos inline (facilmente ignorados)

**Original (Claude Code):**
```markdown
Após gerar os models, rode `npm run build` para compilar e use `npm test` para verificar que tudo funciona.
```

**Convertido (Deep Agents):**
```markdown
Após gerar os models, compile via `execute`:
```bash
npm run build
```

Em seguida, verifique via `execute`:
```bash
npm test
```
```

### Exemplo 8: Variáveis de ambiente

**Original (Claude Code):**
```markdown
Defina sua chave OpenAI: `export OPENAI_API_KEY=sk-...`
O script lê `$DATABASE_URL` do ambiente.
```

**Convertido (Deep Agents):**
```markdown
## Configuração de Ambiente

Verifique as variáveis de ambiente necessárias via `execute`:
```bash
for var in OPENAI_API_KEY DATABASE_URL; do
  if [ -z "${!var}" ]; then
    echo "ERRO: $var não está definida"
    exit 1
  fi
done
echo "Todas as variáveis de ambiente OK"
```

Se não estiverem definidas, configure via `execute`:
```bash
export OPENAI_API_KEY="sk-..."   # Substitua pela sua chave real
export DATABASE_URL="postgresql://..."
```

**Nota de segurança:** Nunca coloque secrets de produção no código. Use arquivo `.env` adicionado ao `.gitignore`.
```

### Exemplo 9: Condicional / específico por plataforma

**Original (Claude Code):**
```markdown
No macOS, instale com `brew install redis`. No Linux, use `apt-get install redis-server`.
```

**Convertido (Deep Agents):**
```markdown
Instale o Redis via `execute` (detectando a plataforma):
```bash
OS=$(uname -s)
case "$OS" in
  Darwin) brew install redis ;;
  Linux)  sudo apt-get install -y redis-server ;;
  *)      echo "SO não suportado: $OS"; exit 1 ;;
esac
```
```

### Exemplo 10: Agent tool do Claude Code

**Original (Claude Code):**
```markdown
Use a ferramenta Agent para lançar um agente em background que rode a suíte completa de testes enquanto você continua com a próxima tarefa.
```

**Convertido (Deep Agents):**
```markdown
Use `task` para delegar a execução dos testes a um sub-agent com contexto isolado:
```
task("Rode a suíte completa de testes: cd /path/to/projeto && npm test. Reporte resumo de passa/falha.")
```

O sub-agent roda independentemente. Continue com a próxima tarefa no agente principal.
```

### Exemplo 11: Conversão completa real (antes/depois completo)

**Original (Claude Code) — Skill de scaffold de API REST:**
```markdown
# Skill: Express API Generator

Crie uma API REST Express.js pronta para produção com autenticação.

## Pré-requisitos

Certifique-se de que Node.js 18+ e npm estão instalados. Docker também é necessário para o banco de dados.

## Passos

Crie a estrutura do projeto. Inicialize com `npm init -y` e instale as dependências:
`npm install express jsonwebtoken bcrypt pg dotenv`

Crie o arquivo `src/index.js`:
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

Crie `src/routes/auth.js` com rotas de login e registro JWT.

Crie `src/routes/users.js` com endpoints CRUD protegidos por middleware de autenticação.

Crie `.env` com:
```
PORT=3000
JWT_SECRET=your-secret-key
DATABASE_URL=postgresql://user:pass@localhost:5432/mydb
```

Suba o banco de dados: `docker compose up -d`

Teste a API:
```bash
curl -X POST http://localhost:3000/auth/register -H "Content-Type: application/json" -d '{"email":"test@test.com","password":"123456"}'
```

Adicione as convenções do projeto ao CLAUDE.md.
```

**Convertido (Deep Agents):**
```markdown
---
name: express-api-generator
description: "Cria uma API REST Express.js pronta para produção com autenticação JWT, PostgreSQL e Docker"
metadata:
  converted-from: claude-code
  converter-version: "2.0"
  deep-agents-compat: ">=0.0.34"
---

# Skill: Express API Generator

> Cria uma API REST Express.js pronta para produção com autenticação.

## Contexto de Execução

Esta skill roda dentro do **Deep Agents CLI** (v0.0.34+). Tools disponíveis:

| Tool | Uso nesta skill |
|------|----------------|
| `write_file` | Criar arquivos do projeto (index.js, rotas, .env) |
| `execute` | Rodar npm, docker, curl e comandos de validação |
| `edit_file` | Modificar arquivos se ajustes forem necessários |
| `write_todos` | Planejar os passos de execução |

**Regras críticas de execução:**
1. Sempre comece criando o plano via `write_todos`.
2. Crie arquivos um a um via `write_file` — nunca tente gerar tudo de uma vez.
3. Teste cada módulo via `execute` imediatamente após criá-lo.

## Plano de Execução (use com `write_todos`)

- [ ] 1. Verificar pré-requisitos (Node.js 18+, npm, Docker)
- [ ] 2. Verificar variáveis de ambiente
- [ ] 3. Inicializar projeto e instalar dependências
- [ ] 4. Criar src/index.js
- [ ] 5. Criar src/routes/auth.js
- [ ] 6. Criar src/routes/users.js
- [ ] 7. Criar configuração .env
- [ ] 8. Subir banco de dados via Docker
- [ ] 9. Testar fluxo completo da API

## Verificação de Pré-requisitos

Use `execute` para verificar:
```bash
node --version   # Requer 18+
npm --version
docker --version
docker compose version
```

## Configuração de Ambiente

Verifique as variáveis de ambiente necessárias via `execute`:
```bash
for var in JWT_SECRET DATABASE_URL; do
  if [ -z "${!var}" ]; then
    echo "AVISO: $var não definida — usará defaults do .env"
  fi
done
```

## Implementação

Inicialize o projeto via `execute`:
```bash
npm init -y
```

Instale as dependências via `execute`:
```bash
npm install express jsonwebtoken bcrypt pg dotenv
```

Use `write_file` para criar `src/index.js`:
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

Teste via `execute`:
```bash
node -e "require('./src/index.js')" &
sleep 2 && kill %1 && echo "OK: index.js carrega sem erros"
```

Use `write_file` para criar `src/routes/auth.js` com rotas de login e registro JWT.

Teste via `execute`:
```bash
node -e "require('./src/routes/auth.js'); console.log('OK: rotas auth carregadas')"
```

Use `write_file` para criar `src/routes/users.js` com endpoints CRUD protegidos por middleware de autenticação.

Teste via `execute`:
```bash
node -e "require('./src/routes/users.js'); console.log('OK: rotas users carregadas')"
```

Use `write_file` para criar `.env`:
```
PORT=3000
JWT_SECRET=your-secret-key
DATABASE_URL=postgresql://user:pass@localhost:5432/mydb
```

**Nota de segurança:** Este `.env` contém secrets placeholder. Substitua com valores reais antes de produção. Adicione `.env` ao `.gitignore`.

Suba o banco de dados via `execute`:
```bash
docker compose up -d
```

Teste a API completa via `execute`:
```bash
curl -s -X POST http://localhost:3000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"123456"}'
```

Adicione as convenções do projeto ao `AGENTS.md` na raiz (equivalente ao CLAUDE.md do Claude Code).

## Guia de Uso com Deep Agents CLI

### Modo 1 — Construção (one-shot)
```bash
deepagents -y "Crie uma API Express com auth seguindo a skill express-api-generator"
```

### Modo 2 — Execução interativa
```bash
deepagents
> Construa uma API REST com autenticação JWT
```

### Modo 3 — Não-interativo (CI/CD)
```bash
deepagents -n -y -S "npm,node,docker" "Gere scaffold de API Express em ./api"
```

## Troubleshooting

### Node.js não encontrado
```bash
node --version
# Instalar via nvm:
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
```

### Docker não está rodando
```bash
docker info
# Se não estiver rodando:
sudo systemctl start docker
```

### Porta 3000 já em uso
```bash
lsof -i :3000
# Mate o processo ou altere PORT no .env
```

### Context window estourando
```
Use /compact para forçar compactação antes de continuar.
Considere dividir a geração de rotas em sub-agents via `task`.
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

Converter caminho de configuração e adicionar nota de aprovação:

```markdown
# Claude Code: .claude/mcp.json
# Deep Agents: .deepagents/mcp.json (mesmo formato JSON)
# Também procurado: .mcp.json na raiz do projeto

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

Nota: Servidores MCP de projeto (stdio) requerem aprovação do usuário no primeiro uso.
Use `--trust-project-mcp` para pular aprovação. Servidores remotos (SSE/HTTP) são sempre permitidos.
```

### Skills com chamadas a tools MCP customizadas

Se a skill referencia tools MCP específicas (ex: `mcp__slack__send_message`):

```markdown
As tools MCP são carregadas automaticamente no Deep Agents CLI a partir da config MCP.
Os nomes e convenção de chamada são idênticos. Certifique-se de que o servidor MCP
está configurado no `.deepagents/mcp.json` antes de chamar qualquer tool MCP.
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

### Skills com hooks ou automação

```markdown
Hooks do Claude Code (settings.json) não têm equivalente direto no Deep Agents CLI.
Converta hooks para shell scripts e documente-os no AGENTS.md como passos manuais ou
acionados por CI.
```

### Skills com lógica condicional / específica por plataforma

```markdown
Envolva seções específicas de plataforma em condicionais shell via `execute`.
Use `uname -s` para detecção de SO, `command -v` para verificar disponibilidade de ferramentas.
Não deixe texto solto "se macOS / se Linux" — torne-o executável.
```

---

## Conversão Reversa: Deep Agents → Claude Code

Ao converter **do Deep Agents para Claude Code**, aplique as transformações inversas:

### Procedimento reverso

1. **Remover frontmatter YAML** — Skills do Claude Code não usam isso.
2. **Remover T1 (Tabela de Contexto de Execução)** — Claude Code não precisa de listagem explícita de tools.
3. **Remover T2 (Plano de Execução)** — Claude Code usa raciocínio implícito do LLM.
4. **Simplificar T3 (Pré-requisitos)** — Manter as verificações mas remover wrapper `execute`:
   ```markdown
   # Antes: Use `execute` para verificar: node --version
   # Depois: Verifique se Node.js 18+ está instalado: node --version
   ```
5. **Des-explicitar operações de arquivo:**
   | Deep Agents | Claude Code |
   |-------------|-------------|
   | `Use write_file para criar X:` | `Crie o arquivo X:` |
   | `Use edit_file para modificar X:` | `Edite X:` |
   | `Use read_file para ler X` | `Leia X` |
   | `Use execute para rodar:` | (apenas o bloco ```bash) |
   | `Use task para delegar:` | `Use a ferramenta Agent para lançar um sub-agent:` |
6. **Remover T5 (testes inline)** — Claude Code testa implicitamente quando necessário.
7. **Converter referências de volta:**
   | Deep Agents | Claude Code |
   |-------------|-------------|
   | `AGENTS.md` | `CLAUDE.md` |
   | `.deepagents/` | `.claude/` |
   | `Deep Agents CLI` | `Claude Code` |
   | tool `http_request` | `curl` via bash |
   | tool `web_search` | Não disponível (remover ou anotar) |
8. **Simplificar T7 (Uso)** — Substituir por invocação simples do Claude Code:
   ```markdown
   ## Uso
   Abra o Claude Code no diretório do projeto e diga: "{comando natural}"
   ```
9. **Simplificar T8 (Troubleshooting)** — Manter apenas entradas realmente úteis, remover boilerplate.

### Validação reversa

Escaneie a skill convertida em busca de termos específicos do Deep Agents que não devem permanecer:
- `write_file`, `edit_file`, `read_file`, `execute`, `task`, `write_todos`
- `.deepagents/`, `AGENTS.md`
- `http_request`, `web_search`

---

## Estrutura Final da Skill Convertida

Toda skill convertida deve seguir esta estrutura (em ordem):

```
1. --- Frontmatter YAML ---                              ← Passo 4
2. # Título da Skill
3. > Descrição (blockquote)
4. ## Contexto de Execução (tabela de tools)             ← T1
5. ## Plano de Execução (checklist write_todos)          ← T2
6. ## Verificação de Pré-requisitos                      ← T3
7. ## Configuração de Ambiente (se aplicável)            ← 2j
8. ## Arquitetura (preservar da original)
9. ## Estrutura de Arquivos (com instruções write_file)  ← T4
10. ## Dependências (com instruções execute)
11. ## [Seções técnicas da original, convertidas]         ← T4/T5/T6
12. ## Guia de Uso com Deep Agents CLI                    ← T7
13. ## Troubleshooting                                    ← T8
```

As seções 7–11 variam conforme a skill. O importante é que TODAS as seções técnicas passem pela conversão de padrões (Passo 2) e pelas 8 transformações (Passo 3).

---

## Regras de Ouro

1. **Nunca perder conteúdo.** A skill convertida tem tamanho ≥ original.
2. **Nunca assumir implícitos.** O Deep Agents CLI precisa de instruções explícitas de qual tool usar.
3. **Sempre começar com `write_todos`.** O plano é o alicerce de toda execução no Deep Agents.
4. **Testar depois de cada `write_file`.** O padrão cria → testa → próximo é inquebrável.
5. **Usar `task` para paralelismo.** Se a skill processa N itens, N sub-agents.
6. **Preservar todo conhecimento de domínio.** Tabelas, regex, fórmulas, templates — tudo.
7. **Capturar comandos inline.** Comandos entre crases dentro de frases também precisam de conversão.
8. **Tratar env vars explicitamente.** Nunca assumir que variáveis estão disponíveis — verificar ou documentar.
9. **Tornar condicionais executáveis.** Verificações de plataforma viram blocos shell `case`/`if`, não prosa.
10. **Validar com o checklist.** Rodar a validação baseada em grep antes de salvar.
