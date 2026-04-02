# 👨‍💻 Guia de Desenvolvimento - Scoras Academy Agent

## 🚀 Setup do Ambiente de Desenvolvimento

### 📋 Pré-requisitos

- **Python 3.10+** - Linguagem principal
- **Docker** - Para Redis container
- **Git** - Controle de versão
- **Node.js** (opcional) - Para ferramentas de desenvolvimento

### 🔧 Instalação Rápida

```bash
# 1. Clone o repositório
git clone https://github.com/scorastecnologialtda/scoras_academy_agent.git
cd scoras_academy_agent

# 2. Crie o ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure as variáveis de ambiente
cp .env.example .env
# Edite o .env com suas credenciais Azure AI

# 5. Inicie o Redis
docker run -d --name scoras-redis -p 6379:6379 redis:alpine

# 6. Inicie todos os serviços
chmod +x start_all.sh
./start_all.sh
```

## 🏗️ Estrutura do Projeto

```
scoras_academy_agent/
├── 📁 frontend/                    # Interface do usuário
│   ├── index.html                  # Página principal
│   ├── style.css                   # Estilos modernos
│   ├── script.js                   # Lógica do cliente
│   └── server.py                   # Servidor de desenvolvimento
├── 📁 admin_dashboard/             # Dashboard administrativo
│   ├── admin_dashboard.py          # Backend do dashboard
│   └── admin_dashboard.html        # Interface administrativa
├── 📁 logs/                        # Logs do sistema
│   ├── chat_api.log
│   ├── admin_dashboard.log
│   └── frontend.log
├── 📁 docs/                        # Documentação (você está aqui!)
│   ├── ARCHITECTURE.md
│   ├── DEVELOPMENT.md
│   └── API_REFERENCE.md
├── 🐍 chat_api_with_redis.py       # API principal
├── 🔧 requirements.txt             # Dependências Python
├── 🚀 start_all.sh                 # Script de inicialização
├── 🛑 stop_all.sh                  # Script de parada
├── 📋 .env.example                 # Template de configuração
├── 📖 README.md                    # Documentação principal
├── 📝 CHANGELOG.md                 # Histórico de versões
└── 🏗️ ARCHITECTURE.md             # Documentação de arquitetura
```

## 🛠️ Comandos de Desenvolvimento

### Inicialização
```bash
# Iniciar todos os serviços
./start_all.sh

# Iniciar serviços individualmente
python chat_api_with_redis.py              # API na porta 8003
python admin_dashboard/admin_dashboard.py  # Dashboard na porta 8002
cd frontend && python server.py --port 3001  # Frontend na porta 3001
```

### Debugging
```bash
# Ver logs em tempo real
tail -f logs/chat_api.log
tail -f logs/admin_dashboard.log
tail -f logs/frontend.log

# Verificar status dos serviços
curl http://localhost:8003/health    # API Health Check
curl http://localhost:3001           # Frontend
curl http://localhost:8002/admin     # Dashboard
```

### Testes
```bash
# Teste manual da API
curl -X POST http://localhost:8003/chat-simple \
  -H "Content-Type: application/json" \
  -d '{"message": "Oi, quais cursos vocês têm?", "user_id": "test_dev"}'

# Teste do Redis
docker exec -it scoras-redis redis-cli ping

# Verificar dados no Redis
docker exec -it scoras-redis redis-cli keys "*"
```

## 🔧 Configuração Detalhada

### Arquivo .env
```bash
# Azure AI Configuration
AZURE_AI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_AI_API_KEY=your-secret-key-here
AZURE_AI_MODEL=DeepSeek-V3-0324

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password (opcional)

# System Configuration
ENVIRONMENT=development
LOG_LEVEL=DEBUG
API_BASE_URL=http://localhost:8003
```

### Dependências Python
```python
# Core Framework
fastapi>=0.104.0           # API framework
uvicorn>=0.24.0            # ASGI server

# AI & Data
azure-ai-inference>=1.0.0  # Azure AI client
redis>=5.0.0               # Redis client

# Utilities
python-dotenv>=1.0.0       # Environment variables
pydantic>=2.5.0            # Data validation
```

## 🧪 Testing e Debugging

### Debug Mode
```python
# Para debug detalhado, modifique chat_api_with_redis.py
import logging
logging.basicConfig(level=logging.DEBUG)

# Ou inicie com:
uvicorn chat_api_with_redis:app --host 0.0.0.0 --port 8003 --reload --log-level debug
```

### Teste de Carga
```bash
# Instalar ferramentas de teste
pip install pytest httpx

# Teste simples de carga
for i in {1..10}; do
  curl -X POST http://localhost:8003/chat-simple \
    -H "Content-Type: application/json" \
    -d "{\"message\": \"teste $i\", \"user_id\": \"load_test_$i\"}" &
done
```

