#!/bin/bash

# =============================================================================
# 🚀 SCORAS AI AGENT - STARTUP SCRIPT
# =============================================================================
# Inicia todos os serviços necessários para o sistema completo
# - Chat API (port 8000) - Backend principal com Redis
# - Admin Dashboard (port 8001) - Monitoramento e gestão
# - Frontend Chat (port 3000) - Interface do usuário
# - Redis Container - Armazenamento de conversas
# =============================================================================

echo "═══════════════════════════════════════════════════════════════"
echo "          🤖 SCORAS AI AGENT - SISTEMA COMPLETO"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para log colorido
log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# =============================================================================
# 1. VERIFICAÇÕES INICIAIS
# =============================================================================

log_info "Verificando dependências..."

# Verificar se Docker está instalado e rodando
if ! command -v docker &> /dev/null; then
    log_error "Docker não encontrado! Instale o Docker primeiro."
    exit 1
fi

if ! docker info &> /dev/null; then
    log_error "Docker não está rodando! Execute: sudo systemctl start docker"
    exit 1
fi

log_success "Docker está funcionando"

# Verificar se Python está disponível
if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
    log_error "Python não encontrado! Instale Python 3.11+"
    exit 1
fi

# Usar python3 se python não estiver disponível
PYTHON_CMD="python"
if ! command -v python &> /dev/null; then
    PYTHON_CMD="python3"
fi

log_success "Python encontrado: $($PYTHON_CMD --version)"

# Verificar se pip está disponível
if ! command -v pip &> /dev/null; then
    log_warning "pip não encontrado. Tentando instalar dependências com $PYTHON_CMD -m pip"
fi

# =============================================================================
# 2. PARAR PROCESSOS EXISTENTES
# =============================================================================

log_info "Parando processos existentes..."

# Parar processos Python nas portas específicas
pkill -f "chat_api_with_redis" 2>/dev/null
pkill -f "admin_dashboard" 2>/dev/null
pkill -f "port.*8000" 2>/dev/null
pkill -f "port.*8001" 2>/dev/null
pkill -f "port.*3000" 2>/dev/null

# Dar tempo para os processos terminarem
sleep 2

log_success "Processos anteriores terminados"

# =============================================================================
# 3. INICIAR REDIS CONTAINER
# =============================================================================

log_info "Iniciando Redis Container..."

# Verificar se container já existe
if docker ps -a --format 'table {{.Names}}' | grep -q "scoras-redis"; then
    log_info "Container Redis já existe. Iniciando..."
    docker start scoras-redis
else
    log_info "Criando novo container Redis..."
    docker run -d \
        --name scoras-redis \
        -p 6379:6379 \
        redis:7-alpine \
        redis-server --save 60 1 --loglevel warning
fi

# Aguardar Redis inicializar
log_info "Aguardando Redis inicializar..."
sleep 5

# Testar conexão Redis
if docker exec scoras-redis redis-cli ping | grep -q "PONG"; then
    log_success "Redis está funcionando"
else
    log_error "Falha ao iniciar Redis"
    exit 1
fi

# =============================================================================
# 4. INSTALAR DEPENDÊNCIAS PYTHON
# =============================================================================

log_info "Verificando dependências Python..."

# Lista de dependências necessárias
dependencies=(
    "fastapi"
    "uvicorn"
    "redis"
    "azure-ai-inference"
    "pydantic"
    "python-dotenv"
)

for dep in "${dependencies[@]}"; do
    if ! $PYTHON_CMD -c "import ${dep//-/_}" 2>/dev/null; then
        log_info "Instalando $dep..."
        pip install $dep
    fi
done

log_success "Dependências verificadas"

# =============================================================================
# 5. VERIFICAR VARIÁVEIS DE AMBIENTE
# =============================================================================

log_info "Verificando configurações..."

# Verificar se .env existe
if [ ! -f ".env" ]; then
    log_warning "Arquivo .env não encontrado. Criando arquivo de exemplo..."
    cat > .env << EOF
# Azure AI Configuration
AZURE_ENDPOINT=https://ai-andersonai017430836643.services.ai.azure.com/models
AZURE_API_KEY=sua_chave_azure_aqui
AZURE_API_VERSION=2024-05-01-preview
DEEPSEEK_MODEL=DeepSeek-V3-0324

# Redis Configuration (Local)
REDIS_URL=redis://localhost:6379/0

# Environment
ENVIRONMENT=development
EOF
    log_warning "Configure suas chaves Azure no arquivo .env antes de continuar"
fi

# Verificar se chaves Azure estão configuradas
if grep -q "sua_chave_azure_aqui" .env 2>/dev/null; then
    log_warning "Configure suas chaves Azure no arquivo .env para funcionalidade completa"
