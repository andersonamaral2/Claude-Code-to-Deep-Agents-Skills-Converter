# Configuração do Azure Cache for Redis 🔧

## 📋 Passos para obter as credenciais do seu Redis

### 1. Acesse o Azure Portal
- Vá para [https://portal.azure.com](https://portal.azure.com)
- Faça login com sua conta

### 2. Encontre seu Redis Cache
- Procure por "cache-redis" na barra de pesquisa
- Ou vá em "Todos os recursos" e procure por "cache-redis"

### 3. Obtenha as informações de conexão

#### Hostname:
- No menu lateral, clique em **"Propriedades"**
- Copie o valor do **"Nome do host"** (deve ser algo como: `cache-redis.redis.cache.windows.net`)

#### Chaves de Acesso:
- No menu lateral, clique em **"Chaves de acesso"**
- Copie a **"Chave primária"** ou **"Chave secundária"**

#### Porta:
- Para conexões SSL (recomendado): **6380**
- Para conexões não-SSL: **6379**

### 4. Configure seu arquivo `.env`

Copie o arquivo `.env.example` para `.env`:
```bash
cp .env.example .env
```

Edite o arquivo `.env` e substitua os valores:

```bash
# Azure Redis Cache Configuration
REDIS_HOST=cache-redis.redis.cache.windows.net
REDIS_PORT=6380
REDIS_PASSWORD=SUA_CHAVE_PRIMARIA_AQUI
REDIS_SSL=true

# Ou use a URL completa (mais simples):
REDIS_URL=rediss://:SUA_CHAVE_PRIMARIA_AQUI@cache-redis.redis.cache.windows.net:6380/0
```

### 5. Configuração de Rede (Importante!)

Seu Redis tem **"publicNetworkAccess": "Disabled"**, então você só pode acessá-lo através de:

#### Opção A: Private Endpoint (Recomendado para produção)
- Certifique-se de que sua aplicação está rodando na mesma VNet ou tem conectividade
- Use VPN ou ExpressRoute se estiver acessando externamente

#### Opção B: Habilitar Acesso Público (Para desenvolvimento)
1. No Azure Portal, vá para seu Redis
2. No menu lateral, clique em **"Configurações avançadas"**
3. Em **"Permitir acesso via endpoint público"**, selecione **"Habilitado"**
4. Configure as regras de firewall se necessário

### 6. Testando a Conexão

Execute o teste de conexão:
```bash
python -c "
import os
from redis import Redis
from dotenv import load_dotenv

load_dotenv()

redis_url = os.getenv('REDIS_URL')
if redis_url:
    client = Redis.from_url(redis_url, decode_responses=False)
else:
    client = Redis(
        host=os.getenv('REDIS_HOST'),
        port=int(os.getenv('REDIS_PORT', 6380)),
        password=os.getenv('REDIS_PASSWORD'),
        ssl=True,
        ssl_cert_reqs=None
    )

try:
    result = client.ping()
    print('✅ Conexão com Azure Redis Cache bem-sucedida!')
    print(f'Resposta do ping: {result}')
except Exception as e:
    print(f'❌ Erro na conexão: {e}')
"
```

## 🔐 Autenticação AAD (Avançado)

Se preferir usar Azure Active Directory em vez de chaves de acesso:

1. No Azure Portal, vá para seu Redis
2. No menu lateral, clique em **"Autenticação"**
3. Configure o **"Microsoft Entra ID authentication"**
4. Use estas variáveis no `.env`:

```bash
REDIS_USE_AAD=true
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
AZURE_TENANT_ID=your-tenant-id
```

## 🚨 Troubleshooting

### Erro: "Connection timeout"
- Verifique se o acesso público está habilitado
- Confirme as regras de firewall
- Teste a conectividade de rede

### Erro: "Authentication failed"
- Verifique se a chave de acesso está correta
- Confirme se não há caracteres especiais na chave

### Erro: "SSL connection error"
- Use a porta 6380 para SSL
- Certifique-se de que `REDIS_SSL=true`
- Use `rediss://` (com 's') na URL

## 📊 Monitoramento

No Azure Portal, você pode monitorar:
- **Métricas**: CPU, memória, conexões
- **Alertas**: Configure alertas para alta utilização
- **Logs**: Veja logs de conexão e erros 