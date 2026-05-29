# FAQ — Conversor Universal de SKILL.md

Perguntas comuns sobre o que esta ferramenta faz, como ela converte e onde foi verificada.
Versão em inglês: [FAQ.md](FAQ.md).

---

## Eu preciso disso mesmo?

### O Cursor já lê `.claude/skills/` — por que converter?

Para **Claude Code → Cursor**, muitas vezes você não precisa: o Cursor lê `.claude/skills/`
(e `.codex/skills/`) como caminhos legados, então uma skill existente frequentemente já
funciona. Converter te dá duas coisas: um layout nativo `.cursor/skills/` limpo e acesso ao
frontmatter exclusivo do Cursor (`paths`, `disable-model-invocation`).

Os ganhos maiores estão nas direções que o Cursor **não** trata sozinho — Claude Code ↔
**Codex** (regras estritas de frontmatter), ↔ **Qwen Code** (`allowedTools` camelCase com
nomes de ferramentas snake_case) e ↔ **Deep Agents** (ferramentas tipadas e explícitas).

### Estão todos convergindo para `SKILL.md` — isso não vai ficar obsoleto?

O *arquivo* está convergindo; as *regras em volta dele* não — e esse é todo o problema. Mesmo
nome de arquivo, mas:

- O Codex proíbe `<`/`>` na description e aceita só cinco chaves de frontmatter.
- O Qwen quer `allowedTools` em camelCase com nomes de ferramentas snake_case.
- O Cursor exige que o `name` seja igual à pasta e não usa `allowed-tools`.
- O arquivo de memória (`CLAUDE.md` vs `AGENTS.md` vs `QWEN.md`) e a config MCP mudam por ferramenta.

Enquanto isso não convergir também, "só copiar o arquivo" quebra silenciosamente. Se convergir
de vez, ótimo — isto vira um validador enxuto, o que ainda é útil.

### Isso não é só find-and-replace? Por que uma skill / LLM?

Para os três alvos de linguagem natural, é proposital ser próximo disso — chamamos de **Tier
A**: remapear chaves de frontmatter, caminhos, arquivo de memória e config MCP. Essa parte
mecânica é real, e o `scripts/validate-conversion.sh` aplica as regras de cada CLI de forma
determinística em bash puro.

O modelo importa nas partes complicadas — derivar um `name`/`description` válido, reescrever uma
description que contém `<`/`>` para o Codex, preservar 100% da prosa de domínio — e no **Tier
B** (Claude Code ↔ Deep Agents), onde o "crie o arquivo" implícito precisa virar chamadas
explícitas `write_file` / `execute` / `task`. Essa parte não é regex.

---

## Fidelidade e corretude da conversão

### Vocês verificaram de verdade que as skills convertidas carregam em cada ferramenta?

Em parte, e o escopo importa. Verificamos os **formatos e validadores contra os binários
instalados**:

- **Codex 0.98.0** descobre skills em `$CODEX_HOME/skills` e traz o
  `skill-creator/scripts/quick_validate.py`, que restringe o frontmatter a
  `{name, description, license, allowed-tools, metadata}`, exige `name` em `^[a-z0-9-]+$`
  (≤64 chars) e **rejeita `<`/`>` na description** (≤1024 chars). O exemplo Codex passa nesse validador.
- **Qwen Code 0.17.0** — o exemplo é modelado nas próprias skills bundled do Qwen (`qc-helper`,
  `review`), então é válido por construção.

O que **não** fizemos foi rodar um agente ponta-a-ponta ao vivo em cada ferramenta (o token do
Codex estava expirado durante os testes; o Qwen exige sessão interativa). Ou seja:
validado-por-formato e checado-no-validador, não "vi o agente executar nas quatro". Evidência de
execução ao vivo será adicionada com o tempo.

### A conversão bidirecional / ida-e-volta perde informação?

O conhecimento de domínio (código, tabelas, passos, fórmulas) é preservado nas duas direções —
esse é o invariante rígido. O *envelope* nem sempre é sem perdas: ex., Deep Agents → Claude Code
remove as anotações explícitas de ferramentas (que são implícitas no Claude Code), e um alvo que
não tem certo campo não tem onde colocá-lo. Essas perdas são sinalizadas, nunca escondidas.

