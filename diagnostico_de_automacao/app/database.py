import duckdb
import os
from dotenv import load_dotenv

load_dotenv()

DUCKDB_PATH = os.getenv("DUCKDB_PATH", "data/diagnostico.duckdb")


def get_connection():
    return duckdb.connect(DUCKDB_PATH)


def init_db():
    con = get_connection()
    con.execute("CREATE SEQUENCE IF NOT EXISTS seq_alunos START 1")
    con.execute("""
        CREATE TABLE IF NOT EXISTS alunos (
            id INTEGER DEFAULT nextval('seq_alunos') PRIMARY KEY,
            nome VARCHAR NOT NULL,
            sobrenome VARCHAR NOT NULL,
            email VARCHAR NOT NULL UNIQUE,
            celular VARCHAR,
            created_at TIMESTAMP DEFAULT current_timestamp
        )
    """)
    con.execute("CREATE SEQUENCE IF NOT EXISTS seq_leads START 1")
    con.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER DEFAULT nextval('seq_leads') PRIMARY KEY,
            nome VARCHAR NOT NULL,
            sobrenome VARCHAR NOT NULL,
            email VARCHAR NOT NULL UNIQUE,
            celular VARCHAR NOT NULL,
            token VARCHAR NOT NULL,
            verificado BOOLEAN DEFAULT false,
            created_at TIMESTAMP DEFAULT current_timestamp,
            verificado_at TIMESTAMP
        )
    """)
    con.close()


def is_aluno(email: str) -> bool:
    con = get_connection()
    result = con.execute(
        "SELECT COUNT(*) FROM alunos WHERE LOWER(email) = LOWER(?)", [email]
    ).fetchone()
    con.close()
    return result[0] > 0


def is_lead_verificado(email: str) -> bool:
    con = get_connection()
    result = con.execute(
        "SELECT COUNT(*) FROM leads WHERE LOWER(email) = LOWER(?) AND verificado = true",
        [email],
    ).fetchone()
    con.close()
    return result[0] > 0


def register_lead(nome: str, sobrenome: str, email: str, celular: str, token: str):
    con = get_connection()
    # Upsert: if email exists, update token
    existing = con.execute(
        "SELECT id FROM leads WHERE LOWER(email) = LOWER(?)", [email]
    ).fetchone()
    if existing:
        con.execute(
            "UPDATE leads SET nome=?, sobrenome=?, celular=?, token=?, verificado=false WHERE LOWER(email) = LOWER(?)",
            [nome, sobrenome, celular, token, email],
        )
    else:
        con.execute(
            "INSERT INTO leads (nome, sobrenome, email, celular, token) VALUES (?, ?, ?, ?, ?)",
            [nome, sobrenome, email, celular, token],
        )
    con.close()


def verify_lead(token: str) -> "str | None":
    """Verify a lead by token. Returns email if found, None otherwise."""
    con = get_connection()
    result = con.execute(
        "SELECT email FROM leads WHERE token = ? AND verificado = false", [token]
    ).fetchone()
    if result:
        con.execute(
            "UPDATE leads SET verificado = true, verificado_at = current_timestamp WHERE token = ?",
            [token],
        )
        email = result[0]
        con.close()
        return email
    con.close()
    return None
