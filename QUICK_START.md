# 🚀 Início Rápido - Scoras AI Agent + Admin Dashboard

## ✅ Sistema Pronto!

Todos os arquivos foram criados com sucesso:

```
📁 Arquivos Criados:
├── 🤖 admin_dashboard.py        # Backend do dashboard (16KB)
├── 🎨 admin_dashboard.html      # Frontend do dashboard (34KB)  
├── 🚀 start_admin.py           # Script de inicialização
├── 🧪 test_admin_system.py     # Testes do sistema
├── 🔧 setup_redis.sh           # Setup Redis via Docker
├── 📚 ADMIN_DASHBOARD.md       # Documentação completa
└── 📋 QUICK_START.md           # Este guia
```

## 🎯 Como Usar

### 1. ✅ Redis já está funcionando
```bash
# ✅ Redis já configurado via Docker
docker ps | grep scoras-redis
```

### 2. 🚀 Iniciar os Serviços
```bash
# Opção A: Iniciar tudo de uma vez (RECOMENDADO)
python start_admin.py

# Opção B: Iniciar separadamente
# Terminal 1: Chat API
python chat_api_rag_fixed.py

# Terminal 2: Admin Dashboard  
python admin_dashboard.py
```

### 3. 🌐 Acessar as Interfaces

| 🔗 **Links de Acesso** |
|-------------------------|
| **🤖 Chat Interface**: http://localhost:8000 |
| **📊 Admin Dashboard**: http://localhost:8001/admin |
| **📖 API Docs**: http://localhost:8000/docs |
| **❤️ Health Check**: http://localhost:8000/health |

## 📊 Funcionalidades do Admin Dashboard

### 🎯 Overview
- Total de conversas e leads qualificados
- Taxa de qualificação em tempo real
- Métricas por tipo (Academy vs Digital)
- Atividade recente (hoje, ontem, semana)
- Status do Redis (memória, performance)

### 💬 Gestão de Conversas
- **Filtros avançados**: Por nome, tipo, qualificação
- **Lista completa**: Todas as conversas com detalhes
- **Visualização individual**: Timeline completa de mensagens
- **Dados de qualificação**: Nome, telefone, email extraídos
- **Ações**: Ver detalhes, deletar conversa (LGPD)

### 🔧 Redis Console
- **Console interativo**: Execute comandos Redis diretamente
- **Comandos seguros**: Apenas leitura (GET, KEYS, INFO, etc.)
- **Output formatado**: JSON pretty-print automático
- **Informações detalhadas**: Servidor, memória, estatísticas

## 🧪 Testar o Sistema

```bash
# Executar testes completos
python test_admin_system.py

# Teste manual rápido
curl http://localhost:8001/admin/analytics/overview
```

## 🔧 Comandos Redis Úteis

```bash
# No Admin Dashboard > Redis Console, teste:
KEYS conversation:*           # Listar todas as conversas
KEYS qualification:*         # Listar qualificações
GET conversation:user-123    # Ver conversa específica
INFO memory                  # Status da memória
DBSIZE                      # Total de chaves
```

## 🚨 Troubleshooting

### 🔴 Problemas Comuns

#### Redis não conecta
```bash
# Verificar se está rodando
docker ps | grep scoras-redis

# Reiniciar se necessário
./setup_redis.sh
```

#### Services não iniciam
```bash
# Verificar dependências
pip install fastapi uvicorn redis azure-ai-inference pydantic

# Verificar variáveis de ambiente
echo $AZURE_API_KEY
echo $AZURE_ENDPOINT
```

#### Dashboard não carrega
```bash
# Verificar se arquivo existe
ls -la admin_dashboard.html

# Testar backend diretamente
curl http://localhost:8001/admin/analytics/overview
```

## 🎉 Próximos Passos

1. **📊 Acesse o Admin Dashboard**: http://localhost:8001/admin
2. **🧪 Teste uma conversa**: http://localhost:8000
3. **👁️ Monitore no dashboard**: Veja a conversa aparecer em tempo real
4. **🔍 Explore o Redis**: Use o console para ver os dados
5. **📈 Analise métricas**: Overview com KPIs em tempo real

## 🏆 Funcionalidades Avançadas

### 🎯 Qualificação Automática
- Sistema detecta automaticamente leads Academy vs Digital
- Coleta obrigatória de nome, telefone, email para Digital
- Preços só liberados para leads qualificados
- Calendly oferecido automaticamente

### 🔍 RAG Híbrido  
- 27 documentos indexados (Academy + Digital)
- Busca BM25 + correspondência exata
- Cache Redis inteligente para performance
- Logging detalhado de todas as operações

### 🛡️ Segurança e Compliance
- Rate limiting configurable
- Comandos Redis apenas de leitura
- CORS habilitado para desenvolvimento
- Compliance LGPD (export/delete data)

## 💡 Dicas Importantes

- **🔄 Auto-refresh**: Dashboard atualiza automaticamente
- **📱 Responsivo**: Funciona em mobile, tablet, desktop
- **⚡ Performance**: Cache Redis otimizado para velocidade
- **🔒 Seguro**: Apenas comandos seguros no Redis Console
- **📊 Analytics**: Métricas em tempo real sem delay

## 🤝 Suporte

- **📚 Documentação**: `ADMIN_DASHBOARD.md` (completa)
- **🧪 Testes**: `python test_admin_system.py`
- **🔧 Setup**: `./setup_redis.sh` (Redis via Docker)
- **🚀 Start**: `python start_admin.py` (tudo de uma vez)

---

**🎯 Sistema pronto para uso! Agora você tem um dashboard administrativo completo para monitorar todas as conversas do seu chatbot Scoras AI Agent.**

**Desenvolvido com ❤️ pela equipe Scoras Digital** 