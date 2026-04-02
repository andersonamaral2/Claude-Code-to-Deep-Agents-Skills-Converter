#!/usr/bin/env python3
"""
Scoras Chatbot API - Versão com Redis Storage
API que realmente armazena conversas no Redis
"""

import os
import json
import uuid
import uvicorn
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
from dotenv import load_dotenv
import redis
import re

# Load environment variables
load_dotenv()

app = FastAPI(title="Scoras Chatbot API - With Redis Storage")

# Configurar CORS para permitir requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todas as origens para desenvolvimento
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuração Azure DeepSeek V3
AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT")
AZURE_API_KEY = os.getenv("AZURE_API_KEY")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "DeepSeek-V3")

# Redis Configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Initialize Redis client
try:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    redis_client.ping()
    print("✅ Redis client connected successfully")
except Exception as e:
    print(f"❌ Failed to connect to Redis: {e}")
    redis_client = None

# Simple Azure AI client
try:
    from azure.ai.inference import ChatCompletionsClient
    from azure.core.credentials import AzureKeyCredential
    
    # Azure AI Foundry requires /models in the endpoint path
    azure_endpoint = AZURE_ENDPOINT.rstrip("/")
    if not azure_endpoint.endswith("/models"):
        azure_endpoint += "/models"
    client = ChatCompletionsClient(
        endpoint=azure_endpoint,
        credential=AzureKeyCredential(AZURE_API_KEY)
    )
    print("✅ Azure AI client initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize Azure AI client: {e}")
    client = None

# Models
class ChatMessage(BaseModel):
    user_id: Optional[str] = None
    message: str
    reset: Optional[bool] = False

# Simple prompts
ACADEMY_PROMPT = """Você é a Cora, consultora comercial da Scoras Academy, especialista em Engenharia de IA.

🎯 OBJETIVO INTERNO (não mencione):
Qualificar clientes coletando nome, e-mail e telefone/WhatsApp do interessado.

🔥 PROMOÇÃO ESPECIAL JULHO 2025:
Válida de 01 a 31 de julho ou enquanto durarem os lotes!
🔓 1º LOTE: 50 licenças por R$ 2.599 (à vista)
⏳ 2º LOTE: Mais 50 licenças por R$ 2.999
💰 Preço normal: R$ 3.519,81
📊 Valor avulso total: R$ 14.970

FORMAÇÃO CONTINUADA - CICLO COMPLETO DE ENGENHARIA DE IA:
✅ Teoria, casos de uso e deployment
✅ Acesso às aulas atuais e futuros lançamentos
✅ 12x de R$ 268,80/ano ou R$ 2.599/ano à vista
✅ Conteúdo exclusivo com Anderson Amaral
✅ Atualizações constantes (2+ cursos novos/mês)
✅ Aprendizado prático em módulos estruturados
✅ Acesso ao GitHub exclusivo do curso
✅ Acesso a vagas exclusivas de empresas parceiras

📚 TRILHA RECOMENDADA PARA INICIANTES:
1. Python para Iniciantes em IA (base essencial)
2. Fundamentos de LLMs e SLMs
3. RAG (Retrieval Augmented Generation)
4. Todos os outros cursos intermediários
5. LangGraph e PydanticAI (mais complexos)

🚀 PRÓXIMOS CURSOS NO BACKLOG:
CrewAI, Ontologia com LangGraph, Computação Quântica, Agno, A2A e vários outros.

🏢 SCORAS DIGITAL - DETECÇÃO DE LEADS DE PROJETOS:
Quando alguém perguntar sobre implementar IA em empresas, projetos corporativos,
desenvolver agentes de IA, consultoria, fábrica de software, ou qualquer serviço
que NÃO seja sobre cursos da Academy:
- Explique que a Scoras Digital é a primeira "Fábrica de Agentes de IA do Brasil"
- Colete nome e email ANTES de redirecionar
- Direcione para o formulário: https://scorasdigital.com.br/contato
- Diga que a equipe entrará em contato o mais rápido possível

REGRAS CRÍTICAS DE FORMATAÇÃO:
- MÁXIMO 250 caracteres por resposta (JAMAIS exceda!)
- SEMPRE termine frases completas - NUNCA corte no meio
- SEMPRE pergunte "Precisa de mais alguma informação?" ao final
- Use frases curtas e diretas
- Se o assunto for extenso, responda parte e pergunte se quer continuar

REGRAS DE INTERAÇÃO:
- Seu nome é Cora - apresente-se como Cora quando apropriado
- Seja simpática e educada como consultora comercial
- JAMAIS se identifique como IA - você é a Cora, do Time Comercial
- JAMAIS chame o cliente de "lead" - use "cliente" ou nome
- JAMAIS inicie pedindo dados pessoais - responda dúvidas primeiro
- SÓ colete email, telefone/WhatsApp e nome quando cliente não tiver mais dúvidas
- Sempre mencione: cursos podem ser vendidos separadamente
- Quando qualificar, apenas agradeça e se despeça educadamente

REGRAS DE MEMÓRIA E CONTINUIDADE:
- NUNCA repita perguntas já respondidas pelo cliente
- NUNCA peça dados que já foram coletados (veja DADOS JÁ COLETADOS acima)
- Leia o histórico da conversa antes de responder
- Avance para o próximo passo natural da conversa
- Se o cliente já disse seu nome, USE o nome dele nas respostas
- Se o cliente já mostrou interesse em um curso específico, foque nesse curso

CONTATO COMERCIAL ESPECIALIZADO:
Para propostas corporativas, licenças empresariais, métodos alternativos de pagamento ou informações específicas fora do escopo: https://api.whatsapp.com/send/?phone=5511912948575&text&type=phone_number&app_absent=0

SITE OFICIAL DA SCORAS ACADEMY:
🔗 https://scorasacademy.com.br
Na página principal, você encontrará todos os nossos cursos disponíveis. Cada curso tem um botão "Comprar" que permite aquisição individual, caso aquele curso específico esteja sendo vendido separadamente.

IMPORTANTE: JAMAIS ofereça links individuais de cursos. Sempre direcione para o site principal e explique que o cliente pode clicar em "Comprar" de cada curso para comprar individualmente."""

