#!/bin/bash

# =============================================================================
# 🚀 SCORAS AI AGENT - DOCKER STARTUP SCRIPT
# =============================================================================
# Inicia os serviços principais (Chat API, Admin Dashboard, Frontend)
# Assumindo que o Redis já está disponível em redis://localhost:6379/0
# =============================================================================

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

log_info "Criando diretório de logs..."
mkdir -p logs

log_info "Iniciando Chat API (porta 8000)..."
export REDIS_URL="redis://localhost:6379/0"
nohup python chat_api_with_redis.py > logs/chat_api.log 2>&1 &
CHAT_API_PID=$!
sleep 5
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    log_success "Chat API funcionando (PID: $CHAT_API_PID)"
else
    log_error "Falha ao iniciar Chat API"
    log_info "Verificar logs em: logs/chat_api.log"
fi

log_info "Iniciando Admin Dashboard (porta 8001)..."
nohup python admin_dashboard.py > logs/admin_dashboard.log 2>&1 &
ADMIN_PID=$!
sleep 5
if curl -s http://localhost:8001/admin | grep -q "Dashboard" 2>/dev/null; then
    log_success "Admin Dashboard funcionando (PID: $ADMIN_PID)"
else
    log_error "Falha ao iniciar Admin Dashboard"
    log_info "Verificar logs em: logs/admin_dashboard.log"
fi

log_info "Iniciando Frontend Chat Interface (porta 3000)..."
cd frontend
nohup python server.py > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
sleep 3
if curl -s -I http://localhost:3000 | grep -q "200 OK"; then
    log_success "Frontend funcionando (PID: $FRONTEND_PID)"
else
    log_error "Falha ao iniciar Frontend"
    log_info "Verificar logs em: logs/frontend.log"
fi

log_info "Sistema iniciado!"

# Exibe status final
log_info "Chat API: PID $CHAT_API_PID"
log_info "Admin Dashboard: PID $ADMIN_PID"
log_info "Frontend: PID $FRONTEND_PID"

# Aguarda todos os serviços terminarem para manter o container vivo
wait
