# 📊 Admin Dashboard - Scoras AI Agent

**Dashboard administrativo completo para monitoramento e gerenciamento do chatbot Scoras AI Agent**

## 🎯 Visão Geral

O Admin Dashboard é uma interface web moderna e user-friendly que permite monitorar todas as conversas do chatbot, visualizar métricas em tempo real, executar queries no Redis e gerenciar o sistema de forma intuitiva.

## 🚀 Início Rápido

### 1. Inicialização Completa

```bash
# Iniciar chat API + admin dashboard simultaneamente
python start_admin.py
```

### 2. Inicialização Separada

```bash
# Terminal 1: Chat API (porta 8000)
python chat_api_rag_fixed.py

# Terminal 2: Admin Dashboard (porta 8001)
python admin_dashboard.py
```

### 3. Testar Sistema

```bash
# Executar testes completos
python test_admin_system.py
```

## 🌐 URLs de Acesso

| Serviço | URL | Descrição |
|---------|-----|-----------|
| **Admin Dashboard** | http://localhost:8001/admin | Interface principal |
| **Chat API** | http://localhost:8000 | API do chatbot |
| **API Docs** | http://localhost:8000/docs | Documentação OpenAPI |
| **Health Check** | http://localhost:8000/health | Status do sistema |

## 📱 Funcionalidades do Dashboard

### 📊 Overview (Métricas Gerais)

- **Total de Conversas**: Número total de conversas registradas
- **Leads Qualificados**: Quantidade de leads com dados completos
- **Taxa de Qualificação**: Percentual de conversão
- **Leads Academy vs Digital**: Distribuição por tipo
- **Atividade Recente**: Conversas por período (hoje, ontem, semana)
- **Status Redis**: Uso de memória e estatísticas

### 💬 Gestão de Conversas

#### Filtros Avançados
- **Busca por Texto**: ID, nome, telefone, email
- **Tipo de Lead**: Academy, Digital, Todos
- **Status de Qualificação**: Qualificados, Não qualificados, Todos
- **Período**: Filtro por data (em desenvolvimento)

#### Lista de Conversas
- **User ID**: Identificador único da conversa
- **Nome**: Nome do lead (se qualificado)
- **Tipo**: Badge colorido (Academy = azul, Digital = amarelo)
- **Mensagens**: Quantidade total de mensagens
- **Qualificado**: Status com badge (Sim = verde, Não = vermelho)
- **Última Atividade**: Data/hora da última interação
- **Ações**: Ver detalhes | Deletar conversa

#### Visualização de Detalhes
- **Dados de Qualificação**: JSON estruturado com informações do lead
- **Metadados**: Informações técnicas (TTL, chaves Redis, timestamps)
- **Histórico de Mensagens**: Timeline completa da conversa
  - Mensagens do usuário (azul)
  - Respostas do assistente (cinza)
  - Timestamps formatados
  - Conteúdo completo preservado

### 🔧 Redis Console

#### Console Interativo
- **Interface tipo terminal**: Background escuro, fonte monospace
- **Execução via Enter**: Digite comando e pressione Enter
- **Comandos Seguros**: Apenas leitura e consultas permitidas
- **Output Formatado**: JSON pretty-print automático
- **Histórico Visível**: Log de comandos executados

#### Comandos Disponíveis
```bash
# Listar chaves
KEYS conversation:*
KEYS qualification:*

# Obter dados
GET conversation:user-123
GET qualification:user-123

# Informações do Redis
INFO memory
INFO stats
DBSIZE

# Listas
LRANGE conversation:user-123 0 -1
LLEN conversation:user-123

# TTL e tipos
TTL conversation:user-123
TYPE conversation:user-123

# Scan (para grandes volumes)
SCAN 0 MATCH conversation:* COUNT 100
```

#### Informações Detalhadas do Redis
- **Servidor**: Versão, uptime
- **Memória**: Uso atual, pico de uso
- **Clientes**: Conexões ativas
- **Estatísticas**: Ops/segundo, cache hits/misses, total de chaves

## 🎨 Interface e UX

