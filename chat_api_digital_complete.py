#!/usr/bin/env python3
"""
Scoras Chatbot API - Versão Completa (Academy + Digital)
Sistema RAG híbrido com qualificação de leads para preços
"""

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import os
from dotenv import load_dotenv
import json

# Configuração LLM
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential

# Sistema RAG híbrido
from hybrid_search import search_scoras_hybrid

# Load environment variables
load_dotenv()

app = FastAPI(title="Scoras Chatbot API - Complete")

# Configurar CORS para permitir requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuração Azure DeepSeek V3
AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT")
AZURE_API_KEY = os.getenv("AZURE_API_KEY")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "DeepSeek-V3")

# Client Azure AI
client = ChatCompletionsClient(
    endpoint=AZURE_ENDPOINT,
    credential=AzureKeyCredential(AZURE_API_KEY)
)

# Armazenamento simples de conversas (em produção usar Redis)
conversations = {}
lead_qualifications = {}

class ChatMessage(BaseModel):
    user_id: Optional[str] = None
    message: str
    reset: Optional[bool] = False

class ChatResponse(BaseModel):
    user_id: str
    response: str
    lead_type: str
    is_qualified: bool = False
    qualification_status: Dict = {}

def get_keywords_from_message(message: str) -> List[str]:
    """Extrai palavras-chave relevantes da mensagem"""
    keywords = []
    message_lower = message.lower()
    
    # Keywords Academy
    academy_keywords = [
        'curso', 'cursos', 'academy', 'scoras academy', 'modulo', 'módulo', 'módulos',
        'langgraph', 'pydantic', 'pydanticai', 'rag', 'python', 'langflow', 'routing',
        'deployment', 'projetos práticos', 'cases', 'trilha', 'aprendizagem',
        'aula', 'aulas', 'video', 'vídeo', 'certificado', 'certificação'
    ]
    
    # Keywords Digital  
    digital_keywords = [
        'consultoria', 'consultar', 'projeto', 'projetos', 'squad', 'empresa', 'empresarial',
        'digital transformation', 'transformação digital', 'ia empresarial', 'solução',
        'implementação', 'desenvolvimento', 'arquitetura', 'estratégia', 'roadmap',
        'maturidade digital', 'automação', 'chatbot', 'sistema rag', 'análise', 'kpis',
        'orientação técnica', 'full-time', 'part-time', 'orientação estratégica'
    ]
    
    # Pricing keywords (ambos)
    pricing_keywords = [
        'preço', 'preços', 'valor', 'valores', 'custo', 'custos', 'investimento',
        'quanto custa', 'tabela', 'orçamento', 'proposta', 'basico', 'essencial', 
        'expandido', 'part-time', 'full-time'
    ]
    
    all_keywords = academy_keywords + digital_keywords + pricing_keywords
    
    for keyword in all_keywords:
        if keyword in message_lower:
            keywords.append(keyword)
    
    return keywords

def classify_lead_type(message: str) -> str:
    """Classifica o tipo de lead baseado na mensagem"""
    message_lower = message.lower()
    
    # Academy indicators
    academy_indicators = [
        'curso', 'cursos', 'academy', 'scoras academy', 'modulo', 'módulo', 'módulos',
        'langgraph', 'pydantic', 'pydanticai', 'rag', 'python', 'langflow', 'routing',
        'deployment', 'aprender', 'estudar', 'certificado', 'aula', 'vídeo'
    ]
    
    # Digital indicators
    digital_indicators = [
        'consultoria', 'consultar', 'projeto', 'projetos', 'squad', 'empresa', 'empresarial',
        'digital transformation', 'transformação digital', 'ia empresarial', 'solução',
        'implementação', 'desenvolvimento', 'arquitetura', 'estratégia', 'roadmap',
        'maturidade digital', 'automação', 'chatbot empresarial', 'sistema empresarial'
    ]
    
    academy_score = sum(1 for indicator in academy_indicators if indicator in message_lower)
    digital_score = sum(1 for indicator in digital_indicators if indicator in message_lower)
    
    # Se houver empate ou nenhum score, usar keywords secundárias
    if academy_score == digital_score:
        if any(word in message_lower for word in ['negócio', 'equipe', 'time', 'equipe técnica', 'empresa']):
            return "DIGITAL"
        elif any(word in message_lower for word in ['aprender', 'estudar', 'quero fazer', 'interessado em curso']):
            return "ACADEMY"
    
    return "ACADEMY" if academy_score > digital_score else "DIGITAL"

