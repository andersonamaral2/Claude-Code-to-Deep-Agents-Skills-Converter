from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, EmailStr, validator

# Enumerador para tipo de lead
class LeadType(str, Enum):
    ACADEMY = "academy"
    DIGITAL = "digital"

# Modelo de dados do lead com validação
class LeadInfo(BaseModel):
    intent: str                # Intenção ou assunto de interesse do usuário
    name: str                  # Nome do lead
    email: EmailStr            # Email (EmailStr realiza validação básica de formato)
    phone: str                 # Telefone de contato
    lead_type: LeadType        # Tipo de lead (academy ou digital)

    # Validador customizado para garantir email corporativo
    @validator("email")
    def email_must_be_corporate(cls, v: str) -> str:
        # Lista de domínios públicos não permitidos
        public_domains = {"gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "live.com"}
        domain = v.split("@")[-1].lower()
        if domain in public_domains:
            raise ValueError("Por favor, forneça um email corporativo (domínio empresarial), não aceitamos emails públicos.")
        return v

# Estado da conversa para LangGraph (mensagens e dados coletados)
class ChatState(BaseModel):
    messages: List              # histórico de mensagens (tuplas ou objetos de mensagem)
    lead_info: Optional[LeadInfo] = None  # dados coletados do lead (preenchido ao final da qualificação)

# Enumerador para idiomas suportados
class SupportedLanguage(str, Enum):
    PORTUGUESE = "pt-BR"  # Português do Brasil (padrão)
    ENGLISH = "en"        # Inglês
    SPANISH = "es"        # Espanhol

# Modelo de requisição para o endpoint de chat
class ChatRequest(BaseModel):
    user_id: Optional[str] = None  # identificador opcional do usuário/conversa
    message: str
    reset: bool = False
    language: SupportedLanguage = SupportedLanguage.PORTUGUESE  # idioma preferido
