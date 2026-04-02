# 🚀 **GUIA COMPLETO DEPLOY AZURE VM UBUNTU 24**

**Para o Time Scoras - Instruções Detalhadas para Produção**

---

## 📋 **CHECKLIST PRÉ-DEPLOY**

- [ ] **Azure Subscription** ativa
- [ ] **Azure CLI** instalado no seu computador  
- [ ] **Chaves SSH** configuradas
- [ ] **Azure AI Services** configurado (DeepSeek V3)
- [ ] **Resource Group** criado na Azure

---

## 🖥️ **1. PREPARAÇÃO LOCAL (SEU COMPUTADOR)**

### Instalar Azure CLI

```bash
# Ubuntu/Debian
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# macOS
brew install azure-cli

# Windows
# Baixar instalador: https://aka.ms/installazurecliwindows
```

### Login e Configuração

```bash
# Login na Azure
az login

# Definir subscription (se tiver múltiplas)
az account list --output table
az account set --subscription "YOUR_SUBSCRIPTION_ID"

# Verificar configuração
az account show
```

---

## 🔧 **2. CRIAÇÃO DA VM STEP-BY-STEP**

### Criar Resource Group

```bash
# Definir variáveis
RESOURCE_GROUP="rg-scoras-ai-agent"
LOCATION="brazilsouth"
VM_NAME="vm-scoras-ai-agent"
VM_USER="scoras"

# Criar resource group
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION
```

### Criar Virtual Network

```bash
# Criar VNet
az network vnet create \
  --resource-group $RESOURCE_GROUP \
  --name vnet-scoras \
  --address-prefix 10.0.0.0/16 \
  --subnet-name subnet-default \
  --subnet-prefix 10.0.0.0/24
```

### Criar Network Security Group

```bash
# Criar NSG
az network nsg create \
  --resource-group $RESOURCE_GROUP \
  --name nsg-scoras-ai-agent

# Regras de firewall específicas
# SSH
az network nsg rule create \
  --resource-group $RESOURCE_GROUP \
  --nsg-name nsg-scoras-ai-agent \
  --name AllowSSH \
  --protocol Tcp \
  --priority 1000 \
  --destination-port-range 22 \
  --access Allow

# HTTP/HTTPS
az network nsg rule create \
  --resource-group $RESOURCE_GROUP \
  --nsg-name nsg-scoras-ai-agent \
  --name AllowHTTP \
  --protocol Tcp \
  --priority 1001 \
  --destination-port-ranges 80 443 \
  --access Allow

# Portas da aplicação
az network nsg rule create \
  --resource-group $RESOURCE_GROUP \
  --nsg-name nsg-scoras-ai-agent \
  --name AllowScoras \
  --protocol Tcp \
  --priority 1002 \
  --destination-port-ranges 3000 8000 8001 \
  --access Allow
```

### Criar Virtual Machine

```bash
# Criar VM
az vm create \
  --resource-group $RESOURCE_GROUP \
  --name $VM_NAME \
  --image Ubuntu2204 \
  --size Standard_B2s \
  --admin-username $VM_USER \
  --generate-ssh-keys \
  --vnet-name vnet-scoras \
  --subnet subnet-default \
  --nsg nsg-scoras-ai-agent \
  --public-ip-address-allocation static \
  --public-ip-sku Standard \
  --storage-sku Premium_LRS

# Obter IP público
VM_IP=$(az vm show \
  --resource-group $RESOURCE_GROUP \
  --name $VM_NAME \
  --show-details \
  --query publicIps \
  --output tsv)

echo "🌐 IP Público da VM: $VM_IP"
echo "🔗 SSH: ssh $VM_USER@$VM_IP"
```

---

## 📁 **3. TRANSFERIR CÓDIGO PARA VM**

### Opção A: Via SCP (Recomendado)

