# 🔄 **WORKFLOW GIT PARA EQUIPE - SCORAS AI AGENT**

**Como trabalhar com alterações da equipe no repositório GitHub**

---

## 🎯 **CENÁRIO: ALGUÉM DA EQUIPE ALTEROU O CÓDIGO**

### 📋 **Situação**
- ✅ Você tem o repositório local
- 👥 Alguém da equipe fez alterações e push para GitHub
- 🔄 Você quer trabalhar com as mudanças mais recentes

---

## 🚀 **COMANDOS ESSENCIAIS**

### 1️⃣ **VERIFICAR SE HÁ MUDANÇAS NO GITHUB**

```bash
# Verificar se há commits novos no GitHub
git fetch origin

# Ver diferenças entre seu local e o GitHub
git status

# Ver log de commits no GitHub que você não tem
git log HEAD..origin/main --oneline
```

### 2️⃣ **BAIXAR AS MUDANÇAS (SEM CONFLITOS)**

```bash
# Baixar e aplicar mudanças automaticamente
git pull origin main

# OU passo a passo:
git fetch origin    # Baixa mudanças
git merge origin/main  # Aplica no seu branch
```

### 3️⃣ **SE VOCÊ TEM MUDANÇAS LOCAIS NÃO COMMITADAS**

```bash
# Verificar status das suas mudanças
git status

# OPÇÃO A: Salvar suas mudanças temporariamente
git stash
git pull origin main
git stash pop

# OPÇÃO B: Fazer commit das suas mudanças primeiro
git add .
git commit -m "Minhas alterações locais"
git pull origin main
```

---

## ⚠️ **RESOLVENDO CONFLITOS**

### 🔍 **Identificar Conflitos**

```bash
# Se aparecer conflito após pull:
git status  # Mostra arquivos em conflito

# Arquivos em conflito terão marcações como:
# <<<<<<< HEAD
# seu código
# =======
# código da equipe
# >>>>>>> commit-hash
```

### 🛠️ **Resolver Conflitos**

```bash
# 1. Editar arquivos em conflito manualmente
vim arquivo_em_conflito.py  # OU seu editor preferido

# 2. Remover marcações de conflito e manter código correto

# 3. Marcar conflito como resolvido
git add arquivo_em_conflito.py

# 4. Finalizar merge
git commit -m "Resolve conflito: merge com alterações da equipe"
```

---

## 📊 **WORKFLOW RECOMENDADO**

### 🔄 **ROTINA DIÁRIA**

```bash
# 1. SEMPRE começar o dia com:
cd /caminho/para/scoras_agent
git pull origin main

# 2. Trabalhar normalmente

# 3. Antes de fazer commit, verificar se há mudanças:
git fetch origin
git status

# 4. Se há mudanças no GitHub:
git pull origin main  # Baixar primeiro

# 5. Depois fazer seu commit e push:
git add .
git commit -m "Suas alterações"
git push origin main
```

### 📝 **ANTES DE FAZER GRANDES ALTERAÇÕES**

```bash
# 1. Sempre puxar mudanças mais recentes
git pull origin main

# 2. Criar branch para sua feature (opcional)
git checkout -b feature/minha-alteracao

# 3. Trabalhar na sua alteração

# 4. Quando terminar:
git checkout main
git pull origin main  # Pegar mudanças mais recentes
git merge feature/minha-alteracao
git push origin main
```

---

## 🔧 **COMANDOS DE DIAGNÓSTICO**

### 📊 **Ver Status Completo**

```bash
# Ver status local vs remoto
git status -v

# Ver diferenças não commitadas
git diff

# Ver diferenças com o GitHub
git diff origin/main

# Ver histórico de commits
git log --oneline -10

# Ver quem alterou o quê
git log --author="nome" --oneline
```

### 🔍 **Ver Mudanças Específicas**

```bash
# Ver mudanças em arquivo específico
git log -p arquivo.py

# Ver quem alterou linha específica
git blame arquivo.py

# Ver mudanças entre commits
git diff commit1..commit2
```

