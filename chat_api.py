import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import ChatRequest, ChatState, LeadType, SupportedLanguage
from state_graph import create_compiled_graph, redis_saver
from azure_llm_config import llm, ACADEMY_SYSTEM_PROMPT, DIGITAL_SYSTEM_PROMPT
from rag_setup import search_scoras_content

# Cria a aplicação FastAPI
app = FastAPI(
    title="Scoras Chatbot API",
    description="API para o chatbot da Scoras Academy e Digital",
    version="1.0.0"
)

# Configura CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Compila o grafo uma vez na inicialização
compiled_graph = create_compiled_graph()

@app.get("/")
async def root():
    """Endpoint de health check."""
    return {"message": "Scoras Chatbot API está funcionando!", "status": "online"}

@app.get("/health")
async def health_check():
    """Endpoint de verificação de saúde do sistema."""
    try:
        # Testa conexão com Redis
        from state_graph import redis_client
        redis_client.ping()
        return {"status": "healthy", "redis": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.post("/chat-simple")
async def chat_simple(req: ChatRequest):
    """Endpoint simplificado de chat com RAG integrado."""
    try:
        # Classifica o tipo de lead
        content_low = req.message.lower()
        if any(word in content_low for word in ["curso", "academy", "academia", "treinamento", "ensino", "aprender"]):
            lead_type = "academy"
            system_prompt = ACADEMY_SYSTEM_PROMPT
        else:
            lead_type = "digital"
            system_prompt = DIGITAL_SYSTEM_PROMPT
        
        # Para leads da Academy, verifica se precisa de busca RAG
        rag_context = ""
        if lead_type == "academy":
            # Keywords que indicam necessidade de informações específicas sobre cursos
            course_indicators = [
                "módulos", "módulo", "conteúdo", "programa", "ementa", "curriculo",
                "langgraph", "rag", "pydantic", "routing", "cases", "python",
                "aulas", "matérias", "materia", "disciplinas", "smalllanguage",
                "o que", "quais", "como", "onde", "quando", "qual é", "quantos",
                "detalhe", "detalhes", "específico", "especifico", "tem",
                "ensina", "aprende", "consta", "inclui", "aborda"
            ]
            
            if any(indicator in content_low for indicator in course_indicators):
                print(f"🔍 Buscando informações RAG para: {req.message[:50]}...")
                try:
                    rag_results = search_scoras_content(req.message, limit=2)
                    if rag_results:
                        rag_snippets = []
                        for result in rag_results:
                            title = result.get("title", "")
                            content = result.get("content", "")
                            if title and content:
                                rag_snippets.append(f"**{title}**\n{content}")
                        
                        if rag_snippets:
                            rag_context = "\n\n**INFORMAÇÕES ESPECÍFICAS DOS CURSOS:**\n" + "\n\n".join(rag_snippets)
                            print(f"✅ RAG Context adicionado: {len(rag_context)} caracteres")
                except Exception as e:
                    print(f"❌ Erro na busca RAG: {e}")
        
        # Adiciona instruções específicas de idioma
        language_instructions = ""
        if req.language == SupportedLanguage.ENGLISH:
            language_instructions = "\n\n**CRITICAL: RESPOND ONLY IN ENGLISH**\nYou MUST respond exclusively in English. Never use Portuguese, Chinese, or any other language. This is mandatory.\nUser language preference: ENGLISH"
        elif req.language == SupportedLanguage.SPANISH:
            language_instructions = "\n\n**CRÍTICO: RESPONDE SOLO EN ESPAÑOL**\nDEBES responder exclusivamente en español. Nunca uses portugués, chino u otro idioma. Esto es obligatorio.\nPreferencia de idioma del usuario: ESPAÑOL"
        else:
            language_instructions = "\n\n**CRÍTICO: RESPONDA APENAS EM PORTUGUÊS DO BRASIL**\nVocê DEVE responder exclusivamente em português do Brasil. Nunca use chinês, inglês ou outros idiomas.\nPreferência de idioma do usuário: PORTUGUÊS BRASILEIRO"
        
        # Combina prompt do sistema com RAG context e instruções de idioma
        full_system_prompt = language_instructions + "\n\n" + system_prompt + rag_context
        
        # Prepara mensagens
        messages = [
            {"role": "system", "content": full_system_prompt},
            {"role": "user", "content": req.message}
        ]
        
        # Chama o LLM (temperatura mais alta para inglês/espanhol para quebrar padrões)
        temp = 0.9 if req.language != SupportedLanguage.PORTUGUESE else 0.7
        response = llm.generate(messages, max_tokens=512, temperature=temp)
        
        return {
            "user_id": req.user_id or "simple_chat",
            "response": response,
            "lead_type": lead_type,
            "language": req.language.value,
            "used_rag": bool(rag_context)  # Indica se usou RAG
        }
        
    except Exception as e:
        print(f"❌ Erro no chat simples: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Erro ao processar conversa: {str(e)}"
        )

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    """Endpoint principal de conversa."""
    try:
        # Define thread_id: usa user_id se fornecido, caso contrário gera um novo
        thread_id = req.user_id if req.user_id else os.urandom(8).hex()
        
        if req.reset:
            # Limpa histórico anterior se reset solicitado
            try:
                redis_saver.clear_state(thread_id=thread_id)
                print(f"✅ Histórico limpo para thread: {thread_id}")
            except Exception as e:
                print(f"⚠️ Erro ao limpar histórico: {e}")
        
        # Monta estado inicial para o grafo (como dict para compatibilidade)
        initial_state = {
            "messages": [("human", req.message)],
            "lead_info": None
        }
        
        # Configuração para o grafo
        config = {"configurable": {"thread_id": thread_id}}
        
        # Executa o grafo com o estado inicial e thread_id para persistência
        final_state = compiled_graph.invoke(initial_state, config=config)
        
        # Extrai a última mensagem do assistente do estado final
        resposta = ""
        messages = final_state.get("messages", [])
        
        for msg in reversed(messages):
            if isinstance(msg, tuple) and len(msg) >= 2:
                role, content = msg[0], msg[1]
                if role in ("assistant", "ai"):
                    resposta = content
                    break
        
        if not resposta:
            resposta = "Desculpe, não consegui processar sua mensagem. Tente novamente."
        
        # Extrai lead_type se disponível
        lead_info = final_state.get("lead_info")
        lead_type = None
        if lead_info and hasattr(lead_info, 'lead_type'):
            lead_type = lead_info.lead_type.value
        elif isinstance(lead_info, dict) and 'lead_type' in lead_info:
            lead_type = lead_info['lead_type']
        
        return {
            "user_id": thread_id,
            "response": resposta,
            "lead_type": lead_type
        }
        
    except Exception as e:
        print(f"❌ Erro no endpoint de chat: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Erro ao processar conversa: {str(e)}"
        )

@app.post("/reset-conversation")
async def reset_conversation(user_id: str):
    """Endpoint para resetar uma conversa específica."""
    try:
        redis_saver.clear_state(thread_id=user_id)
        return {"message": f"Conversa resetada para user_id: {user_id}"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao resetar conversa: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