### Monitoramento Redis
```bash
# Monitor em tempo real
docker exec -it scoras-redis redis-cli monitor

# Estatísticas
docker exec -it scoras-redis redis-cli info stats

# Verificar memória
docker exec -it scoras-redis redis-cli memory usage conversation:test_user
```

## 🎨 Desenvolvimento Frontend

### Live Reload
```bash
# Para desenvolvimento com auto-reload
cd frontend
python server.py --port 3001 --no-browser

# Em outro terminal, watch para mudanças
# (instale inotify-tools no Linux)
while inotifywait -e modify style.css script.js index.html; do
  echo "Files changed, refresh browser"
done
```

### Debugging JavaScript
```javascript
// Adicione no script.js para debug
console.log('CONFIG:', CONFIG);
console.log('Current conversation ID:', conversationId);

// Teste API diretamente no console do navegador
fetch('http://localhost:8003/health')
  .then(r => r.json())
  .then(console.log);
```

### CSS Development
```css
/* Para debugging visual, adicione temporariamente: */
* {
  border: 1px solid red !important;
}

/* Para visualizar grid/flexbox: */
.app-container {
  background: repeating-linear-gradient(
    45deg,
    transparent,
    transparent 10px,
    rgba(255,0,0,0.1) 10px,
    rgba(255,0,0,0.1) 20px
  );
}
```

## 🔄 Workflow de Desenvolvimento

### 1. Feature Development
```bash
# 1. Criar branch para feature
git checkout -b feature/nova-funcionalidade

# 2. Desenvolver e testar
./start_all.sh
# ... desenvolver ...

# 3. Testar localmente
curl http://localhost:8003/health

# 4. Commit e push
git add .
git commit -m "feat: adiciona nova funcionalidade"
git push origin feature/nova-funcionalidade
```

### 2. Debugging Workflow
```bash
# 1. Reproduzir o problema
./start_all.sh

# 2. Verificar logs
tail -f logs/chat_api.log | grep ERROR

# 3. Teste isolado
python -c "
import redis
r = redis.Redis(host='localhost', port=6379)
print(r.ping())
"

# 4. Fix e teste
# ... corrigir código ...
./stop_all.sh
./start_all.sh
```

### 3. Performance Optimization
```bash
# Profiling da API
pip install py-spy
py-spy top --pid $(pgrep -f chat_api_with_redis)

# Análise de memória Redis
docker exec -it scoras-redis redis-cli --bigkeys

# Monitor de requisições
tail -f logs/chat_api.log | grep "POST /chat-simple"
```

## 🐛 Troubleshooting Comum

### Problema: Porta já em uso
```bash
# Encontrar processo usando a porta
lsof -i :8003
kill -9 <PID>

# Ou usar nosso script
./stop_all.sh
```

### Problema: Redis não conecta
```bash
# Verificar se Redis está rodando
docker ps | grep redis

# Restart Redis
docker restart scoras-redis

# Verificar logs
docker logs scoras-redis
```

### Problema: Azure AI não responde
```bash
# Testar credenciais
curl -H "Authorization: Bearer $AZURE_AI_API_KEY" \
     "$AZURE_AI_ENDPOINT/openai/deployments/$AZURE_AI_MODEL/chat/completions?api-version=2024-05-01-preview"
```

### Problema: Frontend não carrega estilos
```bash
# Verificar servidor frontend
curl -I http://localhost:3001/style.css

# Limpar cache do navegador
# Ctrl+Shift+R (hard refresh)

# Verificar CORS
curl -H "Origin: http://localhost:3001" http://localhost:8003/health
```

## 📊 Métricas de Desenvolvimento

### Performance Targets
- **API Response Time**: < 2 segundos
- **Frontend Load Time**: < 1 segundo
- **Redis Operations**: < 10ms
- **Memory Usage**: < 500MB total

### Code Quality
```bash
# Linting (futuro)
pip install black flake8
black . --check
flake8 .

# Type checking (futuro)
pip install mypy
mypy chat_api_with_redis.py
```

## 🚀 Deploy de Desenvolvimento

### Docker Development
```dockerfile
# Dockerfile.dev
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 3001 8002 8003
CMD ["./start_all.sh"]
```

```bash
# Build e run
docker build -f Dockerfile.dev -t scoras-academy-dev .
docker run -p 3001:3001 -p 8002:8002 -p 8003:8003 scoras-academy-dev
```

---

## 📞 Suporte para Desenvolvedores

### Contatos
- **Tech Lead**: anderson@scoras.com.br
- **GitHub Issues**: Para bugs e features
- **Slack**: #scoras-academy-dev (interno)

### Recursos Úteis
- **Azure AI Docs**: [docs.microsoft.com/azure/ai](https://docs.microsoft.com/azure/ai)
- **FastAPI Docs**: [fastapi.tiangolo.com](https://fastapi.tiangolo.com)
- **Redis Docs**: [redis.io/documentation](https://redis.io/documentation)

---

<div align="center">

**🎓 Happy Coding!**

*Desenvolvendo o futuro da Engenharia de IA*

</div> 