#!/usr/bin/env python3
"""
Teste Redis usando a connection string exata do Azure
"""
import redis

# Connection string do Azure (exata como fornecida)
connection_string = "andersonaitest1.redis.cache.windows.net:6380,password=***REMOVIDO***,ssl=True,abortConnect=False"

def test_with_azure_connection_string():
    """Testa usando a connection string nativa do Azure"""
    print("🔄 Testando com connection string do Azure...")
    print(f"   Connection: andersonaitest1.redis.cache.windows.net:6380")
    
    try:
        # Formato StackExchange.Redis para Python
        client = redis.Redis(
            host='andersonaitest1.redis.cache.windows.net',
            port=6380,
            password='***REMOVIDO***',
            ssl=True,
            ssl_cert_reqs=None,  # Importante para Azure
            socket_connect_timeout=10,
            socket_timeout=10,
            retry_on_timeout=True
        )
        
        print("🔄 Ping...")
        result = client.ping()
        print(f"✅ SUCESSO! Ping: {result}")
        
        # Teste básico
        client.set("azure_test", "funcionando!", ex=60)
        value = client.get("azure_test")
        print(f"✅ Escrita/Leitura: {value.decode() if value else 'Falhou'}")
        
    except redis.exceptions.ConnectionError as e:
        print(f"❌ Erro de conexão: {e}")
        if "timeout" in str(e).lower():
            print("💡 CAUSA: Acesso público desabilitado ou firewall")
            print("   SOLUÇÃO: Habilite 'Public network access' no Azure Portal")
        elif "authentication" in str(e).lower():
            print("💡 CAUSA: Problema de autenticação")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    test_with_azure_connection_string() 