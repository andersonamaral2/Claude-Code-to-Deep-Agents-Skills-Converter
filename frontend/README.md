# 🎨 Frontend - Scoras AI Agent

Interface web moderna e interativa para o agente de IA da Scoras.

## 🚀 Iniciar o Frontend

### Método 1: Servidor Python (Recomendado)

```bash
# Navegar para o diretório frontend
cd frontend/

# Iniciar servidor (porta 3000)
python server.py

# Ou porta personalizada
python server.py --port 8080

# Sem abrir navegador automaticamente
python server.py --no-browser
```

### Método 2: Live Server (VS Code)

1. Instale a extensão "Live Server" no VS Code
2. Abra o arquivo `index.html`
3. Clique em "Go Live" no canto inferior direito

### Método 3: Servidor HTTP simples

```bash
# Python 3
python -m http.server 3000

# Python 2
python -m SimpleHTTPServer 3000
```

## 🌐 URLs

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## ✨ Funcionalidades

### 🎯 Teste Rápido de Leads

- **Botão Academy**: Simula lead interessado em cursos
- **Botão Digital**: Simula lead empresarial

### 🔍 Classificação Visual

- **Indicador de Lead**: Mostra visualmente o tipo identificado
- **Cores Dinâmicas**: Roxo para Academy, Azul para Digital

### 💬 Chat Interativo

- **Mensagens em Tempo Real**: Comunicação com a API
- **Typing Indicator**: Mostra quando o bot está "digitando"
- **Markdown Support**: Links, negrito, quebras de linha
- **Timestamps**: Horário de cada mensagem

### 🛠️ Controles

- **Limpar Chat**: Remove histórico local
- **Nova Conversa**: Reset completo da sessão
- **Status Online**: Indicador de conexão com API

## 🎨 Design

### Paleta de Cores

- **Primary**: `#2563eb` (Azul)
- **Academy**: `#8b5cf6` (Roxo)
- **Digital**: `#06b6d4` (Ciano)
- **Success**: `#10b981` (Verde)

### Tipografia

- **Font**: Inter (Google Fonts)
- **Icons**: Font Awesome 6.4.0

### Responsividade

- **Desktop**: Layout completo
- **Mobile**: Interface adaptada
- **Tablet**: Otimizado para touch

## 🔧 Desenvolvimento

### Estrutura de Arquivos

```
frontend/
├── index.html      # Página principal
├── style.css       # Estilos CSS
├── script.js       # Lógica JavaScript
├── server.py       # Servidor Python
└── README.md       # Esta documentação
```

### Debug Console

Abra o console do navegador e use:

```javascript
// Verificar status da API
window.scorasDebug.getApiStatus()

// IDs de usuário
window.scorasDebug.getCurrentUserId()

// Simular leads
window.scorasDebug.simulateAcademyLead()
window.scorasDebug.simulateDigitalLead()

// Limpar chat
window.scorasDebug.clearChat()
```

### Customização

#### Alterar URL da API

No arquivo `script.js`, linha 2:

```javascript
const API_BASE_URL = 'http://localhost:8000';
```

#### Adicionar Mensagens de Teste

No arquivo `script.js`, objeto `quickMessages`:

```javascript
const quickMessages = {
    academy: [
        "Sua mensagem personalizada aqui..."
    ],
    digital: [
        "Sua mensagem empresarial aqui..."
    ]
};
```

## 🐛 Troubleshooting

### Erro de CORS

Se houver erros de CORS, use o servidor Python incluído:

```bash
python server.py
```

### API não conecta

1. Verifique se o backend está rodando na porta 8000
2. Teste: `curl http://localhost:8000/health`
3. Verifique os logs do Docker: `docker compose logs chatbot-dev`

### Porta em uso

```bash
# Usar porta alternativa
python server.py --port 3001
```

### Navegador não abre

```bash
# Iniciar sem abrir navegador
python server.py --no-browser

# Depois abrir manualmente
open http://localhost:3000
```

## 🚀 Deploy

### Netlify

1. Faça upload dos arquivos `index.html`, `style.css`, `script.js`
2. Configure a variável `API_BASE_URL` para seu backend
3. Publique

### Vercel

```bash
# Instalar Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

### GitHub Pages

1. Crie um repositório no GitHub
2. Faça upload dos arquivos do frontend
3. Ative GitHub Pages nas configurações
4. Atualize `API_BASE_URL` para seu backend público

## 📱 Mobile

A interface é totalmente responsiva e funciona bem em:

- **iPhone/Android**: Safari, Chrome Mobile
- **iPad/Tablet**: Otimizado para touch
- **Progressive Web App**: Adicione à tela inicial

## 🎯 Exemplo de Uso

1. **Acesse**: http://localhost:3000
2. **Clique**: "Scoras Academy" para simular lead educacional
3. **Observe**: Indicador muda para roxo
4. **Teste**: Digite uma mensagem personalizada
5. **Reset**: Use "Nova Conversa" para testar outro tipo

## 🤝 Contribuição

Para contribuir com o frontend:

1. Faça suas alterações nos arquivos
2. Teste em diferentes navegadores
3. Verifique responsividade
4. Teste integração com API
5. Documente mudanças

---

**Desenvolvido com ❤️ pela equipe Scoras Digital** 