# 🚀 REFERÊNCIA RÁPIDA: Campos Opcionais Pydantic

## ⚡ Comando Automático
```bash
# Para implementar rapidamente
./scripts/make_field_optional.sh app/schemas/chat.py sector geral
```

## 📝 Template Manual

### 1. Import necessário
```python
from typing import Optional
```

### 2. Definição do campo
```python
# ❌ ANTES:
campo: str = Field(..., max_length=50)

# ✅ DEPOIS:
campo: Optional[str] = Field(default="valor_padrao", max_length=50)
```

### 3. Validator padrão
```python
@validator('campo', pre=True, always=True)
def validate_campo(cls, v):
    if v is None or (isinstance(v, str) and not v.strip()):
        return "valor_padrao"
    return v.strip().lower()
```

## 🔄 Processo de 30 segundos

1. **Localizar campo**: `grep -n "campo.*Field" arquivo.py`
2. **Substituir**: `str = Field(...` → `Optional[str] = Field(default="valor"`
3. **Adicionar validator** (se não existir)
4. **Reiniciar**: `pkill -f python; python start_server.py &`
5. **Testar**: `curl -X POST ... -d '{"outros": "valores"}'`

## ✅ Checklist Rápido
- [ ] `Optional[Type]` na definição
- [ ] `Field(default="valor")`
- [ ] Validator com `pre=True, always=True`
- [ ] Import `Optional`
- [ ] Servidor reiniciado
- [ ] Teste passou

## 🚨 Erros Comuns
- Esquecer `Optional` 
- Usar `Field(...)` em vez de `Field(default=...)`
- Não reiniciar servidor
- Validator sem `pre=True`

---
**Tempo estimado**: 30 segundos  
**Complexidade**: Baixa  
**Risco**: Mínimo (com backup automático)
