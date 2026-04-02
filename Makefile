# =============================================================================
# 🚀 SCORAS AI AGENT - MAKEFILE
# =============================================================================
# Comandos simples para gerenciar o sistema Scoras AI Agent
# =============================================================================

.PHONY: help up down restart status logs clean install deploy-scoras

# Comando padrão
help:
	@echo "═══════════════════════════════════════════════════════════════"
	@echo "          🤖 SCORAS AI AGENT - COMANDOS DISPONÍVEIS"
	@echo "═══════════════════════════════════════════════════════════════"
	@echo ""
	@echo "📋 COMANDOS PRINCIPAIS:"
	@echo "  make up        - 🚀 Iniciar todo o sistema"
	@echo "  make down      - 🛑 Parar todo o sistema"
	@echo "  make restart   - 🔄 Reiniciar todo o sistema"
	@echo "  make status    - 📊 Verificar status dos serviços"
	@echo ""
	@echo "📁 COMANDOS DE MONITORAMENTO:"
	@echo "  make logs      - 📖 Ver logs de todos os serviços"
	@echo "  make logs-chat - 📖 Ver logs do Chat API"
	@echo "  make logs-admin - 📖 Ver logs do Admin Dashboard"
	@echo "  make logs-frontend - 📖 Ver logs do Frontend"
	@echo ""
	@echo "🔧 COMANDOS DE MANUTENÇÃO:"
	@echo "  make install   - 📦 Instalar dependências"
	@echo "  make clean     - 🧹 Limpar logs e arquivos temporários"
	@echo "  make redis     - 🗄️  Verificar status do Redis"
	@echo ""
	@echo "🌐 INTERFACES DISPONÍVEIS (após make up):"
	@echo "  http://localhost:3000      - 🤖 Chatbot Interface"
	@echo "  http://localhost:8001/admin - 📊 Admin Dashboard"
	@echo "  http://localhost:8000/docs  - 📚 API Documentation"
	@echo ""
	@echo "═══════════════════════════════════════════════════════════════"

# Iniciar todo o sistema
up:
	@echo "🚀 Iniciando Scoras AI Agent..."
	@chmod +x start_all.sh
	@./start_all.sh

# Parar todo o sistema
down:
	@echo "🛑 Parando Scoras AI Agent..."
	@chmod +x stop_all.sh
	@./stop_all.sh

# Reiniciar sistema
restart: down up
	@echo "🔄 Sistema reiniciado!"

# Verificar status
status:
	@echo "📊 Status dos Serviços:"
	@echo ""
	@echo "🤖 Chat API (porta 8000):"
	@curl -s http://localhost:8000/health 2>/dev/null | grep -q "healthy" && echo "  ✅ Funcionando" || echo "  ❌ Não está respondendo"
	@echo ""
	@echo "📊 Admin Dashboard (porta 8001):"
	@curl -s http://localhost:8001/admin 2>/dev/null | grep -q "Dashboard" && echo "  ✅ Funcionando" || echo "  ❌ Não está respondendo"
	@echo ""
	@echo "🌐 Frontend (porta 3000):"
	@curl -s -I http://localhost:3000 2>/dev/null | grep -q "200 OK" && echo "  ✅ Funcionando" || echo "  ❌ Não está respondendo"
	@echo ""
	@echo "🗄️  Redis Container:"
	@docker ps --format 'table {{.Names}}\t{{.Status}}' | grep scoras-redis || echo "  ❌ Container não encontrado"

# Ver todos os logs
logs:
	@echo "📖 Logs dos Serviços (Ctrl+C para sair):"
	@mkdir -p logs
	@tail -f logs/*.log 2>/dev/null || echo "Nenhum log encontrado. Execute 'make up' primeiro."

# Ver logs específicos
logs-chat:
	@echo "📖 Logs do Chat API:"
	@tail -f logs/chat_api.log 2>/dev/null || echo "Log não encontrado"

logs-admin:
	@echo "📖 Logs do Admin Dashboard:"
	@tail -f logs/admin_dashboard.log 2>/dev/null || echo "Log não encontrado"

logs-frontend:
	@echo "📖 Logs do Frontend:"
	@tail -f logs/frontend.log 2>/dev/null || echo "Log não encontrado"

# Instalar dependências
install:
	@echo "📦 Instalando dependências..."
	@pip install fastapi uvicorn redis azure-ai-inference pydantic python-dotenv
	@echo "✅ Dependências instaladas!"

# Limpeza
clean:
	@echo "🧹 Limpando arquivos temporários..."
	@rm -rf logs/*.log 2>/dev/null || true
	@rm -rf .pids 2>/dev/null || true
	@rm -rf __pycache__ 2>/dev/null || true
	@find . -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Limpeza concluída!"

# Verificar Redis
redis:
	@echo "🗄️  Status do Redis:"
	@docker exec scoras-redis redis-cli ping 2>/dev/null && echo "✅ Redis funcionando" || echo "❌ Redis não está respondendo"
	@echo "📊 Estatísticas do Redis:"
	@docker exec scoras-redis redis-cli info memory 2>/dev/null | grep used_memory_human || echo "Não foi possível obter estatísticas"
	@echo "🔑 Chaves armazenadas:"
	@docker exec scoras-redis redis-cli dbsize 2>/dev/null || echo "Não foi possível obter informações"

# Comando para desenvolvimento - iniciar apenas um serviço
dev-chat:
	@echo "🚀 Iniciando apenas Chat API para desenvolvimento..."
	@REDIS_URL="redis://localhost:6379/0" python chat_api_with_redis.py

dev-admin:
	@echo "🚀 Iniciando apenas Admin Dashboard para desenvolvimento..."
	@REDIS_URL="redis://localhost:6379/0" python admin_dashboard.py

dev-frontend:
	@echo "🚀 Iniciando apenas Frontend para desenvolvimento..."
	@cd frontend && python server.py 
deploy-scoras:
	az login
	az acr login --name scorascontainer
	docker build -t scoras-agent .
	docker tag scoras-agent scorascontainer.azurecr.io/scoras-agent
	docker push scorascontainer.azurecr.io/scoras-agent
	# Build, tag e push do frontend
	docker build -t scoras-agent-frontend -f frontend/Dockerfile frontend
	docker tag scoras-agent-frontend scorascontainer.azurecr.io/scoras-agent-frontend
	docker push scorascontainer.azurecr.io/scoras-agent-frontend
	# Build, tag e push do admin_dashboard
	docker build -t scoras-agent-admin-dashboard -f admin_dashboard/Dockerfile admin_dashboard
	docker tag scoras-agent-admin-dashboard scorascontainer.azurecr.io/scoras-agent-admin-dashboard
	docker push scorascontainer.azurecr.io/scoras-agent-admin-dashboard