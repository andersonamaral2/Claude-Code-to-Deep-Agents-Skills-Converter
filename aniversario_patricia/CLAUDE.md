# CLAUDE.md

Landing da **campanha de aniversário da Patricia Costa (29/07/2026)**.
Deployed em **`aniversario-patricia.scorasacademy.com.br`** (CF Pages project: `aniversario-patricia`).

Irmã da landing `de_gargalos_a_agentes`, mesma stack e mesma identidade visual (preto/roxo/cyan,
Familjen Grotesk + Instrument Serif + JetBrains Mono). A diferença é a promessa: aqui o inscrito
recebe **dois presentes na hora** (manual + skill) e fica esperando o **terceiro no dia 29** (cupom).

## Architecture

- `site/` — estático servido como Pages
  - `site/index.html` — landing (form + countdown de 3 estados + FAQ + JSON-LD)
  - `site/downloads/` — lead magnet em **URL fixa** (nunca anexo: zip anexado é gatilho de spam,
    e link permite trocar o arquivo sem reenviar e-mail)
  - `site/assets/` — foto da Patricia (192px) e og-image 1200x630
  - `site/_headers` — headers de segurança + cache curto em `/downloads/*`
- `functions/api/inscrever.js` — Pages Function que recebe o form
- `functions/api/descadastrar.js` — opt-out funcional (LGPD): GET mostra página, POST atende
  one-click RFC 8058
- `scripts/gen_assets.py` — regenera foto redimensionada + og-image (Playwright com as fontes reais)
- `aniversario.html` — HTML original entregue pelo Anderson, mantido como referência
  (o `site/index.html` é ele com a foto extraída do base64 + SEO + submit síncrono)

Captura em **Promise.allSettled** com 4 paths: audience Resend + e-mail de entrega + backup KV +
notificação pro time. Se um falhar, os outros continuam.

## Deploy

```bash
export CLOUDFLARE_API_TOKEN=$(grep '^CLOUDFLARE_API_TOKEN=' /home/anderson/live_quantica/.env | cut -d= -f2)
export CLOUDFLARE_ACCOUNT_ID=$(grep '^CLOUDFLARE_ACCOUNT_ID=' /home/anderson/live_quantica/.env | cut -d= -f2)

npx --yes wrangler@latest pages deploy site \
  --project-name=aniversario-patricia \
  --branch=main \
  --commit-dirty=true
```

## Infra IDs (one-time, persist)

- **CF Account ID:** `028f732e5712d10f3c776f834ddf8f94`
- **CF Zone (scorasacademy.com.br):** `a8b5a834e66582d6b1aafa894013028c`
- **CF Pages project:** `aniversario-patricia` (`aniversario-patricia.pages.dev`)
- **CF KV namespace `INSCRITOS_ANIVERSARIO`:** `03302c05339d4defa0a31d3ac1c8ba88`
- **Resend audience:** `febf80e7-0a50-459e-a3ed-e41689dd9602` (`gargalos_prelancamento_2026`)
- **DNS:** CNAME `aniversario-patricia` → `aniversario-patricia.pages.dev`, **proxied**

⚠️ **A audience é compartilhada com a landing do gargalos, de propósito.** O FAQ da página promete
que "o cupom vai por e-mail para toda a lista, incluindo quem se cadastrou antes da
campanha" — com duas audiences separadas esse envio viraria dois disparos e alguém ficaria de fora.
O que separa as duas origens é o KV (namespace próprio) e o campo `origem` do payload.

## Env vars (configuradas no Pages project, production **e** preview)

- `RESEND_API_KEY` — secret_text
- `AUDIENCE_ID` — `febf80e7-0a50-459e-a3ed-e41689dd9602`
- KV binding **`INSCRITOS`** → namespace `03302c05339d4defa0a31d3ac1c8ba88`
  (o código procura `env.INSCRITOS`; o suffix `_ANIVERSARIO` está só no título do namespace)

## Sender / reply-to

- From: `Patricia Costa · Scoras Academy <cora@scorasacademy.com.br>` (domínio raiz, verified,
  tracking ON). **Nunca** `news.scorasacademy.com.br` — subdomínio queimado.
- Reply-to: `suporte@scorasacademy.com.br` — e-mail de entrega é no-reply.
- Notificação interna vai pra `anderson@scoras.com.br` + `patricia@scoras.com.br`, com reply-to
  no e-mail de quem se cadastrou.

## Os três presentes

| # | O quê | Quando | Onde |
|---|---|---|---|
| 01 | Manual `Automação com Critério` (PDF, 18 pág.) | na hora | `/downloads/automacao-com-criterio.pdf` |
| 02 | Skill do método pro Claude (.zip) | na hora, mesmo e-mail | `/downloads/automacao-com-criterio.zip` |
| 03 | Cupom `ANIVERSARIOPATI`, 50% no curso | na hora, mesmo e-mail | constante `CUPOM` em `inscrever.js` |

