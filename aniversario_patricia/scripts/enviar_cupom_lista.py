#!/usr/bin/env python3
"""Dispara o e-mail avulso do cupom (emails/cupom-lista.html) para a lista da campanha.

Este e-mail é só o presente 03: quem está na audience já recebeu o manual e a skill no
cadastro, então repetir os anexos aqui só encompridaria a mensagem.

    python3 scripts/enviar_cupom_lista.py --teste             # dry-run nos 2 e-mails internos
    python3 scripts/enviar_cupom_lista.py --teste --enviar    # envia de verdade
    python3 scripts/enviar_cupom_lista.py --landing           # dry-run: só quem veio desta landing (KV)
    python3 scripts/enviar_cupom_lista.py --landing --enviar
    python3 scripts/enviar_cupom_lista.py --lista             # dry-run: audience Resend inteira
    python3 scripts/enviar_cupom_lista.py --lista --enviar    # dispara pra audience inteira

Sem --enviar nada sai: o default é dry-run de propósito, porque a audience é compartilhada
com a landing do gargalos e um disparo errado atinge a base toda.
"""

import argparse
import hashlib
import hmac
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ENV_FILE = Path("/home/anderson/live_quantica/.env")
EMAILS = Path(__file__).resolve().parent.parent / "emails"
# Cada segmento recebe o e-mail que faz sentido pra ele: quem veio desta landing já tem
# o manual e a skill, então recebe só o cupom; quem veio do gargalos nunca recebeu nada,
# então recebe os três presentes.
TEMPLATES = {
    "landing":   (EMAILS / "cupom-lista.html",    "Hoje é meu aniversário. Seu presente está aqui."),
    "restantes": (EMAILS / "tres-presentes.html", "Seus 3 presentes: o manual, a skill e 50% no curso"),
    "teste":     (EMAILS / "cupom-lista.html",    "Hoje é meu aniversário. Seu presente está aqui."),
}

AUDIENCE_ID = "febf80e7-0a50-459e-a3ed-e41689dd9602"
CF_ACCOUNT = "028f732e5712d10f3c776f834ddf8f94"
KV_NAMESPACE = "03302c05339d4defa0a31d3ac1c8ba88"
SITE = "https://aniversario-patricia.scorasacademy.com.br"
FROM = "Patricia Costa · Scoras Academy <cora@scorasacademy.com.br>"
REPLY_TO = "suporte@scorasacademy.com.br"

# Os dois endereços internos de teste. Nada vai pra base antes de passar por aqui.
TESTE = [("Anderson", "luis.anderson.sp@gmail.com"), ("Patricia", "patriciafc1988@gmail.com")]

# Endereços do time e de teste: ficam fora de qualquer disparo à base.
INTERNOS = {
    "luis.anderson.sp@gmail.com", "patriciafc1988@gmail.com", "pafigueiredo.costa@gmail.com",
    "familia.f.amaral@gmail.com", "anderson@scoras.com.br", "admin@scoras.com.br",
    "anderson.amaral@nutrien.com", "anderson.luis.amaral@outlook.com",
    "patricia@scoras.com.br", "suporte@scorasacademy.com.br", "cora@scorasacademy.com.br",
    # Cadastrados na audience com nome de teste ("Teste Scoras", "Eu testandk").
    "pa_figueiredo@outlook.com", "antropofanzine@gmail.com",
}


def env(chave: str) -> str:
    for linha in ENV_FILE.read_text(encoding="utf-8").splitlines():
        if linha.startswith(f"{chave}="):
            return linha.split("=", 1)[1].strip()
    sys.exit(f"{chave} não encontrado em {ENV_FILE}")


def api(caminho: str, key: str, metodo: str = "GET", corpo: dict | None = None) -> dict:
    req = urllib.request.Request(
        f"https://api.resend.com{caminho}",
        method=metodo,
        data=json.dumps(corpo).encode() if corpo else None,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            # Sem User-Agent próprio, o Cloudflare na frente da Resend derruba o
            # "Python-urllib/3.x" com 403 error code 1010.
            "User-Agent": "scoras-academy-cupom/1.0",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read() or "{}")
    except urllib.error.HTTPError as e:
        return {"erro": e.code, "detalhe": e.read().decode(errors="replace")}


def unsub_url(email: str, secret: str) -> str:
    """Mesmo token de functions/api/inscrever.js: HMAC-SHA256(email, RESEND_API_KEY)[:32].

    As três cópias (inscrever.js, descadastrar.js e esta) têm que gerar o mesmo valor,
    senão o link do rodapé cai em "Link inválido ou expirado".
    """
    assinatura = hmac.new(secret.encode(), email.strip().lower().encode(), hashlib.sha256)
    token = assinatura.hexdigest()[:32]
    return f"{SITE}/api/descadastrar?e={urllib.parse.quote(email)}&t={token}"


