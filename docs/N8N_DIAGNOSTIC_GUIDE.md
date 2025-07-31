# 🚀 GUIA DE CONFIGURAÇÃO N8N - DIAGNÓSTICO E SOLUÇÃO

## ✅ DIAGNÓSTICO REALIZADO EM 30/07/2025

### 🔍 RESUMO DOS TESTES
- **Status do Servidor**: ✅ FUNCIONANDO PERFEITAMENTE
- **Testes Realizados**: 8/8 sucessos 
- **URLs Funcionais**: Todas testadas e funcionando
- **Tempo de Resposta**: < 10ms (excelente)
- **HTTPS**: ❌ Não configurado (apenas HTTP)

---

## 🎯 CONFIGURAÇÕES RECOMENDADAS PARA N8N

### 📌 1. CONFIGURAÇÃO HTTP REQUEST NODE

**URL Base Recomendada (Mais Estável):**
```
http://127.0.0.1:8000
```

**URLs Alternativas (Todas Testadas):**
```
http://localhost:8000      ✅ (Funciona, mas pode ter problema IPv6)
http://192.168.15.43:8000  ✅ (IP da rede local)
http://0.0.0.0:8000        ✅ (Funciona localmente)
```

### 📌 2. ENDPOINT PARA TESTE RÁPIDO

**Health Check (GET):**
```
URL: http://127.0.0.1:8000/health
Method: GET
Headers: Content-Type: application/json
```

**Endpoint Principal (POST):**
```
URL: http://127.0.0.1:8000/api/v1/messages/test
Method: POST
Headers: Content-Type: application/json
```

### 📌 3. PAYLOAD PARA N8N

**Payload Mínimo (Teste):**
```json
{
  "client_id": "123e4567-e89b-12d3-a456-426614174000",
  "sector": "suporte",
  "message": "Teste do N8N"
}
```

**Setores Válidos:**
- `financeiro`
- `suporte` 
- `vendas`
- `admin`
- `geral`

---

## 🔧 CONFIGURAÇÃO N8N HTTP REQUEST NODE

### ⚙️ Configurações Básicas:
1. **Method**: POST
2. **URL**: `http://127.0.0.1:8000/api/v1/messages/test`
3. **Content-Type**: `application/json`
4. **Response Format**: JSON

### ⚙️ Headers:
```
Content-Type: application/json
Accept: application/json
User-Agent: N8N-Webhook/1.0
```

### ⚙️ Timeout Settings:
- **Connection Timeout**: 30 segundos
- **Response Timeout**: 60 segundos

### ⚙️ Body (JSON):
```json
{
  "client_id": "{{ $json.sessionId || '123e4567-e89b-12d3-a456-426614174000' }}",
  "sector": "{{ $json.sector || 'suporte' }}",
  "message": "{{ $json.message || $json.chatInput }}"
}
```

---

## ❗ PROBLEMAS IDENTIFICADOS E SOLUÇÕES

### 🚨 1. PROBLEMA IPv6
**Sintoma**: N8N tenta conectar em IPv6 (::1) primeiro
**Solução**: ✅ **JÁ IMPLEMENTADA** - Servidor força IPv4

### 🚨 2. HTTPS vs HTTP  
**Sintoma**: N8N pode estar tentando HTTPS
**Problema**: Servidor rodando apenas HTTP
**Soluções**:
   - ✅ **Imediata**: Use URLs HTTP explicitamente
   - 🔄 **Futura**: Implementar certificado SSL

### 🚨 3. Setores Inválidos
**Sintoma**: Erro 422 "Setor não válido"
**Solução**: Use apenas setores da lista: `financeiro`, `suporte`, `vendas`, `admin`, `geral`

---

## 🧪 TESTE DE CONECTIVIDADE

### Teste Manual (Terminal):
```bash
# Teste Health Check
curl -X GET http://127.0.0.1:8000/health

# Teste Endpoint Principal
curl -X POST http://127.0.0.1:8000/api/v1/messages/test \
  -H "Content-Type: application/json" \
  -d '{"client_id": "123e4567-e89b-12d3-a456-426614174000", "sector": "suporte", "message": "Teste N8N"}'
```

### Teste Automático:
```bash
python3 n8n_diagnostic.py
```

---

## 📊 RESPOSTA ESPERADA

### Health Check:
```json
{
  "status": "healthy",
  "timestamp": "2025-07-30T00:00:00Z",
  "version": "0.1.0",
  "components": {
    "database": "healthy",
    "embeddings": "healthy"
  },
  "settings": {
    "debug_mode": true,
    "embedding_model": "huggingface",
    "embedding_dimension": 768
  }
}
```

### Endpoint Test:
```json
{
  "status": "success",
  "message": "N8N conectado com sucesso!",
  "received": {
    "client_id": "123e4567-e89b-12d3-a456-426614174000",
    "sector": "suporte",
    "message": "Teste N8N"
  },
  "timestamp": "2025-07-30T00:00:00Z"
}
```

---

## 🔍 NEXT STEPS - DIAGNÓSTICO N8N

Se o N8N ainda não conseguir conectar, precisamos verificar:

### 1. **N8N Network Settings**
   - Verificar se N8N está na mesma rede
   - Testar proxy/firewall settings
   - Verificar configurações de container (se aplicável)

### 2. **N8N Logs**  
   - Checar logs do N8N para erros específicos
   - Ver tentativas de conexão
   - Verificar timeout errors

### 3. **Network Debugging**
   ```bash
   # Teste de conectividade de rede
   telnet 127.0.0.1 8000
   
   # Verificar portas abertas
   lsof -i :8000
   
   # Trace de rede
   traceroute 127.0.0.1
   ```

---

## 📞 STATUS ATUAL

✅ **Servidor FastAPI**: Funcionando perfeitamente  
✅ **Todos os endpoints**: Respondendo corretamente  
✅ **Banco de dados**: Conectado e operacional  
✅ **IPv4**: Configurado corretamente  
❓ **N8N**: Aguardando teste com configurações corretas  

**Última atualização**: 30/07/2025 08:05  
**Servidor rodando em**: `http://127.0.0.1:8000`  
**PID do processo**: 6925
