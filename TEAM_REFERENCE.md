# 👥 **REFERÊNCIA RÁPIDA PARA O TIME**

**Comandos essenciais para operar o sistema Scoras AI Agent**

---

## 🚀 **COMANDOS BÁSICOS**

### Iniciar/Parar Sistema

```bash
make up          # Iniciar todo o sistema
make down        # Parar todo o sistema
make restart     # Reiniciar tudo
make status      # Ver status dos serviços
```

### Monitoramento

```bash
make logs        # Ver logs de todos os serviços
~/health_check.sh # Health check completo
curl -s ifconfig.me # Ver IP público da VM
```

### Logs Específicos

```bash
make logs-chat      # Logs do Chat API
make logs-admin     # Logs do Admin Dashboard
make logs-frontend  # Logs do Frontend
sudo journalctl -u scoras-ai-agent -f  # Logs do systemd
```

---

## 🔧 **COMANDOS DE MANUTENÇÃO**

### Serviço Systemd

```bash
sudo systemctl status scoras-ai-agent    # Ver status
sudo systemctl start scoras-ai-agent     # Iniciar serviço
sudo systemctl stop scoras-ai-agent      # Parar serviço
sudo systemctl restart scoras-ai-agent   # Reiniciar serviço
sudo systemctl enable scoras-ai-agent    # Auto-start
```

### Docker

```bash
docker ps                    # Ver containers rodando
docker logs scoras-redis     # Logs do Redis
docker restart scoras-redis  # Reiniciar Redis
docker exec scoras-redis redis-cli ping  # Testar Redis
```

---

## 🌐 **URLS IMPORTANTES**

**Substitua `VM_IP` pelo IP real da sua VM**

- **🤖 Chatbot**: `http://VM_IP:3000`
- **📊 Admin Dashboard**: `http://VM_IP:8001/admin`
- **⚙️ API Docs**: `http://VM_IP:8000/docs`
- **❤️ Health Check**: `http://VM_IP:8000/health`

### Descobrir IP da VM

```bash
curl -s ifconfig.me          # IP público
hostname -I                  # IP interno
```

---

## 🆘 **TROUBLESHOOTING RÁPIDO**

### 1. Sistema não responde

```bash
# Verificar se serviços estão rodando
make status

# Reiniciar tudo
sudo systemctl restart scoras-ai-agent

# Ver logs para identificar problema
make logs
```

### 2. Porta em uso

```bash
# Ver o que está usando a porta
sudo netstat -tulpn | grep :8000

# Parar processo específico
sudo kill -9 PID_NUMBER

# Reiniciar sistema
make restart
```

### 3. Redis não conecta

```bash
# Verificar container Redis
docker ps | grep redis

# Reiniciar Redis
docker restart scoras-redis

# Testar conexão
docker exec scoras-redis redis-cli ping
```

### 4. API Azure falha

```bash
# Verificar configuração
cat .env | grep AZURE

# Testar API manualmente
curl -X POST $AZURE_ENDPOINT/chat/completions \
  -H "Authorization: Bearer $AZURE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"teste"}],"model":"DeepSeek-V3-0324"}'
```

### 5. Chat não carrega

```bash
# Verificar se frontend está rodando
curl -s -I http://localhost:3000

# Verificar logs do frontend
make logs-frontend

# Reiniciar apenas frontend
cd frontend && python server.py
```

---

## 📊 **COMANDOS DE VERIFICAÇÃO**

### Health Check Completo

```bash
#!/bin/bash
echo "🔍 Verificando sistema..."

# API Chat
curl -s http://localhost:8000/health | grep -q "healthy" && echo "✅ Chat API" || echo "❌ Chat API"

# Admin Dashboard
curl -s http://localhost:8001/admin | grep -q "Dashboard" && echo "✅ Admin" || echo "❌ Admin"

# Frontend
curl -s -I http://localhost:3000 | grep -q "200 OK" && echo "✅ Frontend" || echo "❌ Frontend"

# Redis
docker exec scoras-redis redis-cli ping | grep -q "PONG" && echo "✅ Redis" || echo "❌ Redis"

# URLs públicas
VM_IP=$(curl -s ifconfig.me)
echo "🌐 URLs:"
echo "  Chatbot: http://$VM_IP:3000"
echo "  Admin: http://$VM_IP:8001/admin"
echo "  API: http://$VM_IP:8000/docs"
```

### Teste de Chat

```bash
# Testar chat simples
curl -X POST http://localhost:8000/chat-simple \
  -H "Content-Type: application/json" \
  -d '{"message": "oi"}' | jq

# Verificar conversas no Redis
docker exec scoras-redis redis-cli KEYS "*"
docker exec scoras-redis redis-cli DBSIZE
```

---

## 📋 **ARQUIVOS IMPORTANTES**

### Configuração

```bash
/home/scoras/apps/scoras-ai-agent/.env      # Configurações principais
/home/scoras/apps/scoras-ai-agent/logs/     # Logs da aplicação
/etc/systemd/system/scoras-ai-agent.service # Serviço systemd
```

### Scripts

```bash
/home/scoras/health_check.sh               # Script de monitoramento
/home/scoras/apps/scoras-ai-agent/start_all.sh # Script de inicialização
/home/scoras/apps/scoras-ai-agent/stop_all.sh  # Script de parada
```

---

## 🔄 **COMANDOS DE EMERGÊNCIA**

### Reset Completo (CUIDADO!)

```bash
# Parar tudo
sudo systemctl stop scoras-ai-agent
make down
docker stop scoras-redis

# Limpar Docker (remove dados!)
docker system prune -a

# Reiniciar
sudo systemctl start scoras-ai-agent
```

### Backup Manual

```bash
# Backup Redis
docker exec scoras-redis redis-cli BGSAVE
docker cp scoras-redis:/data/dump.rdb ~/backup_redis_$(date +%Y%m%d).rdb

# Backup logs
tar -czf ~/backup_logs_$(date +%Y%m%d).tar.gz /home/scoras/apps/scoras-ai-agent/logs/

# Backup configuração
cp /home/scoras/apps/scoras-ai-agent/.env ~/backup_env_$(date +%Y%m%d).txt
```

---

## 📞 **ESCALAÇÃO**

### Nível 1 - Problemas Simples
- Reiniciar serviço: `sudo systemctl restart scoras-ai-agent`
- Ver logs: `make logs`
- Health check: `~/health_check.sh`

### Nível 2 - Problemas Médios
- Reset Docker: `docker restart scoras-redis`
- Verificar .env: `cat .env | grep AZURE`
- Reiniciar VM: `sudo reboot`

### Nível 3 - Problemas Críticos
- **Contato**: admin@scoras.com.br
- **Logs para enviar**: `/home/scoras/apps/scoras-ai-agent/logs/`
- **Info do sistema**: `~/health_check.sh > ~/system_info.txt`

---

## ✅ **CHECKLIST DIÁRIO**

```bash
# 1. Verificar sistema
~/health_check.sh

# 2. Ver logs de erro
make logs | grep -i error

# 3. Verificar espaço em disco
df -h

# 4. Verificar memória
free -h

# 5. Verificar conversas no Redis
docker exec scoras-redis redis-cli DBSIZE
```

---

**Mantenha este documento sempre atualizado!**  
**Em caso de dúvidas**: admin@scoras.com.br 