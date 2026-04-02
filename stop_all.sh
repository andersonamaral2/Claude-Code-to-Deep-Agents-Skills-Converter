#!/bin/bash

# =============================================================================
# 🛑 SCORAS AI AGENT - STOP SCRIPT
# =============================================================================
# Para todos os serviços do sistema Scoras AI Agent
# =============================================================================

echo "═══════════════════════════════════════════════════════════════"
echo "         🛑 PARANDO SCORAS AI AGENT - SISTEMA COMPLETO"
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
# 1. PARAR PROCESSOS PYTHON
# =============================================================================

log_info "Parando serviços Python..."

# Parar usando PIDs salvos se existirem
if [ -d ".pids" ]; then
    if [ -f ".pids/chat_api.pid" ]; then
        CHAT_PID=$(cat .pids/chat_api.pid)
        if kill $CHAT_PID 2>/dev/null; then
            log_success "Chat API parado (PID: $CHAT_PID)"
        fi
    fi
    
    if [ -f ".pids/admin_dashboard.pid" ]; then
        ADMIN_PID=$(cat .pids/admin_dashboard.pid)
        if kill $ADMIN_PID 2>/dev/null; then
            log_success "Admin Dashboard parado (PID: $ADMIN_PID)"
        fi
    fi
    
    if [ -f ".pids/frontend.pid" ]; then
        FRONTEND_PID=$(cat .pids/frontend.pid)
        if kill $FRONTEND_PID 2>/dev/null; then
            log_success "Frontend parado (PID: $FRONTEND_PID)"
        fi
    fi
    
    # Limpar PIDs
    rm -rf .pids
fi

# Forçar parada de processos por nome (fallback)
pkill -f "chat_api_with_redis" 2>/dev/null
pkill -f "admin_dashboard" 2>/dev/null
pkill -f "server.py" 2>/dev/null
pkill -f "port.*8000" 2>/dev/null
pkill -f "port.*8001" 2>/dev/null
pkill -f "port.*3000" 2>/dev/null

log_success "Processos Python terminados"

# =============================================================================
# 2. PARAR REDIS CONTAINER (OPCIONAL)
# =============================================================================

log_info "Gerenciando Redis Container..."

# Perguntar se deve parar o Redis
echo "Parar Redis Container? (S/n):"
read -r STOP_REDIS

if [[ $STOP_REDIS =~ ^[Ss]$ ]] || [[ -z $STOP_REDIS ]]; then
    if docker ps --format 'table {{.Names}}' | grep -q "scoras-redis"; then
        docker stop scoras-redis
        log_success "Redis Container parado"
    else
        log_info "Redis Container já estava parado"
    fi
else
    log_info "Redis Container mantido rodando"
fi

# =============================================================================
# 3. VERIFICAR STATUS
# =============================================================================

log_info "Verificando se serviços foram parados..."

# Verificar portas
PORTS_IN_USE=0

if ss -tuln | grep -q ":8000 "; then
    log_warning "Porta 8000 ainda em uso"
    PORTS_IN_USE=1
fi

if ss -tuln | grep -q ":8001 "; then
    log_warning "Porta 8001 ainda em uso"
    PORTS_IN_USE=1
fi

if ss -tuln | grep -q ":3000 "; then
    log_warning "Porta 3000 ainda em uso"
    PORTS_IN_USE=1
fi

if [ $PORTS_IN_USE -eq 0 ]; then
    log_success "Todas as portas foram liberadas"
else
    log_warning "Algumas portas ainda estão em uso. Execute 'netstat -tulpn | grep \":8000\\|:8001\\|:3000\"' para verificar"
fi

# =============================================================================
# 4. LIMPEZA FINAL
# =============================================================================

log_info "Limpeza final..."

# Limpar logs antigos se solicitado
echo "Limpar logs? (s/N):"
read -r CLEAR_LOGS

if [[ $CLEAR_LOGS =~ ^[Ss]$ ]]; then
    if [ -d "logs" ]; then
        rm -f logs/*.log
        log_success "Logs limpos"
    fi
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "                 ✅ SISTEMA PARADO COM SUCESSO!"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Para reiniciar o sistema, execute:"
echo "   ./start_all.sh"
echo ""
echo "═══════════════════════════════════════════════════════════════" 