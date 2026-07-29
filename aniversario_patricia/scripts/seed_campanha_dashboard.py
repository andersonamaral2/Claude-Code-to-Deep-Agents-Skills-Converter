#!/usr/bin/env python3
"""Cria/atualiza a campanha da landing de aniversário no dashboard `/campanhas`.

Idempotente: roda quantas vezes precisar, não dropa nada.

O dashboard não lê a Cloudflare sozinho. Ele lê `campanha_leads`, populada por
`src/automations/sync_landing_inscritos.py`, que descobre de qual KV puxar lendo
`campanhas.metadata.kv_namespace_id`. Sem esta linha, a landing é invisível pro painel.

⚠️ O DuckDB é single-writer e o serviço `scoras-dashboard` segura o lock de escrita.
Este script precisa rodar com o serviço PARADO:

    sudo systemctl stop scoras-dashboard
    /home/ubuntu/app/.venv/bin/python3 seed_campanha_dashboard.py
    sudo systemctl start scoras-dashboard
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import duckdb

DB_PATH = Path("/home/ubuntu/app/data/hotmart_analytics.duckdb")

CAMPANHA_ID = "aniversario_patricia_2907"
NOME = "Aniversário Patricia 29/07 · Landing de presentes"
DESCRICAO = (
    "Form da landing https://aniversario-patricia.scorasacademy.com.br. "
    "Captura nome+email+WhatsApp+UTM+IP+país. Entrega na hora o manual "
    "'Automação com Critério' (PDF) e a skill do Claude (.zip); o cupom do curso "
    "vai por e-mail em 29/07 pra lista inteira. Sincroniza Cloudflare KV → "
    "campanha_leads pelo botão 'Atualizar inscritos' e pelo cron de 15 em 15 min."
)
CURSO_ID = "gargalos-agentes"
DATA_INICIO = date(2026, 7, 26)
DATA_FIM = date(2026, 7, 31)   # cupom expira 31/07 23h59 BRT
METADATA = {
    "kv_namespace_id": "03302c05339d4defa0a31d3ac1c8ba88",   # INSCRITOS_ANIVERSARIO
    "kv_prefix": "inscrito:",
    "resend_audience_id": "febf80e7-0a50-459e-a3ed-e41689dd9602",
    "cf_pages_project": "aniversario-patricia",
    "landing_url": "https://aniversario-patricia.scorasacademy.com.br",
}
OBSERVACOES = (
    "Audience Resend compartilhada com gargalos_landing_precadastro de propósito: "
    "o cupom do dia 29 vai pra lista inteira, então duas audiences virariam dois "
    "disparos. O que separa as origens é o KV próprio."
)


def main() -> int:
    if not DB_PATH.exists():
        print(f"ERRO: {DB_PATH} não existe")
        return 1

    con = duckdb.connect(str(DB_PATH))

    curso_ok = con.execute(
        "SELECT COUNT(*) FROM cursos WHERE curso_id = ?", [CURSO_ID]
    ).fetchone()[0]
    if not curso_ok:
        print(f"ERRO: curso '{CURSO_ID}' não existe em `cursos` — abortando")
        return 1

    existe = con.execute(
        "SELECT 1 FROM campanhas WHERE campanha_id = ?", [CAMPANHA_ID]
    ).fetchone()

    meta_json = json.dumps(METADATA, ensure_ascii=False)

    if existe:
        con.execute(
            """UPDATE campanhas SET
                   nome = ?, tipo = 'landing_form', descricao = ?, curso_id = ?,
                   data_inicio = ?, data_fim = ?, duracao_dias = ?, status = 'rodando',
                   utm_source = 'direto', utm_medium = 'landing',
                   utm_campaign = 'aniversario_29_07',
                   metadata = ?, observacoes = ?, updated_at = current_timestamp
               WHERE campanha_id = ?""",
            [NOME, DESCRICAO, CURSO_ID, DATA_INICIO, DATA_FIM,
             (DATA_FIM - DATA_INICIO).days, meta_json, OBSERVACOES, CAMPANHA_ID],
        )
        print(f"  {CAMPANHA_ID}: atualizado")
    else:
        con.execute(
            """INSERT INTO campanhas (
                   campanha_id, nome, tipo, descricao, evento_id, curso_id,
                   data_inicio, data_fim, duracao_dias, status,
                   budget_planejado_brl, gasto_real_brl,
                   impressoes, alcance, cliques, leads_gerados, conversoes,
                   receita_atribuida_brl,
                   utm_source, utm_medium, utm_campaign, utm_content,
                   metadata, observacoes, updated_at
               ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?, current_timestamp)""",
            [
                CAMPANHA_ID, NOME, "landing_form", DESCRICAO, None, CURSO_ID,
                DATA_INICIO, DATA_FIM, (DATA_FIM - DATA_INICIO).days, "rodando",
                0.0, 0.0,
                0, 0, 0, 0, 0,
                0.0,
                "direto", "landing", "aniversario_29_07", None,
                meta_json, OBSERVACOES,
            ],
        )
        print(f"  {CAMPANHA_ID}: criado")

    con.execute("CHECKPOINT")
    row = con.execute(
        "SELECT campanha_id, nome, tipo, status, curso_id, data_inicio, data_fim, "
        "leads_gerados, metadata FROM campanhas WHERE campanha_id = ?", [CAMPANHA_ID]
    ).fetchone()
    con.close()

    print("\n  confirmado no banco:")
    for k, v in zip(
        ["campanha_id", "nome", "tipo", "status", "curso_id",
         "data_inicio", "data_fim", "leads_gerados"], row[:8]
    ):
        print(f"    {k:14} = {v}")
    print(f"    metadata       = {row[8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
