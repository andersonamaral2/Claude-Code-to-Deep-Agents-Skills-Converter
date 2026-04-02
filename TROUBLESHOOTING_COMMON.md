# 🆘 **TROUBLESHOOTING - PROBLEMAS COMUNS**

**Soluções rápidas para erros frequentes da equipe**

---

## ❌ **RuntimeError: Directory 'admin_static' does not exist**

### 🔍 **Problema**
- Erro ao executar o admin dashboard
- Diretório `admin_static` não existe após clonar repositório

### ✅ **Solução**
```bash
# Se já tem o repositório clonado:
git pull origin main

# Se é primeira vez clonando:
git clone https://github.com/scorastecnologialtda/scoras_agent.git
cd scoras_agent
```

### 📝 **Causa**
O Git não inclui diretórios vazios. O código foi corrigido para criar o diretório automaticamente.

**✅ CORREÇÃO APLICADA:** Problema resolvido nas versões mais recentes do repositório.

---

## ❌ **Erro: Falha ao escrever logs/arquivo.log**

### 🔍 **Problema**
- Erro "No such file or directory: logs/chat_api.log"
- Sistema tenta escrever logs mas diretório não existe

### ✅ **Solução**
```bash
# Criar diretório manualmente:
mkdir -p logs

# OU atualizar para versão corrigida:
git pull origin main
```

### 📝 **Causa**
O diretório `logs/` estava sendo ignorado pelo Git. Já foi corrigido no repositório.

**✅ CORREÇÃO APLICADA:** Problema resolvido - start_all.sh agora cria o diretório automaticamente.

---

## ❌ **Erro: "Authentication failed" no Git**

### 🔍 **Problema**
- `git push` ou `git pull` falha com erro de autenticação

### ✅ **Solução**
```bash
# Usar token na URL (substitua pelo token real):
git pull https://andersonamaral2:SEU_TOKEN@github.com/scorastecnologialtda/scoras_agent.git main
git push https://andersonamaral2:SEU_TOKEN@github.com/scorastecnologialtda/scoras_agent.git main
```

---

## ❌ **Erro: "make: command not found"**

### 🔍 **Problema**
- Comandos `make up`, `make status` não funcionam

### ✅ **Solução**
```bash
# Ubuntu/Debian:
sudo apt install make

# OU usar scripts diretamente:
./start_all.sh    # Em vez de make up
./stop_all.sh     # Em vez de make down
```

---

## ❌ **Erro: "docker: command not found"**

### 🔍 **Problema**
- Sistema não encontra Docker

### ✅ **Solução**
```bash
# Instalar Docker:
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Adicionar usuário ao grupo docker:
sudo usermod -aG docker $USER
newgrp docker
```

---

## ❌ **Erro: Redis não conecta**

### 🔍 **Problema**
- `ConnectionError: Error connecting to Redis`

### ✅ **Solução**
```bash
# Verificar se Redis está rodando:
docker ps | grep redis

# Se não estiver rodando:
docker start scoras-redis

# OU reiniciar tudo:
make restart
```

---

## ❌ **Erro: Porta já em uso**

### 🔍 **Problema**
- `Address already in use` nas portas 3000, 8000, 8001

### ✅ **Solução**
```bash
# Ver o que está usando a porta:
sudo netstat -tulpn | grep :8000

# Matar processo específico:
sudo kill -9 PID_NUMBER

# OU reiniciar tudo:
make down
make up
```

---

## ❌ **Erro: Python package não encontrado**

### 🔍 **Problema**
- `ModuleNotFoundError: No module named 'fastapi'`

### ✅ **Solução**
```bash
# Instalar dependências:
pip install -r requirements.txt

# OU verificar versão Python:
python --version  # Deve ser 3.11+
```

---

## ❌ **Erro: Permission denied (arquivo não executável)**

### 🔍 **Problema**
- `Permission denied: ./start_all.sh`

### ✅ **Solução**
```bash
# Dar permissão de execução:
chmod +x start_all.sh
chmod +x stop_all.sh
chmod +x pull_team_changes.sh

# OU executar com bash:
bash start_all.sh
```

---

## 🆘 **COMANDOS DE EMERGÊNCIA**

### 🔄 **Reset Completo**
```bash
# Parar tudo:
make down

# Limpar containers:
docker system prune -a

# Reiniciar:
make up
```

### 📊 **Verificar Status**
```bash
# Status geral:
make status

# Health check:
./pull_team_changes.sh

# Logs:
make logs
```

### 🔍 **Diagnóstico**
```bash
# Verificar portas:
sudo netstat -tulpn | grep -E ":(3000|8000|8001)"

# Verificar Docker:
docker ps
docker logs scoras-redis

# Verificar Python:
python --version
pip list | grep fastapi
```

---

## 📞 **ESCALAÇÃO**

### 🆘 **Se nada funcionar:**
1. **Backup**: Copie suas mudanças locais
2. **Clean slate**: `git clone` do repositório novamente  
3. **Contato**: admin@scoras.com.br

### 📋 **Informações para suporte:**
- Erro completo (copiar/colar)
- Sistema operacional
- Output de: `python --version`, `docker --version`
- Output de: `git status`, `make status`

---

**Mantenha este arquivo como referência rápida!** 📖 