fi

log_success "Configurações verificadas"

# =============================================================================
# 6. CRIAR DIRETÓRIO DE LOGS E INICIAR CHAT API (PORTA 8000)
# =============================================================================

log_info "Criando diretório de logs..."
mkdir -p logs

log_info "Iniciando Chat API (porta 8000)..."

# Exportar variável Redis para garantir conexão local
export REDIS_URL="redis://localhost:6379/0"

# Iniciar Chat API em background
nohup $PYTHON_CMD chat_api_with_redis.py > logs/chat_api.log 2>&1 &
CHAT_API_PID=$!

# Aguardar inicialização
sleep 5

# Verificar se está funcionando
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    log_success "Chat API funcionando (PID: $CHAT_API_PID)"
else
    log_error "Falha ao iniciar Chat API"
    log_info "Verificar logs em: logs/chat_api.log"
fi

# =============================================================================
# 7. INICIAR ADMIN DASHBOARD (PORTA 8001)
# =============================================================================

log_info "Iniciando Admin Dashboard (porta 8001)..."

# Iniciar Admin Dashboard em background
nohup $PYTHON_CMD admin_dashboard.py > logs/admin_dashboard.log 2>&1 &
ADMIN_PID=$!

# Aguardar inicialização
sleep 5

# Verificar se está funcionando
if curl -s http://localhost:8001/admin | grep -q "Dashboard" 2>/dev/null; then
    log_success "Admin Dashboard funcionando (PID: $ADMIN_PID)"
else
    log_error "Falha ao iniciar Admin Dashboard"
    log_info "Verificar logs em: logs/admin_dashboard.log"
fi

# =============================================================================
# 8. INICIAR FRONTEND (PORTA 3000)
# =============================================================================

log_info "Iniciando Frontend Chat Interface (porta 3000)..."

# Entrar no diretório frontend
cd frontend

# Iniciar Frontend em background
nohup $PYTHON_CMD server.py --port 3001 --no-browser > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!

# Voltar ao diretório principal
cd ..

# Aguardar inicialização
sleep 3

# Verificar se está funcionando
if curl -s -I http://localhost:3000 | grep -q "200 OK"; then
    log_success "Frontend funcionando (PID: $FRONTEND_PID)"
else
    log_error "Falha ao iniciar Frontend"
    log_info "Verificar logs em: logs/frontend.log"
fi

# =============================================================================
# 9. TESTE FINAL DO SISTEMA
# =============================================================================

log_info "Testando sistema completo..."

# Teste Chat API
if curl -s -X POST http://localhost:8000/chat-simple \
    -H "Content-Type: application/json" \
    -d '{"message": "teste"}' | grep -q "response"; then
    log_success "Chat API respondendo corretamente"
else
    log_warning "Chat API pode ter problemas"
fi

# Teste Admin Dashboard
if curl -s http://localhost:8001/admin/analytics/overview | grep -q "overview"; then
    log_success "Admin Dashboard funcionando"
else
    log_warning "Admin Dashboard pode ter problemas"
fi

# =============================================================================
# 10. EXIBIR STATUS FINAL
# =============================================================================

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "                    🎉 SISTEMA INICIADO!"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "📱 INTERFACES DISPONÍVEIS:"
echo ""
echo "🤖 Chatbot Interface:"
echo "   👉 http://localhost:3000"
echo "   📝 Interface principal para usuários"
echo ""
echo "📊 Admin Dashboard:"
echo "   👉 http://localhost:8001/admin"
echo "   📈 Monitoramento de conversas e Redis"
echo ""
echo "⚙️  Chat API:"
echo "   👉 http://localhost:8000"
echo "   🔧 API backend com documentação em /docs"
echo ""
echo "🗄️  Redis Database:"
echo "   👉 localhost:6379"
echo "   💾 Armazenamento de conversas"
echo ""
echo "📋 PROCESSOS RODANDO:"
echo "   Chat API: PID $CHAT_API_PID"
echo "   Admin Dashboard: PID $ADMIN_PID"
echo "   Frontend: PID $FRONTEND_PID"
echo ""
echo "📁 LOGS DISPONÍVEIS:"
echo "   Chat API: logs/chat_api.log"
echo "   Admin Dashboard: logs/admin_dashboard.log"
echo "   Frontend: logs/frontend.log"
echo ""
echo "🛑 Para parar todos os serviços, execute:"
echo "   ./stop_all.sh"
echo ""
echo "═══════════════════════════════════════════════════════════════"

# Salvar PIDs para o script de parada
mkdir -p .pids
echo $CHAT_API_PID > .pids/chat_api.pid
echo $ADMIN_PID > .pids/admin_dashboard.pid
echo $FRONTEND_PID > .pids/frontend.pid 