DIGITAL_PROMPT = """Você é consultor da Scoras Digital focado em soluções empresariais de IA.

REGRAS CRÍTICAS DE FORMATAÇÃO:
- Suas respostas devem ter EXATAMENTE entre 200-300 caracteres  
- SEMPRE termine frases completas - NUNCA corte no meio
- Se precisar de mais informações, termine a resposta e diga "Quer que eu continue?"
- Use frases curtas e diretas
- JAMAIS inicie pedindo dados pessoais - responda as dúvidas primeiro

REGRAS DE CONTEÚDO:
- Seja consultivo sobre: Consultoria IA, Projetos IA, Chatbots, RAG, Squad dedicado
- SOMENTE colete dados quando cliente quer proposta: nome, email corporativo, telefone, detalhes
- NÃO mencione valores diretos
- Seja cordial e educado
- Para leads qualificados: https://calendly.com/d/crfy-4df-hqs/scoras-ltda-services-meeting

EXEMPLO BOAS RESPOSTAS (280-300 chars):
"Na Scoras Digital oferecemos consultoria e projetos de IA: chatbots inteligentes, sistemas RAG, automação de processos. Squad dedicado para sua empresa. Como posso ajudar com seu projeto? Quer detalhes sobre algum serviço específico?" """

def classify_lead_type(message: str) -> str:
    """Classifica o tipo de lead baseado na mensagem"""
    message_lower = message.lower()
    
    # Academy indicators (incluindo preços e valores dos cursos)
    academy_indicators = [
        'curso', 'cursos', 'academy', 'modulo', 'módulo', 'módulos',
        'langgraph', 'pydantic', 'rag', 'python', 'langflow',
        'aprender', 'estudar', 'certificado', 'aula', 'vídeo', 'treinamento',
        'formação continuada', 'formacao continuada', 'valor do curso', 'preço do curso',
        'investimento curso', 'quanto custa', 'valor', 'preço', 'investimento',
        'educação', 'ensino', 'didático', 'iniciantes', 'fundamentos'
    ]
    
    # Digital indicators (específicos para projetos empresariais)
    digital_indicators = [
        'consultoria empresarial', 'projeto empresarial', 'projetos da empresa',
        'solução empresarial', 'implementação empresarial', 'desenvolvimento empresarial',
        'chatbot empresarial', 'sistema empresarial', 'squad', 'negócio corporativo',
        'corporativo', 'automação empresarial', 'agente para empresa',
        'projeto', 'empresa', 'consultoria', 'implementar', 'desenvolver',
        'fábrica', 'negócio', 'sistema', 'automação',
        'implementar ia', 'agente de ia', 'fábrica de agentes'
    ]
    
    academy_score = sum(1 for indicator in academy_indicators if indicator in message_lower)
    digital_score = sum(1 for indicator in digital_indicators if indicator in message_lower)
    
    # Priorizar Academy se houver empate ou palavras específicas de educação
    educational_keywords = ['curso', 'academy', 'aprender', 'estudar', 'formação']
    has_educational = any(keyword in message_lower for keyword in educational_keywords)
    
    if academy_score >= digital_score or has_educational:
        return "ACADEMY"
    else:
        return "DIGITAL"

def store_conversation_in_redis(user_id: str, user_message: str, bot_response: str, lead_type: str):
    """Armazena a conversa no Redis"""
    if not redis_client:
        print("❌ Redis não disponível - conversa não foi salva")
        return False
    
    try:
        # Chave para a conversa do usuário
        conversation_key = f"conversation:{user_id}"
        
        # Criar objeto da mensagem
        message_data = {
            "timestamp": datetime.now().isoformat(),
            "user_message": user_message,
            "bot_response": bot_response,
            "lead_type": lead_type
        }
        
        # Buscar conversa existente
        existing_conversation = redis_client.get(conversation_key)
        if existing_conversation:
            conversation_history = json.loads(existing_conversation)
        else:
            conversation_history = {
                "user_id": user_id,
                "created_at": datetime.now().isoformat(),
                "lead_type": lead_type,
                "messages": []
            }
        
        # Adicionar nova mensagem
        conversation_history["messages"].append(message_data)
        
        # Salvar de volta no Redis
        redis_client.set(conversation_key, json.dumps(conversation_history))
        
        # Também manter uma chave simples para qualificação (compatível com admin dashboard)
        qualification_key = f"qualification:{user_id}"
        existing_qual = redis_client.get(qualification_key)
        if existing_qual:
            qualification_data = json.loads(existing_qual)
            qualification_data["lead_type"] = lead_type
            qualification_data["last_interaction"] = datetime.now().isoformat()
        else:
            qualification_data = {
                "nome": None,
                "telefone": None,
                "email": None,
                "whatsapp": None,
                "interesse": user_message[:200] if "interesse" in user_message.lower() else None,
                "lead_type": lead_type,
                "last_interaction": datetime.now().isoformat()
            }
        redis_client.set(qualification_key, json.dumps(qualification_data))
        
        print(f"✅ Conversa salva no Redis: {user_id}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao salvar no Redis: {e}")
        return False