```bash
# No seu computador local, do diretório do projeto:

# Compactar projeto
tar -czf scoras-ai-agent.tar.gz --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' .

# Transferir para VM
scp scoras-ai-agent.tar.gz $VM_USER@$VM_IP:~/

# Conectar na VM e extrair
ssh $VM_USER@$VM_IP
mkdir -p ~/apps
cd ~/apps
tar -xzf ~/scoras-ai-agent.tar.gz
mv scoras-ai-agent scoras-ai-agent-backup 2>/dev/null || true
mkdir scoras-ai-agent
tar -xzf ~/scoras-ai-agent.tar.gz -C scoras-ai-agent
cd scoras-ai-agent
```

---

## ⚙️ **4. CONFIGURAÇÃO AUTOMÁTICA DA VM**

### Script de Setup Completo

```bash
# Criar script de setup na VM
cat > setup_vm.sh << 'SCRIPT_EOF'
#!/bin/bash

echo "🚀 Configurando VM para Scoras AI Agent..."

# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar ferramentas essenciais
sudo apt install -y curl wget git vim htop unzip make \
  software-properties-common apt-transport-https \
  ca-certificates gnupg lsb-release tree jq

# Instalar Python 3.11
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip

# Configurar Python
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1

# Instalar Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Configurar Docker
sudo usermod -aG docker $USER
sudo systemctl enable docker
sudo systemctl start docker

echo "✅ Setup básico concluído!"
echo "⚠️  Execute 'newgrp docker' ou faça logout/login para aplicar permissões Docker"
SCRIPT_EOF

chmod +x setup_vm.sh
./setup_vm.sh

# Aplicar mudanças Docker
newgrp docker
```

---

## 🔧 **5. CONFIGURAÇÃO DA APLICAÇÃO**

### Criar Arquivo .env Personalizado

```bash
# Na VM, no diretório da aplicação
cd ~/apps/scoras-ai-agent

# Obter IP público da VM
VM_PUBLIC_IP=$(curl -s ifconfig.me)

# Criar .env personalizado
cat > .env << ENV_EOF
# Azure AI Configuration
AZURE_ENDPOINT=https://ai-andersonai017430836643.services.ai.azure.com/models
AZURE_API_KEY=SUA_CHAVE_AZURE_AQUI
AZURE_API_VERSION=2024-05-01-preview
DEEPSEEK_MODEL=DeepSeek-V3-0324

# Redis Configuration (Local Docker)
REDIS_URL=redis://localhost:6379/0

# Environment
ENVIRONMENT=production
DEBUG=false

# Server Configuration
HOST=0.0.0.0
WORKERS=2
MAX_CONNECTIONS=100

# Security
ALLOWED_HOSTS=localhost,127.0.0.1,$VM_PUBLIC_IP
CORS_ORIGINS=http://localhost:3000,http://$VM_PUBLIC_IP:3000

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/application.log
ENV_EOF

echo "✅ Arquivo .env criado com IP: $VM_PUBLIC_IP"
echo "⚠️  IMPORTANTE: Configure sua chave Azure no arquivo .env"
```

### Instalar Dependências

```bash
# Instalar dependências Python
pip install -r requirements.txt

# OU usar make
make install

# Criar diretório de logs
mkdir -p logs

# Verificar instalação
python --version
docker --version
make help
```

---

## 🔄 **6. CONFIGURAR COMO SERVIÇO SYSTEMD**

### Criar Serviço do Sistema

```bash
# Criar arquivo de serviço
sudo tee /etc/systemd/system/scoras-ai-agent.service > /dev/null << SERVICE_EOF
[Unit]
Description=Scoras AI Agent System
Documentation=https://scoras.com.br
After=network.target docker.service
Requires=docker.service
StartLimitIntervalSec=0

[Service]
Type=forking
User=scoras
Group=scoras
WorkingDirectory=/home/scoras/apps/scoras-ai-agent
Environment=PATH=/home/scoras/.local/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=/home/scoras/apps/scoras-ai-agent/start_all.sh
ExecStop=/home/scoras/apps/scoras-ai-agent/stop_all.sh
ExecReload=/bin/kill -HUP \$MAINPID
Restart=always
RestartSec=10
TimeoutStartSec=300
TimeoutStopSec=120

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=/home/scoras/apps/scoras-ai-agent

[Install]
WantedBy=multi-user.target
SERVICE_EOF

# Configurar permissões
sudo systemctl daemon-reload
sudo systemctl enable scoras-ai-agent

echo "✅ Serviço systemd configurado"
```

