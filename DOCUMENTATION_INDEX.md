# 📚 **ÍNDICE DE DOCUMENTAÇÃO - SCORAS AI AGENT**

**Navegação completa de toda a documentação disponível**

---

## 🚀 **DOCUMENTAÇÃO PRINCIPAL**

### 📖 [README.md](README.md) - **COMEÇE AQUI**
- Visão geral completa do sistema
- Instruções de deploy em Azure VM Ubuntu 24
- Comandos básicos e troubleshooting
- Checklist de produção

### 🎯 [QUICK_START.md](QUICK_START.md) - **INÍCIO RÁPIDO**
- Comandos para iniciar o sistema rapidamente
- URLs importantes
- Teste básico de funcionalidade

---

## 🌐 **DEPLOY E INFRAESTRUTURA**

### 🏗️ [DEPLOY_AZURE_COMPLETE.md](DEPLOY_AZURE_COMPLETE.md) - **DEPLOY DETALHADO**
- Guia completo passo-a-passo para Azure VM
- Configuração de VM, redes, firewall
- Scripts de automação e monitoramento
- Backup e manutenção
- **ESSENCIAL para deploy em produção**

### 👥 [TEAM_REFERENCE.md](TEAM_REFERENCE.md) - **REFERÊNCIA RÁPIDA**
- Comandos essenciais para o dia-a-dia
- Troubleshooting rápido
- Checklist de verificação
- Escalação de problemas

---

## 📊 **ADMIN DASHBOARD**

### 🖥️ [ADMIN_DASHBOARD.md](ADMIN_DASHBOARD.md) - **DASHBOARD ADMIN**
- Documentação completa do painel administrativo
- Funcionalidades de monitoramento
- API endpoints
- Guia de uso

### 🌐 [admin_dashboard.html](admin_dashboard.html) - **INTERFACE ADMIN**
- Interface web do dashboard (arquivo HTML)
- Acesse em: `http://VM_IP:8001/admin`

---

## ⚙️ **CONFIGURAÇÃO E SCRIPTS**

### 🔧 [Makefile](Makefile) - **COMANDOS MAKE**
- Comandos de automação do sistema
- `make up`, `make down`, `make status`
- Scripts de build e deploy

### 🚀 [start_all.sh](start_all.sh) - **SCRIPT DE INICIALIZAÇÃO**
- Script principal para iniciar o sistema
- Verificações de dependências
- Gerenciamento de serviços

### 🛑 [stop_all.sh](stop_all.sh) - **SCRIPT DE PARADA**
- Script para parar todos os serviços
- Limpeza opcional de dados

### 🗄️ [setup_redis.sh](setup_redis.sh) - **SETUP REDIS**
- Configuração do container Redis
- Inicialização automática

---

## 🧪 **TESTES E VALIDAÇÃO**

### 🧪 [test_admin_system.py](test_admin_system.py) - **TESTES ADMIN**
- Testes automatizados do sistema admin
- Validação de endpoints
- Testes de integração

### 🔌 [test_connections.py](test_connections.py) - **TESTES CONEXÃO**
- Testes de conectividade Redis
- Validação de APIs Azure
- Diagnóstico de problemas

---

## 🤖 **CÓDIGO PRINCIPAL**

### 💬 [chat_api_with_redis.py](chat_api_with_redis.py) - **API CHAT PRINCIPAL**
- API principal do chatbot
- Integração com Redis para storage
- Lógica de classificação de leads

### 📊 [admin_dashboard.py](admin_dashboard.py) - **BACKEND ADMIN**
- Backend do dashboard administrativo
- APIs de monitoramento
- Gestão de conversas

### 🎯 [chat_api_simple_fixed.py](chat_api_simple_fixed.py) - **API CHAT SIMPLES**
- Versão simplificada da API
- Para testes e desenvolvimento

---

## 📁 **FRONTEND**

### 🌐 [frontend/](frontend/) - **INTERFACE DO USUÁRIO**
- `index.html` - Interface principal do chatbot
- `script.js` - Lógica JavaScript
- `style.css` - Estilos CSS
- `server.py` - Servidor Python do frontend

