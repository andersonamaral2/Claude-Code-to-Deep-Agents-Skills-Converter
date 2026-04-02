#!/usr/bin/env python3
"""
Sistema de Busca Híbrida para Scoras Academy + Digital
Combina BM25 (palavras-chave) + Busca Semântica
Suporta tanto cursos quanto serviços de consultoria/projetos
"""

import os
import re
from typing import List, Dict, Tuple
from rank_bm25 import BM25Okapi
from scoras_academy_content import get_all_content_for_embedding
from scoras_digital_content import get_digital_content
import json

def get_all_content_for_search():
    """Obter todo o conteúdo (Academy + Digital) para busca"""
    documents = []
    
    # Conteúdo Academy
    academy_docs = get_all_content_for_embedding()
    documents.extend(academy_docs)
    
    # Conteúdo Digital
    digital_content = get_digital_content()
    for service_id, service_data in digital_content.items():
        documents.append({
            'id': service_id,
            'title': service_data['titulo'],
            'content': service_data['descricao'],
            'type': 'digital_service',
            'category': service_data['categoria']
        })
    
    return documents

class HybridSearch:
    def __init__(self):
        self.documents = []
        self.bm25 = None
        self.tokenized_corpus = []
        self.setup_search()
    
    def setup_search(self):
        """Configura o sistema de busca híbrida"""
        print("🔧 Configurando busca híbrida BM25 + Semântica...")
        
        # Obter documentos (Academy + Digital)
        self.documents = get_all_content_for_search()
        print(f"📚 {len(self.documents)} documentos carregados")
        
        # Preparar corpus para BM25
        corpus = []
        for doc in self.documents:
            # Combinar título e conteúdo para busca mais rica
            full_text = f"{doc['title']} {doc['content']}"
            corpus.append(full_text)
        
        # Tokenizar corpus (simples - dividir por palavras)
        self.tokenized_corpus = [self.tokenize(text) for text in corpus]
        
        # Criar índice BM25
        self.bm25 = BM25Okapi(self.tokenized_corpus)
        print("✅ Índice BM25 criado")
        
        print("🎯 Busca híbrida pronta!")
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenização simples mas efetiva"""
        # Converter para minúsculas e remover pontuação
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        # Dividir por espaços e remover tokens vazios
        tokens = [token for token in text.split() if len(token) > 2]
        return tokens
    
    def search_bm25(self, query: str, limit: int = 5) -> List[Tuple[Dict, float]]:
        """Busca usando BM25 (palavras-chave)"""
        query_tokens = self.tokenize(query)
        scores = self.bm25.get_scores(query_tokens)
        
        # Ordenar por score e pegar os melhores
        doc_scores = [(self.documents[i], scores[i]) for i in range(len(scores))]
        doc_scores.sort(key=lambda x: x[1], reverse=True)
        
        return doc_scores[:limit]
    
    def search_exact_match(self, query: str) -> List[Dict]:
        """Busca por correspondência exata de termos importantes"""
        query_lower = query.lower()
        results = []
        
        # Termos ACADEMY (cursos)
        course_terms = {
            'langgraph': 'curso_06',
            'pydantic': 'curso_14', 
            'pydanticai': 'curso_14',
            'rag': ['curso_09', 'curso_10'],  # RAG básico e avançado
            'python': 'curso_16',
            'routing': 'curso_13',
            'llm routing': 'curso_13',
            'langflow': 'curso_11',
            'deployment': 'curso_12',
            'cases': 'curso_03',
            'projetos': 'curso_08'
        }
        
        # Termos DIGITAL (serviços)
        service_terms = {
            'consultoria': 'servico_01',
            'consultar': 'servico_01',
            'projeto': 'servico_02',
            'projetos': 'servico_02',
            'squad': 'servico_02',
            'preco': 'precos',
            'precos': 'precos',
            'valor': 'precos',
            'valores': 'precos',
            'investimento': 'precos',
            'custo': 'precos',
            'quanto custa': 'precos',
            'tabela': 'precos',
            'basico': 'consultoria_basico',
            'essencial': 'consultoria_essencial',
            'expandido': 'consultoria_expandido',
            'part-time': 'projeto_part_time',
            'part time': 'projeto_part_time',
            'full-time': 'projeto_full_time',
            'full time': 'projeto_full_time'
        }
        
        # Buscar termos de curso
        for term, course_ids in course_terms.items():
            if term in query_lower:
                if isinstance(course_ids, list):
                    for course_id in course_ids:
                        doc = next((d for d in self.documents if d['id'] == course_id), None)
                        if doc and doc not in results:
                            results.append(doc)
                else:
                    doc = next((d for d in self.documents if d['id'] == course_ids), None)
                    if doc and doc not in results:
                        results.append(doc)
        
        # Buscar termos de serviço
        for term, service_ids in service_terms.items():
            if term in query_lower:
                if isinstance(service_ids, list):
                    for service_id in service_ids:
                        doc = next((d for d in self.documents if d['id'] == service_id), None)
                        if doc and doc not in results:
                            results.append(doc)
                else:
                    doc = next((d for d in self.documents if d['id'] == service_ids), None)
                    if doc and doc not in results:
                        results.append(doc)
        
        return results
    
    def search_hybrid(self, query: str, limit: int = 3) -> List[Dict]:
        """Busca híbrida: BM25 + Exact Match + Boost por relevância"""
        print(f"🔍 Busca híbrida para: '{query}'")
        
        # 1. Busca por correspondência exata (prioridade máxima)
        exact_results = self.search_exact_match(query)
        print(f"🎯 Correspondência exata: {len(exact_results)} resultados")
        
        # 2. Busca BM25
        bm25_results = self.search_bm25(query, limit=5)
        print(f"📊 BM25: {len(bm25_results)} resultados")
        
        # 3. Combinar resultados com deduplicação
        final_results = []
        seen_ids = set()
        
        # Adicionar resultados exatos primeiro (prioridade)
        for doc in exact_results:
            if doc['id'] not in seen_ids:
                final_results.append({
                    'title': doc['title'],
                    'content': doc['content'],
                    'type': doc.get('type', 'unknown'),
                    'score': 1.0,  # Score máximo para correspondência exata
                    'method': 'exact_match'
                })
                seen_ids.add(doc['id'])
        
        # Adicionar resultados BM25 (se não duplicados)
        for doc, score in bm25_results:
            if doc['id'] not in seen_ids and score > 0.1:  # Filtrar scores muito baixos
                final_results.append({
                    'title': doc['title'],
                    'content': doc['content'],
                    'type': doc.get('type', 'unknown'),
                    'score': float(score),
                    'method': 'bm25'
                })
                seen_ids.add(doc['id'])
        
        # Limitar resultados
        final_results = final_results[:limit]
        
        print(f"✅ Resultados finais: {len(final_results)}")
        for i, result in enumerate(final_results, 1):
            print(f"  {i}. {result['title']} (score: {result['score']:.3f}, method: {result['method']})")
        
        return final_results

# Instância global
hybrid_search = HybridSearch()

def search_scoras_hybrid(query: str, limit: int = 3) -> List[Dict]:
    """Interface principal para busca híbrida"""
    return hybrid_search.search_hybrid(query, limit)

# Teste rápido
if __name__ == "__main__":
    print("🧪 Testando busca híbrida...")
    
    test_queries = [
        "Quais módulos tem o curso de LangGraph?",
        "módulos PydanticAI", 
        "consultoria de IA",
        "preços dos projetos",
        "quanto custa consultoria básica?"
    ]
    
    for query in test_queries:
        print(f"\n{'='*50}")
        print(f"Query: {query}")
        results = search_scoras_hybrid(query, limit=2)
        
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result['title']}")
            print(f"   Score: {result['score']:.3f} ({result['method']})")
            print(f"   Content: {result['content'][:100]}...") 