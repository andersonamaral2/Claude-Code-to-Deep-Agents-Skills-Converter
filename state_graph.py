import os
from typing import Dict, Any
from redis import Redis
from langgraph.checkpoint.redis import RedisSaver
from langgraph.graph import StateGraph, START, END
# from langgraph.prebuilt import tools_condition  # Removido - não usado

# Importações dos módulos locais
from models import ChatState, LeadInfo, LeadType
from azure_llm_config import llm, ACADEMY_SYSTEM_PROMPT, DIGITAL_SYSTEM_PROMPT
from vector_search import create_tool_node

# Configuração do Redis (Azure Cache for Redis)
def create_redis_client():
    """Cria cliente Redis configurado para Azure Cache for Redis."""
    redis_url = os.getenv("REDIS_URL")
    
    if redis_url:
        # Usar URL completa (recomendado para Azure Redis)
        return Redis.from_url(redis_url, decode_responses=False)
    else:
        # Configuração manual para Azure Redis
        redis_host = os.getenv("REDIS_HOST", "cache-redis.redis.cache.windows.net")
        redis_port = int(os.getenv("REDIS_PORT", "6380"))
        redis_password = os.getenv("REDIS_PASSWORD")
        redis_ssl = os.getenv("REDIS_SSL", "true").lower() == "true"
        
        return Redis(
            host=redis_host,
            port=redis_port,
            password=redis_password,
            ssl=redis_ssl,
            ssl_cert_reqs=None,  # Para Azure Redis
            decode_responses=False
        )

# Conecta ao Redis
redis_client = create_redis_client()

try:
    redis_client.ping()
    print("✅ Redis (Azure Cache) conectado com sucesso!")
except Exception as e:
    print(f"❌ Erro na conexão Redis: {e}")
    print("💡 Verifique as credenciais do Azure Redis Cache no arquivo .env")

# Inicializa o checkpointer RedisSaver
redis_saver = RedisSaver(redis_client=redis_client)
redis_saver.setup()

# Função nó: Classificar tipo de lead e configurar prompt de sistema inicial
def classify_lead(state: Dict) -> Dict:
    """Classifica o tipo de lead e configura o prompt de sistema apropriado."""
    # Assume que a primeira mensagem humana indica a intenção do usuário
    messages = state.get("messages", [])
    if not messages:
        return state
    
    user_message = messages[-1][1] if isinstance(messages[-1], tuple) else messages[-1].get("content", "")
    content_low = user_message.lower()
    
    # Heurística simples de classificação por palavras-chave
    if any(word in content_low for word in ["curso", "academy", "academia", "treinamento", "ensino", "aprender"]):
        lead_type = LeadType.ACADEMY
        # Insere mensagem de sistema do perfil Academy no histórico
        messages.insert(0, ("system", ACADEMY_SYSTEM_PROMPT))
        state_lead_intent = "Interesse em cursos"
    else:
        lead_type = LeadType.DIGITAL
        messages.insert(0, ("system", DIGITAL_SYSTEM_PROMPT))
        state_lead_intent = "Interesse em soluções empresariais"
    
    # Cria objeto LeadInfo parcial
    state["lead_info"] = {
        "intent": state_lead_intent,
        "name": "", 
        "email": "user@placeholder.com", 
        "phone": "",
        "lead_type": lead_type.value
    }
    state["messages"] = messages
    return state

# Função nó: Chamar o modelo de linguagem para gerar próxima resposta
def call_llm(state: Dict) -> Dict:
    """Chama o modelo de linguagem para gerar a próxima resposta."""
    try:
        # Prepara mensagens no formato esperado
        messages = []
        for msg in state.get("messages", []):
            if isinstance(msg, tuple):
                role, content = msg
                messages.append({"role": role, "content": content})
            else:
                role = msg.get("role", "user")
                content = msg.get("content", str(msg))
                messages.append({"role": role, "content": content})
        
        # Chama o LLM usando o wrapper
        assistant_reply = llm.generate(messages, max_tokens=512, temperature=0.7)
        
        # Adiciona resposta do assistente ao histórico
        state["messages"].append(("assistant", assistant_reply))
        
    except Exception as e:
        error_msg = f"Desculpe, ocorreu um erro técnico. Tente novamente em alguns instantes."
        state["messages"].append(("assistant", error_msg))
        print(f"Erro no LLM: {e}")
    
    return state

# Função para decidir se deve usar ferramentas
def should_use_tools(state: Dict) -> str:
    """Decide se deve usar ferramentas de busca ou continuar o fluxo normal."""
    messages = state.get("messages", [])
    if not messages:
        return END
        
    # Verifica a mensagem do usuário (não a do assistente)
    user_message = None
    for msg in reversed(messages):
        if isinstance(msg, tuple) and len(msg) >= 2:
            role, content = msg[0], msg[1]
            if role in ("human", "user"):
                user_message = content.lower()
                break
    
    if not user_message:
        return END
        
    # Verifica se é sobre lead da academy (precisa de informações dos cursos)
    lead_info = state.get("lead_info", {})
    if isinstance(lead_info, dict) and lead_info.get("lead_type") == "academy":
        # Keywords que indicam necessidade de busca detalhada sobre cursos
        course_indicators = [
            "módulos", "módulo", "conteúdo", "programa", "ementa", "curriculo",
            "langgraph", "rag", "pydantic", "routing", "cases", "python",
            "curso", "cursos", "aulas", "matérias", "materia", "disciplinas",
            "o que", "quais", "como", "onde", "quando", "qual é", "quantos",
            "detalhe", "detalhes", "específico", "especifico"
        ]
        
        if any(indicator in user_message for indicator in course_indicators):
            print(f"🔍 Detectou necessidade de busca RAG para: {user_message[:50]}...")
            return "tools"
    
    return END

# Instancia o grafo de estado do LangGraph
graph = StateGraph(dict)  # Usar dict em vez de ChatState

# Adiciona nós ao grafo
graph.add_node("classify_lead", classify_lead)
graph.add_node("chatbot", call_llm)
graph.add_node("tools", create_tool_node())

# Define fluxo: início -> classificação -> chatbot
graph.add_edge(START, "classify_lead")
graph.add_edge("classify_lead", "chatbot")

# Adiciona edges condicionais para ferramentas
graph.add_conditional_edges("chatbot", should_use_tools)
graph.add_edge("tools", "chatbot")

# Compila o grafo
def create_compiled_graph():
    """Cria e retorna o grafo compilado com checkpointer."""
    return graph.compile(checkpointer=redis_saver)
