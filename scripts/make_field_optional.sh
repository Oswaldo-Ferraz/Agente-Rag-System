#!/bin/bash

# Script para implementar campos opcionais com valores padrão no Pydantic
# Uso: ./make_field_optional.sh <arquivo_schema> <nome_campo> <valor_padrao>

set -e

SCHEMA_FILE="$1"
FIELD_NAME="$2"
DEFAULT_VALUE="$3"

if [ "$#" -ne 3 ]; then
    echo "❌ Uso: $0 <arquivo_schema> <nome_campo> <valor_padrao>"
    echo "   Exemplo: $0 app/schemas/chat.py sector geral"
    exit 1
fi

if [ ! -f "$SCHEMA_FILE" ]; then
    echo "❌ Arquivo não encontrado: $SCHEMA_FILE"
    exit 1
fi

echo "🔧 Implementando campo opcional: $FIELD_NAME = '$DEFAULT_VALUE'"
echo "📄 Arquivo: $SCHEMA_FILE"
echo ""

# Backup
cp "$SCHEMA_FILE" "${SCHEMA_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
echo "💾 Backup criado: ${SCHEMA_FILE}.backup.$(date +%Y%m%d_%H%M%S)"

# Verificar se Optional está importado
if ! grep -q "from typing import.*Optional" "$SCHEMA_FILE"; then
    echo "📦 Adicionando import Optional..."
    sed -i '' 's/from typing import /from typing import Optional, /' "$SCHEMA_FILE"
fi

# Encontrar e substituir a definição do campo
echo "🔍 Procurando definição do campo '$FIELD_NAME'..."

# Procurar padrão: campo: str = Field(...
FIELD_PATTERN="${FIELD_NAME}:[[:space:]]*str[[:space:]]*=[[:space:]]*Field([[:space:]]*\.\.\."

if grep -q "$FIELD_PATTERN" "$SCHEMA_FILE"; then
    echo "✅ Campo encontrado. Modificando..."
    
    # Substituir str por Optional[str] e Field(...) por Field(default="valor")
    sed -i '' "s/${FIELD_NAME}:[[:space:]]*str[[:space:]]*=[[:space:]]*Field([[:space:]]*\.\.\.[^)]*)/${FIELD_NAME}: Optional[str] = Field(default=\"$DEFAULT_VALUE\"/g" "$SCHEMA_FILE"
    
    echo "✅ Campo modificado para opcional"
else
    echo "⚠️  Padrão não encontrado. Verificando definições existentes..."
    grep -n "$FIELD_NAME.*Field" "$SCHEMA_FILE" || echo "❌ Campo não encontrado"
fi

# Verificar se já existe validator
if grep -q "@validator('$FIELD_NAME'" "$SCHEMA_FILE"; then
    echo "✅ Validator existente encontrado"
else
    echo "📝 Adicionando validator..."
    
    # Encontrar onde adicionar o validator (após a definição da classe)
    CLASS_LINE=$(grep -n "class.*BaseModel" "$SCHEMA_FILE" | head -1 | cut -d: -f1)
    NEXT_METHOD_LINE=$(tail -n +$((CLASS_LINE + 1)) "$SCHEMA_FILE" | grep -n "@\|def\|class" | head -1 | cut -d: -f1)
    
    if [ -n "$NEXT_METHOD_LINE" ]; then
        INSERT_LINE=$((CLASS_LINE + NEXT_METHOD_LINE))
    else
        INSERT_LINE=$((CLASS_LINE + 5))  # Fallback
    fi
    
    # Criar validator
    VALIDATOR="    @validator('$FIELD_NAME', pre=True, always=True)
    def validate_${FIELD_NAME}(cls, v):
        \"\"\"Validar e normalizar $FIELD_NAME. Se não fornecido ou vazio, usa '$DEFAULT_VALUE'.\"\"\"
        if v is None or (isinstance(v, str) and not v.strip()):
            v = \"$DEFAULT_VALUE\"
            logger.info(\"$FIELD_NAME não fornecido ou vazio, usando '$DEFAULT_VALUE' como padrão\")
        
        # Normalizar para minúsculo e remover espaços
        v = str(v).strip().lower()
        
        return v
"
    
    # Inserir validator no arquivo
    sed -i '' "${INSERT_LINE}i\\
$VALIDATOR
" "$SCHEMA_FILE"
    
    echo "✅ Validator adicionado"
fi

echo ""
echo "🎉 Implementação concluída!"
echo ""
echo "📋 Próximos passos:"
echo "1. Revisar as mudanças:"
echo "   git diff $SCHEMA_FILE"
echo ""
echo "2. Reiniciar o servidor:"
echo "   pkill -f 'python.*start_server'"
echo "   python start_server.py &"
echo ""
echo "3. Testar o endpoint:"
echo "   curl -X POST 'http://localhost:8000/api/v1/endpoint' \\"
echo "   -H 'Content-Type: application/json' \\"
echo "   -d '{\"outros_campos\": \"valores\"}'"
echo ""
echo "4. Verificar logs para confirmar o comportamento"
echo ""
echo "💾 Arquivo original salvo como backup"