### Design System
- **Cores Principais**: Azul (#2563eb), cinza (#64748b)
- **Typography**: Inter, sistema nativo
- **Espaçamento**: Grid consistente 8px
- **Bordas**: Radius 8-12px
- **Shadows**: Sutil, elevação progressiva

### Componentes UI
- **Cards**: Container principal com shadow
- **Badges**: Status coloridos (sucesso, aviso, erro, info)
- **Buttons**: Hover effects, estados ativos
- **Modal**: Overlay responsivo para detalhes
- **Table**: Hover rows, headers fixos
- **Navigation**: Tabs com indicador ativo

### Responsividade
- **Desktop**: Layout em grid, sidebar fixa
- **Tablet**: Grid adaptativo, navegação compacta
- **Mobile**: Stack vertical, menu hamburger

## 📊 Métricas e Analytics

### KPIs Principais
```javascript
{
  "overview": {
    "total_conversations": 1247,
    "qualified_leads": 89,
    "qualification_rate": 7.1,
    "total_messages": 4832
  },
  "lead_types": {
    "academy": 67,
    "digital": 22,
    "unknown": 1158
  },
  "activity": {
    "conversations_today": 15,
    "conversations_yesterday": 23,
    "conversations_this_week": 89
  }
}
```

### Métricas Redis
```javascript
{
  "server": {
    "redis_version": "7.0.8",
    "uptime_in_days": 5
  },
  "memory": {
    "used_memory_human": "2.4M",
    "used_memory_peak_human": "3.1M"
  },
  "stats": {
    "instantaneous_ops_per_sec": 12,
    "keyspace_hits": 1543,
    "keyspace_misses": 67
  }
}
```

## 🔒 Segurança e Limitações

### Comandos Redis Permitidos
✅ **Seguros (Leitura apenas)**:
- `GET`, `KEYS`, `EXISTS`, `TTL`, `TYPE`
- `LRANGE`, `LLEN`, `HGET`, `HGETALL`
- `SCARD`, `SMEMBERS`, `ZCARD`, `ZRANGE`
- `SCAN`, `INFO`, `DBSIZE`

❌ **Bloqueados (Escrita/Perigosos)**:
- `SET`, `DEL`, `FLUSHDB`, `FLUSHALL`
- `EVAL`, `SCRIPT`, `CONFIG`
- `SHUTDOWN`, `DEBUG`

### Rate Limiting
- **Console Redis**: Sem limite (apenas leitura)
- **API Endpoints**: Configurável via middleware
- **CORS**: Habilitado para desenvolvimento

### LGPD Compliance
- **Deletion**: Endpoint `/admin/conversation/{user_id}` (DELETE)
- **Export**: Dados completos via API
- **Audit**: Logs de todas as operações

## 🚀 Performance

### Benchmarks Típicos
| Operação | Tempo Médio | Observações |
|----------|-------------|-------------|
| **Analytics Overview** | ~200ms | Cache Redis ativo |
| **Lista Conversas** | ~150ms | 100 conversas |
| **Detalhes Conversa** | ~50ms | Single record |
| **Redis Query** | ~10ms | Comando simples |

### Otimizações
- **Lazy Loading**: Dados carregados sob demanda
- **Cache Client**: localStorage para filtros
- **Debounce**: Busca com delay 300ms
- **Pagination**: 20-100 items por página

## 🔧 Troubleshooting

### Problemas Comuns

#### Dashboard não carrega
```bash
# Verificar se o serviço está rodando
curl http://localhost:8001/admin/analytics/overview

# Verificar logs
python admin_dashboard.py
```

#### Erro 404 no admin
```bash
# Verificar se o arquivo HTML existe
ls -la admin_dashboard.html

# Criar se necessário
touch admin_dashboard.html
```

#### Redis não conecta
```bash
# Testar conexão Redis
redis-cli ping

# Verificar URL no código
echo $REDIS_URL
```

#### CORS errors
```python
# Verificar CORS no admin_dashboard.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ajustar para produção
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Logs e Debug
```bash
# Logs detalhados
export LOG_LEVEL=DEBUG
python admin_dashboard.py

# Verificar Redis keys
redis-cli KEYS "*"

# Monitor Redis em tempo real
redis-cli MONITOR
```

## 🔄 Desenvolvimento

### Estrutura de Arquivos
```
├── admin_dashboard.py          # Backend FastAPI
├── admin_dashboard.html        # Frontend interface
├── start_admin.py             # Script inicialização
├── test_admin_system.py       # Testes completos
└── ADMIN_DASHBOARD.md         # Esta documentação
```

### Adicionando Novos Endpoints
```python
@app.get("/admin/custom/endpoint")
async def custom_endpoint():
    return {"custom": "data"}
```

### Modificando Interface
```javascript
// Adicionar nova seção
function showSection(sectionName) {
    // Lógica existente...
    if (sectionName === 'custom') loadCustomData();
}
```

### Testes
```bash
# Teste específico
python -c "
import requests
resp = requests.get('http://localhost:8001/admin/analytics/overview')
print(resp.json())
"

# Teste completo
python test_admin_system.py
```

## 📈 Roadmap

### Próximas Funcionalidades
- [ ] **Gráficos Interativos**: Charts.js para métricas
- [ ] **Filtros por Data**: Calendar picker
- [ ] **Export CSV**: Download de dados
- [ ] **Alertas Real-time**: WebSocket notifications
- [ ] **User Management**: Autenticação admin
- [ ] **API Rate Limiting**: Dashboard de quotas
- [ ] **Logs Viewer**: Interface para logs sistema
- [ ] **Backup/Restore**: Ferramentas de backup

### Melhorias UX
- [ ] **Dark Mode**: Tema escuro
- [ ] **Mobile First**: PWA capabilities
- [ ] **Keyboard Shortcuts**: Navegação rápida
- [ ] **Auto-refresh**: Métricas em tempo real
- [ ] **Search History**: Histórico de buscas
- [ ] **Favorites**: Conversas favoritas

## 🤝 Suporte

### Contatos Técnicos
- **Email**: admin@scoras.com.br
- **GitHub**: Issues no repositório
- **Documentação**: README.md principal

### Recursos Adicionais
- **API Docs**: http://localhost:8001/docs
- **Health Check**: http://localhost:8001/admin/analytics/overview
- **Redis Info**: http://localhost:8001/admin/redis/info

---

**Desenvolvido com ❤️ pela equipe Scoras Digital** 