### Como ele trata sub-agentes, hooks e extended thinking?

Ele **sinaliza recursos não portáveis em vez de removê-los em silêncio**. O Cursor não tem
sub-agentes a nível de skill, então uma skill que distribui trabalho via `Task` recebe uma nota
de que esses passos rodam sequencialmente lá; Codex/Qwen mantêm `task`. Hooks do Claude Code
(`settings.json`) e blocos de extended thinking recebem o mesmo tratamento: uma nota visível em
vez de uma skill que parece completa mas não é.

### Como ele trata servidores MCP?

Ele remapeia o **caminho** e o **formato**, e preserva os nomes de chamada `mcp__server__tool`
inalterados:

- Claude Code `.claude/mcp.json` → Deep Agents `.deepagents/mcp.json` (mesmo schema JSON)
- → Codex `[mcp_servers.*]` em `config.toml`
- → Qwen Code `mcpServers` em `settings.json`
- → Cursor `.cursor/mcp.json`

Veja o **Exemplo 12** no `SKILL.pt.md` para um before/after completo, incluindo a nota sobre
`--trust-project-mcp` para a aprovação de primeiro uso de servidores stdio de projeto.

---

## Especificidades por ferramenta

### O que exatamente difere entre os alvos?

O mapeamento completo está na
[matriz de referência entre formatos](../SKILL.pt.md#matriz-de-referência-entre-formatos). Resumo:

| Conceito | Claude Code | Deep Agents | Codex | Qwen Code | Cursor |
|----------|-------------|-------------|-------|-----------|--------|
| Dir. skills (usuário) | `~/.claude/skills/` | `~/.deepagents/agent/skills/` | `~/.codex/skills/` | `~/.qwen/skills/` | `~/.cursor/skills/` |
| Arquivo de memória | `CLAUDE.md` | `AGENTS.md` | `AGENTS.md` | `QWEN.md` | `AGENTS.md` / Rules |
| Ferramentas | implícitas | tipadas (`write_file`…) | implícitas (`apply_patch`) | snake_case (`read_file`…) | implícitas |
| Regra do `name` | hyphen-case | hyphen-case | hyphen-case ≤64 | slug unicode | `name` == pasta |

### Por que o Deep Agents é o "ponto fora da curva"?

Os outros quatro rodam skills em linguagem natural (o agente infere quando ler/escrever/rodar).
O Deep Agents CLI usa ferramentas tipadas e explícitas — `write_file`, `edit_file`, `execute`,
`task`, `write_todos` — então "crie o arquivo X" precisa virar "use `write_file` para criar X",
com testes inline após cada passo. Essa tradução mais pesada é o caminho **Tier B** com que o
projeto começou.

---

## Projeto

### Licença? Uso comercial?

MIT — use, faça fork, adapte e distribua.

### Por que bilíngue (EN/PT)?

O mantenedor é brasileiro e quis cobrir também a comunidade dev lusófona. A documentação, a
skill e este FAQ saem nos dois idiomas, e uma checagem de paridade EN/PT roda no CI.

### Como vocês acompanham as mudanças de formato dessas CLIs?

Os fatos de formato são fixados em **versões verificadas específicas** (Codex 0.98.0, Qwen Code
0.17.0) e documentados assim, e o `scripts/validate-conversion.sh` codifica as regras reais de
cada CLI, de modo que qualquer divergência aparece como um check falhando. Quando uma CLI muda,
a matriz e o validador são atualizados contra o novo binário instalado — não contra docs
possivelmente desatualizadas.

### Como eu instalo e uso?

Uma linha (padrão é Deep Agents; use `--target` para outra CLI):

```bash
curl -fsSL https://raw.githubusercontent.com/andersonamaral2/Claude-Code-to-Deep-Agents-Skills-Converter/main/install.sh | bash
```

Instruções completas, todos os métodos de instalação e exemplos de uso estão no
[README](../README.pt.md).