---

## 🧪 **7. TESTE INICIAL**

### Primeiro Teste Manual

```bash
# Testar o sistema manualmente primeiro
cd ~/apps/scoras-ai-agent

# Iniciar sistema
make up

# Aguardar inicialização (30 segundos)
sleep 30

# Verificar status
make status

# Testar endpoints
VM_IP=$(curl -s ifconfig.me)
echo "🌐 Testing URLs:"
echo "  🤖 Chatbot: http://$VM_IP:3000"
echo "  📊 Admin: http://$VM_IP:8001/admin"
echo "  ⚙️ API: http://$VM_IP:8000/docs"

# Se tudo funcionou, parar para configurar como serviço
make down
```

### Configurar Inicialização Automática

```bash
# Se o teste manual funcionou, configurar serviço
sudo systemctl start scoras-ai-agent
sudo systemctl status scoras-ai-agent

# Verificar logs do serviço
sudo journalctl -u scoras-ai-agent -f
```

---

## 📊 **8. MONITORAMENTO E HEALTH CHECK**

### Script de Health Check

```bash
# Criar script de monitoramento
cat > ~/health_check.sh << 'HEALTH_EOF'
#!/bin/bash

# Configurações
VM_IP=$(curl -s ifconfig.me)
DATE=$(date '+%Y-%m-%d %H:%M:%S')
LOG_FILE="/home/scoras/health_check.log"

# Função de log
log() {
    echo "[$DATE] $1" | tee -a $LOG_FILE
}

log "🔍 Health Check iniciado"

# Verificar serviços
SERVICES_OK=0

# Chat API
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    log "✅ Chat API (8000): OK"
    ((SERVICES_OK++))
else
    log "❌ Chat API (8000): FALHA"
fi

# Admin Dashboard
if curl -s http://localhost:8001/admin | grep -q "Dashboard"; then
    log "✅ Admin Dashboard (8001): OK" 
    ((SERVICES_OK++))
else
    log "❌ Admin Dashboard (8001): FALHA"
fi

# Frontend
if curl -s -I http://localhost:3000 | grep -q "200 OK"; then
    log "✅ Frontend (3000): OK"
    ((SERVICES_OK++))
else
    log "❌ Frontend (3000): FALHA"
fi

# Redis
if docker exec scoras-redis redis-cli ping 2>/dev/null | grep -q "PONG"; then
    log "✅ Redis: OK"
    ((SERVICES_OK++))
else
    log "❌ Redis: FALHA"
fi

# Resultado final
if [ $SERVICES_OK -eq 4 ]; then
    log "🎉 Todos os serviços OK (4/4)"
    echo "Status: OK" > /tmp/scoras_status
else
    log "⚠️  Apenas $SERVICES_OK/4 serviços funcionando"
    echo "Status: PARTIAL" > /tmp/scoras_status
fi

# URLs públicas
log "📈 URLs Públicas:"
log "  🤖 Chatbot: http://$VM_IP:3000"
log "  📊 Admin: http://$VM_IP:8001/admin"
log "  ⚙️ API: http://$VM_IP:8000/docs"

HEALTH_EOF

chmod +x ~/health_check.sh

# Testar health check
~/health_check.sh
```

---

## 📋 **9. CHECKLIST FINAL**

### Script de Verificação Final

