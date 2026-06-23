import os
import secrets
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from itsdangerous import URLSafeTimedSerializer

from .database import init_db, is_aluno, is_lead_verificado, register_lead, verify_lead, get_all_leads
from .email_service import send_welcome_email
from fastapi.middleware.cors import CORSMiddleware
import hashlib

load_dotenv()

COOKIE_NAME = "diag_access"
COOKIE_MAX_AGE = 86400 * 90  # 90 days
TARGET_PAGE = "/diagnostico-de-automacao/"
AUTH_PREFIX = os.getenv("AUTH_PREFIX", "/diagnostico-auth")

app = FastAPI(title="Auth Gate - Diagnóstico de Automação")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://dashboard.scorasacademy.com.br"],
    allow_methods=["GET"],
    allow_headers=["X-API-Key"],
)

SECRET_KEY = os.getenv("APP_SECRET_KEY", "diagnostico-automacao-2026")
serializer = URLSafeTimedSerializer(SECRET_KEY)

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.on_event("startup")
def startup():
    init_db()


def make_cookie(email: str) -> str:
    """Create a signed cookie value for the given email."""
    return serializer.dumps(email, salt="cookie")


def validate_cookie(cookie_value: str):
    """Validate cookie. Returns email or None."""
    try:
        return serializer.loads(cookie_value, salt="cookie", max_age=COOKIE_MAX_AGE)
    except Exception:
        return None


# --- nginx auth_request endpoint ---


@app.get("/validate")
async def validate(request: Request):
    """Called by nginx auth_request. Returns 200 if valid cookie, 401 otherwise."""
    cookie = request.cookies.get(COOKIE_NAME)
    if cookie and validate_cookie(cookie):
        return Response(status_code=200)
    return Response(status_code=401)


# --- Login page ---


@app.get("/", response_class=HTMLResponse)
async def login_page():
    return (FRONTEND_DIR / "index.html").read_text()


# --- API ---


@app.post("/check-email")
async def check_email(request: Request):
    body = await request.json()
    email = body.get("email", "").strip().lower()
    if not email:
        return JSONResponse({"error": "Email obrigatório"}, status_code=400)

    # Aluno or verified user → set cookie, redirect to WordPress page
    if is_aluno(email) or is_lead_verificado(email):
        cookie = make_cookie(email)
        response = JSONResponse({"status": "autorizado", "redirect": TARGET_PAGE})
        response.set_cookie(
            COOKIE_NAME, cookie,
            max_age=COOKIE_MAX_AGE,
            httponly=True,
            secure=True,
            samesite="lax",
            path="/",
        )
        return response

    # Not found → needs registration
    return JSONResponse({"status": "nao_encontrado"})


@app.post("/register")
async def register(request: Request):
    body = await request.json()
    nome = body.get("nome", "").strip()
    sobrenome = body.get("sobrenome", "").strip()
    email = body.get("email", "").strip().lower()
    celular = body.get("celular", "").strip()

    if not all([nome, sobrenome, email, celular]):
        return JSONResponse({"error": "Todos os campos são obrigatórios"}, status_code=400)

    if is_aluno(email):
        cookie = make_cookie(email)
        response = JSONResponse({"status": "autorizado", "redirect": TARGET_PAGE})
        response.set_cookie(
            COOKIE_NAME, cookie,
            max_age=COOKIE_MAX_AGE,
            httponly=True,
            secure=True,
            samesite="lax",
            path="/",
        )
        return response

    # Register and send single welcome email with access link
    token = secrets.token_urlsafe(32)
    register_lead(nome, sobrenome, email, celular, token)

    base_url = os.getenv("BASE_URL", "http://localhost:8000")
    send_welcome_email(email, nome, token, base_url)

    return JSONResponse({"status": "email_enviado"})


@app.get("/verify/{token}")
async def verify_email(token: str):
    """User clicks link in email → verify, set cookie, go to calculator."""
    email = verify_lead(token)
    if not email:
        return RedirectResponse(f"{AUTH_PREFIX}/?error=token_invalido")

    cookie = make_cookie(email)
    response = RedirectResponse(TARGET_PAGE, status_code=302)
    response.set_cookie(
        COOKIE_NAME, cookie,
        max_age=COOKIE_MAX_AGE,
        httponly=True,
        secure=True,
        samesite="lax",
        path="/",
    )
    return response


## --- Leads Admin Panel ---

ADMIN_EMAILS = {"anderson@scoras.com.br", "patricia@scoras.com.br"}
ADMIN_PASSWORD_HASH = hashlib.sha256(os.getenv("ADMIN_PASSWORD", "scoras2026!").encode()).hexdigest()
ADMIN_COOKIE = "diag_admin"


