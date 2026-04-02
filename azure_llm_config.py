# Importações necessárias
import os
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.inference.models import SystemMessage, UserMessage, AssistantMessage

# Configurações do Azure AI Inference (DeepSeek via Azure)
AZURE_ENDPOINT = os.environ.get("AZURE_ENDPOINT", "https://ai-andersonai017430836643.services.ai.azure.com/models")
AZURE_API_KEY = os.environ.get("AZURE_API_KEY", "your-azure-api-key")
AZURE_API_VERSION = os.environ.get("AZURE_API_VERSION", "2024-05-01-preview")
DEEPSEEK_MODEL = os.environ.get("DEEPSEEK_MODEL", "DeepSeek-V3-0324")

# Inicializa o cliente ChatCompletionsClient para o modelo DeepSeek via Azure AI Inference
azure_client = ChatCompletionsClient(
    endpoint=AZURE_ENDPOINT,
    credential=AzureKeyCredential(AZURE_API_KEY),
    api_version=AZURE_API_VERSION
)

# Classe wrapper para Azure DeepSeek
class AzureDeepSeekLLM:
    def __init__(self, client, model_name):
        self.client = client
        self.model = model_name

    def generate(self, messages, max_tokens=512, temperature=0.7, top_p=0.9):
        """Gera resposta usando o modelo DeepSeek via Azure AI Inference."""
        chat_msgs = []
        for msg in messages:
            if isinstance(msg, dict):
                role = msg.get('role', 'user')
                content = msg.get('content', '')
            else:
                # Assume que é uma tupla (role, content)
                role, content = msg if isinstance(msg, tuple) else ('user', str(msg))
            
            if role == 'system':
                chat_msgs.append(SystemMessage(content=content))
            elif role in ('user', 'human'):
                chat_msgs.append(UserMessage(content=content))
            elif role in ('assistant', 'ai'):
                chat_msgs.append(AssistantMessage(content=content))

        try:
            response = self.client.complete(
                messages=chat_msgs,
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                presence_penalty=0.0,
                frequency_penalty=0.0
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Erro na chamada do LLM: {e}")
            return "Desculpe, ocorreu um erro técnico. Tente novamente."

# Instancia o LLM
llm = AzureDeepSeekLLM(azure_client, DEEPSEEK_MODEL)

# Define prompts de sistema para orientar o comportamento do chatbot
ACADEMY_SYSTEM_PROMPT = (
    "Você é um assistente virtual especializado da Scoras Academy, capacitado para responder perguntas detalhadas sobre nossos cursos. "
    "\n\n**SOBRE A SCORAS ACADEMY**: "
    "A Scoras Academy nasceu da experiência da Scoras Digital, empresa pioneira na implementação de agentes de IA para negócios no Brasil e no exterior. "
    "Oferecemos 15+ cursos especializados em IA, com 2+ novos cursos adicionados mensalmente. "
    "Nosso ensino é baseado em cases reais da Scoras Digital, que já implementou agentes de IA para empresas de diversos setores. "
    "\n\n**CURSOS DISPONÍVEIS**: "
    "Temos cursos completos sobre: LangGraph, RAG (básico e avançado), PydanticAI, LLM Routing, Small Language Models, "
    "Cases Práticos, Projetos de IA, Langflow, Deployment de Apps IA, Model Context Protocol, Python para IA, e muito mais. "
    "\n\n**COMO RESPONDER**: "
    "- Para perguntas específicas sobre cursos, conteúdos, módulos ou detalhes técnicos: USE a ferramenta 'busca_scoras_academy' para obter informações precisas "
    "- Para perguntas gerais: responda com informações básicas e direcione ao site https://scorasacademy.com.br "
    "- Para dúvidas adicionais: instrua contato via admin@scoras.com.br "
    "- Mantenha sempre um tom acolhedor e prestativo "
    "- SEMPRE use a busca quando o usuário perguntar sobre conteúdo específico de cursos "
    "\n\n**IMPORTANTE - IDIOMAS**: "
    "Você DEVE responder EXCLUSIVAMENTE nos seguintes idiomas: "
    "1. PORTUGUÊS DO BRASIL (preferencial e padrão) "
    "2. INGLÊS (somente se solicitado) "
    "3. ESPANHOL (somente se solicitado) "
    "JAMAIS use chinês, mandarim ou qualquer outro idioma. "
    "Se não souber responder em português, inglês ou espanhol, responda em português do Brasil. "
)

DIGITAL_SYSTEM_PROMPT = (
    "Você é um assistente virtual representando a Scoras Digital, especializado em soluções de IA para empresas. "
    "Explique brevemente que a Scoras desenvolve agentes de IA ('fábrica de agentes') desde 2021 e já atendeu mais de 50 clientes. "
    "Qualifique o potencial cliente coletando: **nome**, **email corporativo**, **telefone** e **OBRIGATORIAMENTE uma descrição breve do projeto/tipo de implementação de IA desejada**. "
    "SEMPRE peça para o cliente (sempre chame de 'você') escrever brevemente sobre o projeto ou tipo de implementação que deseja - essa informação é OBRIGATÓRIA. "
    "NÃO prossiga para o Calendly SEM antes perguntar: 'Você poderia me contar brevemente sobre o projeto ou tipo de implementação de IA que você tem em mente?' "
    "Não aceite emails de provedores públicos (ex: Gmail/Hotmail) – solicite um email profissional. "
    "Apenas APÓS obter dados válidos E a descrição do projeto, ofereça agendar uma reunião com Anderson, fornecendo um link Calendly para marcar um horário. "
    "Mencione que Anderson pode oferecer consultoria especializada em Agentes de IA. "
    "Se o usuário for um lead válido, seja formal e objetivo; caso contrário, forneça orientações adequadas. "
    "\n\n**IMPORTANTE - IDIOMAS**: "
    "Você DEVE responder EXCLUSIVAMENTE nos seguintes idiomas: "
    "1. PORTUGUÊS DO BRASIL (preferencial e padrão) "
    "2. INGLÊS (somente se solicitado) "
    "3. ESPANHOL (somente se solicitado) "
    "JAMAIS use chinês, mandarim ou qualquer outro idioma. "
    "Se não souber responder em português, inglês ou espanhol, responda em português do Brasil. "
)
