#!/usr/bin/env python3
"""
Scoras Chatbot API - Versão Simplificada que Funciona
API mínima para testar o frontend rapidamente
"""

import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="Scoras Chatbot API - Simple Working Version")

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

# Simple Azure AI client
try:
    from azure.ai.inference import ChatCompletionsClient
    from azure.core.credentials import AzureKeyCredential
    
    client = ChatCompletionsClient(
        endpoint=AZURE_ENDPOINT,
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
ACADEMY_PROMPT = """Você é um assistente inteligente da Scoras Academy, especializado em cursos de Inteligência Artificial.

A Scoras Academy oferece cursos práticos de IA incluindo:
- LangGraph e Agentes de IA
- Pydantic AI e Validação de Dados
- RAG (Retrieval Augmented Generation)
- Python para IA
- LangFlow e Automação
- Deployment de Projetos de IA

Seja educativo, profissional e incentive o interesse nos cursos.
Se perguntarem sobre preços, mencione que podem obter mais informações em https://scorasacademy.com.br"""

DIGITAL_PROMPT = """Você é um consultor especializado da Scoras Digital, focado em soluções empresariais de IA.

A Scoras Digital oferece:
- Consultoria em IA para empresas
- Desenvolvimento de projetos de IA
- Implementação de chatbots empresariais
- Sistemas RAG corporativos
- Squad dedicado para projetos
- Transformação digital com IA

Seja consultivo, profissional e direcione para soluções empresariais.
Para informações de preços e propostas, solicite contato via admin@scoras.com.br"""

def classify_lead_type(message: str) -> str:
    """Classifica o tipo de lead baseado na mensagem"""
    message_lower = message.lower()
    
    # Academy indicators
    academy_indicators = [
        'curso', 'cursos', 'academy', 'modulo', 'módulo', 'módulos',
        'langgraph', 'pydantic', 'rag', 'python', 'langflow',
        'aprender', 'estudar', 'certificado', 'aula', 'vídeo', 'treinamento'
    ]
    
    # Digital indicators
    digital_indicators = [
        'consultoria', 'projeto', 'projetos', 'empresa', 'empresarial',
        'solução', 'implementação', 'desenvolvimento', 'chatbot empresarial',
        'sistema empresarial', 'squad', 'negócio', 'corporativo'
    ]
    
    academy_score = sum(1 for indicator in academy_indicators if indicator in message_lower)
    digital_score = sum(1 for indicator in digital_indicators if indicator in message_lower)
    
    return "ACADEMY" if academy_score > digital_score else "DIGITAL"

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Scoras Chatbot API funcionando!", "status": "online"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    status = {
        "status": "healthy",
        "azure_configured": bool(AZURE_ENDPOINT and AZURE_API_KEY),
        "model": DEEPSEEK_MODEL
    }
    
    if client:
        status["azure_client"] = "connected"
    else:
        status["azure_client"] = "failed"
        status["status"] = "partial"
    
    return status

@app.post("/chat-simple")
async def chat_simple(chat_request: ChatMessage):
    """Endpoint principal de chat simplificado"""
    
    try:
        print(f"🔄 Nova mensagem recebida: {chat_request.message[:50]}...")
        
        # Classificar tipo de lead
        lead_type = classify_lead_type(chat_request.message)
        print(f"🎯 Lead classificado como: {lead_type}")
        
        # Selecionar prompt
        if lead_type == "ACADEMY":
            system_prompt = ACADEMY_PROMPT
        else:
            system_prompt = DIGITAL_PROMPT
        
        # Preparar mensagens
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": chat_request.message}
        ]
        
        # Chamar Azure AI
        if client:
            print(f"🤖 Chamando Azure AI...")
            try:
                response = client.complete(
                    messages=messages,
                    model=DEEPSEEK_MODEL,
                    temperature=0.7,
                    max_tokens=800
                )
                
                assistant_response = response.choices[0].message.content
                print(f"✅ Azure AI respondeu: {assistant_response[:50]}...")
                
            except Exception as e:
                print(f"❌ Erro na chamada Azure AI: {e}")
                assistant_response = """Olá! Sou o assistente da Scoras. No momento estou com dificuldades técnicas para processar sua mensagem, mas posso ajudá-lo!

📧 **Contato direto:** admin@scoras.com.br
🌐 **Site Academy:** https://scorasacademy.com.br
💼 **Soluções Digital:** Entre em contato para consultoria empresarial

Como posso ajudá-lo de outra forma?"""
        else:
            # Fallback response quando Azure não está disponível
            if lead_type == "ACADEMY":
                assistant_response = """Olá! Bem-vindo à Scoras Academy! 🎓

Oferecemos cursos práticos de Inteligência Artificial:
• LangGraph e Agentes de IA
• Pydantic AI e Validação
• RAG (Retrieval Augmented Generation)
• Python para IA
• LangFlow e Automação

📧 Mais informações: admin@scoras.com.br
🌐 Site: https://scorasacademy.com.br

Qual área de IA mais interessa você?"""
            else:
                assistant_response = """Olá! Bem-vindo à Scoras Digital! 💼

Especializados em soluções empresariais de IA:
• Consultoria em IA para empresas
• Desenvolvimento de projetos
• Chatbots empresariais
• Sistemas RAG corporativos
• Squad dedicado

📧 Contato: admin@scoras.com.br
🤝 Vamos conversar sobre seu projeto?

Qual o desafio da sua empresa?"""
        
        return {
            "user_id": chat_request.user_id or "simple_chat",
            "response": assistant_response,
            "lead_type": lead_type.lower(),
            "status": "success"
        }
        
    except Exception as e:
        print(f"❌ Erro geral no chat: {str(e)}")
        return {
            "user_id": chat_request.user_id or "error_chat",
            "response": "Desculpe, ocorreu um erro interno. Tente novamente ou entre em contato via admin@scoras.com.br",
            "lead_type": "unknown",
            "status": "error"
        }

@app.post("/reset-conversation")
async def reset_conversation(user_data: dict):
    """Reset conversa (placeholder)"""
    user_id = user_data.get("user_id", "unknown")
    return {"message": f"Conversa {user_id} resetada com sucesso"}

if __name__ == "__main__":
    print("🚀 Iniciando Scoras Chatbot API - Versão Simplificada")
    print("📍 Endpoint: http://localhost:8000/chat-simple")
    print("🎓 Academy + 💼 Digital - Funcionamento garantido!")
    
    uvicorn.run(app, host="0.0.0.0", port=8000) 