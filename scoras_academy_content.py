"""
Conteúdo completo da Scoras Academy para RAG
Estruturado por cursos e seções para embedding vetorial

REGRAS DE INTERAÇÃO:
- Respostas devem ter máximo 250 caracteres
- Ser didático e educativo, fornecendo dados dos cursos, preços e detalhes
- JAMAIS oferecer link do Calendly
- Sempre mencionar que cursos podem ser vendidos separadamente
- Formação Continuada de 12 meses para todos os níveis (iniciantes a avançados)
- Incluir: Python para Iniciantes em IA, Fundamentos de LLMs e SLMs
- Ser sempre cordial e educado
"""

# Prompt sistema para Academy (máximo 280 caracteres por resposta)
ACADEMY_SHORT_PROMPT = """Você é assistente da Scoras Academy, especialista em Engenharia de IA.

🎯 QUALIFICAÇÃO DE LEADS:
Lead qualificado = conseguir nome, e-mail e telefone/WhatsApp do potencial aluno.

🔥 PROMOÇÃO ESPECIAL JULHO 2025:
Válida de 01 a 31 de julho ou enquanto durarem os lotes!
🔓 1º LOTE: 50 licenças por R$ 2.599 (à vista)
⏳ 2º LOTE: Mais 50 licenças por R$ 2.999
💰 Preço normal: R$ 3.519,81
📊 Valor avulso total: R$ 14.970

FORMAÇÃO CONTINUADA - CICLO COMPLETO DE ENGENHARIA DE IA:
✅ Teoria, casos de uso e deployment
✅ Acesso às aulas atuais e futuros lançamentos
✅ 12x de R$ 268,80/ano ou R$ 2.599/ano à vista
✅ Conteúdo exclusivo com Anderson Amaral
✅ Atualizações constantes (2+ cursos novos/mês)
✅ Aprendizado prático em módulos estruturados
✅ Acesso ao GitHub exclusivo do curso
✅ Acesso a vagas exclusivas de empresas parceiras

📚 TRILHA RECOMENDADA PARA INICIANTES:
1. Python para Iniciantes em IA (base essencial)
2. Fundamentos de LLMs e SLMs
3. RAG (Retrieval Augmented Generation)
4. Todos os outros cursos intermediários
5. LangGraph e PydanticAI (mais complexos)

🚀 PRÓXIMOS CURSOS NO BACKLOG:
CrewAI, Ontologia com LangGraph, Computação Quântica, Agno, A2A e vários outros.

REGRAS DE INTERAÇÃO:
- Máximo 280 caracteres por resposta
- Seja simpático e solícito
- Pergunte se o potencial aluno quer mais informações
- Se ele responder em até 2 minutos, agradeça e encerre
- Se continuar a conversa e se despedir, considere lead qualificado
- Sempre mencione: cursos podem ser vendidos separadamente

CONTATO COMERCIAL ESPECIALIZADO:
Para propostas corporativas, licenças empresariais, métodos alternativos de pagamento ou informações específicas fora do escopo: https://api.whatsapp.com/send/?phone=5511912948575&text&type=phone_number&app_absent=0

Site oficial: https://scorasacademy.com.br"""