def get_conversation_history(user_id: str) -> List[Dict]:
    """Recupera histórico de conversa do Redis"""
    if not redis_client:
        return []
    
    try:
        conversation_key = f"conversation:{user_id}"
        conversation_data = redis_client.get(conversation_key)
        
        if conversation_data:
            conversation = json.loads(conversation_data)
            return conversation.get("messages", [])
        return []
    except Exception as e:
        print(f"❌ Erro ao recuperar conversa do Redis: {e}")
        return []

def check_conversation_timeout(user_id: str) -> bool:
    """Verifica se a conversa atingiu timeout de 10 minutos"""
    if not redis_client:
        return False
    
    try:
        conversation_key = f"conversation:{user_id}"
        conversation_data = redis_client.get(conversation_key)
        
        if not conversation_data:
            return False
        
        conversation = json.loads(conversation_data)
        messages = conversation.get("messages", [])
        
        if not messages:
            return False
        
        # Pegar última mensagem
        last_message = messages[-1]
        last_timestamp = datetime.fromisoformat(last_message["timestamp"])
        
        # Verificar se passaram 10 minutos
        time_diff = datetime.now() - last_timestamp
        return time_diff > timedelta(minutes=10)
        
    except Exception as e:
        print(f"❌ Erro ao verificar timeout: {e}")
        return False

def extract_contact_info(messages: List[Dict]) -> Dict:
    """Extrai informações de contato das mensagens"""
    contact_info = {
        "nome": None,
        "email": None,
        "telefone": None,
        "whatsapp": None,
        "interesse": None
    }
    
    # Patterns para extração
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    phone_pattern = r'(?:\+55\s?)?(?:\(\d{2}\)\s?)?(?:\d{4,5}[-.\s]?\d{4})'
    
    all_text = " ".join([msg.get("user_message", "") for msg in messages])
    
    # Extrair email
    emails = re.findall(email_pattern, all_text)
    if emails:
        contact_info["email"] = emails[0]
    
    # Extrair telefone
    phones = re.findall(phone_pattern, all_text)
    if phones:
        contact_info["telefone"] = phones[0]
        # WhatsApp defaults to same as phone
        contact_info["whatsapp"] = phones[0]

    # Tentar extrair nome (procurar por "meu nome é", "me chamo", etc)
    name_patterns = [
        r'(?:meu nome [eé]|me chamo|sou o|sou a)\s+([A-Za-zÀ-ÿ\s]+)',
        r'(?:nome:)\s*([A-Za-z\s]+)',
        r'^([A-Za-z\s]{2,20})(?:\s|$)'  # Primeiro padrão que parece nome
    ]
    
    for pattern in name_patterns:
        matches = re.findall(pattern, all_text, re.IGNORECASE)
        if matches:
            contact_info["nome"] = matches[0].strip()
            break
    
    # Interesse - pegar primeira mensagem longa
    for msg in messages:
        user_msg = msg.get("user_message", "")
        if len(user_msg) > 20 and not contact_info["interesse"]:
            contact_info["interesse"] = user_msg[:200]
    
    return contact_info

def auto_qualify_lead(user_id: str, lead_type: str) -> Dict:
    """Qualifica automaticamente o lead após timeout"""
    if not redis_client:
        return {}
    
    try:
        # Pegar histórico da conversa
        messages = get_conversation_history(user_id)
        if not messages:
            return {}
        
        # Extrair informações de contato
        contact_info = extract_contact_info(messages)
        
        # Verificar requisitos mínimos
        is_qualified = False
        missing_info = []
        
        if lead_type.lower() == "academy":
            # Academy precisa: nome, email, telefone
            if not contact_info["nome"]:
                missing_info.append("nome")
            if not contact_info["email"]:
                missing_info.append("email")
            if not contact_info["telefone"]:
                missing_info.append("telefone")
            
            is_qualified = len(missing_info) == 0
            
        elif lead_type.lower() == "digital":
            # Digital precisa: nome, email corporativo, telefone, descrição projeto
            if not contact_info["nome"]:
                missing_info.append("nome")
            if not contact_info["email"]:
                missing_info.append("email corporativo")
            elif contact_info["email"]:
                # Verificar se é email corporativo
                public_domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com"]
                domain = contact_info["email"].split("@")[-1].lower()
                if domain in public_domains:
                    missing_info.append("email corporativo")
            
            if not contact_info["telefone"]:
                missing_info.append("telefone")
            if not contact_info["interesse"]:
                missing_info.append("descrição do projeto")
            
            is_qualified = len(missing_info) == 0
        
        # Atualizar qualificação no Redis
        qualification_data = {
            **contact_info,
            "lead_type": lead_type.lower(),
            "qualified": is_qualified,
            "missing_info": missing_info,
            "auto_qualified": True,
            "timeout_at": datetime.now().isoformat(),
            "last_interaction": messages[-1]["timestamp"] if messages else None
        }
        
        qualification_key = f"qualification:{user_id}"
        redis_client.set(qualification_key, json.dumps(qualification_data))
        
        print(f"🎯 Lead {user_id} auto-qualificado: {'✅' if is_qualified else '❌'}")
        if missing_info:
            print(f"   Faltando: {', '.join(missing_info)}")
        
        return qualification_data
        
    except Exception as e:
        print(f"❌ Erro na qualificação automática: {e}")
        return {}

