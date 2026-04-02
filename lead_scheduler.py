import os
from redis import Redis
from models import ChatState, LeadInfo, LeadType

# Configurações
CALENDLY_LINK = os.getenv("CALENDLY_LINK", "https://calendly.com/scoras/reuniao")

def create_redis_client():
    """Cria cliente Redis configurado para Azure Cache for Redis."""
    redis_url = os.getenv("REDIS_URL")
    
    if redis_url:
        return Redis.from_url(redis_url, decode_responses=False)
    else:
        redis_host = os.getenv("REDIS_HOST", "cache-redis.redis.cache.windows.net")
        redis_port = int(os.getenv("REDIS_PORT", "6380"))
        redis_password = os.getenv("REDIS_PASSWORD")
        redis_ssl = os.getenv("REDIS_SSL", "true").lower() == "true"
        
        return Redis(
            host=redis_host,
            port=redis_port,
            password=redis_password,
            ssl=redis_ssl,
            ssl_cert_reqs=None,
            decode_responses=False
        )

redis_client = create_redis_client()

def finalize_lead_and_schedule(state: ChatState) -> ChatState:
    """Verifica se lead_info está completo e retorna mensagem final com link de agendamento."""
    if not state.lead_info:
        return state
    
    lead = state.lead_info
    
    try:
        # Tenta validar os dados coletados
        lead_validated = LeadInfo(
            intent=lead.intent,
            name=lead.name,
            email=lead.email,
            phone=lead.phone,
            lead_type=lead.lead_type
        )
        
        # Se passou na validação, salvar no Redis
        lead_key = f"lead:{lead.email}"
        try:
            redis_client.hset(lead_key, mapping={
                "intent": lead.intent,
                "name": lead.name,
                "email": lead.email,
                "phone": lead.phone,
                "lead_type": lead.lead_type.value
            })
            print(f"✅ Lead salvo no Azure Redis: {lead.email}")
        except Exception as e:
            print(f"⚠️ Erro ao salvar lead no Azure Redis: {e}")
        
        # Adiciona mensagem final com link de Calendly
        if lead.lead_type == LeadType.DIGITAL:
            msg = (
                "assistant",
                f"{lead.name}, obrigado pelas informações! 📆 Segue o link para agendar nossa reunião: {CALENDLY_LINK}\n\n"
                "Estou à disposição e ansioso para conversarmos em breve sobre como podemos ajudar sua empresa com soluções de IA."
            )
        else:
            msg = (
                "assistant",
                f"{lead.name}, obrigado pelo interesse na Scoras Academy! 🎓\n\n"
                "Acesse nosso site para mais informações sobre os cursos: https://scorasacademy.com.br/\n"
                "Para dúvidas específicas, entre em contato: admin@scoras.com.br"
            )
        
        state.messages.append(msg)
        
    except Exception as e:
        # Se houver erro de validação (e.g. email não corporativo)
        error_msg = str(e)
        state.messages.append(("assistant", f"Lamento, {error_msg}"))
        # Remove dados inválidos para usuário fornecer novamente
        if "email" in error_msg.lower():
            state.lead_info.email = "user@placeholder.com"
    
    return state

def should_finalize(state: ChatState) -> str:
    """Determina se deve finalizar o lead ou continuar a conversa."""
    if not state.lead_info:
        return "END"
    
    lead = state.lead_info
    
    # Para leads da Academy, finaliza se tiver pelo menos o nome
    if lead.lead_type == LeadType.ACADEMY and lead.name:
        return "finalize"
    
    # Para leads Digital, precisa de todos os dados
    if (lead.lead_type == LeadType.DIGITAL and 
        lead.name and 
        lead.email and 
        lead.email != "user@placeholder.com" and 
        lead.phone):
        return "finalize"
    
    return "END"

def extract_lead_info_from_message(state: ChatState) -> ChatState:
    """Extrai informações do lead das mensagens da conversa."""
    if not state.lead_info:
        return state
    
    # Procura por informações nas últimas mensagens
    recent_messages = state.messages[-5:] if len(state.messages) >= 5 else state.messages
    
    for role, content in recent_messages:
        if role == "user" or role == "human":
            content_lower = content.lower()
            
            # Extrai nome (heurística simples)
            if "nome" in content_lower or "chamo" in content_lower:
                # Implementar lógica de extração de nome
                pass
            
            # Extrai email
            if "@" in content:
                import re
                email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', content)
                if email_match and state.lead_info.email == "user@placeholder.com":
                    state.lead_info.email = email_match.group()
            
            # Extrai telefone
            phone_patterns = [r'\(\d{2}\)\s*\d{4,5}-\d{4}', r'\d{2}\s*\d{4,5}-\d{4}', r'\d{10,11}']
            for pattern in phone_patterns:
                import re
                phone_match = re.search(pattern, content.replace(" ", ""))
                if phone_match and not state.lead_info.phone:
                    state.lead_info.phone = phone_match.group()
    
    return state

# Podemos chamar finalize_lead_and_schedule em um ponto adequado.
# Por exemplo, após o chatbot node, poderíamos checar se perfil é DIGITAL e dados preenchidos, então inserir essa etapa.
# Uma forma: substituir a aresta chatbot->END por chatbot->finalize->END no fluxo para leads Digital.
graph.add_node("finalize", finalize_lead_and_schedule)
# Ajustar edges: se lead_type == DIGITAL, vai para finalize antes de END
def should_finalize(state: ChatState):
    return "finalize" if state.lead_info and state.lead_info.lead_type == LeadType.DIGITAL and state.lead_info.email and state.lead_info.phone and state.lead_info.name else END

graph.add_conditional_edges("chatbot", should_finalize)
graph.add_edge("finalize", END)