@app.get("/leads", response_class=HTMLResponse)
async def leads_page(request: Request):
    cookie = request.cookies.get(ADMIN_COOKIE)
    if cookie and validate_admin_cookie(cookie):
        return render_leads_panel()
    return (FRONTEND_DIR / "leads_login.html").read_text()


@app.post("/leads/auth")
async def leads_auth(request: Request):
    body = await request.json()
    email = body.get("email", "").strip().lower()
    password = body.get("password", "")
    pw_hash = hashlib.sha256(password.encode()).hexdigest()

    if email not in ADMIN_EMAILS:
        return JSONResponse({"error": "Acesso restrito."}, status_code=403)
    if pw_hash != ADMIN_PASSWORD_HASH:
        return JSONResponse({"error": "Senha incorreta."}, status_code=403)

    cookie = serializer.dumps(email, salt="admin")
    response = JSONResponse({"status": "ok", "redirect": f"{AUTH_PREFIX}/leads"})
    response.set_cookie(
        ADMIN_COOKIE, cookie,
        max_age=86400,  # 24h
        httponly=True,
        secure=True,
        samesite="lax",
        path="/",
    )
    return response


def validate_admin_cookie(cookie_value: str):
    try:
        email = serializer.loads(cookie_value, salt="admin", max_age=86400)
        return email in ADMIN_EMAILS
    except Exception:
        return False


def render_leads_panel():
    leads = get_all_leads()
    total = len(leads)
    verificados = sum(1 for l in leads if l["verificado"])

    rows = ""
    for l in leads:
        status = "Verificado" if l["verificado"] else "Pendente"
        status_color = "#10b981" if l["verificado"] else "#f59e0b"
        rows += f"""<tr>
            <td>{l['nome']} {l['sobrenome']}</td>
            <td>{l['email']}</td>
            <td>{l['celular']}</td>
            <td><span style="color:{status_color};font-weight:600">{status}</span></td>
            <td>{l['created_at'][:16]}</td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cadastros — Diagnóstico de Automação</title>
    <style>
        * {{ margin:0; padding:0; box-sizing:border-box; }}
        body {{ font-family:'Segoe UI',system-ui,sans-serif; background:#050510; color:#e0e0e0; min-height:100vh; padding:24px; }}
        .header {{ display:flex; justify-content:space-between; align-items:center; margin-bottom:24px; }}
        h1 {{ font-size:22px; background:linear-gradient(135deg,#6366f1,#a78bfa); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }}
        .stats {{ display:flex; gap:16px; margin-bottom:24px; }}
        .stat {{ background:#0d0d1a; border:1px solid #1a1a2e; border-radius:10px; padding:16px 24px; }}
        .stat-value {{ font-size:28px; font-weight:700; color:#f0f0f0; }}
        .stat-label {{ font-size:12px; color:#888; margin-top:2px; }}
        table {{ width:100%; border-collapse:collapse; background:#0d0d1a; border:1px solid #1a1a2e; border-radius:10px; overflow:hidden; }}
        th {{ background:#111125; padding:12px 16px; text-align:left; font-size:13px; color:#aaa; font-weight:600; border-bottom:1px solid #1a1a2e; }}
        td {{ padding:10px 16px; font-size:14px; border-bottom:1px solid #1a1a2e; color:#ccc; }}
        tr:hover td {{ background:#111125; }}
        .logout {{ color:#888; text-decoration:none; font-size:13px; border:1px solid #2a2a40; padding:6px 14px; border-radius:6px; }}
        .logout:hover {{ color:#f0f0f0; border-color:#444; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Scoras Academy — Cadastros</h1>
        <a href="/" class="logout">Sair</a>
    </div>
    <div class="stats">
        <div class="stat"><div class="stat-value">{total}</div><div class="stat-label">Total de cadastros</div></div>
        <div class="stat"><div class="stat-value">{verificados}</div><div class="stat-label">Verificados</div></div>
        <div class="stat"><div class="stat-value">{total - verificados}</div><div class="stat-label">Pendentes</div></div>
    </div>
    <table>
        <thead><tr><th>Nome</th><th>E-mail</th><th>Celular</th><th>Status</th><th>Data</th></tr></thead>
        <tbody>{rows}</tbody>
    </table>
</body>
</html>"""


## --- API for external dashboard ---

DASHBOARD_API_KEY = os.getenv("DASHBOARD_API_KEY", "diag-api-2026-scoras")


@app.get("/api/leads")
async def api_leads(request: Request):
    """Protected JSON API for the Hotmart dashboard to fetch leads."""
    api_key = request.headers.get("X-API-Key", "")
    if api_key != DASHBOARD_API_KEY:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    return JSONResponse({"data": get_all_leads()})


@app.get("/api/health")
async def health():
    return {"status": "ok"}