def is_digital_lead_qualified(user_id: str) -> Dict:
    """Verifica se o lead Digital está qualificado para receber Calendly"""
    if not redis_client:
        return {"qualified": False, "missing": ["redis_unavailable"]}
    
    try:
        # Buscar dados de qualificação
        qual_key = f"qualification:{user_id}"
        qual_data = redis_client.get(qual_key)
        if not qual_data:
            return {"qualified": False, "missing": ["dados_incompletos"]}
        
        qualification = json.loads(qual_data)
        
        # Verificar requisitos para Digital
        missing = []
        
        if not qualification.get("nome"):
            missing.append("nome")
        
        email = qualification.get("email")
        if not email:
            missing.append("email corporativo")
        else:
            # Verificar se é email corporativo
            public_domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "live.com"]
            domain = email.split("@")[-1].lower()
            if domain in public_domains:
                missing.append("email corporativo (não aceita Gmail/Yahoo/Hotmail)")
        
        if not qualification.get("telefone"):
            missing.append("telefone")
        
        if not qualification.get("interesse") or len(qualification.get("interesse", "")) < 20:
            missing.append("detalhes do projeto")
        
        return {
            "qualified": len(missing) == 0,
            "missing": missing,
            "data": qualification
        }
        
    except Exception as e:
        print(f"❌ Erro ao verificar qualificação Digital: {e}")
        return {"qualified": False, "missing": ["erro_sistema"]}

def update_qualification_data(user_id: str, user_message: str, lead_type: str) -> Dict:
    """Atualiza dados de qualificação baseado na mensagem do usuário"""
    if not redis_client:
        return {}
    
    try:
        qual_key = f"qualification:{user_id}"
        existing_qual = redis_client.get(qual_key)
        
        if existing_qual:
            qualification = json.loads(existing_qual)
        else:
            qualification = {
                "nome": None,
                "email": None,
                "telefone": None,
                "whatsapp": None,
                "interesse": None,
                "lead_type": lead_type.lower(),
                "qualified": False
            }

        # Update lead_type based on current message classification
        current_lead_type = classify_lead_type(user_message)
        qualification["lead_type"] = current_lead_type.lower()
        
        # Extrair informações da mensagem atual
        message_lower = user_message.lower()
        
        # Extrair email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, user_message)
        if emails and not qualification.get("email"):
            qualification["email"] = emails[0]
        
        # Extrair telefone
        phone_pattern = r'(?:\+55\s?)?(?:\(\d{2}\)\s?)?(?:\d{4,5}[-.\s]?\d{4})'
        phones = re.findall(phone_pattern, user_message)
        if phones and not qualification.get("telefone"):
            qualification["telefone"] = phones[0]

        # Extrair WhatsApp (mesmo padrão de telefone, mas detectar menção a whatsapp)
        if phones and not qualification.get("whatsapp"):
            if 'whatsapp' in message_lower or 'whats' in message_lower or 'zap' in message_lower:
                qualification["whatsapp"] = phones[0]
            elif not qualification.get("whatsapp") and phones:
                # Se informou telefone mas não whatsapp, assumir que é o mesmo
                qualification["whatsapp"] = phones[0]

        # Extrair nome
        name_patterns = [
            r'(?:meu nome [eé]|me chamo|sou o|sou a)\s+([A-Za-zÀ-ÿ\s]+)',
            r'(?:nome:)\s*([A-Za-z\s]+)'
        ]
        for pattern in name_patterns:
            matches = re.findall(pattern, user_message, re.IGNORECASE)
            if matches and not qualification.get("nome"):
                qualification["nome"] = matches[0].strip()
                break

        # Atualizar interesse/detalhes do projeto
        if len(user_message) > 30 and any(word in message_lower for word in ['projeto', 'empresa', 'negócio', 'sistema', 'consultoria', 'preciso', 'quero']):
            if not qualification.get("interesse"):
                qualification["interesse"] = user_message[:200]

        qualification["last_interaction"] = datetime.now().isoformat()
        
        # Salvar dados atualizados
        redis_client.set(qual_key, json.dumps(qualification))
        
        return qualification
        
    except Exception as e:
        print(f"❌ Erro ao atualizar qualificação: {e}")
        return {}

