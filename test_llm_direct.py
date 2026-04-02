#!/usr/bin/env python3
"""
Teste direto do LLM Azure DeepSeek (sem LangGraph)
"""

import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv()

def test_llm_direct():
    """Testa o LLM diretamente"""
    try:
        from azure_llm_config import llm, ACADEMY_SYSTEM_PROMPT, DIGITAL_SYSTEM_PROMPT
        
        print("🔄 Testando LLM Azure DeepSeek diretamente...")
        
        # Teste 1: Academy
        print("\n1️⃣ Teste Academy:")
        messages_academy = [
            {"role": "system", "content": ACADEMY_SYSTEM_PROMPT},
            {"role": "user", "content": "Olá, tenho interesse em cursos"}
        ]
        
        response_academy = llm.generate(messages_academy, max_tokens=256, temperature=0.7)
        print(f"✅ Resposta Academy: {response_academy[:200]}...")
        
        # Teste 2: Digital
        print("\n2️⃣ Teste Digital:")
        messages_digital = [
            {"role": "system", "content": DIGITAL_SYSTEM_PROMPT},
            {"role": "user", "content": "Preciso de soluções de IA para minha empresa"}
        ]
        
        response_digital = llm.generate(messages_digital, max_tokens=256, temperature=0.7)
        print(f"✅ Resposta Digital: {response_digital[:200]}...")
        
        print("\n🎉 LLM funcionando perfeitamente!")
        
    except Exception as e:
        print(f"❌ Erro no LLM: {e}")

if __name__ == "__main__":
    test_llm_direct() 