```bash
# Script de verificação final
cat > ~/production_check.sh << 'CHECK_EOF'
#!/bin/bash

echo "🔍 Verificação Final de Produção"
echo "================================="

CHECKS_PASSED=0
TOTAL_CHECKS=10

check() {
    if eval "$2"; then
        echo "✅ $1"
        ((CHECKS_PASSED++))
    else
        echo "❌ $1"
    fi
}

# Verificações
check "Python 3.11+ instalado" "python --version | grep -q '3.1[1-9]'"
check "Docker funcionando" "docker --version && docker ps >/dev/null 2>&1"
check "Aplicação existe" "[ -d /home/scoras/apps/scoras-ai-agent ]"
check "Arquivo .env configurado" "[ -f /home/scoras/apps/scoras-ai-agent/.env ]"
check "Chave Azure configurada" "grep -q 'AZURE_API_KEY.*[A-Za-z0-9]' /home/scoras/apps/scoras-ai-agent/.env"
check "Chat API respondendo" "curl -s http://localhost:8000/health | grep -q healthy"
check "Admin Dashboard ativo" "curl -s http://localhost:8001/admin | grep -q Dashboard"
check "Frontend funcionando" "curl -s -I http://localhost:3000 | grep -q '200 OK'"
check "Redis funcionando" "docker exec scoras-redis redis-cli ping | grep -q PONG"
check "Health check configurado" "[ -f /home/scoras/health_check.sh ]"

echo ""
echo "📊 Resultado: $CHECKS_PASSED/$TOTAL_CHECKS verificações passou"

if [ $CHECKS_PASSED -eq $TOTAL_CHECKS ]; then
    echo "🎉 SISTEMA PRONTO PARA PRODUÇÃO!"
    
    VM_IP=$(curl -s ifconfig.me)
    echo ""
    echo "🌐 URLs de Acesso:"
    echo "  🤖 Chatbot: http://$VM_IP:3000"
    echo "  📊 Admin: http://$VM_IP:8001/admin"  
    echo "  ⚙️ API: http://$VM_IP:8000/docs"
else
    echo "⚠️  Algumas verificações falharam. Revisar antes de usar em produção."
fi

CHECK_EOF

chmod +x ~/production_check.sh
~/production_check.sh
```

---

## 🆘 **10. COMANDOS DE EMERGÊNCIA PARA O TIME**

### Status Rápido

```bash
# Verificar tudo rapidamente
make status
~/health_check.sh
```

### Reiniciar Serviços

```bash
# Reiniciar aplicação
sudo systemctl restart scoras-ai-agent

# Reiniciar Docker se necessário
sudo systemctl restart docker

# Reiniciar tudo
make restart
```

### Ver Logs

```bash
# Logs da aplicação
make logs

# Logs do sistema
sudo journalctl -u scoras-ai-agent -f

# Logs específicos
make logs-chat
make logs-admin
make logs-frontend
```

### Troubleshooting

```bash
# Verificar portas
sudo netstat -tulpn | grep -E ":(3000|8000|8001)"

# Verificar processos
ps aux | grep python

# Verificar Docker
docker ps
docker logs scoras-redis

# Teste de conectividade
curl -s http://localhost:8000/health
curl -s http://localhost:8001/admin
curl -s -I http://localhost:3000
```

---

## 🎯 **RESUMO PARA O TIME**

### Comandos Essenciais

1. **Iniciar sistema**: `make up`
2. **Parar sistema**: `make down`
3. **Ver status**: `make status`
4. **Ver logs**: `make logs`
5. **Health check**: `~/health_check.sh`
6. **Verificação completa**: `~/production_check.sh`

### URLs de Acesso (substituir IP_DA_VM)

- **🤖 Chatbot**: http://IP_DA_VM:3000
- **📊 Admin Dashboard**: http://IP_DA_VM:8001/admin
- **⚙️ API Docs**: http://IP_DA_VM:8000/docs

### Contatos

- **Email**: admin@scoras.com.br
- **Logs**: `/home/scoras/apps/scoras-ai-agent/logs/`

---

## ✅ **RESULTADO FINAL**

Seguindo este guia, sua equipe terá:

✅ **VM Azure Ubuntu 24** otimizada  
✅ **Sistema funcionando 24/7**  
✅ **Monitoramento automático**  
✅ **Comandos simples** (`make up/down`)  
✅ **Troubleshooting** completo  

**Sistema pronto para receber usuários!** 🚀