def detect_no_more_questions(message: str) -> bool:
    """Detecta se o cliente confirmou que não tem mais dúvidas"""
    message_lower = message.lower()
    
    # Palavras/frases que indicam fim de dúvidas
    confirmation_patterns = [
        'não tenho mais dúvidas',
        'não tenho dúvidas',
        'sem dúvidas',
        'tudo esclarecido',
        'entendi tudo',
        'está claro',
        'perfeito',
        'ok',
        'beleza',
        'certo',
        'entendi',
        'compreendi',
        'muito obrigado',
        'obrigado',
        'valeu',
        'show',
        'ótimo',
        'legal',
        'consegui entender',
        'esclareceu',
        'ficou claro'
    ]
    
    # Verificar se algum padrão está na mensagem
    for pattern in confirmation_patterns:
        if pattern in message_lower:
            return True
    
    return False

def should_collect_academy_contact(user_id: str, message: str) -> bool:
    """Verifica se deve coletar dados de contato para Academy"""
    # Só coletar se cliente confirmou que não tem mais dúvidas
    if not detect_no_more_questions(message):
        return False
    
    # Verificar se já tem os dados
    if not redis_client:
        return True
    
    try:
        qual_key = f"qualification:{user_id}"
        qual_data = redis_client.get(qual_key)
        if qual_data:
            qualification = json.loads(qual_data)
            # Se já tem nome, email e telefone, não precisa pedir novamente
            if qualification.get("nome") and qualification.get("email") and qualification.get("telefone"):
                return False
        return True
    except:
        return True

def smart_truncate_response(text: str, max_chars: int = 300) -> str:
    """NUNCA corta texto - retorna completo se não conseguir cortar adequadamente"""
    if len(text) <= max_chars:
        return text.strip()
    
    # Primeiro, tentar encontrar um ponto final natural antes do limite
    for end_char in ['.', '!', '?']:
        last_pos = text.rfind(end_char, 0, max_chars)
        if last_pos > 200:  # Só aceitar se não ficar muito curto
            return text[:last_pos + 1].strip()
    
    # Se não encontrar ponto final, procurar vírgula ou ponto e vírgula
    for punct in [',', ';']:
        last_pos = text.rfind(punct, 0, max_chars)
        if last_pos > 220:  # Só aceitar se não ficar muito curto
            return text[:last_pos + 1].strip()
    
    # IMPORTANTE: Se não conseguir cortar adequadamente, retornar texto completo
    # Melhor ter uma resposta longa e completa do que cortada no meio
    print(f"⚠️ Texto não pode ser cortado adequadamente ({len(text)} chars) - retornando completo")
    return text.strip()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Scoras Chatbot API com Redis funcionando!", "status": "online"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    status = {
        "status": "healthy",
        "azure_configured": bool(AZURE_ENDPOINT and AZURE_API_KEY),
        "model": DEEPSEEK_MODEL,
        "redis_connected": bool(redis_client)
    }
    
    if client:
        status["azure_client"] = "connected"
    else:
        status["azure_client"] = "failed"
        status["status"] = "partial"
    
    # Test Redis connection
    if redis_client:
        try:
            redis_client.ping()
            status["redis"] = "connected"
            status["redis_keys"] = redis_client.dbsize()
        except:
            status["redis"] = "disconnected"
            status["status"] = "partial"
    else:
        status["redis"] = "not_configured"
    
    return status