UTM de entrega nos dois botões: `utm_source=email&utm_medium=entrega&utm_campaign=aniversario_29_07`,
com `utm_content=manual_pdf` vs `skill_zip`.

⚠️ **UTM em link de arquivo estático não vira dado no GA4** (não roda JS). A métrica de clique real
vem do click tracking do Resend, que já está ON no domínio raiz.

### Presente 03 virou automático em 29/07

Até 28/07 o cupom era disparo manual no dia. Desde 29/07 ele sai **no mesmo e-mail** dos outros
dois, na hora do cadastro: `presentesEmailHtml` monta os três presentes em um corpo só, no
template claro (faixa `#4400A5` sobre card branco, Arial), que substituiu o template escuro
anterior. O que define o cupom é a constante `CUPOM` (código, percentual, de/por, link de
checkout com `offDiscount`, `expiraEm`).

⚠️ **`cupomAtivo()` corta o bloco 03 depois de 31/07 23h59 BRT** (mesma data do countdown da
landing). Passada a janela, o e-mail deixa de prometer desconto e o bloco vira convite ao curso,
com o assunto acompanhando. Sem essa trava, quem se cadastrasse em agosto receberia um código
que não passa no checkout. Mudar a data do cupom = mudar `CUPOM.expiraEm` **e** as duas datas do
countdown em `site/index.html`.

