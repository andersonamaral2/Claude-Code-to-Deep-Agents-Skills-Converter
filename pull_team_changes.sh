#!/bin/bash

# Script para baixar mudanças da equipe - Scoras AI Agent
# Uso: ./pull_team_changes.sh

echo "🔄 Scoras AI Agent - Sincronizar com mudanças da equipe"
echo "====================================================="
echo ""

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Verificar se estamos no diretório correto
if [ ! -f "README.md" ] || [ ! -f "Makefile" ]; then
    echo -e "${RED}❌ Erro: Execute este script no diretório do projeto Scoras AI Agent${NC}"
    echo "   Navegue para: cd /home/anderson/scoras/Agente_Scoras"
    exit 1
fi

echo -e "${BLUE}📍 Diretório atual: $(pwd)${NC}"
echo ""

# Verificar status local
echo -e "${YELLOW}1️⃣ Verificando status local...${NC}"
LOCAL_CHANGES=$(git status --porcelain | wc -l)

if [ $LOCAL_CHANGES -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Você tem mudanças locais não commitadas:${NC}"
    git status --short
    echo ""
    echo -e "${YELLOW}Escolha uma opção:${NC}"
    echo "1) Fazer commit das mudanças primeiro"
    echo "2) Salvar mudanças temporariamente (stash)"
    echo "3) Cancelar e revisar mudanças"
    read -p "Digite sua escolha (1-3): " choice
    
    case $choice in
        1)
            echo -e "${BLUE}📝 Fazendo commit das mudanças locais...${NC}"
            git add .
            read -p "Digite a mensagem do commit: " commit_msg
            git commit -m "$commit_msg"
            echo -e "${GREEN}✅ Commit realizado${NC}"
            ;;
        2)
            echo -e "${BLUE}💾 Salvando mudanças temporariamente...${NC}"
            git stash push -m "Mudanças locais - $(date)"
            echo -e "${GREEN}✅ Mudanças salvas no stash${NC}"
            STASH_CREATED=true
            ;;
        3)
            echo -e "${YELLOW}⏸️  Cancelado pelo usuário${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Opção inválida${NC}"
            exit 1
            ;;
    esac
    echo ""
fi

# Verificar mudanças no GitHub
echo -e "${YELLOW}2️⃣ Verificando mudanças no GitHub...${NC}"
git fetch origin

# Verificar se há commits novos
COMMITS_BEHIND=$(git rev-list HEAD..origin/main --count 2>/dev/null || echo "0")

if [ "$COMMITS_BEHIND" = "0" ]; then
    echo -e "${GREEN}✅ Seu repositório está atualizado!${NC}"
    echo "   Não há mudanças novas da equipe."
    
    # Restaurar stash se necessário
    if [ "$STASH_CREATED" = true ]; then
        echo -e "${BLUE}🔄 Restaurando suas mudanças salvas...${NC}"
        git stash pop
        echo -e "${GREEN}✅ Mudanças restauradas${NC}"
    fi
    
    exit 0
fi

echo -e "${BLUE}📥 Há $COMMITS_BEHIND novos commits da equipe${NC}"
echo ""

# Mostrar novos commits
echo -e "${YELLOW}📋 Novos commits da equipe:${NC}"
git log --oneline HEAD..origin/main
echo ""

# Fazer pull
echo -e "${YELLOW}3️⃣ Baixando mudanças da equipe...${NC}"
if git pull origin main; then
    echo -e "${GREEN}✅ Mudanças baixadas com sucesso!${NC}"
    
    # Restaurar stash se necessário
    if [ "$STASH_CREATED" = true ]; then
        echo -e "${BLUE}🔄 Restaurando suas mudanças salvas...${NC}"
        if git stash pop; then
            echo -e "${GREEN}✅ Mudanças restauradas com sucesso${NC}"
        else
            echo -e "${RED}⚠️  Conflito ao restaurar mudanças. Resolva manualmente:${NC}"
            echo "   git status"
            echo "   # Edite arquivos em conflito"
            echo "   git add ."
            echo "   git commit -m 'Resolve conflitos após pull'"
        fi
    fi
else
    echo -e "${RED}❌ Erro durante o pull. Possível conflito.${NC}"
    echo ""
    echo -e "${YELLOW}📋 Para resolver conflitos:${NC}"
    echo "1. Veja arquivos em conflito: git status"
    echo "2. Edite arquivos manualmente"
    echo "3. Marque como resolvido: git add arquivo.py"
    echo "4. Finalize o merge: git commit"
    exit 1
fi

echo ""

# Testar sistema
echo -e "${YELLOW}4️⃣ Testando sistema após mudanças...${NC}"
if command -v make >/dev/null 2>&1; then
    if make status >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Sistema funcionando corretamente${NC}"
    else
        echo -e "${YELLOW}⚠️  Aviso: Problemas detectados no sistema${NC}"
        echo "   Execute 'make status' para mais detalhes"
    fi
else
    echo -e "${BLUE}ℹ️  Comando 'make' não disponível, pule o teste${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Sincronização concluída!${NC}"
echo ""
echo -e "${BLUE}📊 Status final:${NC}"
git status --short
echo ""
echo -e "${BLUE}📝 Últimos commits:${NC}"
git log --oneline -5
echo ""
echo -e "${YELLOW}💡 Próximos passos:${NC}"
echo "   • Trabalhe nas suas alterações"
echo "   • Faça commits frequentes: git add . && git commit -m 'descrição'"
echo "   • Faça push: git push origin main" 