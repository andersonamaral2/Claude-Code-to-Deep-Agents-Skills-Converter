import os
import secrets
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from itsdangerous import URLSafeTimedSerializer

from .database import init_db, is_aluno, is_lead_verificado, register_lead, verify_lead
from .email_service import send_access_link_email, send_verification_email

load_dotenv()

# Root path for running behind nginx at /diagnostico-de-automacao/
ROOT = os.getenv("ROOT_PATH", "")

app = FastAPI(title="Diagnóstico de Automação - Scoras Academy", root_path=ROOT)

SECRET_KEY = os.getenv("APP_SECRET_KEY", "diagnostico-automacao-2026")
serializer = URLSafeTimedSerializer(SECRET_KEY)

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.on_event("startup")
def startup():
    init_db()


# --- Pages ---


@app.get("/", response_class=HTMLResponse)
async def index():
    return (FRONTEND_DIR / "index.html").read_text()


@app.get("/diagnostico", response_class=HTMLResponse)
async def diagnostico_page(token: str = ""):
    if not token:
        return RedirectResponse(f"{ROOT}/")
    try:
        email = serializer.loads(token, salt="access", max_age=86400 * 30)  # 30 days
    except Exception:
        return RedirectResponse(f"{ROOT}/?error=token_expirado")
    if not is_aluno(email) and not is_lead_verificado(email):
        return RedirectResponse(f"{ROOT}/?error=nao_autorizado")
    return (FRONTEND_DIR / "diagnostico.html").read_text()


# --- API ---


@app.post("/auth/check-email")
async def check_email(request: Request):
    body = await request.json()
    email = body.get("email", "").strip().lower()
    if not email:
        return JSONResponse({"error": "Email obrigatório"}, status_code=400)

    if is_aluno(email):
        access_token = serializer.dumps(email, salt="access")
        return JSONResponse({"status": "aluno", "redirect": f"{ROOT}/diagnostico?token={access_token}"})

    if is_lead_verificado(email):
        access_token = serializer.dumps(email, salt="access")
        return JSONResponse({"status": "cadastrado", "redirect": f"{ROOT}/diagnostico?token={access_token}"})

    return JSONResponse({"status": "nao_encontrado"})


@app.post("/auth/register")
async def register(request: Request):
    body = await request.json()
    nome = body.get("nome", "").strip()
    sobrenome = body.get("sobrenome", "").strip()
    email = body.get("email", "").strip().lower()
    celular = body.get("celular", "").strip()

    if not all([nome, sobrenome, email, celular]):
        return JSONResponse({"error": "Todos os campos são obrigatórios"}, status_code=400)

    if is_aluno(email):
        access_token = serializer.dumps(email, salt="access")
        return JSONResponse({"status": "aluno", "redirect": f"{ROOT}/diagnostico?token={access_token}"})

    token = secrets.token_urlsafe(32)
    register_lead(nome, sobrenome, email, celular, token)
    send_verification_email(email, nome, token)

    return JSONResponse({"status": "email_enviado"})


@app.get("/auth/verify/{token}", response_class=HTMLResponse)
async def verify_email(token: str):
    email = verify_lead(token)
    if not email:
        return RedirectResponse(f"{ROOT}/?error=token_invalido")

    access_token = serializer.dumps(email, salt="access")

    from .database import get_connection
    con = get_connection()
    result = con.execute("SELECT nome FROM leads WHERE LOWER(email) = LOWER(?)", [email]).fetchone()
    con.close()
    nome = result[0] if result else ""

    send_access_link_email(email, nome, access_token)

    return RedirectResponse(f"{ROOT}/diagnostico?token={access_token}")


@app.get("/api/health")
async def health():
    return {"status": "ok"}