def check_lead_qualification(user_id: str, message: str) -> Dict:
    """Verifica se o lead está qualificado para ver preços"""
    qualification = lead_qualifications.get(user_id, {
        'nome': None,
        'telefone': None,
        'email': None,
        'interesse': None,
        'is_qualified': False
    })
    
    message_lower = message.lower()
    
    # Detectar nome (simples - melhorar com NLP)
    if not qualification['nome']:
        import re
        # Procurar por "meu nome é", "sou", "me chamo", etc.
        name_patterns = [
            r'meu nome é ([a-záêçõñü\s]+)',
            r'me chamo ([a-záêçõñü\s]+)',
            r'sou o? ([a-záêçõñü\s]+)',
            r'nome: ([a-záêçõñü\s]+)',
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, message_lower)
            if match:
                qualification['nome'] = match.group(1).strip().title()
                break
    
    # Detectar telefone
    if not qualification['telefone']:
        import re
        phone_pattern = r'(?:\+55\s?)?(?:\(?\d{2}\)?\s?)?\d{4,5}[-.\s]?\d{4}'
        match = re.search(phone_pattern, message)
        if match:
            qualification['telefone'] = match.group(0)
    
    # Detectar email corporativo
    if not qualification['email']:
        import re
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, message)
        if match:
            email = match.group(0).lower()
            # Rejeitar emails públicos
            public_domains = ['gmail.com', 'hotmail.com', 'yahoo.com', 'outlook.com', 'live.com']
            if not any(domain in email for domain in public_domains):
                qualification['email'] = email
    
    # Detectar interesse/necessidade
    if not qualification['interesse']:
        interest_keywords = [
            'consultoria', 'projeto', 'automação', 'chatbot', 'sistema', 'solução',
            'implementação', 'desenvolvimento', 'arquitetura', 'estratégia', 'roadmap'
        ]
        if any(keyword in message_lower for keyword in interest_keywords):
            qualification['interesse'] = message[:200]  # Primeiros 200 chars
    
    # Verificar se está qualificado
    qualification['is_qualified'] = all([
        qualification['nome'],
        qualification['telefone'], 
        qualification['email'],
        qualification['interesse']
    ])
    
    # Salvar qualificação
    lead_qualifications[user_id] = qualification
    return qualification

def should_use_rag(keywords: List[str], lead_type: str) -> bool:
    """Determina se deve usar RAG baseado nas keywords"""
    # Academy - sempre usar RAG para queries sobre cursos/conteúdo
    if lead_type == "ACADEMY":
        academy_triggers = [
            'módulo', 'módulos', 'modulo', 'modulos', 'curso', 'cursos',
            'langgraph', 'pydantic', 'rag', 'python', 'langflow', 'routing',
            'deployment', 'cases', 'projetos', 'trilha', 'academy',
            'quantos', 'quais', 'como', 'onde', 'quando', 'detalhes',
            'conteúdo', 'conteudo', 'o que', 'específico'
        ]
        return any(keyword in academy_triggers for keyword in keywords)
    
    # Digital - usar RAG para queries sobre serviços/preços (se qualificado)
    elif lead_type == "DIGITAL":
        digital_triggers = [
            'consultoria', 'projeto', 'projetos', 'squad', 'preço', 'preços',
            'valor', 'valores', 'custo', 'investimento', 'quanto custa',
            'tabela', 'basico', 'essencial', 'expandido', 'part-time', 'full-time',
            'o que', 'quais', 'como', 'detalhes', 'específico'
        ]
        return any(keyword in digital_triggers for keyword in keywords)
    
    return False

