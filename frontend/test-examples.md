# 🌍 Teste de Idiomas - Scoras AI Agent

## 🎯 Como Testar os Idiomas

### Acesse: http://localhost:3000

## 🇧🇷 Português do Brasil (Padrão)

1. **Clique na bandeirinha** 🇧🇷
2. **Teste Academy**: Clique "Scoras Academy"
3. **Teste Digital**: Clique "Scoras Digital"
4. **Ou digite**: "Preciso de cursos de Python"

**Resultado esperado**: Resposta em português do Brasil

---

## 🇬🇧 English

1. **Click the flag** 🇬🇧
2. **Test Academy**: Click "Scoras Academy"
3. **Test Digital**: Click "Scoras Digital"  
4. **Or type**: "I need Python courses"

**Expected result**: Response in English

---

## 🇪🇸 Español

1. **Haz clic en la bandera** 🇪🇸
2. **Test Academy**: Haz clic en "Scoras Academy"
3. **Test Digital**: Haz clic en "Scoras Digital"
4. **O escribe**: "Necesito cursos de Python"

**Resultado esperado**: Respuesta en español

---

## 🧪 Mensagens FIXAS dos Botões

### 🇧🇷 Português

#### Botão Academy (sempre):
**"Estou interessado nos cursos da Scoras Academy, e gostaria de saber mais a respeito"**

#### Botão Digital (sempre):
**"Gostaria de implementar IA na minha empresa, ou pedir uma consultoria do Anderson para a implementação de Agentes de IA"**

### 🇬🇧 English

#### Academy Button (always):
**"I'm interested in Scoras Academy courses, and would like to know more about them"**

#### Digital Button (always):
**"I would like to implement AI in my company, or request Anderson's consulting for AI Agents implementation"**

### 🇪🇸 Español

#### Botón Academy (siempre):
**"Estoy interesado en los cursos de Scoras Academy, y me gustaría saber más al respecto"**

#### Botón Digital (siempre):
**"Me gustaría implementar IA en mi empresa, o solicitar una consultoría de Anderson para la implementación de Agentes de IA"**

---

## 🔍 Verificação de Funcionalidade

### ✅ Checklist de Teste

- [ ] **Bandeirinha 🇧🇷**: Resposta em português
- [ ] **Bandeirinha 🇬🇧**: Resposta em inglês
- [ ] **Bandeirinha 🇪🇸**: Resposta em espanhol
- [ ] **Academy Button**: Funciona em todos os idiomas
- [ ] **Digital Button**: Funciona em todos os idiomas
- [ ] **Indicador de Lead**: Muda de cor conforme tipo
- [ ] **Status Online**: Mostra conexão com API

### 🚫 Idiomas Proibidos

O sistema **JAMAIS** deve responder em:
- ❌ Chinês/Mandarim
- ❌ Francês
- ❌ Alemão
- ❌ Italiano
- ❌ Japonês
- ❌ Qualquer outro idioma

---

## 🐛 Troubleshooting

### Resposta em idioma errado?

1. **Verifique**: Bandeirinha selecionada
2. **Teste**: Click na bandeira novamente
3. **Reset**: Use "Nova Conversa"
4. **Debug**: Abra console (F12) e use:
   ```javascript
   window.scorasDebug.getCurrentLanguage()
   window.scorasDebug.setLanguage('en') // ou 'es', 'pt-BR'
   ```

### API não responde?

1. **Check Backend**: `curl http://localhost:8000/health`
2. **Check Frontend**: Console do navegador
3. **Restart**: `docker compose restart chatbot-dev`

---

## 📱 Mobile

As bandeirinhas funcionam perfeitamente em:
- **iPhone Safari**
- **Android Chrome**
- **Tablets**

---

**Desenvolvido com 🌍 pela equipe Scoras Digital** 