def esc(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;").replace("'", "&#39;"))


def montar(nome: str, email: str, secret: str, template: str) -> str:
    primeiro = esc((nome or "").strip().split(" ")[0]) or "olá"
    return template.replace("{{NOME}}", primeiro).replace("{{UNSUB_URL}}", unsub_url(email, secret))


def contatos_kv() -> list[tuple[str, str]]:
    """Só quem se cadastrou NESTA landing, lendo o KV chave a chave.

    A audience do Resend é compartilhada com a landing do gargalos de propósito, então
    ela é maior que esta lista. Aqui a origem é a própria campanha de aniversário.
    """
    token = env("CLOUDFLARE_API_TOKEN")
    base = (f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT}"
            f"/storage/kv/namespaces/{KV_NAMESPACE}")

    def cf(url: str) -> dict:
        req = urllib.request.Request(url, headers={
            "Authorization": f"Bearer {token}", "User-Agent": "scoras-academy-cupom/1.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())

    chaves = [k["name"] for k in cf(f"{base}/keys?limit=1000&prefix=inscrito:")["result"]]
    # Mesmo e-mail pode ter se cadastrado duas vezes: fica o registro mais recente.
    por_email: dict[str, str] = {}
    for k in sorted(chaves):
        por_email[k.rsplit(":", 1)[1].lower()] = k

    saida = []
    for email, chave in por_email.items():
        dado = cf(f"{base}/values/{urllib.parse.quote(chave, safe='')}")
        saida.append(((dado.get("nome") or "").strip(), email))
        time.sleep(0.1)
    return sorted(saida, key=lambda x: x[1])


def destinatarios(modo: str, key: str) -> list[tuple[str, str]]:
    if modo == "teste":
        return TESTE
    if modo == "landing":
        return contatos_kv()

    contatos = api(f"/audiences/{AUDIENCE_ID}/contacts", key).get("data") or []
    fora = [c for c in contatos if c.get("unsubscribed")]
    if fora:
        print(f"  {len(fora)} contato(s) descadastrado(s) ficam de fora.")
    ativos = [(c.get("first_name") or "", c["email"].lower())
              for c in contatos if not c.get("unsubscribed")]
    if modo == "lista":
        return ativos

    # modo "restantes": a audience menos quem já veio desta landing (esse grupo recebe o
    # e-mail só do cupom) e menos os endereços internos, que não são inscritos de verdade.
    ja_tem = {e for _, e in contatos_kv()}
    pulados = [e for _, e in ativos if e in ja_tem or e in INTERNOS]
    if pulados:
        print(f"  {len(pulados)} fora: {len(ja_tem & {e for _, e in ativos})} desta landing "
              f"+ {len([e for e in pulados if e in INTERNOS])} internos/teste.")
    return [(n, e) for n, e in ativos if e not in ja_tem and e not in INTERNOS]


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    alvo = p.add_mutually_exclusive_group(required=True)
    alvo.add_argument("--teste", action="store_const", const="teste", dest="modo")
    alvo.add_argument("--landing", action="store_const", const="landing", dest="modo",
                      help="só quem se cadastrou nesta landing (KV)")
    alvo.add_argument("--restantes", action="store_const", const="restantes", dest="modo",
                      help="audience menos os desta landing: recebem os 3 presentes")
    alvo.add_argument("--lista", action="store_const", const="lista", dest="modo",
                      help="audience Resend inteira, compartilhada com a landing do gargalos")
    p.add_argument("--enviar", action="store_true", help="sem esta flag, roda em dry-run")
    args = p.parse_args()

    key = env("RESEND_API_KEY")
    caminho, assunto = TEMPLATES[args.modo]
    template = caminho.read_text(encoding="utf-8")
    # O comentário de instruções não precisa viajar dentro do e-mail.
    template = re.sub(r"^<!--.*?-->\s*", "", template, count=1, flags=re.S)

    alvos = destinatarios(args.modo, key)
    if not alvos:
        sys.exit("Nenhum destinatário.")

    print(f"\nModo: {args.modo} · {len(alvos)} destinatário(s) · "
          f"{'ENVIO REAL' if args.enviar else 'DRY-RUN (nada sai)'}")
    print(f"Template: {caminho.name}\nAssunto: {assunto}\n")

    for nome, email in alvos:
        if not args.enviar:
            print(f"  [dry-run] {nome or '(sem nome)'} <{email}>")
            continue

        unsub = unsub_url(email, key)
        r = api("/emails", key, "POST", {
            "from": FROM,
            "to": [email],
            "reply_to": REPLY_TO,
            "subject": assunto,
            "html": montar(nome, email, key, template),
            "headers": {
                "List-Unsubscribe": f"<{unsub}>",
                "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
            },
        })
        status = r.get("id") or f"FALHOU {r.get('erro')} {r.get('detalhe', '')[:160]}"
        print(f"  {email} → {status}")
        time.sleep(0.6)  # a Resend limita a 2 req/s no plano atual

    print()


if __name__ == "__main__":
    main()