def get_system_prompt(lead_type: str, qualification: Dict) -> str:
    """Retorna o prompt do sistema baseado no tipo de lead"""
    
    if lead_type == "ACADEMY":
        return """Você é um assistente inteligente da Scoras Academy, especializado em cursos de Inteligência Artificial.

INSTRUÇÕES CRÍTICAS:
- Use APENAS as informações fornecidas no contexto RAG
- NUNCA invente ou crie conteúdo que não esteja no contexto
- Se não houver informação no contexto, diga que não tem essa informação específica
- Seja preciso e detalhado ao listar módulos de cursos
- Mantenha um tom profissional e educativo
- Incentive o interesse nos cursos da Scoras Academy

OBJETIVO: Fornecer informações precisas sobre cursos e ajudar na jornada de aprendizado em IA."""

    elif lead_type == "DIGITAL":
        is_qualified = qualification.get('is_qualified', False)
        
        if is_qualified:
            return """Você é um consultor especializado da Scoras Digital, focado em soluções empresariais de IA.

INSTRUÇÕES CRÍTICAS:
- Use APENAS as informações fornecidas no contexto RAG
- NUNCA invente preços ou condições que não estejam no contexto
- Seja preciso ao apresentar valores e condições
- Mantenha tom consultivo e profissional
- Direcione para próximos passos (proposta, reunião, contrato)

LEAD QUALIFICADO ✅
- Nome: {nome}
- Telefone: {telefone}
- Email: {email}
- Interesse: {interesse}

PODE APRESENTAR PREÇOS E VALORES.

REGRA ESPECIAL - CALENDLY:
Quando o lead qualificado disser que não tem mais dúvidas (palavras como "não", "não tenho", "sem dúvidas", "tudo certo", "ok", "entendi", "perfeito"), SEMPRE ofereça o link do Calendly:

"Perfeito! Como próximo passo, convido você para agendar uma reunião comigo para discutirmos os detalhes e elaborarmos uma proposta personalizada:

📅 **AGENDE SUA REUNIÃO AQUI:**
👉 https://calendly.com/d/crfy-4df-hqs/scoras-ltda-services-meeting

Na reunião, vamos:
• Detalhar seu projeto específico
• Elaborar proposta personalizada
• Definir cronograma e próximos passos
• Esclarecer qualquer dúvida técnica

Aguardo nosso encontro!"

Use esta regra sempre que detectar que o lead não tem mais dúvidas.""".format(
                nome=qualification.get('nome', 'N/A'),
                telefone=qualification.get('telefone', 'N/A'),
                email=qualification.get('email', 'N/A'),
                interesse=qualification.get('interesse', 'N/A')
            )
        else:
            missing_info = []
            if not qualification.get('nome'): missing_info.append('nome completo')
            if not qualification.get('telefone'): missing_info.append('telefone')
            if not qualification.get('email'): missing_info.append('e-mail corporativo')
            if not qualification.get('interesse'): missing_info.append('descrição do interesse/necessidade')
            
            return f"""Você é um consultor especializada da Scoras Digital, focado em soluções empresariais de IA.

INSTRUÇÕES CRÍTICAS:
- NÃO FORNEÇA PREÇOS OU VALORES até o lead estar qualificado
- Use as informações do contexto RAG para apresentar serviços
- Seja consultivo e profissional
- SEMPRE solicite as informações faltantes antes de apresentar preços

LEAD NÃO QUALIFICADO ❌
Informações faltantes: {', '.join(missing_info)}

PRIMEIRO colete todas as informações necessárias, DEPOIS apresente preços."""
    
    return "Você é um assistente da Scoras. Seja útil e profissional."

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "model": DEEPSEEK_MODEL}

