#!/usr/bin/env python3
"""
Script de teste para o sistema completo Scoras AI Agent + Admin Dashboard
"""

import requests
import json
import time
import asyncio
import redis
from datetime import datetime

# Configurações
CHAT_API_URL = "http://localhost:8000"
ADMIN_API_URL = "http://localhost:8001"
REDIS_URL = "redis://localhost:6379/0"

def test_connection(url, service_name):
    """Testar conexão com um serviço"""
    try:
        response = requests.get(f"{url}/health" if service_name == "Chat API" else f"{url}/admin/analytics/overview", timeout=5)
        if response.status_code == 200:
            print(f"✅ {service_name}: Conectado")
            return True
        else:
            print(f"❌ {service_name}: Status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ {service_name}: Erro de conexão - {e}")
        return False

def test_redis_connection():
    """Testar conexão com Redis"""
    try:
        r = redis.from_url(REDIS_URL, decode_responses=True)
        r.ping()
        print("✅ Redis: Conectado")
        return True
    except Exception as e:
        print(f"❌ Redis: Erro de conexão - {e}")
        return False

def create_test_conversation():
    """Criar uma conversa de teste"""
    print("\n🧪 Criando conversa de teste...")
    
    test_messages = [
        "Olá, tenho interesse em cursos de IA",
        "Meu nome é João Silva, telefone (11) 99999-9999, email joao@teste.com",
        "Qual o preço do curso de Python?"
    ]
    
    user_id = f"test-{int(time.time())}"
    
    for i, message in enumerate(test_messages):
        try:
            response = requests.post(
                f"{CHAT_API_URL}/chat-simple",
                json={
                    "user_id": user_id,
                    "message": message
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"  📝 Mensagem {i+1}: {message[:30]}...")
                print(f"  🤖 Resposta: {data['response'][:50]}...")
                time.sleep(1)
            else:
                print(f"  ❌ Erro na mensagem {i+1}: Status {response.status_code}")
                return None
                
        except Exception as e:
            print(f"  ❌ Erro na mensagem {i+1}: {e}")
            return None
    
    print(f"✅ Conversa de teste criada: {user_id}")
    return user_id

def test_admin_endpoints():
    """Testar endpoints do dashboard administrativo"""
    print("\n🔧 Testando endpoints administrativos...")
    
    endpoints = [
        ("/admin/analytics/overview", "Analytics Overview"),
        ("/admin/conversations?page=1&per_page=10", "Lista de Conversas"),
        ("/admin/redis/info", "Informações Redis")
    ]
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"{ADMIN_API_URL}{endpoint}", timeout=10)
            if response.status_code == 200:
                print(f"  ✅ {name}: OK")
            else:
                print(f"  ❌ {name}: Status {response.status_code}")
        except Exception as e:
            print(f"  ❌ {name}: Erro - {e}")

def test_redis_console():
    """Testar console Redis"""
    print("\n🔍 Testando console Redis...")
    
    test_commands = [
        {"command": "DBSIZE", "args": []},
        {"command": "KEYS", "args": ["conversation:*"]},
        {"command": "INFO", "args": ["memory"]}
    ]
    
    for cmd_data in test_commands:
        try:
            response = requests.post(
                f"{ADMIN_API_URL}/admin/redis/query",
                json=cmd_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"  ✅ {cmd_data['command']}: {result['type']}")
            else:
                print(f"  ❌ {cmd_data['command']}: Status {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ {cmd_data['command']}: Erro - {e}")

def test_conversation_details(user_id):
    """Testar visualização de detalhes da conversa"""
    if not user_id:
        return
    
    print(f"\n👁️ Testando detalhes da conversa {user_id}...")
    
    try:
        response = requests.get(f"{ADMIN_API_URL}/admin/conversation/{user_id}", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Conversa carregada: {len(data['messages'])} mensagens")
            print(f"  📊 Qualificação: {len(data['qualification_data'])} campos")
            print(f"  🗂️ Metadados: {len(data['metadata'])} campos")
        else:
            print(f"  ❌ Erro ao carregar conversa: Status {response.status_code}")
            
    except Exception as e:
        print(f"  ❌ Erro ao carregar conversa: {e}")

def test_performance():
    """Testar performance básica"""
    print("\n⚡ Testando performance...")
    
    start_time = time.time()
    
    try:
        response = requests.get(f"{ADMIN_API_URL}/admin/analytics/overview", timeout=5)
        end_time = time.time()
        
        if response.status_code == 200:
            duration = (end_time - start_time) * 1000
            print(f"  ✅ Analytics: {duration:.0f}ms")
            
            if duration < 1000:
                print("  🚀 Performance: Excelente")
            elif duration < 3000:
                print("  ⚡ Performance: Boa")
            else:
                print("  ⚠️ Performance: Lenta")
        else:
            print("  ❌ Erro no teste de performance")
            
    except Exception as e:
        print(f"  ❌ Erro no teste de performance: {e}")

def main():
    """Executar todos os testes"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                    🧪 TESTE DO SISTEMA                       ║
║              Scoras AI Agent + Admin Dashboard               ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    print("🔍 Verificando conexões...")
    
    # Testar conexões básicas
    chat_ok = test_connection(CHAT_API_URL, "Chat API")
    admin_ok = test_connection(ADMIN_API_URL, "Admin Dashboard")
    redis_ok = test_redis_connection()
    
    if not all([chat_ok, admin_ok, redis_ok]):
        print("\n❌ Nem todos os serviços estão funcionando. Verifique a configuração.")
        print("\n💡 Para iniciar os serviços, execute:")
        print("   python start_admin.py")
        return
    
    print("\n✅ Todos os serviços estão funcionando!")
    
    # Executar testes funcionais
    test_user_id = create_test_conversation()
    test_admin_endpoints()
    test_redis_console()
    test_conversation_details(test_user_id)
    test_performance()
    
    print("\n" + "="*60)
    print("🎉 TESTE CONCLUÍDO!")
    print("\n📱 URLs para acesso manual:")
    print(f"  • Chat Interface: {CHAT_API_URL}")
    print(f"  • Admin Dashboard: {ADMIN_API_URL}/admin")
    print(f"  • API Documentation: {CHAT_API_URL}/docs")
    
    print("\n💡 Próximos passos:")
    print("  1. Acesse o Admin Dashboard no navegador")
    print("  2. Teste as funcionalidades de monitoramento")
    print("  3. Execute queries Redis no console")
    print("  4. Monitore métricas em tempo real")
    
    if test_user_id:
        print(f"\n🔍 ID da conversa de teste criada: {test_user_id}")
        print("   Use este ID para testar a visualização no dashboard")

if __name__ == "__main__":
    main() 