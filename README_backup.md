# 🤖 Scoras AI Agent - Sistema Completo

[![License](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![Azure](https://img.shields.io/badge/Azure-DeepSeek--V3-0078d4.svg)](https://azure.microsoft.com)

**Agente de IA Inteligente para Qualificação e Atendimento de Leads da Scoras**

> Desenvolvido pela **Scoras Digital Tecnologia Digital Ltda** - Soluções de IA desde 2021

---

## 📋 **INÍCIO RÁPIDO**

### 🚀 **Comando Único para Iniciar**

```bash
# Iniciar todo o sistema
make up

# OU alternativamente
./start_all.sh
```

### 🛑 **Parar o Sistema**

```bash
# Parar todo o sistema
make down

# OU alternativamente
./stop_all.sh
```

### 📊 **Verificar Status**

```bash
make status
```

### 🔧 **Comandos Úteis**

```bash
make help          # Ver todos os comandos disponíveis
make logs           # Ver logs em tempo real
make restart        # Reiniciar sistema
make redis          # Verificar status do Redis
make clean          # Limpar logs e arquivos temporários
```

---

## 🌐 **INTERFACES DO SISTEMA**

| Serviço | URL | Descrição |
|---------|-----|-----------|
| 🤖 **Chatbot** | http://localhost:3000 | Interface principal para usuários |
| 📊 **Admin Dashboard** | http://localhost:8001/admin | Monitoramento de conversas |
| ⚙️ **API Backend** | http://localhost:8000/docs | Documentação da API |
| 🗄️ **Redis** | localhost:6379 | Banco de dados de conversas |

---

## 🎯 **FUNCIONALIDADES**

### ✨ **Sistema Completo**
- **🤖 Chat API**: Backend principal com Azure DeepSeek V3
- **📊 Admin Dashboard**: Monitoramento completo de conversas
- **🗄️ Redis Storage**: Armazenamento persistente de conversas
- **🎨 Frontend**: Interface moderna e responsiva
- **🔄 Auto-restart**: Scripts inteligentes de inicialização

### 🧠 **Inteligência Artificial**
- **🔍 Classificação de Leads**: Academy vs Digital automática
- **💬 Conversas Contextuais**: Histórico mantido no Redis
- **🎯 Qualificação**: Coleta automática de dados de leads Digital
- **📈 Analytics**: Métricas em tempo real no dashboard

### 🛡️ **Segurança e Compliance**
- **🔒 CORS**: Configurado para desenvolvimento
- **📊 Rate Limiting**: Proteção contra abuso
- **🏢 LGPD**: Compliance com delete/export de dados
- **🔐 Redis Seguro**: Comandos limitados no dashboard

---

## 🚀 **DEPLOY EM VM AZURE UBUNTU 24**

### 📋 **Pré-requisitos da VM**

```bash
# Especificações mínimas recomendadas:
# - VM Size: Standard_B2s (2 vCPUs, 4GB RAM)
# - OS: Ubuntu 24.04 LTS
# - Storage: 30GB SSD
# - Network: Permitir portas 22, 80, 443, 3000, 8000, 8001
```

---

### 🖥️ **1. CRIAR VM NA AZURE**

#### Via Azure Portal

1. **Criar Resource Group**
   ```bash
   Resource Group: rg-scoras-ai-agent
   Region: Brazil South
   ```

2. **Criar Virtual Machine**
   ```
   Name: vm-scoras-ai-agent
   Region: Brazil South
   Image: Ubuntu 24.04 LTS - x64 Gen2
   Size: Standard_B2s (2 vcpus, 4 GiB memory)
   Username: scoras
   Authentication: SSH public key
   ```

3. **Configurar Networking**
   ```
   Virtual network: vnet-scoras (criar nova)
   Subnet: subnet-default (10.0.0.0/24)
   Public IP: pip-scoras-ai-agent (criar nova)
   NIC network security group: Advanced
   ```

4. **Regras de Firewall (NSG)**
   ```bash
   # Permitir SSH
   Port 22: Source Any, Destination Any, Protocol TCP
   
   # Permitir HTTP/HTTPS
   Port 80: Source Any, Destination Any, Protocol TCP
   Port 443: Source Any, Destination Any, Protocol TCP
   
   # Permitir portas da aplicação
   Port 3000: Source Any, Destination Any, Protocol TCP (Frontend)
   Port 8000: Source Any, Destination Any, Protocol TCP (API)
   Port 8001: Source Any, Destination Any, Protocol TCP (Admin)
   ```

#### Via Azure CLI

```bash
# Login na Azure
az login

# Criar Resource Group
az group create \
  --name rg-scoras-ai-agent \
  --location brazilsouth

# Criar VM
az vm create \
  --resource-group rg-scoras-ai-agent \
  --name vm-scoras-ai-agent \
  --image Ubuntu2204 \
  --size Standard_B2s \
  --admin-username scoras \
  --generate-ssh-keys \
  --public-ip-address-allocation static

# Abrir portas necessárias
az vm open-port --resource-group rg-scoras-ai-agent --name vm-scoras-ai-agent --port 22
az vm open-port --resource-group rg-scoras-ai-agent --name vm-scoras-ai-agent --port 80
az vm open-port --resource-group rg-scoras-ai-agent --name vm-scoras-ai-agent --port 443
az vm open-port --resource-group rg-scoras-ai-agent --name vm-scoras-ai-agent --port 3000
az vm open-port --resource-group rg-scoras-ai-agent --name vm-scoras-ai-agent --port 8000
az vm open-port --resource-group rg-scoras-ai-agent --name vm-scoras-ai-agent --port 8001

# Obter IP público
az vm show \
  --resource-group rg-scoras-ai-agent \
  --name vm-scoras-ai-agent \
  --show-details \
  --query publicIps \
  --output tsv
```

---

### 🔧 **2. CONFIGURAÇÃO INICIAL DA VM**

#### Conectar via SSH

```bash
# Obter IP público da VM
VM_IP=$(az vm show --resource-group rg-scoras-ai-agent --name vm-scoras-ai-agent --show-details --query publicIps --output tsv)

# Conectar via SSH
ssh scoras@$VM_IP
```

#### Atualizar Sistema

```bash
# Atualizar packages
sudo apt update && sudo apt upgrade -y

# Instalar ferramentas essenciais
sudo apt install -y curl wget git vim htop unzip software-properties-common apt-transport-https ca-certificates gnupg lsb-release
```

---

### 🐍 **3. INSTALAR PYTHON 3.11+**

```bash
# Adicionar repositório Python
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update

# Instalar Python 3.11
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip

# Configurar Python como padrão
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1

# Verificar instalação
python --version  # Deve mostrar Python 3.11.x
pip --version
```

---

### 🐳 **4. INSTALAR DOCKER**

```bash
# Remover versões antigas
sudo apt remove -y docker docker-engine docker.io containerd runc

# Adicionar chave GPG oficial do Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Adicionar repositório Docker
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instalar Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER

# Habilitar Docker para iniciar automaticamente
sudo systemctl enable docker
sudo systemctl start docker

# Aplicar mudanças de grupo (relogar)
newgrp docker

# Verificar instalação
docker --version
docker compose version
```

---

### 📥 **5. INSTALAR A APLICAÇÃO**

#### Clonar Repositório

```bash
# Criar diretório de aplicações
mkdir -p ~/apps
cd ~/apps

# Clonar repositório (substitua pela URL real)
git clone https://github.com/scoras/scoras-ai-agent.git
cd scoras-ai-agent

# OU transferir arquivos via SCP se não usar Git
# scp -r ./Agente_Scoras scoras@$VM_IP:~/apps/
```

#### Configurar Ambiente

```bash
# Instalar dependências Python
pip install -r requirements.txt

# OU usar make para instalar
make install

# Configurar arquivo .env
cp .env.example .env
vim .env  # Configurar suas chaves Azure
```

#### Arquivo `.env` de Produção

```bash
# Azure AI Configuration
AZURE_ENDPOINT=https://ai-andersonai017430836643.services.ai.azure.com/models
AZURE_API_KEY=sua_chave_azure_real_aqui
AZURE_API_VERSION=2024-05-01-preview
DEEPSEEK_MODEL=DeepSeek-V3-0324

# Redis Configuration (Local Docker)
REDIS_URL=redis://localhost:6379/0

# Environment
ENVIRONMENT=production
DEBUG=false

# Security
ALLOWED_HOSTS=localhost,127.0.0.1,YOUR_VM_PUBLIC_IP

# Performance
WORKERS=2
MAX_CONNECTIONS=100
```

---

### 🚀 **6. INICIAR A APLICAÇÃO**

#### Teste Local

```bash
# Testar se tudo está funcionando
make up

# Verificar status
make status

# Ver logs se necessário
make logs
```

#### Configurar como Serviço do Sistema (Opcional)

```bash
# Criar script de serviço
sudo vim /etc/systemd/system/scoras-ai-agent.service
```

```ini
[Unit]
Description=Scoras AI Agent System
After=network.target docker.service
Requires=docker.service

[Service]
Type=forking
User=scoras
WorkingDirectory=/home/scoras/apps/scoras-ai-agent
ExecStart=/home/scoras/apps/scoras-ai-agent/start_all.sh
ExecStop=/home/scoras/apps/scoras-ai-agent/stop_all.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Habilitar e iniciar serviço
sudo systemctl daemon-reload
sudo systemctl enable scoras-ai-agent
sudo systemctl start scoras-ai-agent

# Verificar status
sudo systemctl status scoras-ai-agent
```

---

### 🌐 **7. CONFIGURAR NGINX (OPCIONAL)**

#### Instalar Nginx

```bash
sudo apt install -y nginx

# Configurar site
sudo vim /etc/nginx/sites-available/scoras-ai-agent
```

```nginx
server {
    listen 80;
    server_name YOUR_VM_PUBLIC_IP;

    # Frontend (Chatbot)
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Admin Dashboard
    location /admin {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # API Backend
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Habilitar site
sudo ln -s /etc/nginx/sites-available/scoras-ai-agent /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default

# Testar configuração
sudo nginx -t

# Reiniciar Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

---

### 🔒 **8. CONFIGURAR SSL COM CERTBOT (OPCIONAL)**

```bash
# Instalar Certbot
sudo apt install -y certbot python3-certbot-nginx

# Configurar domínio (se tiver)
sudo certbot --nginx -d seu-dominio.com

# OU usar IP público (não recomendado para produção)
# Criar certificado self-signed para teste
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/scoras-selfsigned.key \
  -out /etc/ssl/certs/scoras-selfsigned.crt
```

---

### 📊 **9. MONITORAMENTO**

#### Configurar Logs Centralizados

```bash
# Configurar logrotate
sudo vim /etc/logrotate.d/scoras-ai-agent
```

```
/home/scoras/apps/scoras-ai-agent/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 scoras scoras
    postrotate
        systemctl restart scoras-ai-agent
    endscript
}
```

#### Script de Monitoramento

```bash
# Criar script de health check
vim ~/health_check.sh
```

```bash
#!/bin/bash
# Health check script

VM_IP=$(curl -s ifconfig.me)
echo "🔍 Health Check - $(date)"
echo "🌐 VM IP: $VM_IP"
echo ""

# Verificar serviços
echo "📊 Status dos Serviços:"
curl -s http://localhost:8000/health | grep -q "healthy" && echo "  ✅ Chat API (8000)" || echo "  ❌ Chat API (8000)"
curl -s http://localhost:8001/admin | grep -q "Dashboard" && echo "  ✅ Admin Dashboard (8001)" || echo "  ❌ Admin Dashboard (8001)"
curl -s -I http://localhost:3000 | grep -q "200 OK" && echo "  ✅ Frontend (3000)" || echo "  ❌ Frontend (3000)"

# Verificar Redis
docker exec scoras-redis redis-cli ping | grep -q "PONG" && echo "  ✅ Redis" || echo "  ❌ Redis"

echo ""
echo "📈 URLs Públicas:"
echo "  🤖 Chatbot: http://$VM_IP:3000"
echo "  📊 Admin: http://$VM_IP:8001/admin"
echo "  ⚙️ API: http://$VM_IP:8000/docs"
```

```bash
chmod +x ~/health_check.sh

# Executar health check
~/health_check.sh
```

---

### 🔄 **10. BACKUP E MANUTENÇÃO**

#### Script de Backup

```bash
# Criar script de backup
vim ~/backup.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/home/scoras/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup Redis
docker exec scoras-redis redis-cli BGSAVE
sleep 5
docker cp scoras-redis:/data/dump.rdb $BACKUP_DIR/redis_backup_$DATE.rdb

# Backup código
tar -czf $BACKUP_DIR/code_backup_$DATE.tar.gz -C /home/scoras/apps scoras-ai-agent

# Backup logs
tar -czf $BACKUP_DIR/logs_backup_$DATE.tar.gz -C /home/scoras/apps/scoras-ai-agent logs

# Limpar backups antigos (manter últimos 30 dias)
find $BACKUP_DIR -name "*backup*" -mtime +30 -delete

echo "✅ Backup concluído: $DATE"
```

```bash
chmod +x ~/backup.sh

# Configurar cron para backup diário
crontab -e
# Adicionar linha:
# 0 2 * * * /home/scoras/backup.sh >> /home/scoras/backup.log 2>&1
```

---

## 🐛 **TROUBLESHOOTING**

### ❌ **Problemas Comuns**

#### 1. Porta já em uso
```bash
# Verificar o que está usando a porta
sudo netstat -tulpn | grep :8000

# Matar processo específico
sudo kill -9 PID_NUMBER

# OU reiniciar tudo
make down && make up
```

#### 2. Redis não conecta
```bash
# Verificar container Redis
docker ps | grep redis

# Verificar logs Redis
docker logs scoras-redis

# Reiniciar Redis
docker restart scoras-redis
```

#### 3. Azure API não responde
```bash
# Verificar chaves no .env
cat .env | grep AZURE

# Testar API diretamente
curl -X POST $AZURE_ENDPOINT/chat/completions \
  -H "Authorization: Bearer $AZURE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"test"}],"model":"DeepSeek-V3-0324"}'
```

#### 4. Frontend não carrega
```bash
# Verificar logs do frontend
make logs-frontend

# Verificar se arquivo existe
ls frontend/server.py

# Reiniciar apenas frontend
cd frontend && python server.py
```

### 📋 **Logs Úteis**

```bash
# Ver todos os logs
make logs

# Logs específicos
make logs-chat      # Chat API
make logs-admin     # Admin Dashboard  
make logs-frontend  # Frontend

# Logs do sistema
sudo journalctl -u scoras-ai-agent -f

# Logs do Docker
docker logs scoras-redis
```

---

## 🔧 **DESENVOLVIMENTO**

### 📝 **Para Desenvolvedores**

```bash
# Iniciar apenas um serviço para desenvolvimento
make dev-chat      # Apenas Chat API
make dev-admin     # Apenas Admin Dashboard
make dev-frontend  # Apenas Frontend

# Ver status
make status

# Limpar e reiniciar
make clean && make up
```

### 🧪 **Testes**

```bash
# Instalar dependências de teste
pip install pytest pytest-asyncio httpx

# Executar testes
pytest tests/

# Teste específico
python test_admin_system.py
```

---

## 📞 **SUPORTE**

### 🆘 **Em caso de problemas:**

1. **Verificar logs**: `make logs`
2. **Reiniciar sistema**: `make restart`
3. **Verificar status**: `make status`
4. **Executar health check**: `~/health_check.sh`

### 📧 **Contato**

- **Email**: admin@scoras.com.br
- **Website**: https://scoras.com.br
- **Documentação**: Disponível no Admin Dashboard

---

## 📄 **LICENÇA**

```
Copyright (c) 2025 Scoras Digital Tecnologia Digital Ltda
Todos os direitos reservados.

Este software é propriedade exclusiva da Scoras Digital.
É proibida a reprodução, distribuição ou uso não autorizado.
```

---

## 🎉 **SISTEMA PRONTO PARA PRODUÇÃO!**

Após seguir este guia, você terá:

✅ **VM Azure Ubuntu 24** configurada  
✅ **Sistema completo** rodando  
✅ **Monitoramento** ativo  
✅ **Backup automático** configurado  
✅ **SSL** habilitado (opcional)  
✅ **Nginx** como proxy reverso (opcional)  

**Execute `make up` e comece a usar!** 🚀 