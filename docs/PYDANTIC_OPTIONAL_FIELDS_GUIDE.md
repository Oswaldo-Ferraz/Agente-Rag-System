# Guia: Campos Opcionais com Valores Padrão no Pydantic

## Problema Comum
Transformar um campo obrigatório em opcional com valor padrão em esquemas Pydantic com herança.

## ❌ O que NÃO funciona

### Tentativa 1: Manter Field(...) obrigatório
```python
class ChatMessageBase(BaseModel):
    sector: str = Field(..., max_length=50)  # ❌ Obrigatório
    
    @validator('sector', pre=True, always=True)
    def validate_sector(cls, v):
        if v is None:
            return "geral"  # ❌ Nunca executa - validação falha antes
        return v
```

### Tentativa 2: Sobrescrever em classe filha
```python
class ChatMessageBase(BaseModel):
    sector: str = Field(..., max_length=50)  # ❌ Obrigatório na base

class ChatMessageCreate(ChatMessageBase):
    sector: Optional[str] = Field(default="geral")  # ❌ Não funciona - herda obrigatoriedade
```

### Tentativa 3: Root validator
```python
class ChatMessageCreate(BaseModel):
    sector: str = Field(...)  # ❌ Ainda obrigatório
    
    @root_validator(pre=True)
    def set_defaults(cls, values):
        if 'sector' not in values:
            values['sector'] = "geral"  # ❌ Nunca executa - falha antes
        return values
```

## ✅ Solução Correta

### 1. Tornar opcional na classe base
```python
from typing import Optional
from pydantic import BaseModel, Field, validator

class ChatMessageBase(BaseModel):
    client_id: UUID = Field(..., description="ID único do cliente")
    sector: Optional[str] = Field(default="geral", max_length=50, description="Setor do atendimento")
    message: str = Field(..., min_length=1, max_length=10000, description="Mensagem do cliente")
    
    @validator('sector', pre=True, always=True)
    def validate_sector(cls, v):
        """Validar e normalizar setor. Se não fornecido ou vazio, usa 'geral'."""
        # Se valor não fornecido, None ou vazio após strip, usar 'geral'
        if v is None or (isinstance(v, str) and not v.strip()):
            v = "geral"
            logger.info("Setor não fornecido ou vazio, usando 'geral' como padrão")
        
        # Normalizar para minúsculo e remover espaços
        v = str(v).strip().lower()
        
        # Validar se está na lista de setores válidos
        valid_sectors = ['financeiro', 'suporte', 'vendas', 'admin', 'geral']
        if v not in valid_sectors:
            logger.warning(f"Setor '{v}' não está na lista de setores válidos: {valid_sectors}, usando 'geral'")
            v = "geral"
        
        return v
```

### 2. Herdar sem redefinir
```python
class ChatMessageCreate(BaseModel):
    """Schema para criação de novas mensagens."""
    
    client_id: UUID = Field(..., description="ID único do cliente")
    sector: str = Field(default="geral", max_length=50, description="Setor do atendimento")
    message: str = Field(..., min_length=1, max_length=10000, description="Mensagem do cliente")
    
    # Herda o validator da classe base automaticamente
```

## 🔧 Processo de Implementação Rápida

### Passo 1: Identificar o campo
```bash
# Procurar definições do campo
grep -n "sector.*Field" app/schemas/chat.py
```

### Passo 2: Modificar a classe base
```python
# ANTES:
sector: str = Field(..., max_length=50)

# DEPOIS:
sector: Optional[str] = Field(default="valor_padrao", max_length=50)
```

### Passo 3: Adicionar/ajustar validator
```python
@validator('campo', pre=True, always=True)
def validate_campo(cls, v):
    if v is None or (isinstance(v, str) and not v.strip()):
        return "valor_padrao"
    return v.strip().lower()  # ou outra normalização
```

### Passo 4: Atualizar imports
```python
from typing import Optional  # Adicionar se não existir
```

### Passo 5: Remover redefinições desnecessárias
```python
# Se havia redefinições em classes filhas, remover
class ClasseFilha(BaseModel):
    # ❌ Remover: sector: str = Field(...)
    pass
```

### Passo 6: Testar
```bash
# Reiniciar servidor
pkill -f "python.*start_server"
python start_server.py &

# Testar sem o campo
curl -X POST "http://localhost:8000/api/v1/endpoint" \
-H "Content-Type: application/json" \
-d '{
  "outros_campos": "valores",
  // "campo_opcional": não incluir
}'

# Testar com campo vazio
curl -X POST "http://localhost:8000/api/v1/endpoint" \
-H "Content-Type: application/json" \
-d '{
  "outros_campos": "valores",
  "campo_opcional": ""
}'
```

## 📋 Checklist de Validação

- [ ] Campo definido como `Optional[Type]` na classe base
- [ ] `Field(default="valor")` configurado
- [ ] Validator com `pre=True, always=True`
- [ ] Validator trata `None` e strings vazias
- [ ] Import `Optional` adicionado
- [ ] Redefinições desnecessárias removidas
- [ ] Servidor reiniciado
- [ ] Teste sem campo passou
- [ ] Teste com campo vazio passou
- [ ] Teste com valor válido passou

## 🚨 Armadilhas Comuns

1. **Esquecer `Optional`**: Sem isso, o campo continua obrigatório
2. **Usar `Field(...)` em vez de `Field(default=...)`**: Torna obrigatório
3. **Validator sem `pre=True`**: Pode não executar para `None`
4. **Não reiniciar servidor**: Mudanças em schemas precisam restart
5. **Redefinir em classes filhas**: Pode quebrar a herança do comportamento

## ⚡ Comando Rápido para Implementar

```bash
# Template para substituição rápida
# PROCURAR:    campo: str = Field(..., 
# SUBSTITUIR:  campo: Optional[str] = Field(default="padrao", 

# Adicionar validator se não existir:
@validator('campo', pre=True, always=True)
def validate_campo(cls, v):
    if v is None or (isinstance(v, str) and not v.strip()):
        return "valor_padrao"
    return v.strip().lower()
```

## 📝 Exemplo Completo Funcionando

```python
from typing import Optional
from pydantic import BaseModel, Field, validator

class ExemploBase(BaseModel):
    nome: str = Field(..., description="Nome obrigatório")
    categoria: Optional[str] = Field(default="geral", max_length=50, description="Categoria opcional")
    
    @validator('categoria', pre=True, always=True)
    def validate_categoria(cls, v):
        if v is None or (isinstance(v, str) and not v.strip()):
            return "geral"
        return v.strip().lower()

# Teste:
# ExemploBase(nome="teste") -> categoria="geral"
# ExemploBase(nome="teste", categoria="") -> categoria="geral"  
# ExemploBase(nome="teste", categoria="custom") -> categoria="custom"
```

---

**Data**: 31/07/2025  
**Versão**: 1.0  
**Aplicação**: FastAPI Chat System  
**Caso de Uso**: Campo `sector` opcional com padrão "geral"