@app.post("/chat-simple")
async def chat_simple(chat_request: ChatMessage):
    """Endpoint principal de chat com armazenamento Redis e timeout de 10 min"""
    
    try:
        print(f"🔄 Nova mensagem recebida: {chat_request.message[:50]}...")
        
        # Gerar user_id se não fornecido
        user_id = chat_request.user_id or str(uuid.uuid4())[:8]
        
        # Reset conversa se solicitado
        if chat_request.reset:
            if redis_client:
                conversation_key = f"conversation:{user_id}"
                qualification_key = f"qualification:{user_id}"
                redis_client.delete(conversation_key)
                redis_client.delete(qualification_key)
                print(f"🗑️ Conversa resetada para {user_id}")
            
            return {
                "user_id": user_id,
                "response": "Conversa resetada! Como posso ajudá-lo?",
                "lead_type": "unknown",
                "status": "reset"
            }
        
        # Verificar timeout de 5 minutos
        if check_conversation_timeout(user_id):
            # Recuperar lead_type da conversa anterior
            conversation_history = get_conversation_history(user_id)
            previous_lead_type = "unknown"
            if conversation_history:
                previous_lead_type = conversation_history[0].get("lead_type", "unknown")
            
            # Qualificar automaticamente o lead
            qualification_result = auto_qualify_lead(user_id, previous_lead_type)
            
            print(f"⏰ Timeout detectado para {user_id} - Lead qualificado automaticamente")
            
            # Retornar mensagem de reativação
            return {
                "user_id": user_id,
                "response": "Olá! Notei que nossa conversa foi interrompida. Posso ajudá-lo novamente?",
                "lead_type": previous_lead_type,
                "status": "timeout_reactivated",
                "qualification": qualification_result
            }
        
        # Classificar tipo de lead
        lead_type = classify_lead_type(chat_request.message)
        print(f"🎯 Lead classificado como: {lead_type}")
        
        # Atualizar dados de qualificação com base na mensagem
        qualification_data = update_qualification_data(user_id, chat_request.message, lead_type)
        
        # Recuperar histórico de conversa
        conversation_history = get_conversation_history(user_id)
        
        # Build context summary from qualification data
        context_parts = []
        if qualification_data.get("nome"):
            context_parts.append(f"Nome: {qualification_data['nome']}")
        if qualification_data.get("email"):
            context_parts.append(f"Email: {qualification_data['email']}")
        if qualification_data.get("telefone"):
            context_parts.append(f"Telefone: {qualification_data['telefone']}")
        if qualification_data.get("whatsapp"):
            context_parts.append(f"WhatsApp: {qualification_data['whatsapp']}")
        if qualification_data.get("interesse"):
            context_parts.append(f"Interesse: {qualification_data['interesse']}")

        context_summary = ""
        if context_parts:
            context_summary = "\n\n📋 DADOS JÁ COLETADOS DO CLIENTE (NÃO pergunte novamente):\n" + "\n".join(context_parts)
        elif len(conversation_history) > 0:
            context_summary = "\n\n📋 NENHUM DADO COLETADO AINDA - continue a conversa naturalmente."

        # Add message count context
        context_summary += f"\n\n💬 Esta é a mensagem #{len(conversation_history) + 1} da conversa."

        # Preparar prompt baseado no tipo de lead e status de qualificação
        if lead_type == "ACADEMY":
            # Para Academy, verificar se deve coletar dados de contato
            if should_collect_academy_contact(user_id, chat_request.message):
                system_prompt = ACADEMY_PROMPT + "\n\nCLIENTE CONFIRMOU SEM MAIS DÚVIDAS ✅ - Agora colete email, telefone e nome para enviar mais informações dos cursos."
            else:
                system_prompt = ACADEMY_PROMPT + "\n\nRESPONDA DÚVIDAS PRIMEIRO 📚 - Seja informativo sobre cursos. NÃO peça dados ainda."
        else:  # DIGITAL
            # Verificar se o lead Digital está qualificado
            qualification_status = is_digital_lead_qualified(user_id)
            
            if qualification_status["qualified"]:
                system_prompt = DIGITAL_PROMPT + "\n\nLEAD QUALIFICADO ✅ - Pode oferecer Calendly quando apropriado."
            else:
                # Verificar se cliente está perguntando sobre serviços ou quer proposta
                wants_proposal = any(word in chat_request.message.lower() for word in ['proposta', 'orçamento', 'projeto', 'contratar', 'reunião', 'agendar'])
                if wants_proposal:
                    missing_info = ", ".join(qualification_status["missing"])
                    system_prompt = DIGITAL_PROMPT + f"\n\nCLIENTE QUER PROPOSTA 💼 - Colete: {missing_info} para prosseguir."
                else:
                    system_prompt = DIGITAL_PROMPT + "\n\nRESPONDA DÚVIDAS PRIMEIRO 💡 - Seja informativo sobre serviços. NÃO peça dados ainda."
        
        # Append context summary to system prompt
        system_prompt += context_summary

        # Preparar mensagens incluindo histórico
        messages = [{"role": "system", "content": system_prompt}]
        
        # Adicionar histórico recente (últimas 10 trocas)
        for msg in conversation_history[-10:]:
            messages.append({"role": "user", "content": msg["user_message"]})
            messages.append({"role": "assistant", "content": msg["bot_response"]})
        
        # Adicionar mensagem atual
        messages.append({"role": "user", "content": chat_request.message})
        
        # Chamar Azure AI
        if client:
            print(f"🤖 Chamando Azure AI...")
            try:
                response = client.complete(
                    messages=messages,
                    model=DEEPSEEK_MODEL,
                    temperature=0.7,
                    max_tokens=350
                )
                
                assistant_response = response.choices[0].message.content
                
                # Usar a nova função de corte inteligente
                assistant_response = smart_truncate_response(assistant_response, 300)
                
                print(f"✅ Azure AI respondeu ({len(assistant_response)} chars): {assistant_response}")
                
            except Exception as e:
                print(f"❌ Erro na chamada Azure AI: {e}")
                # DETECT SCORAS DIGITAL LEADS in fallback
                digital_keywords = ['projeto', 'empresa', 'consultoria', 'implementar', 'desenvolver',
                                    'fábrica', 'corporativo', 'negócio', 'sistema', 'automação',
                                    'agente de ia', 'implementar ia', 'fábrica de agentes']
                message_lower_fb = chat_request.message.lower()
                if any(keyword in message_lower_fb for keyword in digital_keywords) and lead_type == "ACADEMY":
                    assistant_response = "A Scoras Digital é a primeira Fábrica de Agentes de IA do Brasil! Para projetos empresariais, me informe seu nome e email que nossa equipe entrará em contato. Ou acesse: https://scorasdigital.com.br/contato"
                elif lead_type == "ACADEMY":
                    if should_collect_academy_contact(user_id, chat_request.message):
                        assistant_response = "Perfeito! Para enviar mais informações por email, preciso do seu nome, telefone/WhatsApp e email. Pode me informar esses dados?"
                    else:
                        assistant_response = "Olá! Sou a Cora, do Time Comercial da Scoras Academy! Temos Python para IA, LangGraph, PydanticAI e RAG. Cursos avulsos ou Formação Continuada completa! Precisa de mais alguma informação? https://scorasacademy.com.br"
                else:
                    qualification_status = is_digital_lead_qualified(user_id)
                    wants_proposal = any(word in chat_request.message.lower() for word in ['proposta', 'orçamento', 'projeto', 'contratar', 'reunião', 'agendar'])
                    
                    if qualification_status["qualified"]:
                        assistant_response = "Perfeito! Com seus dados, posso agendar reunião com nosso time. Vamos conversar? https://calendly.com/d/crfy-4df-hqs/scoras-ltda-services-meeting"
                    elif wants_proposal:
                        missing = ", ".join(qualification_status["missing"][:2])  # Limitar para não ficar muito longo
                        assistant_response = f"Para proposta personalizada, preciso de: {missing}. Pode me fornecer?"
                    else:
                        assistant_response = "Olá! Scoras Digital: consultoria IA, projetos, chatbots e sistemas RAG. Squad dedicado para sua empresa. Como posso ajudar?"
                
                # Aplicar corte inteligente nos fallbacks também
                assistant_response = smart_truncate_response(assistant_response, 300)
                
        else:
            # Fallback response quando Azure não está disponível
            # DETECT SCORAS DIGITAL LEADS in fallback
            digital_keywords = ['projeto', 'empresa', 'consultoria', 'implementar', 'desenvolver',
                                'fábrica', 'corporativo', 'negócio', 'sistema', 'automação',
                                'agente de ia', 'implementar ia', 'fábrica de agentes']
            message_lower_fb = chat_request.message.lower()
            if any(keyword in message_lower_fb for keyword in digital_keywords) and lead_type == "ACADEMY":
                assistant_response = "A Scoras Digital é a primeira Fábrica de Agentes de IA do Brasil! Para projetos empresariais, me informe seu nome e email que nossa equipe entrará em contato. Ou acesse: https://scorasdigital.com.br/contato"
            elif lead_type == "ACADEMY":
                if should_collect_academy_contact(user_id, chat_request.message):
                    assistant_response = "Perfeito! Para enviar informações por email, preciso do seu nome, telefone/WhatsApp e email. Pode me informar?"
                else:
                    assistant_response = "Olá! Sou a Cora, do Time Comercial da Scoras Academy! Temos Python para IA, LangGraph, PydanticAI e RAG. Cursos avulsos ou Formação Continuada completa! Precisa de mais alguma informação? https://scorasacademy.com.br"
            else:  # DIGITAL
                qualification_status = is_digital_lead_qualified(user_id)
                wants_proposal = any(word in chat_request.message.lower() for word in ['proposta', 'orçamento', 'projeto', 'contratar', 'reunião', 'agendar'])
                
                if qualification_status["qualified"]:
                    assistant_response = "Perfeito! Com seus dados, posso agendar reunião com nosso time. Vamos conversar? https://calendly.com/d/crfy-4df-hqs/scoras-ltda-services-meeting"
                elif wants_proposal:
                    missing = ", ".join(qualification_status["missing"][:2])  # Limitar para não ficar muito longo
                    assistant_response = f"Para proposta personalizada, preciso de: {missing}. Pode me fornecer?"
                else:
                    assistant_response = "Olá! Scoras Digital: consultoria IA, projetos, chatbots e sistemas RAG. Squad dedicado para sua empresa. Como posso ajudar?"
            
            # Aplicar corte inteligente nos fallbacks também
            assistant_response = smart_truncate_response(assistant_response, 300)
        
        # PROTEÇÃO FINAL: Academy NUNCA deve ter Calendly
        if lead_type == "ACADEMY" and "calendly" in assistant_response.lower():
            print(f"🚨 BLOQUEADO: Academy tentou oferecer Calendly! Removendo...")
            # Remove qualquer linha que contenha Calendly
            lines = assistant_response.split('\n')
            filtered_lines = [line for line in lines if 'calendly' not in line.lower()]
            assistant_response = '\n'.join(filtered_lines).strip()
            
            # Se ficou vazio, usar resposta padrão Academy
            if not assistant_response:
                assistant_response = "Na Scoras Academy oferecemos cursos de IA práticos: Python, LangGraph, Pydantic AI, RAG e muito mais! Cursos avulsos ou Formação Continuada. Como posso ajudar?"
        
        # Armazenar conversa no Redis
        store_conversation_in_redis(user_id, chat_request.message, assistant_response, lead_type)
        
        return {
            "user_id": user_id,
            "response": assistant_response,
            "lead_type": lead_type.lower(),
            "status": "success",
            "redis_stored": bool(redis_client)
        }
        
    except Exception as e:
        print(f"❌ Erro geral no chat: {str(e)}")
        return {
            "user_id": chat_request.user_id or "error_chat",
            "response": "Erro interno. Tente novamente.",
            "lead_type": "unknown",
            "status": "error"
        }

