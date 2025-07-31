# 🚀 Agente IA RAG Professional - GitHub Codespace

## ⚡ Início Rápido no Codespace

### 1. 🎯 **Configuração Automática**
O Codespace já configurou automaticamente:
- ✅ Python 3.11
- ✅ PostgreSQL com pgvector
- ✅ Dependências instaladas
- ✅ Variáveis de ambiente

### 2. 🏃‍♂️ **Iniciar o Servidor**
```bash
python3 start_server.py
```

### 3. 🌐 **Acessar a API**
- **Documentação:** `https://seu-codespace-url.app/docs`
- **API:** `https://seu-codespace-url.app/api/v1/messages`
- **Health:** `https://seu-codespace-url.app/health`

## 🔐 **Autenticação**

### **Header obrigatório:**
```
X-API-Key: agente-ia-rag-professional-key-2025
```

### **Exemplo de uso:**
```bash
curl -H "X-API-Key: agente-ia-rag-professional-key-2025" \
     -H "Content-Type: application/json" \
     -d '{"client_id":"test-123","sector":"geral","message":"Olá!"}' \
     https://seu-codespace-url.app/api/v1/messages
```

## 🔧 **Configuração do N8N**

### **URL para webhook:**
```
https://seu-codespace-url.app/api/v1/messages
```

### **Headers necessários:**
```json
{
  "Content-Type": "application/json",
  "X-API-Key": "agente-ia-rag-professional-key-2025"
}
```

### **Body exemplo:**
```json
{
  "client_id": "{{$json.client_id}}",
  "sector": "geral", 
  "tag": "atendimento",
  "message": "{{$json.message}}"
}
```

## 📊 **Monitoramento**

### **Verificar status:**
- `GET /health` - Status completo do sistema
- `GET /` - Informações básicas
- `GET /docs` - Documentação interativa

### **Logs:**
```bash
tail -f logs/chat_system.log
```

## 🎯 **Para Demonstrações**

1. **Inicie o Codespace** (consome horas apenas quando ativo)
2. **Execute o servidor** 
3. **Compartilhe a URL** da documentação
4. **Demonstre endpoints** no Swagger
5. **Pare o Codespace** para economizar horas

## 💡 **Dicas de Uso**

- 🕐 **Horas:** 60h gratuitas/mês
- 🛑 **Parar:** Para economizar horas quando não usar
- 🔄 **Reiniciar:** Dados persistem entre paradas
- 🌐 **URL pública:** Acessível via internet

## 🚀 **Deploy em Produção**

Quando quiser migrar para VPS/servidor:
1. Use os mesmos arquivos
2. Configure variáveis de ambiente
3. Execute `docker-compose up`

---

**🎉 Seu sistema RAG profissional está pronto!**