---

## 🔧 **CONFIGURAÇÃO E CONTEÚDO**

### ⚙️ [azure_llm_config.py](azure_llm_config.py) - **CONFIG AZURE**
- Configuração da Azure AI
- Modelos e endpoints

### 📚 [scoras_academy_content.py](scoras_academy_content.py) - **CONTEÚDO ACADEMY**
- Conteúdo para leads Academy
- Prompts e respostas

### 💼 [scoras_digital_content.py](scoras_digital_content.py) - **CONTEÚDO DIGITAL**
- Conteúdo para leads Digital
- Qualificação de leads

---

## 🐳 **DOCKER E CONTAINERS**

### 🐳 [docker-compose.yml](docker-compose.yml) - **DOCKER LOCAL**
- Configuração Docker para desenvolvimento local

### 🌐 [docker-compose.azure-vm.yml](docker-compose.azure-vm.yml) - **DOCKER AZURE**
- Configuração específica para Azure VM

### 📦 [Dockerfile](Dockerfile) - **IMAGEM DOCKER**
- Configuração da imagem Docker
- Dependências e setup

---

## 📋 **DEPENDÊNCIAS E REQUISITOS**

### 📦 [requirements.txt](requirements.txt) - **DEPENDÊNCIAS PYTHON**
- Lista de pacotes Python necessários
- Versões específicas

---

## 🗄️ **ARMAZENAMENTO E DADOS**

### 🗃️ [models.py](models.py) - **MODELOS DE DADOS**
- Estruturas de dados
- Schemas para Redis

### 🔍 [vector_search.py](vector_search.py) - **BUSCA VETORIAL**
- Funcionalidades de busca
- Integração com RAG

---

## 📝 **HISTÓRICO E BACKUP**

### 📜 [README_backup.md](README_backup.md) - **BACKUP README**
- Versão anterior do README
- Histórico de mudanças

### 🗄️ [logs/](logs/) - **LOGS DO SISTEMA**
- Diretório de logs da aplicação
- Histórico de atividades

---

## 🎯 **COMO USAR ESTA DOCUMENTAÇÃO**

### 👨‍💻 **Para Desenvolvedores**
1. Começar com [QUICK_START.md](QUICK_START.md)
2. Entender o sistema via [README.md](README.md)
3. Consultar [TEAM_REFERENCE.md](TEAM_REFERENCE.md) para comandos

### 🚀 **Para Deploy em Produção**
1. Seguir [DEPLOY_AZURE_COMPLETE.md](DEPLOY_AZURE_COMPLETE.md)
2. Usar [Makefile](Makefile) para automação
3. Configurar monitoramento via [ADMIN_DASHBOARD.md](ADMIN_DASHBOARD.md)

### 🔧 **Para Operação Diária**
1. Usar [TEAM_REFERENCE.md](TEAM_REFERENCE.md) como guia
2. Comandos `make` para operações básicas
3. Dashboard admin para monitoramento

### 🆘 **Para Troubleshooting**
1. [TEAM_REFERENCE.md](TEAM_REFERENCE.md) - Problemas comuns
2. [test_connections.py](test_connections.py) - Diagnóstico
3. Logs em `logs/` - Análise detalhada

---

## 📞 **SUPORTE**

### 📧 **Contato**
- **Email**: admin@scoras.com.br
- **Website**: https://scoras.com.br

### 📁 **Arquivos de Log**
- **Aplicação**: `/home/scoras/apps/scoras-ai-agent/logs/`
- **Sistema**: `sudo journalctl -u scoras-ai-agent`

### 🔗 **URLs Importantes**
- **Chatbot**: `http://VM_IP:3000`
- **Admin**: `http://VM_IP:8001/admin`
- **API**: `http://VM_IP:8000/docs`

---

**Esta documentação é mantida pela equipe Scoras Digital**  
**Última atualização**: Janeiro 2025 