@app.post("/reset-conversation")
async def reset_conversation(user_data: dict):
    """Reset conversa específica"""
    user_id = user_data.get("user_id", "unknown")
    
    if redis_client:
        try:
            conversation_key = f"conversation:{user_id}"
            qualification_key = f"qualification:{user_id}"
            
            redis_client.delete(conversation_key)
            redis_client.delete(qualification_key)
            
            return {"message": f"Conversa {user_id} resetada com sucesso", "redis_cleared": True}
        except Exception as e:
            return {"message": f"Erro ao resetar conversa: {e}", "redis_cleared": False}
    else:
        return {"message": "Redis não disponível", "redis_cleared": False}

@app.get("/conversations")
async def list_conversations():
    """Lista todas as conversas armazenadas"""
    if not redis_client:
        return {"error": "Redis não disponível"}
    
    try:
        # Buscar todas as chaves de conversa
        conversation_keys = redis_client.keys("conversation:*")
        conversations = []
        
        for key in conversation_keys:
            conversation_data = redis_client.get(key)
            if conversation_data:
                conversation = json.loads(conversation_data)
                
                # Verificar se tem qualificação automática
                user_id = conversation["user_id"]
                qual_key = f"qualification:{user_id}"
                qual_data = redis_client.get(qual_key)
                qualification = json.loads(qual_data) if qual_data else {}
                
                conversations.append({
                    "user_id": conversation["user_id"],
                    "created_at": conversation["created_at"],
                    "lead_type": conversation["lead_type"],
                    "message_count": len(conversation["messages"]),
                    "has_timeout": qualification.get("auto_qualified", False),
                    "qualified": qualification.get("qualified", False),
                    "missing_info": qualification.get("missing_info", [])
                })
        
        return {
            "total_conversations": len(conversations),
            "conversations": conversations
        }
    except Exception as e:
        return {"error": f"Erro ao listar conversas: {e}"}

