import os
import resend
from dotenv import load_dotenv

load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY")

FROM_EMAIL = os.getenv("RESEND_FROM_EMAIL", "cora@scorasacademy.com.br")
FROM_NAME = os.getenv("RESEND_FROM_NAME", "Cora - Scoras Academy")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")


def send_verification_email(to_email: str, nome: str, token: str):
    verify_url = f"{BASE_URL}/auth/verify/{token}"

    html = f"""
    <div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #0a0a0a; border-radius: 12px; overflow: hidden;">
        <div style="background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); padding: 32px; text-align: center;">
            <h1 style="color: #fff; margin: 0; font-size: 24px;">Scoras Academy</h1>
            <p style="color: #e0e0ff; margin: 8px 0 0; font-size: 14px;">De Gargalos a Agentes</p>
        </div>
        <div style="padding: 32px; color: #e0e0e0;">
            <p style="font-size: 18px; margin-top: 0;">Oi, <strong>{nome}</strong>!</p>
            <p>Obrigada por se cadastrar! Para acessar o <strong>Diagnóstico de Automação</strong> do curso <strong>De Gargalos a Agentes</strong>, confirme seu e-mail clicando no botão abaixo:</p>
            <div style="text-align: center; margin: 32px 0;">
                <a href="{verify_url}" style="background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); color: #fff; text-decoration: none; padding: 14px 32px; border-radius: 8px; font-size: 16px; font-weight: 600; display: inline-block;">
                    Confirmar meu e-mail
                </a>
            </div>
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
            "subject": "Confirme seu e-mail — Diagnóstico de Automação",
            "html": html,
            "reply_to": "anderson@scoras.com.br",
        }
    )


def send_access_link_email(to_email: str, nome: str, access_token: str):
    access_url = f"{BASE_URL}/diagnostico?token={access_token}"

    html = f"""
    <div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #0a0a0a; border-radius: 12px; overflow: hidden;">
        <div style="background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); padding: 32px; text-align: center;">
            <h1 style="color: #fff; margin: 0; font-size: 24px;">Scoras Academy</h1>
            <p style="color: #e0e0ff; margin: 8px 0 0; font-size: 14px;">De Gargalos a Agentes</p>
        </div>
        <div style="padding: 32px; color: #e0e0e0;">
            <p style="font-size: 18px; margin-top: 0;">Oi, <strong>{nome}</strong>!</p>
            <p>Seu e-mail foi confirmado! Agora você pode acessar o <strong>Diagnóstico de Automação</strong> a qualquer momento.</p>
            <p>Da próxima vez, basta informar seu e-mail na página — sem precisar cadastrar de novo.</p>
            <div style="text-align: center; margin: 32px 0;">
                <a href="{access_url}" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: #fff; text-decoration: none; padding: 14px 32px; border-radius: 8px; font-size: 16px; font-weight: 600; display: inline-block;">
                    Acessar Diagnóstico
                </a>
            </div>
            <p style="font-size: 13px; color: #888;">Guarde este e-mail como atalho, mas lembre-se: basta seu e-mail para entrar.</p>
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
            "subject": "Seu acesso ao Diagnóstico de Automação está pronto!",
            "html": html,
            "reply_to": "anderson@scoras.com.br",
        }
    )
