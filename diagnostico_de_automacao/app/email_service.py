import os
import resend
from dotenv import load_dotenv

load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY")

FROM_EMAIL = os.getenv("RESEND_FROM_EMAIL", "cora@scorasacademy.com.br")
FROM_NAME = os.getenv("RESEND_FROM_NAME", "Cora - Scoras Academy")


def send_welcome_email(to_email: str, nome: str, token: str, base_url: str):
    """Single email: confirms registration + gives access link."""
    access_url = f"{base_url}/verify/{token}"

    html = f"""
    <div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #0a0a0a; border-radius: 12px; overflow: hidden;">
        <div style="background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); padding: 32px; text-align: center;">
            <h1 style="color: #fff; margin: 0; font-size: 24px;">Scoras Academy</h1>
            <p style="color: #e0e0ff; margin: 8px 0 0; font-size: 14px;">De Gargalos a Agentes</p>
        </div>
        <div style="padding: 32px; color: #e0e0e0;">
            <p style="font-size: 18px; margin-top: 0;">Oi, <strong>{nome}</strong>!</p>
            <p>Seu cadastro no <strong>Diagnóstico de Automação</strong> foi realizado com sucesso!</p>
            <p>Clique no botão abaixo para acessar a ferramenta:</p>
            <div style="text-align: center; margin: 32px 0;">
                <a href="{access_url}" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: #fff; text-decoration: none; padding: 14px 32px; border-radius: 8px; font-size: 16px; font-weight: 600; display: inline-block;">
                    Acessar Diagnóstico de Automação
                </a>
            </div>
            <p style="font-size: 14px; color: #bbb;">Da próxima vez, basta informar seu e-mail na página — sem precisar cadastrar de novo.</p>
            <p style="font-size: 13px; color: #888;">Se você não se cadastrou, pode ignorar este e-mail.</p>
        </div>
        <div style="background: #111; padding: 16px; text-align: center; border-top: 1px solid #222;">
            <p style="color: #666; font-size: 12px; margin: 0;">Scoras Academy &copy; 2026</p>
        </div>
    </div>
    """

    resend.Emails.send(
        {
            "from": f"{FROM_NAME} <{FROM_EMAIL}>",
            "to": [to_email],
            "subject": "Seu acesso ao Diagnóstico de Automação — Scoras Academy",
            "html": html,
            "reply_to": "anderson@scoras.com.br",
        }
    )