`ehDiaDoAniversario()` só troca a abertura do texto ("hoje é meu aniversário" vs. "a campanha
ainda está de pé"), porque a copy original do Anderson era escrita para o dia 29 e continuaria
no ar dias 30 e 31.

## Dashboard `/campanhas` (dashboard.scorasacademy.com.br)

A landing aparece em `https://dashboard.scorasacademy.com.br/campanhas` como
**`aniversario_patricia_2907`**, tipo `landing_form`, curso `gargalos-agentes`.

O painel **não lê a Cloudflare sozinho**. Ele lê a tabela `campanha_leads` do DuckDB do projeto
`hotmart` (EC2 `i-09a0d3e0b32bea755`, serviço `scoras-dashboard` na porta 8000). Quem popula é
`src/automations/sync_landing_inscritos.py`, que descobre de qual KV puxar lendo
`campanhas.metadata.kv_namespace_id`. Duas peças foram necessárias:

1. A linha em `campanhas` (criada por `scripts/seed_campanha_dashboard.py`, idempotente).
2. Um cron chamando `POST /api/admin/sync-landing/aniversario_patricia_2907`:
   ```
   12,27,42,57 * * * * cd /home/ubuntu/app && .venv/bin/python3 \
     scripts/sync_gargalos_inscritos.py aniversario_patricia_2907 \
     >> /home/ubuntu/app/logs/sync_aniversario_patricia.log 2>&1
   ```
   O offset de 5 min em relação ao cron do gargalos (`7,22,37,52`) é de propósito: as duas
   campanhas escrevem na **mesma conexão DuckDB singleton**, e colisão de minuto já causou
   `Duplicate key violates primary key constraint` no passado.

`scripts/sync_gargalos_inscritos.py` (repo `hotmart`) foi generalizado para aceitar o
`campanha_id` como `sys.argv[1]`, com default no id do gargalos, então o cron antigo segue
funcionando sem argumento. ⚠️ **`/home/ubuntu/app` não é checkout git** — a alteração foi
aplicada no servidor e no repo local `/home/anderson/hotmart`, mas ainda **não foi commitada**;
sem commit, o próximo deploy sobrescreve e o cron novo quebra.

### Gotchas de escrita no DuckDB do dashboard

- É **single-writer** e o serviço segura o lock. Para escrever de fora, tem que parar o serviço
  (`sudo systemctl stop scoras-dashboard`), rodar, e religar. O seed levou 2 s de downtime.
- Snapshot por `cp` do `.duckdb` **não enxerga escrita recente**: ela fica no `.wal` até o
  checkpoint. Se uma consulta em cópia vier vazia, chame
  `POST /api/admin/checkpoint` (header `X-Hottok`) antes de copiar, senão você conclui que o
  sync falhou quando ele funcionou.

## Rodapé de redes (constante `REDES` em `inscrever.js`)

Instagram da Patricia, **LinkedIn da Patricia**, canal da Scoras no WhatsApp, YouTube da Scoras.
O LinkedIn é o que esta campanha adicionou em relação ao e-mail do gargalos.

## Descadastro

Token = `HMAC-SHA256(email, RESEND_API_KEY)` truncado em 32 hex — não exige env var nova e impede
descadastrar terceiros. Gerado em `inscrever.js`, conferido em `descadastrar.js`;
**as duas cópias da função `unsubToken` têm que ficar idênticas.**
O opt-out grava trilha `optout:<ts>:<email>` no KV além de marcar `unsubscribed` no Resend.

## Ler quem se cadastrou

```bash
CF_TOKEN=$(grep '^CLOUDFLARE_API_TOKEN=' /home/anderson/live_quantica/.env | cut -d= -f2)
curl -s "https://api.cloudflare.com/client/v4/accounts/028f732e5712d10f3c776f834ddf8f94/storage/kv/namespaces/03302c05339d4defa0a31d3ac1c8ba88/keys?prefix=inscrito:" \
  -H "Authorization: Bearer $CF_TOKEN" | jq

RESEND_KEY=$(grep '^RESEND_API_KEY=' /home/anderson/live_quantica/.env | cut -d= -f2)
curl -s "https://api.resend.com/audiences/febf80e7-0a50-459e-a3ed-e41689dd9602/contacts" \
  -H "Authorization: Bearer $RESEND_KEY" | jq
```

## Telemetria

Mesmos IDs da landing principal, carregados no `<head>` gated por `window.*` (vazio = não dispara):

| Pixel | Variável | Valor |
|---|---|---|
| GA4 (Scoras Academy) | `GA4_MEASUREMENT_ID` | `G-L3R9VZWPMB` |
| Meta Pixel Scoras | `META_PIXEL_ID` | `538270788815652` |
| Meta Pixel Patricia | `META_PIXEL_ID_PATRICIA` | `1540132670975675` |
| Microsoft Clarity | _hardcoded_ | `xig17oy2vz` |

Eventos: `ViewContent` (`campanha_aniversario_29_07`) no load; `generate_lead` (GA4) + `Lead` (Meta)
**só depois** que o backend confirma 200.

### Atribuição de origem

A landing captura as 5 UTMs (`source`, `medium`, `campaign`, `term`, `content`) e grava em
`sessionStorage` sob a chave `utm_campanha` **já na chegada**, antes de qualquer navegação interna.
No submit a URL atual tem prioridade; na falta dela vale o que ficou guardado, então quem chega por
um anúncio, sai e volta pela mesma aba continua atribuído ao canal que trouxe. Aba nova não herda
nada (sessionStorage é por aba), o que mantém o tráfego direto honesto. Tudo que toca o
sessionStorage é best-effort: aba anônima e cookies bloqueados fazem `setItem` estourar.

O `generate_lead` do GA4 leva junto `canal` = `utm_source/utm_medium` (`instagram/bio`,
`email/entrega`, ou só `direto` quando não veio UTM). ⚠️ **`canal` só aparece nos relatórios do GA4
depois de registrado como dimensão personalizada** no admin; o evento já sobe com o campo.

Nada disso exigiu mudança de backend: `inscrever.js` já persistia as 5 UTMs + referrer + país/cidade
no KV, e o `sync_landing_inscritos.py` já mapeia todas pra `campanha_leads` — a origem aparece
sozinha no `/campanhas` no cron seguinte.

## Gotchas

- O submit **espera a resposta** do `/api/inscrever` antes de mostrar "você está na lista". O
  fire-and-forget do template original prometia o e-mail pra quem nunca entrou na base.
- A foto da Patricia vinha inline em base64 (581 KB dentro do HTML, bloqueando o first paint).
  Foi extraída pra `site/assets/patricia.png` em 192px: HTML caiu de 602 KB pra 21 KB.
- ⚠️ **`aniversario.html` na raiz é o original de referência, não a produção.** "Layout novo" que
  chegar montado em cima dele regride cinco coisas de uma vez: volta o base64 de 581 KB e o submit
  fire-and-forget, e somem o SEO (2 JSON-LD, 10 `og:`, canonical), a UI de erro/"Enviando…" e as
  UTMs `term`/`content`. O caminho certo é diffar contra ele (`diff <(fold -w 200 aniversario.html)
  <(fold -w 200 novo.html)`, que isola o delta apesar do blob base64) e **portar só o delta** pro
  `site/index.html`. Foi assim que a captura de UTM da Patricia entrou em 26/07.
- URLs absolutas no `<head>`, no JSON-LD, no `sitemap.xml` e nas duas Functions apontam pra
  `https://aniversario-patricia.scorasacademy.com.br`. Repivotar de domínio = mass replace.
- O countdown tem 3 estados e vira sozinho: antes de 29/07 conta pro reveal, entre 29 e 31 conta
  pra expiração, depois de 31/07 23h59 aplica `body.campanha-encerrada` e troca o texto.
- Deployment com hash (`<hash>.aniversario-patricia.pages.dev`) **não tem certificado TLS válido** —
  testar sempre em `aniversario-patricia.pages.dev` ou no domínio final.