---

## 👥 **COLABORAÇÃO EM EQUIPE**

### ✅ **BOAS PRÁTICAS**

```bash
# 1. SEMPRE fazer pull antes de começar a trabalhar
git pull origin main

# 2. Fazer commits pequenos e frequentes
git add arquivo_alterado.py
git commit -m "Fix: corrige bug no chat API"

# 3. Usar mensagens de commit descritivas
git commit -m "feat: adiciona função de backup automático"
git commit -m "fix: corrige erro de conexão Redis"
git commit -m "docs: atualiza README com instruções Azure"

# 4. Fazer push frequentemente
git push origin main
```

### 🚨 **EVITAR PROBLEMAS**

```bash
# ❌ NÃO fazer:
git push --force  # NUNCA usar force push

# ✅ FAZER:
git pull origin main  # Sempre puxar antes de push
```

---

## 🆘 **COMANDOS DE EMERGÊNCIA**

### 🔙 **Desfazer Mudanças**

```bash
# Desfazer mudanças não commitadas
git checkout -- arquivo.py

# Desfazer último commit (mantendo mudanças)
git reset --soft HEAD~1

# Voltar para estado específico
git reset --hard commit-hash

# Recuperar arquivo deletado
git checkout HEAD -- arquivo.py
```

### 🆘 **Se Tudo Deu Errado**

```bash
# Backup do seu trabalho atual
cp -r . ../backup_scoras_$(date +%Y%m%d)

# Resetar para estado do GitHub
git fetch origin
git reset --hard origin/main

# Se precisar recuperar suas mudanças:
# Copie arquivos do backup e faça novo commit
```

---

## 📱 **EXEMPLO PRÁTICO**

### 🎯 **Cenário: Colega alterou admin_dashboard.py**

```bash
# 1. Verificar se há mudanças
git fetch origin
git status

# 2. Ver o que mudou
git log HEAD..origin/main --oneline

# 3. Baixar mudanças
git pull origin main

# 4. Verificar se está tudo OK
make status  # Testar se sistema ainda funciona

# 5. Se você também alterou admin_dashboard.py:
# - Git vai mostrar conflito
# - Abrir arquivo e resolver manualmente
# - git add admin_dashboard.py
# - git commit -m "Resolve conflito no admin dashboard"
```

---

## 🔗 **COMANDOS CONFIGURADOS PARA SEU PROJETO**

### ⚙️ **Configuração Específica Scoras**

```bash
# Navegar para projeto
cd /home/anderson/scoras/Agente_Scoras

# Pull com token (se necessário)
git pull https://andersonamaral2:***REMOVIDO***@github.com/scorastecnologialtda/scoras_agent.git main

# Push com token (se necessário)  
git push https://andersonamaral2:***REMOVIDO***@github.com/scorastecnologialtda/scoras_agent.git main
```

---

## 📋 **CHECKLIST DIÁRIO**

### ✅ **Antes de Começar a Trabalhar**
- [ ] `git pull origin main`
- [ ] `make status` (verificar se sistema funciona)
- [ ] Trabalhar nas suas alterações

### ✅ **Antes de Terminar o Dia**
- [ ] `git add .`
- [ ] `git commit -m "descrição das mudanças"`
- [ ] `git pull origin main` (verificar mudanças da equipe)
- [ ] `git push origin main`

---

## 📞 **SUPORTE**

### 🆘 **Em caso de dúvidas:**
1. **Verificar status**: `git status`
2. **Ver logs**: `git log --oneline -5`
3. **Pedir ajuda**: admin@scoras.com.br

### 🔗 **Links Úteis**
- **Repositório**: https://github.com/scorastecnologialtda/scoras_agent
- **Documentação**: README.md
- **Este guia**: GIT_WORKFLOW_TEAM.md

---

**Mantenha este arquivo sempre à mão para consulta rápida!** 📚 