SCORAS_ACADEMY_CONTENT = {
    "overview": {
        "title": "Visão Geral da Scoras Academy",
        "content": """
        A Scoras Academy nasceu da experiência da Scoras Digital, empresa pioneira na implementação de agentes de IA para negócios no Brasil e no exterior. Se a Scoras Digital se especializou em construir soluções personalizadas para empresas, automatizando processos complexos com agentes inteligentes, a Scoras Academy veio para capacitar profissionais a dominar essa tecnologia na prática.

        MODALIDADES DE ENSINO:
        📚 CURSOS SEPARADOS: Todos os nossos cursos podem ser adquiridos individualmente
        🎓 FORMAÇÃO CONTINUADA: Programa de 12 meses com todos os cursos inclusos
        
        NÍVEIS DE CONHECIMENTO:
        👶 INICIANTES: Python para Iniciantes em IA, Fundamentos de LLMs e SLMs
        🚀 INTERMEDIÁRIO: LangGraph, Pydantic AI, RAG Básico
        💪 AVANÇADO: RAG Avançado, LangFlow, Deployment Profissional
        
        A Formação Continuada de 12 meses é ideal para pessoas de TODOS OS NÍVEIS, pois começa do básico e evolui gradualmente. Inclui desde conceitos fundamentais até implementações avançadas.

        Diferente de cursos genéricos sobre IA, a Scoras Academy ensina a engenharia por trás dos agentes de IA, indo muito além de simplesmente ajustar prompts para um LLM gigante. Aqui, você aprende a construir pipelines agentivos do zero, integrar Small Language Models (SLMs) para tarefas específicas, otimizar custos com LLM Routing, estruturar bases de conhecimento com RAG (Retrieval-Augmented Generation) e muito mais.

        Total de cursos: 15 cursos disponíveis, com 2+ novos cursos adicionados mensalmente.
        Acesso inclui: GitHub Exclusivo da Scoras Academy.
        """
    },
    "formacao_continuada": {
        "title": "Formação Continuada - 12 Meses - PROMOÇÃO JULHO",
        "content": """
        📚 FORMAÇÃO CONTINUADA SCORAS ACADEMY (12 MESES)
        
        🔥 PROMOÇÃO ESPECIAL DE FÉRIAS - JULHO 2025:
        Válida de 01 a 31 de julho ou enquanto durarem os lotes!
        
        🔓 1º LOTE: Apenas 50 licenças por R$ 2.599 (à vista)
        ⏳ 2º LOTE: Mais 50 licenças por R$ 2.999
        💰 Preço normal após promoção: R$ 3.519,81
        📊 Se comprar todos os cursos separadamente: R$ 14.970
        
        💳 FORMAS DE PAGAMENTO:
        • 12x de R$ 268,80/ano 
        • R$ 2.599/ano à vista (1º lote)
        
        IDEAL PARA TODOS OS NÍVEIS DE CONHECIMENTO:
        ✅ Iniciantes em programação
        ✅ Desenvolvedores experientes
        ✅ Profissionais mudando de área
        ✅ Empresários querendo entender IA
        
        CURSOS INCLUSOS (16+ CURSOS):
        
        🌱 INICIANTES:
        • Python para Iniciantes em IA
        • Fundamentos de LLMs e SLMs
        • Introdução aos Agentes de IA
        
        🚀 INTERMEDIÁRIO:
        • LangGraph e Agentes de IA
        • Pydantic AI e Validação de Dados
        • RAG (Retrieval Augmented Generation) Básico
        • Prompt Engineering Avançado
        
        💪 AVANÇADO:
        • RAG Multimodal e Agêntico
        • LangFlow e Automação
        • Deployment de Projetos de IA
        • MLOps para IA
        • Otimização e Performance
        
        🚀 PRÓXIMOS CURSOS (em desenvolvimento):
        • CrewAI
        • Ontologia com LangGraph
        • Computação Quântica
        • Agno, A2A e vários outros
        
        VANTAGENS DA FORMAÇÃO:
        📈 Progressão gradual e estruturada
        🎯 Conteúdo exclusivo com Anderson Amaral
        💻 Projetos práticos reais
        🔄 Atualizações constantes (2+ cursos novos/mês)
        🏆 Certificado de conclusão
        📚 Acesso ao GitHub exclusivo do curso
        💼 Acesso a vagas exclusivas de empresas parceiras
        
        GARANTIA: Acesso às aulas atuais e aos futuros lançamentos dos cursos que fazem parte da Formação Continuada.
        
        Site: https://scorasacademy.com.br
        """
    },
    "courses": {
        "curso_01": {
            "title": "Bem-vindos a Scoras Academy",
            "content": """
            Curso 01: Bem-vindos a Scoras Academy
            - Apresentação da plataforma
            - Acesso ao GitHub Exclusivo da Scoras Academy
            - Primeiro contato com a metodologia Scoras
            - Visão geral: Cursos separados vs Formação Continuada
            
            IMPORTANTE: Todos os cursos podem ser adquiridos separadamente ou como parte da Formação Continuada de 12 meses.
            """
        },
        "curso_01b": {
            "title": "Python para Iniciantes em IA",
            "content": """
            Curso: Python para Iniciantes em IA
            
            IDEAL PARA INICIANTES COMPLETOS:
            Módulos:
            - Introdução ao Python (do zero)
            - Variáveis, listas, dicionários
            - Funções e bibliotecas essenciais
            - Pandas para manipulação de dados
            - NumPy para cálculos
            - Matplotlib para visualização
            - Primeiros passos com APIs
            - Conceitos básicos de Machine Learning
            - Quiz e exercícios práticos
            
            Este curso faz parte da Formação Continuada mas pode ser adquirido separadamente.
            Perfeito para quem nunca programou mas quer trabalhar com IA.
            """
        },
        "curso_01c": {
            "title": "Fundamentos de LLMs e SLMs",
            "content": """
            Curso: Fundamentos de LLMs e SLMs
            
            CONCEITOS ESSENCIAIS:
            Módulos:
            - O que são Large Language Models (LLMs)
            - Diferenças entre LLMs e Small Language Models (SLMs)
            - Como funcionam os transformers
            - Tokenização e embeddings
            - Prompts eficazes
            - Limitações e vieses dos modelos
            - Casos de uso práticos
            - Comparação: GPT, Claude, Llama, DeepSeek
            - Quiz: Fundamentos de LLMs e SLMs
            
            Curso fundamental que pode ser feito separadamente ou como parte da Formação Continuada.
            Base essencial para todos os outros cursos avançados.
            """
        },
        "curso_02": {
            "title": "Introdução a Large Language Models (LLMs)",
            "content": """
            Curso 02: Introdução a Large Language Models (LLMs)
            Módulos:
            - Introdução aos LLMs
            - Principais Aplicações de LLMs
            - Como LLMs funcionam?
            - Quiz: Introdução a Large Language Models (LLMs)
            
            Aprenda os fundamentos dos modelos de linguagem grandes, suas aplicações práticas e funcionamento interno.
            """
        },
        "curso_03": {
            "title": "Cases Práticos",
            "content": """
            Curso 03: Cases Práticos da Scoras Digital
            Cases reais implementados:
            - Case: Qualificação de Leads
            - Case: Avaliação de Vendedores de um Call Center
            - Case: Solução para Ruptura em um Rede de Supermercados
            - Case: RAG Multimodal Universidade dos EUA
            - Case: RAG Agêntico Para Gestão de Contratos
            - Case: Análise de Contratos Jurídicos com IA
            - Case: Seguradora Dados Climáticos
            
            Estudos de caso reais da Scoras Digital em diversos setores: jurídico, financeiro, logística e seguradoras.
            """
        },
        "curso_04": {
            "title": "Fundamentos Técnicos de LLMs",
            "content": """
            Curso 04: Fundamentos Técnicos de LLMs
            Módulos detalhados:
            - Visão Geral
            - Arquitetura de Transformadores (Transformers)
            - Como Funcionam os Transformadores
            - Quiz: Arquitetura de Transformadores
            - Mecanismo de Atenção (Self-Attention) e sua Importância
            - Exemplos de "Self-Attention"
            - Quiz: Mecanismo de Atenção
            - Treinamento de LLMs
            - Quiz: Treinamento de LLMs
            - Conceitos de Overfitting, Underfitting e Regularização
            - Módulo Especial: Seria o "Early Stopping" um tipo de regularização?
            - Quiz: Conceitos de Overfitting, Underfitting e Regularização
            - Alucinações em LLMs
            - Por que ocorrem alucinações?
            - Quiz: Alucinações em LLMs
            
            Compreenda profundamente a arquitetura e funcionamento técnico dos LLMs.
            """
        },
        "curso_05": {
            "title": "LLMs em Profundidade: DeepSeek",
            "content": """
            Curso 05: LLMs em Profundidade: Novas Arquiteturas, Treinamento e Casos de Uso
            Foco em DeepSeek:
            - Parte 1: DeepSeek: A Inovação que Desafia os Paradigmas da IA
            - Parte 2: DeepSeek: A Inovação que Desafia os Paradigmas da IA
            - Parte 3: DeepSeek: A Inovação que Desafia os Paradigmas da IA
            - Quiz: DeepSeek- A Inovação que Desafia os Paradigmas da IA
            - DeepSeek API Setup
            - Setup DeepSeek R1 Ollama
            
            Explore a arquitetura revolucionária do DeepSeek e suas aplicações práticas.
            """
        },
        "curso_06": {
            "title": "Curso Introdutório de LangGraph",
            "content": """
            Curso 06: Curso Introdutório de LangGraph
            Módulos completos:
            - Visão Geral
            - Setup LangGraph
            - Grafo
            - Falando de Cadeias
            - Roteadores
            - Agente Simples Com Roteamento
            - Agente com Memória
            - Quiz: Conceitos e Fundamentos do LangGraph
            - Schema de Estado
            - Reducers de Estado
            - Schemas Múltiplos
            - Filtrando e cortando/reduzindo mensagens
            - Quiz: Gerenciamento de Mensagens e Estados
            - Streaming, Interrupção e Human-In-Loop No LangGraph
            - Quiz: Streaming, Interrupção e Human-In-Loop
            - Pontos de Interrupção (Breakpoints)
            - Quiz: Pontos de Interrupção
            - Editando o Estado do Grafo com FeedBack Humano
            - Pontos de Interrupção Dinâmicos
            - Viagem no Tempo
            - Paralelização
            - Sub-Grafos
            - Verificando os Sub-Grafos no Langsmith
            - Quiz sobre Sub-grafos no LangGraph
            - MapReduce
            - Quiz: Conceitual sobre Map-Reduce
            - Parte 1: Assistente de Pesquisa Final
            - Parte 2: Assistente de Pesquisa Final
            - Quiz: Assistente de Pesquisa Final
            
            Domine o LangGraph para orquestração de agentes de IA complexos.
            """
        },
        "curso_07": {
            "title": "Introdução a Small Language Models (SLMs)",
            "content": """
            Curso 07: Introdução a Small Language Models (SLMs)
            Conteúdo completo:
            - Visão Geral
            - Fundamentos dos Modelos de Linguagem
            - Quiz: Fundamentos dos Modelos de Linguagem
            - Arquiteturas Modernas de Small Language Models
            - Quiz: Arquiteturas Modernas de Small Language Models
            - Técnicas de Compressão e Otimização
            - Quiz - Técnicas de Compressão e Otimização
            - Setup
            - Comandos básicos do Ollama
            - Ollama with Qwen2.5
            - Setup - Ollama no Colab com Qwen2.5
            - Desenvolvimento e Treinamento de SLMs
            - Exemplo de Código - Limpeza e Normalização de Texto
            - Treinamento de Modelos de Linguagem
            - Exemplo de Código: Fine-Tuning com LoRA
            - Exemplo Simples de QLoRA, do Início ao Fim
            - Quiz: Introdução a Small Language Models (SLMs)
            - Parte 1: Ferramentas e Plataformas para Small Language Models
            - Parte 2: Ferramentas e Plataformas para Small Language Models
            - Quiz: Ferramentas e Plataformas para Small Language Models
            - HuggingFace Transformers-Groq- Pequenos Modelos-Tensor-Pytorch
            - Nvidia Ferramentas e Conceitos
            
            Aprenda a trabalhar com modelos menores e mais eficientes para tarefas específicas.
            """
        },
        "curso_08": {
            "title": "Projetos Práticos de IA",
            "content": """
            Curso 08: Projetos Práticos de IA
            Projetos hands-on:
            - Visão Geral
            - Agente Avaliador de Correção Gramatical e Coesão Textual
            - Classificador de Texto, Extrator de Entidades e Sumarizador
            - Agente de Suporte ao Cliente com LangGraph
            - NL2SQL
            - Agente de IA com DuckDB e LangGraph
            - Quiz: Agente de IA com DuckDB e LangGraph
            - Agente Duck com Croq e sem LangGraph
            - Quiz: Duck com Groq Sem LangGraph
            - Sistema de Triagem e Classificação de Currículos
            - Quiz: Sistema de Triagem e Classificação de Currículos
            - AgentOps com LangGraph
            - Quiz: AgentOps com LangGraph
            - Parte 1: MongoDB AI Agent
            - Parte 2: MongoDB AI Agent
            - Quiz: MongoDB AI Agent
            - Assistente de Gerenciamento de Inventário
            - Quiz: Assistente de Gerenciamento de Inventário
            - RAG Agêntico com LangGraph
            - Quiz: RAG Agêntico com LangGraph
            - Parte 1: Ferramenta de Geração Automática de Relatórios em PDF
            - Parte 2: Ferramenta de Geração Automática de Relatórios em PDF
            - Quiz: Ferramenta de Geração Automática de Relatórios
            - PydanticAI RAG com ChromaDB e Groq
            - Quiz: PydanticAI RAG com ChromaDB e Groq
            - RAG Busca Hibrida com BM25 e PydanticAI
            - Quiz: RAG Busca Hibrida com BM25 e PydanticAI
            - Parte 1: MCP na pratica (Agregador de noticias)
            - Parte 2: MCP na pratica (Agregador de noticias)
            - Quiz: MCP na pratica (Agregador de noticias)
            
            Desenvolva projetos reais de IA aplicados a problemas empresariais.
            """
        },
        "curso_09": {
            "title": "Fundamentos de RAG",
            "content": """
            Curso 09: Fundamentos de RAG (Retrieval Augmented Generation)
            Conteúdo:
            - Conceitos Básicos de RAG
            - Exemplo simples de implementação de RAG usando Python
            - Quiz: Conceitos Básicos de RAG
            - Arquitetura do RAG
            - Arquitetura do RAG - Exemplo Prático
            - Quiz - Arquitetura do RAG
            
            Domine os fundamentos do RAG para bases de conhecimento inteligentes.
            """
        },
        "curso_10": {
            "title": "Técnicas Avançadas de RAG",
            "content": """
            Curso 10: Técnicas Avançadas de RAG
            Módulos avançados:
            - Introdução: Técnicas Avançadas de RAG
            - Parte 1: Introdução e Limitações dos Sistemas RAG Convencionais
            - Parte 2: Introdução e Limitações dos Sistemas RAG Convencionais
            - Quiz: Introdução e Limitações dos Sistemas RAG Convencionais
            - Técnicas Avançadas de Recuperação de Informação
            - Quiz: Técnicas Avançadas de Recuperação de Informação
            - Implementação de Recuperação Neural com Representações Densas
            - Técnicas Avanças de RAG - Implementação de Pesquisa Híbrida
            - Parte 1: CRAG
            - Parte 2: CRAG
            - Quiz: CRAG
            - RAG, Prompt Caching e Abordagem Híbrida
            - Quiz: RAG, Prompt Caching e Abordagem Híbrida
            - Introdução ao GraphRAG
            - GraphRAG Simples
            - Quiz: GraphRAG Simples
            - GraphRAG com Neo4J
            - Quiz: GraphRAG com Neo4J
            - Mostrando os Grafos no Neo4J
            - Parte 1: GraphRAG com LLM
            - Parte 2: GraphRAG com LLM
            - Quiz: GraphRAG com LLM
            - Parte 1: Nano-GraphRAG
            - Parte 2: Nano-GraphRAG
            - Quiz: Nano‑GraphRAG
            
            Explore técnicas avançadas incluindo GraphRAG, CRAG e recuperação neural.
            """
        },
        "curso_11": {
            "title": "Langflow Fácil e Prático",
            "content": """
            Curso 11: Langflow Fácil e Prático
            Módulos:
            - Visão Geral e Introdução
            - Instalação e Primeiros Passos
            - RAG no LangFlow
            - Introdução Agentes
            - Agentes na Prática
            - Agente Escritor De Newsletter & Atualização Do Langflow
            - Gerador de Newsletter integrado com WEB, YouTube & Scrapping no LangFlow
            
            Interface visual para criação de agentes de IA sem código.
            """
        },
        "curso_12": {
            "title": "Deployment Agnóstico de Apps de IA",
            "content": """
            Curso 12: Deployment Agnóstico de Apps de IA
            Conteúdo:
            - Introdução: Deployment Agnóstico de Apps de IA
            - Entendendo a Arquitetura do RAG Agentico
            - Mais sobre arquitetura e detalhes do RAG Agentico
            - Docker build e docker run do RAG Agentico na AWS
            
            Aprenda a fazer deploy de aplicações de IA em qualquer plataforma.
            """
        },
        "curso_13": {
            "title": "LLM Routing",
            "content": """
            Curso 13: LLM Routing
            Módulos completos:
            - Apresentação
            - Fundamentos do LLM Routing
            - Quiz: Fundamentos do LLM Routing
            - Arquiteturas de Roteamento e Técnicas de Decisão
            - Quiz: Arquiteturas de Roteamento e Técnicas de Decisão
            - Implementação do LLM Routing – Treinamento de Routers e Seleção de Modelos
            - Quiz: Implementação do LLM Routing
            - LLM Routing Usando RouteLLM com Modelos OpenAI
            - Métricas de Avaliação e Monitoramento Contínuo
            - Quiz: Métricas de Avaliação e Monitoramento Contínuo
            - Casos Práticos e Exemplos Reais
            - Quiz: Casos Práticos e Exemplos Reais
            - LLM Routing por Falha de API
            - Quiz: LLM Routing por Falha de API
            - Roteamento Hibrido Usando Controller e por Falha de API com Modelo de Fallback
            - Quiz: Roteamento Hibrido
            - BERTSim BERT Score e MLP Router e NLL
            - Quiz: BERTSim BERT Score e MLP Router e -NLL
            - BERTSim BERTScore NLL MLP Router com Chamadas Reais OpenAI e Groq
            - Quiz: BERTSim BERTScore NLL MLP Router com Chamadas Reais
            
            Otimize custos e performance roteando entre diferentes LLMs.
            """
        },
        "curso_14": {
            "title": "PydanticAI",
            "content": """
            Curso 14: PydanticAI
            Módulos detalhados:
            - Introdução
            - Introdução, Arquitetura Interna do PydanticAI e Fluxo de Execução
            - Estrutura, Criação de Agentes e Conceitos Básicos
            - Injeção de Dependências e Ferramentas (Tools)
            - Quiz: Injeção de Dependências e Ferramentas
            - Execução e Iteração sobre o Grafo de Execução no PydanticAI
            - Quiz: Execução e Iteração sobre o Grafo de Execução
            - Configurações Avançadas de Model Settings e Tratamento de Erros
            - Quiz: Configurações Avançadas e Tratamento de Erros
            - Estratégias de Retry, Autocorreção e Feedback Iterativo
            - Quiz: Estratégias de Retry, Autocorreção e Feedback Iterativo
            - Integração com RAG e Casos de Uso Avançados
            - Quiz: Integração com RAG e Casos de Uso Avançados
            - Boas Práticas de Produção, Testes e Monitoramento
            - Quiz: Boas Práticas de Produção, Testes e Monitoramento
            - Exemplos Práticos e Casos de Uso Reais
            - Quiz: Exemplos Práticos e Casos de Uso Reais do PydanticAI
            - Perspectivas Futuras
            - Conclusão PydanticAI
            - Quiz de Conclusão do Curso Introdutório de PydanticAI
            
            Framework moderno para desenvolvimento de agentes de IA com validação de tipos.
            """
        },
        "curso_15": {
            "title": "Model Context Protocol - De A a Z e AWS",
            "content": """
            Curso 15: Model Context Protocol - De A a Z e AWS
            Conteúdo completo:
            - Introdução
            - Conceitos Fundamentais de MCP
            - Quiz: Conceitos Fundamentais de MCP
            - Parte 1: Integrando com um agente PydanticAI (cliente MCP)
            - Parte 2: Integrando com um agente PydanticAI (cliente MCP)
            - Parte 3: Integrando com um agente PydanticAI (cliente MCP)
            - Introdução ao PydanticAI (Framework de Agentes de IA)
            - Quiz: Introdução ao PydanticAI
            - Introdução ao Langgraph Orquestrando Fluxos de Agentes
            - Quiz: Introdução ao LangGraph Orquestrando Fluxos de Agentes
            - Parte 1: Escrevendo um servidor MCP simples
            - Parte 2: Escrevendo um servidor MCP simples
            - Parte 1: Escrevendo um servidor MCP simples com o SDK Python Oficial do MCP
            - Parte 2: Escrevendo um servidor MCP simples com o SDK Python Oficial do MCP
            - Quiz - Escrevendo um Servidor Simples com SDK Oficial e Gradio
            - Parte 1: História de Pokémon (Groq + MCP)
            - Parte 2: História de Pokémon (Groq + MCP)
            - Quiz: História de Pokémon (Groq + MCP)
            
            Protocolo de contexto para modelos com integração AWS.
            """
        },
        "curso_16": {
            "title": "Python para Iniciantes em Inteligência Artificial",
            "content": """
            Curso 16: Python para Iniciantes em Inteligência Artificial
            Módulos extensos:
            - Apresentação
            - Parte 1: Aula 0
            - Parte 2: Aula 0
            - Docker Install (Windows)
            - CUDA + PyTorch
            - Introdução ao Python e Google Colab
            - Quiz: Introdução ao Python e Google Colab
            - Operações, Estruturas de Controle e Funções
            - Manipulação de Dados com Pandas no Colab
            - Limpeza e Pre-Processamento de Dados
            - Introdução à Criação de Gráficos com Seaborn e Outras Bibliotecas com Pandas
            - Inferência Bayesiana
            - Quiz: Inferência Bayesiana
            - Parte 1: Introdução às Séries Temporais
            - Parte 2: Introdução às Séries Temporais
            - Quiz: Introdução às Séries Temporais
            - Parte 1: Introdução à Modelagem Supervisionada - Regressão
            - Parte 2: Introdução à Modelagem Supervisionada - Regressão
            - Quiz: Introdução à Modelagem Supervisionada - Regressão
            - Parte 1: Introdução à Modelagem Supervisionada - Classificação
            - Parte 2: Introdução à Modelagem Supervisionada - Classificação
            - Quiz: Introdução à Modelagem Supervisionada - Classificação
            - Parte 1: Introdução à Modelagem Não-supervisionada
            - Parte 2: Introdução à Modelagem Não-supervisionada
            - Quiz: Introdução à Modelagem Não-supervisionada
            - Introdução Básica à NLP
            - Quiz: Introdução Básica à NLP
            - Case Lei de Benford
            - Quiz: Case Lei de Benford
            - Case Lei de Zipft
            - Quiz: Case Lei de Zipft
            - Introdução às APIs de LLMs open source com Groq
            - Parte 1: AutoML
            - Parte 2: AutoML
            - Parte 3: AutoML
            - Quiz Final: Python para Iniciantes Inteligência Artificial
            - Conclusão
            
            Base sólida em Python aplicado à Inteligência Artificial.
            """
        }
    },
    "learning_path": {
        "title": "Trilha de Aprendizagem Scoras Academy",
        "content": """
        O que você aprende na Scoras Academy:

        1. Criação de agentes de IA do zero, utilizando frameworks como LangGraph, LangFlow e PydanticAI
        2. Orquestração de multiagentes, com integração de LLMs e SLMs para tarefas complexas
        3. Construção de pipelines RAG, incluindo RAG multimodal para processar texto, imagens e bases de dados
        4. LLM Routing e otimização de custos, reduzindo uso desnecessário de tokens
        5. Automação para negócios, aplicando IA para resolver problemas práticos de empresas

        A Scoras Digital provou que agentes de IA são o futuro da automação empresarial, e agora, através da Scoras Academy, estamos formando os profissionais que vão liderar essa transformação.
        """
    }
}

def get_all_content_for_embedding():
    """
    Retorna todo o conteúdo em formato apropriado para embedding vetorial
    """
    documents = []
    
    # Adicionar visão geral
    documents.append({
        "id": "overview",
        "title": SCORAS_ACADEMY_CONTENT["overview"]["title"],
        "content": SCORAS_ACADEMY_CONTENT["overview"]["content"],
        "type": "overview"
    })
    
    # Adicionar todos os cursos
    for course_id, course_data in SCORAS_ACADEMY_CONTENT["courses"].items():
        documents.append({
            "id": course_id,
            "title": course_data["title"],
            "content": course_data["content"],
            "type": "course"
        })
    
    # Adicionar trilha de aprendizagem
    documents.append({
        "id": "learning_path",
        "title": SCORAS_ACADEMY_CONTENT["learning_path"]["title"],
        "content": SCORAS_ACADEMY_CONTENT["learning_path"]["content"],
        "type": "learning_path"
    })
    
    return documents

if __name__ == "__main__":
    docs = get_all_content_for_embedding()
    print(f"Total de documentos para embedding: {len(docs)}")
    for doc in docs[:3]:  # Mostrar primeiros 3
        print(f"- {doc['title']}") 