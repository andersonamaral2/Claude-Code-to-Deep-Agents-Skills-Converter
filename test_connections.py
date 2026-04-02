#!/usr/bin/env python3
"""
Script de teste para verificar conexões com serviços Azure
Execute: python test_connections.py
"""

import os
import sys
from dotenv import load_dotenv

def test_redis_connection():
    """Testa conexão com Azure Redis Cache"""
    print("🔄 Testando conexão com Azure Redis Cache...")
    
    try:
        from redis import Redis
        
        redis_url = os.getenv('REDIS_URL')
        if redis_url:
            print(f"   Usando REDIS_URL: {redis_url[:20]}...")
            client = Redis.from_url(redis_url, decode_responses=False)
        else:
            host = os.getenv('REDIS_HOST', 'cache-redis.redis.cache.windows.net')
            port = int(os.getenv('REDIS_PORT', 6380))
            password = os.getenv('REDIS_PASSWORD')
            ssl = os.getenv('REDIS_SSL', 'true').lower() == 'true'
            
            print(f"   Host: {host}:{port} (SSL: {ssl})")
            client = Redis(
                host=host,
                port=port,
                password=password,
                ssl=ssl,
                ssl_cert_reqs=None
            )
        
        result = client.ping()
        if result:
            print("✅ Redis: Conexão bem-sucedida!")
            
            # Teste de escrita/leitura
            client.set("test_key", "test_value", ex=10)  # expira em 10 segundos
            value = client.get("test_key")
            if value:
                print("✅ Redis: Teste de escrita/leitura bem-sucedido!")
            client.delete("test_key")
        else:
            print("❌ Redis: Ping falhou")
            
    except ImportError:
        print("❌ Redis: Biblioteca 'redis' não encontrada. Execute: pip install redis")
    except Exception as e:
        print(f"❌ Redis: Erro na conexão - {e}")

def test_azure_ai_connection():
    """Testa conexão com Azure AI Inference"""
    print("\n🔄 Testando conexão com Azure AI Inference...")
    
    try:
        from azure.ai.inference import ChatCompletionsClient
        from azure.core.credentials import AzureKeyCredential
        
        endpoint = os.getenv('AZURE_ENDPOINT')
        api_key = os.getenv('AZURE_API_KEY')
        
        if not endpoint or not api_key:
            print("❌ Azure AI: Variáveis AZURE_ENDPOINT ou AZURE_API_KEY não configuradas")
            return
        
        print(f"   Endpoint: {endpoint}")
        client = ChatCompletionsClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(api_key),
            api_version=os.getenv('AZURE_API_VERSION', '2024-05-01-preview')
        )
        
        # Teste simples sem gastar tokens desnecessariamente
        print("✅ Azure AI: Cliente configurado com sucesso!")
        print("   (Para testar completamente, execute o chatbot)")
        
    except ImportError:
        print("❌ Azure AI: Biblioteca 'azure-ai-inference' não encontrada. Execute: pip install azure-ai-inference")
    except Exception as e:
        print(f"❌ Azure AI: Erro na configuração - {e}")

def test_qdrant_connection():
    """Testa conexão com Qdrant"""
    print("\n🔄 Testando conexão com Qdrant...")
    
    try:
        from qdrant_client import QdrantClient
        
        url = os.getenv('QDRANT_URL', 'http://localhost:6333')
        print(f"   URL: {url}")
        
        client = QdrantClient(url=url)
        collections = client.get_collections()
        
        print("✅ Qdrant: Conexão bem-sucedida!")
        print(f"   Collections encontradas: {len(collections.collections)}")
        
        # Verifica se a collection scoras_kb existe
        collection_names = [c.name for c in collections.collections]
        if 'scoras_kb' in collection_names:
            print("✅ Qdrant: Collection 'scoras_kb' encontrada!")
        else:
            print("⚠️  Qdrant: Collection 'scoras_kb' não encontrada (será criada quando necessário)")
            
    except ImportError:
        print("❌ Qdrant: Biblioteca 'qdrant-client' não encontrada. Execute: pip install qdrant-client")
    except Exception as e:
        print(f"❌ Qdrant: Erro na conexão - {e}")
        print("   💡 Certifique-se de que o Qdrant está rodando: docker run -p 6333:6333 qdrant/qdrant")

def main():
    """Função principal"""
    print("🧪 Teste de Conexões - Scoras Chatbot\n")
    
    # Carrega variáveis de ambiente
    env_file = '.env'
    if not os.path.exists(env_file):
        print("❌ Arquivo .env não encontrado!")
        print("   💡 Copie o arquivo .env.example para .env e configure suas variáveis")
        sys.exit(1)
    
    load_dotenv(env_file)
    print(f"✅ Arquivo {env_file} carregado\n")
    
    # Executa testes
    test_redis_connection()
    test_azure_ai_connection()
    test_qdrant_connection()
    
    print("\n🎯 Teste concluído!")
    print("   Se todos os serviços estão ✅, você pode executar: python chat_api.py")

if __name__ == "__main__":
    main() 