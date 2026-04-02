#!/usr/bin/env python3
"""
API simplificada para chat com RAG integrado
Versão focada apenas no RAG da Scoras Academy com Busca Híbrida
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import ChatRequest, SupportedLanguage
from azure_llm_config import llm, ACADEMY_SYSTEM_PROMPT, DIGITAL_SYSTEM_PROMPT
from hybrid_search import search_scoras_hybrid

# Cria a aplicação FastAPI
app = FastAPI(
    title="Scoras Chatbot API - RAG Hybrid Version",
    description="API para o chatbot da Scoras Academy com RAG híbrido (BM25 + Semântica)",
    version="1.0.0-rag-hybrid"
)

# Configura CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Endpoint de health check."""
    return {"message": "Scoras Chatbot API - RAG Hybrid Version funcionando!", "status": "online"}

@app.get("/health")
async def health_check():
    """Endpoint de verificação de saúde do sistema."""
    try:
        # Teste básico de conectividade
        from qdrant_client import QdrantClient
        client = QdrantClient(url="http://localhost:6333")
        collections = client.get_collections()
        return {"status": "healthy", "qdrant": "connected", "collections": len(collections.collections)}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.post("/chat-simple")
async def chat_simple_rag(req: ChatRequest):
    """Endpoint de chat com RAG híbrido integrado."""
    try:
        print(f"🔄 Nova mensagem recebida: {req.message[:50]}...")
        
        # Classifica o tipo de lead
        content_low = req.message.lower()
        if any(word in content_low for word in ["curso", "academy", "academia", "treinamento", "ensino", "aprender"]):
            lead_type = "academy"
            system_prompt = ACADEMY_SYSTEM_PROMPT
            print(f"🎓 Lead classificado como: ACADEMY")
        else:
            lead_type = "digital"
            system_prompt = DIGITAL_SYSTEM_PROMPT
            print(f"💼 Lead classificado como: DIGITAL")
        
        # Para leads da Academy, verifica se precisa de busca RAG
        rag_context = ""
        used_rag = False
        
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
            
            matching_keywords = [ind for ind in course_indicators if ind in content_low]
            print(f"🔍 Keywords encontradas: {matching_keywords}")
            
            if matching_keywords:
                print(f"🔍 Buscando informações RAG HÍBRIDA para: {req.message[:50]}...")
                try:
                    rag_results = search_scoras_hybrid(req.message, limit=2)
                    print(f"📚 Busca híbrida retornou {len(rag_results)} resultados")
                    
                    if rag_results:
                        rag_snippets = []
                        for result in rag_results:
                            title = result.get("title", "")
                            content = result.get("content", "")
                            method = result.get("method", "unknown")
                            score = result.get("score", 0)
                            
                            if title and content:
                                print(f"  📄 {title} (score: {score:.3f}, method: {method})")
                                rag_snippets.append(f"**{title}**\n{content}")
                        
                        if rag_snippets:
                            rag_context = (
                                "\n\n**INFORMAÇÕES ESPECÍFICAS DOS CURSOS (Use APENAS estas informações - NÃO invente nada):**\n" + 
                                "\n\n".join(rag_snippets) +
                                "\n\n**CRÍTICO**: Você DEVE usar APENAS as informações acima. NÃO invente módulos, conteúdos ou detalhes que não estejam listados. Se não houver informação suficiente, mencione que mais detalhes estão disponíveis no site https://scorasacademy.com.br ou por contato via admin@scoras.com.br"
                            )
                            used_rag = True
                            print(f"✅ RAG Context HÍBRIDO adicionado: {len(rag_context)} caracteres")
                        else:
                            print("❌ RAG não retornou conteúdo útil")
                    else:
                        print("❌ RAG não encontrou resultados")
                except Exception as e:
                    print(f"❌ Erro na busca RAG híbrida: {e}")
            else:
                print("ℹ️ Nenhuma keyword específica encontrada - não usando RAG")
        
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
        
        print(f"🤖 Chamando LLM com prompt de {len(full_system_prompt)} caracteres...")
        
        # Chama o LLM
        temp = 0.9 if req.language != SupportedLanguage.PORTUGUESE else 0.7
        response = llm.generate(messages, max_tokens=512, temperature=temp)
        
        print(f"✅ LLM respondeu: {response[:50]}...")
        
        return {
            "user_id": req.user_id or "simple_chat",
            "response": response,
            "lead_type": lead_type,
            "language": req.language.value,
            "used_rag": used_rag,
            "rag_context_length": len(rag_context) if rag_context else 0
        }
        
    except Exception as e:
        print(f"❌ Erro no chat: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Erro ao processar conversa: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    print("🚀 Iniciando Scoras Chatbot API - RAG Hybrid Version")
    print("📍 Endpoint: http://localhost:8000/chat-simple")
    print("🔍 RAG HÍBRIDO integrado para Scoras Academy (BM25 + Semântica)")
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) 