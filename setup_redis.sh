#!/bin/bash

echo "🔧 Setup Redis para Scoras AI Agent Dashboard"
echo "============================================="

# Verificar se Docker está rodando
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker não está rodando. Inicie o Docker primeiro."
    exit 1
fi

# Parar container Redis existente se houver
echo "🛑 Parando container Redis existente (se houver)..."
docker stop scoras-redis 2>/dev/null || true
docker rm scoras-redis 2>/dev/null || true

# Iniciar novo container Redis
echo "🚀 Iniciando Redis container..."
docker run -d \
  --name scoras-redis \
  -p 6379:6379 \
  --restart unless-stopped \
  redis:7-alpine \
  redis-server --appendonly yes

# Aguardar Redis inicializar
echo "⏳ Aguardando Redis inicializar..."
sleep 3

# Testar conexão
echo "🔍 Testando conexão com Redis..."
if docker exec scoras-redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis iniciado com sucesso!"
    echo "📊 Status do container:"
    docker ps | grep scoras-redis
    echo ""
    echo "💡 Para parar o Redis:"
    echo "   docker stop scoras-redis"
    echo ""
    echo "💡 Para remover completamente:"
    echo "   docker stop scoras-redis && docker rm scoras-redis"
    echo ""
    echo "🎉 Agora você pode executar:"
    echo "   python start_admin.py"
else
    echo "❌ Erro ao inicializar Redis"
    echo "📋 Logs do container:"
    docker logs scoras-redis
    exit 1
fi 