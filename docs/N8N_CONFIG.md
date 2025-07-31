# 🎯 CONFIGURAÇÃO DEFINITIVA PARA N8N
# ENDPOINT RÁPIDO PARA TESTES!

## � ENDPOINT SUPER RÁPIDO (RECOMENDADO PARA TESTES):
http://192.168.15.43:8000/api/v1/messages/test

## 🔗 ENDPOINT COMPLETO (COM EMBEDDING):
http://192.168.15.43:8000/api/v1/messages/

## ⚡ CONFIGURAÇÃO N8N (TESTE RÁPIDO):

### **URL para teste:** 
`http://192.168.15.43:8000/api/v1/messages/test`

### **Método:** POST
### **Timeout:** 10 segundos (suficiente)

### **Headers:**
```
Content-Type: application/json
```

### **Body (JSON):**
```json
{
  "client_id": "550e8400-e29b-41d4-a716-446655440000",
  "sector": "suporte",
  "message": "Teste N8N"
}
```

### **Resposta do teste:**
```json
{
  "status": "success",
  "message": "N8N conectado com sucesso!",
  "received": {
    "client_id": "550e8400-e29b-41d4-a716-446655440000",
    "sector": "suporte",
    "message": "Teste N8N"
  },
  "timestamp": "2025-07-30T00:00:00Z"
}
```

## 🧪 Curls de teste:

**Teste rápido (< 1 segundo):**
```bash
curl -X POST http://192.168.15.43:8000/api/v1/messages/test \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "550e8400-e29b-41d4-a716-446655440000",
    "sector": "suporte",
    "message": "Teste N8N"
  }'
```

**Endpoint completo (4-5 segundos):**
```bash
curl -X POST http://192.168.15.43:8000/api/v1/messages/ \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "550e8400-e29b-41d4-a716-446655440000",
    "sector": "suporte",
    "message": "Teste N8N"
  }'
```

## 🎯 SOLUÇÃO LOADING:
1. **Use primeiro o `/test`** - resposta instantânea
2. **Se funcionar, teste o endpoint completo** com timeout 30s
3. **URL deve ter `/` no final sempre**

## ⚠️ OBSERVAÇÃO IMPORTANTE:
Na sua imagem vejo que falta `/` no final da URL. Use:
- ✅ `http://192.168.15.43:8000/api/v1/messages/test`
- ❌ `http://192.168.15.43:8000/api/v1/messages/test` (sem /)

## 🌐 URLs de monitoramento:
- Health: http://192.168.15.43:8000/health
- Docs: http://192.168.15.43:8000/docs