@app.get("/timeout-analysis")
async def timeout_analysis():
    """Análise de conversas com timeout e qualificação automática"""
    if not redis_client:
        return {"error": "Redis não disponível"}
    
    try:
        qualification_keys = redis_client.keys("qualification:*")
        
        stats = {
            "total_timeouts": 0,
            "academy_timeouts": 0,
            "digital_timeouts": 0,
            "qualified_after_timeout": 0,
            "common_missing_info": {},
            "timeout_conversations": []
        }
        
        for key in qualification_keys:
            qual_data = redis_client.get(key)
            if qual_data:
                qualification = json.loads(qual_data)
                
                if qualification.get("auto_qualified", False):
                    stats["total_timeouts"] += 1
                    
                    lead_type = qualification.get("lead_type", "unknown")
                    if lead_type == "academy":
                        stats["academy_timeouts"] += 1
                    elif lead_type == "digital":
                        stats["digital_timeouts"] += 1
                    
                    if qualification.get("qualified", False):
                        stats["qualified_after_timeout"] += 1
                    
                    # Contar informações faltantes
                    for missing in qualification.get("missing_info", []):
                        stats["common_missing_info"][missing] = stats["common_missing_info"].get(missing, 0) + 1
                    
                    stats["timeout_conversations"].append({
                        "user_id": key.replace("qualification:", ""),
                        "lead_type": lead_type,
                        "qualified": qualification.get("qualified", False),
                        "missing_info": qualification.get("missing_info", []),
                        "timeout_at": qualification.get("timeout_at"),
                        "contact_info": {
                            "nome": qualification.get("nome"),
                            "email": qualification.get("email"),
                            "telefone": qualification.get("telefone")
                        }
                    })
        
        return stats
        
    except Exception as e:
        return {"error": f"Erro na análise de timeout: {e}"}

@app.get("/check-inactivity/{user_id}")
async def check_inactivity(user_id: str):
    """Check how long since last message for inactivity warnings"""
    if not redis_client:
        return {"inactive_minutes": 0, "should_warn": False, "should_close": False}

    try:
        conversation_key = f"conversation:{user_id}"
        conversation_data = redis_client.get(conversation_key)

        if not conversation_data:
            return {"inactive_minutes": 0, "should_warn": False, "should_close": False}

        conversation = json.loads(conversation_data)
        messages = conversation.get("messages", [])

        if not messages:
            return {"inactive_minutes": 0, "should_warn": False, "should_close": False}

        last_timestamp = datetime.fromisoformat(messages[-1]["timestamp"])
        time_diff = datetime.now() - last_timestamp
        inactive_minutes = time_diff.total_seconds() / 60

        return {
            "inactive_minutes": round(inactive_minutes, 1),
            "should_warn": 8 <= inactive_minutes < 10,
            "should_close": inactive_minutes >= 10
        }
    except Exception as e:
        return {"inactive_minutes": 0, "should_warn": False, "should_close": False}

if __name__ == "__main__":
    print("🚀 Iniciando Scoras Chatbot API - Com Armazenamento Redis")
    print("📍 Endpoint: http://localhost:8000/chat-simple")
    print("🎓 Academy + 💼 Digital + 🗄️ Redis Storage")
    print(f"📊 Redis: {REDIS_URL}")
    
    uvicorn.run(app, host="0.0.0.0", port=8003) 