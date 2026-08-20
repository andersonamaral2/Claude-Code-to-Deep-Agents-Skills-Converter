# CLAUDE.md

Landing da **promoção de 2 anos da Scoras Academy** (Formação Continuada por 3.999 à vista
até 19/09/2026, garantia de renovação gratuita do 2º ano). Deployed em
**`aniversario.scorasacademy.com.br`** (CF Pages project: `aniversario-scorasacademy`).

Mesma stack das landings irmãs (`de_gargalos_a_agentes`, `aniversario_patricia`): HTML
estático + Cloudflare Pages Functions. `scoras-promocao-2anos.html` é o original entregue;
`site/index.html` é a versão em produção (OG URLs, seção do e-book, forms ligados).

## Architecture

- `site/` — estático servido como Pages
  - `site/index.html` — landing da promoção
  - `site/downloads/ebook-ia-scoras.pdf` — lead magnet em **URL fixa** (nunca anexo: anexo é
    gatilho de spam; link permite trocar o arquivo sem reenviar e-mail). Conteúdo atual: e-book
    **"Engenharia de Harness: o que é, o que não é, e por que a confusão custa caro"** (13 págs).
    Trocar o arquivo mantendo o nome atualiza o e-book pra quem se cadastrar depois, sem mexer em
    e-mail já enviado — **mas a cópia do e-mail em `inscrever.js` cita o título**, então troca de
    e-book exige atualizar `ebookEmailHtml` lá também.
  - `site/og-image.png` — 1200×630 gerada por script (PIL)
  - `site/_headers` — headers de segurança + cache curto em `/downloads/*`
- `functions/api/inscrever.js` — Pages Function que recebe os forms
- `functions/api/descadastrar.js` — opt-out funcional (LGPD): GET mostra página, POST atende
  one-click RFC 8058

**Dois forms alimentam o mesmo `/api/inscrever`:**

1. **E-book surpresa** (`#ebook`, `lead_magnet=ebook_surpresa_ia`) — seção própria pra
   capturar quem visita e não vai assinar agora. Nome + e-mail + WhatsApp.
2. **Gate de checkout** (modal `#leadForm`, `lead_magnet=gate_checkout_2anos`) — existia no
   HTML original com webhook vazio (lead ia pro limbo); agora posta no mesmo endpoint antes
   de abrir o checkout Hotmart.

Captura em **Promise.allSettled** com 4 paths: audience Resend + e-mail de entrega do e-book
+ backup KV + notificação pro time. Se um falhar, os outros continuam.

O e-mail de entrega menciona a promoção só até 19/09/2026 23h59 BRT (`PROMO.expiraEm` em
`inscrever.js`) — e-mail perene não promete condição vencida. **Não apague essa trava.**

## Deploy

```bash
export CLOUDFLARE_API_TOKEN=$(grep '^CLOUDFLARE_API_TOKEN=' /home/anderson/live_quantica/.env | cut -d= -f2)
export CLOUDFLARE_ACCOUNT_ID=028f732e5712d10f3c776f834ddf8f94

# Rodar da RAIZ do repo (o wrangler resolve functions/ a partir do cwd)
npx --yes wrangler@latest pages deploy site \
  --project-name=aniversario-scorasacademy \
  --branch=main --commit-dirty=true
```

## Infra IDs (one-time, persist)

- **CF Account ID:** `028f732e5712d10f3c776f834ddf8f94`
- **CF Zone (scorasacademy.com.br):** `a8b5a834e66582d6b1aafa894013028c`
- **CF Pages project:** `aniversario-scorasacademy` (`aniversario-scorasacademy.pages.dev`)
- **CF KV namespace `INSCRITOS_ANIVERSARIO_2ANOS`:** `514caf69e06d4b8a88fec4e189b81d9c`
- **Resend audience:** `febf80e7-0a50-459e-a3ed-e41689dd9602` (`gargalos_prelancamento_2026`) —
  **compartilhada com as outras landings de propósito** (base única; o que separa as origens
  é o KV próprio + `lead_magnet`/`origem` do payload)
- **DNS:** CNAME `aniversario` → `aniversario-scorasacademy.pages.dev`, **proxied**

## Env vars (configuradas no Pages project, production e preview)

- `RESEND_API_KEY` — secret_text
- `AUDIENCE_ID` — `febf80e7-0a50-459e-a3ed-e41689dd9602`
- KV binding **`INSCRITOS`** → namespace `514caf69e06d4b8a88fec4e189b81d9c`
  (o código procura `env.INSCRITOS`; não invente outro nome)

## CRM / dashboard (campanha `aniversario_2anos_2026`)

Registrada em `crm.scorasacademy.com.br/campanhas` como **Aniversário 2 anos · Landing
Formação Continuada** (`landing_form`, 19/08–19/09/2026, `curso_id` nulo — a FC não existe
em `campaign_courses`). Cadeia:

1. Linha na tabela `campanhas` do DuckDB do dashboard — criada por
   `scripts/seed_campanha_2anos.py` (idempotente; existe só no servidor, em
   `/home/ubuntu/app/scripts/`). DuckDB é **single-writer**: pra rodar seed de novo,
   `systemctl stop scoras-dashboard` → rodar → `start` (~2s de downtime).
   `metadata.kv_namespace_id` é o que diz ao sync de onde puxar.
2. Cron no servidor (user ubuntu), offset próprio pra não colidir com as outras campanhas
   na conexão DuckDB singleton:
   ```
   9,24,39,54 * * * * cd /home/ubuntu/app && .venv/bin/python3 \
     scripts/sync_gargalos_inscritos.py aniversario_2anos_2026 \
     >> /home/ubuntu/app/logs/sync_aniversario_2anos.log 2>&1
   ```
   (gargalos usa 7/22/37/52, aniversario_patricia 12/27/42/57, data_mundo 2/17/32/47)
3. `POST /api/admin/crm-sync` leva a campanha do DuckDB pro Postgres do CRM
   (campaigns + lists `campanha:aniversario_2anos_2026`, ambos automáticos). O botão
   "Atualizar inscritos" no detalhe da campanha no CRM dispara os dois passos na hora.

## Sender / reply-to

- From: `Cora da Scoras Academy <cora@scorasacademy.com.br>` (domínio raiz, verified).
  **Nunca** `news.scorasacademy.com.br` — subdomínio queimado.
- Reply-to: `suporte@scorasacademy.com.br` — e-mail de entrega é no-reply.
- Notificação interna de novo lead vai pra `anderson@scoras.com.br` + `patricia@scoras.com.br`.

## Descadastro

Token = `HMAC-SHA256(email, RESEND_API_KEY)` truncado em 32 hex — a função `unsubToken` está
**idêntica** em `inscrever.js` e `descadastrar.js` (mexer numa exige mexer na outra).
Rotacionar a RESEND_API_KEY invalida todos os links de descadastro já enviados.

## Ler quem se cadastrou

```bash
CF_TOKEN=$(grep '^CLOUDFLARE_API_TOKEN=' /home/anderson/live_quantica/.env | cut -d= -f2)
curl -s "https://api.cloudflare.com/client/v4/accounts/028f732e5712d10f3c776f834ddf8f94/storage/kv/namespaces/514caf69e06d4b8a88fec4e189b81d9c/keys?prefix=inscrito:" \
  -H "Authorization: Bearer $CF_TOKEN" | jq
```