@app.post("/chat-simple", response_model=ChatResponse)
async def chat_simple(chat_request: ChatMessage):
    """Endpoint principal de chat com RAG híbrido e qualificação"""
    
    # Gerar user_id se não fornecido
    user_id = chat_request.user_id or f"user_{hash(chat_request.message[:50])}"
    
    # Reset conversa se solicitado
    if chat_request.reset:
        conversations.pop(user_id, None)
        lead_qualifications.pop(user_id, None)
        return ChatResponse(
            user_id=user_id,
            response="Conversa resetada! Como posso ajudá-lo?",
            lead_type="UNKNOWN",
            is_qualified=False,
            qualification_status={}
        )
    
    print(f"🔄 Nova mensagem recebida: {chat_request.message[:50]}...")
    
    # Inicializar conversa se não existir
    if user_id not in conversations:
        conversations[user_id] = []
    
    # Classificar tipo de lead
    lead_type = classify_lead_type(chat_request.message)
    print(f"🎓 Lead classificado como: {lead_type}")
    
    # Verificar qualificação (apenas para Digital)
    qualification = {}
    if lead_type == "DIGITAL":
        qualification = check_lead_qualification(user_id, chat_request.message)
        print(f"📋 Status qualificação: {qualification['is_qualified']}")
    
    # Extrair keywords
    keywords = get_keywords_from_message(chat_request.message)
    print(f"🔍 Keywords encontradas: {keywords}")
    
    # Determinar se deve usar RAG
    use_rag = should_use_rag(keywords, lead_type)
    
    # Preparar contexto RAG
    rag_context = ""
    if use_rag:
        print(f"🔍 Buscando informações RAG HÍBRIDA para: {chat_request.message[:50]}...")
        rag_results = search_scoras_hybrid(chat_request.message, limit=2)
        
        if rag_results:
            print(f"📚 Busca híbrida retornou {len(rag_results)} resultados")
            for i, result in enumerate(rag_results, 1):
                print(f"  📄 {result['title']} (score: {result['score']:.3f}, method: {result['method']})")
            
            # Filtrar preços se lead Digital não qualificado
            if lead_type == "DIGITAL" and not qualification.get('is_qualified'):
                filtered_results = []
                for result in rag_results:
                    # Não incluir resultados de preços se não qualificado
                    if 'preço' not in result['title'].lower() and 'investimento' not in result['title'].lower():
                        filtered_results.append(result)
                    else:
                        print(f"🚫 Bloqueando preços - lead não qualificado")
                rag_results = filtered_results
            
            rag_context = "\n\n".join([
                f"**{result['title']}**\n{result['content']}"
                for result in rag_results
            ])
            print(f"✅ RAG Context HÍBRIDO adicionado: {len(rag_context)} caracteres")
        else:
            print("ℹ️ Nenhum resultado RAG encontrado")
    else:
        print("ℹ️ Nenhuma keyword específica encontrada - não usando RAG")
    
    # Preparar prompt
    system_prompt = get_system_prompt(lead_type, qualification)
    
    user_prompt = f"""Mensagem do usuário: {chat_request.message}

{"CONTEXTO RAG:" if rag_context else "SEM CONTEXTO RAG"}
{rag_context}

Responda de forma útil e precisa."""
    
    # Adicionar mensagem ao histórico
    conversations[user_id].append({"role": "user", "content": chat_request.message})
    
    # Preparar mensagens para o LLM
    messages = [
        {"role": "system", "content": system_prompt}
    ]
    
    # Adicionar histórico recente (últimas 4 mensagens)
    recent_history = conversations[user_id][-4:]
    for msg in recent_history[:-1]:  # Não incluir a última (já foi adicionada)
        messages.append(msg)
    
    messages.append({"role": "user", "content": user_prompt})
    
    try:
        print(f"🤖 Chamando LLM com prompt de {len(system_prompt + user_prompt)} caracteres...")
        
        # Chamar Azure DeepSeek V3
        response = client.complete(
            messages=messages,
            model=DEEPSEEK_MODEL,
            temperature=0.3,
            max_tokens=1000
        )
        
        assistant_response = response.choices[0].message.content
        print(f"✅ LLM respondeu: {assistant_response[:50]}...")
        
        # Adicionar resposta ao histórico
        conversations[user_id].append({"role": "assistant", "content": assistant_response})
        
        # Limitar histórico (últimas 10 mensagens)
        if len(conversations[user_id]) > 10:
            conversations[user_id] = conversations[user_id][-10:]
        
        return ChatResponse(
            user_id=user_id,
            response=assistant_response,
            lead_type=lead_type,
            is_qualified=qualification.get('is_qualified', lead_type == "ACADEMY"),
            qualification_status=qualification
        )
        
    except Exception as e:
        print(f"❌ Erro no LLM: {str(e)}")
        error_response = "Desculpe, estou enfrentando dificuldades técnicas. Tente novamente em alguns momentos."
        
        return ChatResponse(
            user_id=user_id,
            response=error_response,
            lead_type=lead_type,
            is_qualified=False,
            qualification_status=qualification
        )

@app.post("/reset-conversation")
async def reset_conversation(user_data: dict):
    """Reset conversa específica"""
    user_id = user_data.get("user_id")
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id é obrigatório")
    
    conversations.pop(user_id, None)
    lead_qualifications.pop(user_id, None)
    return {"message": f"Conversa {user_id} resetada com sucesso"}

@app.get("/qualification-status/{user_id}")
async def get_qualification_status(user_id: str):
    """Consultar status de qualificação do lead"""
    qualification = lead_qualifications.get(user_id, {})
    return {
        "user_id": user_id,
        "qualification": qualification,
        "is_qualified": qualification.get('is_qualified', False)
    }

if __name__ == "__main__":
    print("🚀 Iniciando Scoras Chatbot API - Versão Completa")
    print("📍 Endpoint: http://localhost:8000/chat-simple")
    print("🎓 Academy: RAG híbrido para cursos")
    print("💼 Digital: RAG híbrido + qualificação para preços")
    
    uvicorn.run(app, host="0.0.0.0", port=8000) 