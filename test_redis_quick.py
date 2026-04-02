#!/usr/bin/env python3
"""
Teste rápido APENAS do Azure Redis Cache
Execute após obter a chave de acesso: python test_redis_quick.py
"""

import os
from redis import Redis
from dotenv import load_dotenv

def test_redis_only():
    """Testa apenas a conexão Redis"""
    print("🔄 Testando Azure Redis Cache: andersonaitest1...")
    
    load_dotenv()
    
    # Verifica se tem a chave real
    password = os.getenv('REDIS_PASSWORD')
    if not password or password == 'your-redis-primary-key-here':
        print("❌ REDIS_PASSWORD não configurado!")
        print("💡 Edite o arquivo .env e substitua 'your-redis-primary-key-here' pela chave real")
        return
    
    print(f"   Host: andersonaitest1.redis.cache.windows.net:6380")
    print(f"   SSL: True")
    print(f"   Password: {password[:8]}...")
    
    try:
        # Teste via URL (método recomendado)
        redis_url = f"rediss://:{password}@andersonaitest1.redis.cache.windows.net:6380/0"
        client = Redis.from_url(redis_url, decode_responses=True)
        
        print("🔄 Tentando ping...")
        result = client.ping()
        
        if result:
            print("✅ SUCESSO! Redis conectado!")
            
            # Teste básico de escrita/leitura
            print("🔄 Teste de escrita/leitura...")
            client.set("test_scoras", "funcionando", ex=30)
            value = client.get("test_scoras")
            
            if value == "funcionando":
                print("✅ PERFEITO! Escrita e leitura funcionando!")
                client.delete("test_scoras")
            else:
                print("⚠️ Ping OK, mas leitura falhou")
                
        else:
            print("❌ Ping falhou")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        
        if "Name or service not known" in str(e):
            print("💡 DNS não encontrado - Redis ainda pode estar sendo criado")
        elif "Authentication" in str(e):
            print("💡 Problema de autenticação - verifique a chave")
        elif "Connection refused" in str(e):
            print("💡 Conexão recusada - verifique se acesso público está habilitado")

if __name__ == "__main__":
    test_redis_only() 