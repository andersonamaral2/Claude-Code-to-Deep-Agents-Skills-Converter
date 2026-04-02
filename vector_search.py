import os
from typing import List
from langchain_core.tools import tool
from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models
from langgraph.prebuilt import ToolNode, tools_condition
from rag_setup import search_scoras_content

# Configurações do Qdrant
qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
qdrant_client = QdrantClient(url=qdrant_url)

# Configurações para Scoras Academy
COLLECTION_NAME = "scoras_academy"

# Define a ferramenta de busca no Qdrant usando decorator @tool do LangChain
@tool("busca_scoras_academy", return_direct=False)
def search_qdrant(query: str) -> str:
    """Busca informações detalhadas sobre cursos da Scoras Academy."""
    try:
        # Usar a função de busca RAG da Scoras Academy
        results = search_scoras_content(query, limit=3)
        
        if not results:
            return "Nenhuma informação encontrada sobre os cursos da Scoras Academy."
        
        # Formatar os resultados
        snippets = []
        for result in results:
            title = result.get("title", "")
            content = result.get("content", "")
            if title and content:
                snippets.append(f"**{title}**\n{content}")
        
        if not snippets:
            return "Nenhum conteúdo relevante encontrado nos cursos."
        
        # Devolve os trechos encontrados como um único texto
        context_text = "\n\n".join(snippets)
        return f"Informações da Scoras Academy:\n\n{context_text}"
        
    except Exception as e:
        return f"Erro na busca da Scoras Academy: {str(e)}"

# Lista de ferramentas disponíveis
tools = [search_qdrant]

# Cria o nó de ferramentas
def create_tool_node():
    """Cria e retorna o ToolNode com as ferramentas configuradas."""
    return ToolNode(tools=tools)
