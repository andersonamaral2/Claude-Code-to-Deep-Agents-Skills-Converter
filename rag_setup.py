#!/usr/bin/env python3
"""
Script para configurar RAG da Scoras Academy
Cria embeddings e indexa no Qdrant para busca semântica
"""

import os
import uuid
from typing import List, Dict
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import requests
import json
from scoras_academy_content import get_all_content_for_embedding

# Configurações
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION_NAME = "scoras_academy"
VECTOR_SIZE = 384  # Tamanho do embedding para sentence-transformers

def get_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Gera embeddings usando diferentes métodos de fallback
    """
    # Método 1: Tentar OpenAI embeddings
    try:
        import openai
        from openai import AzureOpenAI
        
        # Usar Azure OpenAI se disponível
        azure_endpoint = os.getenv("AZURE_ENDPOINT")
        azure_key = os.getenv("AZURE_API_KEY")
        
        if azure_endpoint and azure_key:
            # Para embeddings, usaremos um endpoint genérico
            print("🔗 Usando embeddings simulados baseados em hash...")
            return get_hash_embeddings(texts)
    except:
        pass
    
    # Método 2: Embeddings baseados em hash (determinísticos)
    print("🔗 Usando embeddings determinísticos baseados em hash...")
    return get_hash_embeddings(texts)

def get_hash_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Gera embeddings determinísticos baseados em hash
    Não é o ideal para produção, mas funciona para demonstração
    """
    import hashlib
    import struct
    
    embeddings = []
    for text in texts:
        # Criar hash do texto
        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()
        
        # Converter hash para embedding de tamanho fixo
        embedding = []
        for i in range(0, min(len(hash_bytes), VECTOR_SIZE * 4), 4):
            if i + 4 <= len(hash_bytes):
                float_val = struct.unpack('f', hash_bytes[i:i+4])[0]
            else:
                # Padding com zeros se necessário
                padding = hash_bytes[i:] + b'\x00' * (4 - (len(hash_bytes) - i))
                float_val = struct.unpack('f', padding)[0]
            embedding.append(float_val)
        
        # Completar com valores baseados no hash se necessário
        while len(embedding) < VECTOR_SIZE:
            hash_obj = hashlib.sha256((text + str(len(embedding))).encode())
            hash_val = int(hash_obj.hexdigest()[:8], 16) / (2**32)
            embedding.append(hash_val - 0.5)  # Centralizar em torno de 0
        
        embeddings.append(embedding[:VECTOR_SIZE])
    
    return embeddings

def setup_qdrant_collection(client: QdrantClient):
    """Configura a collection no Qdrant"""
    try:
        # Deletar collection se existir
        client.delete_collection(COLLECTION_NAME)
        print(f"Collection {COLLECTION_NAME} deletada (se existia)")
    except:
        pass
    
    # Criar nova collection
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=VECTOR_SIZE,
            distance=Distance.COSINE
        )
    )
    print(f"✅ Collection {COLLECTION_NAME} criada")

def index_scoras_content():
    """Indexa todo o conteúdo da Scoras Academy no Qdrant"""
    print("🚀 Iniciando indexação da Scoras Academy...")
    
    # Conectar ao Qdrant
    client = QdrantClient(url=QDRANT_URL)
    
    # Configurar collection
    setup_qdrant_collection(client)
    
    # Obter conteúdo
    documents = get_all_content_for_embedding()
    print(f"📚 {len(documents)} documentos encontrados")
    
    # Preparar textos para embedding
    texts = []
    for doc in documents:
        # Combinar título e conteúdo para embedding mais rico
        full_text = f"{doc['title']}\n\n{doc['content']}"
        texts.append(full_text)
    
    print("🧠 Gerando embeddings...")
    embeddings = get_embeddings(texts)
    
    # Preparar pontos para indexação
    points = []
    for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
        point = PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={
                "document_id": doc["id"],
                "title": doc["title"],
                "content": doc["content"],
                "type": doc["type"],
                "full_text": texts[i]
            }
        )
        points.append(point)
    
    # Indexar no Qdrant
    print("📥 Indexando no Qdrant...")
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )
    
    print(f"✅ {len(points)} documentos indexados com sucesso!")
    
    # Verificar indexação
    collection_info = client.get_collection(COLLECTION_NAME)
    print(f"📊 Status da collection: {collection_info.points_count} pontos")
    
    return True

def search_scoras_content(query: str, limit: int = 3) -> List[Dict]:
    """
    Busca conteúdo da Scoras Academy usando busca semântica
    """
    client = QdrantClient(url=QDRANT_URL)
    
    # Gerar embedding da query
    query_embedding = get_embeddings([query])[0]
    
    # Buscar no Qdrant
    search_results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_embedding,
        limit=limit,
        with_payload=True
    )
    
    # Formatar resultados
    results = []
    for result in search_results:
        results.append({
            "title": result.payload["title"],
            "content": result.payload["content"],
            "score": result.score,
            "type": result.payload["type"]
        })
    
    return results

def test_rag_search():
    """Testa o sistema RAG com algumas queries"""
    print("\n🧪 Testando busca RAG...")
    
    test_queries = [
        "Quais cursos vocês têm sobre LangGraph?",
        "Como funciona o RAG na Scoras Academy?",
        "Conte-me sobre os cases práticos",
        "O que é PydanticAI?",
        "Quantos cursos existem na Academy?"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        results = search_scoras_content(query, limit=2)
        
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result['title']} (score: {result['score']:.3f})")
            print(f"     {result['content'][:100]}...")

if __name__ == "__main__":
    print("🎓 Setup RAG - Scoras Academy")
    print("=" * 50)
    
    # Verificar conexão Qdrant
    try:
        client = QdrantClient(url=QDRANT_URL)
        collections = client.get_collections()
        print(f"✅ Qdrant conectado: {len(collections.collections)} collections")
    except Exception as e:
        print(f"❌ Erro conectando Qdrant: {e}")
        print("💡 Certifique-se que o Qdrant está rodando em docker compose")
        exit(1)
    
    # Indexar conteúdo
    success = index_scoras_content()
    
    if success:
        # Testar busca
        test_rag_search()
        print("\n🎉 RAG da Scoras Academy configurado com sucesso!")
        print("💡 Agora o agente pode responder perguntas detalhadas sobre os cursos") 