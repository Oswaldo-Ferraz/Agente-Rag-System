#!/bin/bash

# Script de configuração do ambiente local para o sistema de chat
# com PostgreSQL + pgvector + FastAPI
# Autor: Sistema de Chat AI
# Data: 29 de julho de 2025

set -e  # Sair em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para imprimir mensagens coloridas
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERRO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[AVISO]${NC} $1"
}

# Detectar o sistema operacional
OS="$(uname -s)"
print_status "Sistema detectado: $OS"

# Verificar se está rodando como root (não recomendado)
if [ "$EUID" -eq 0 ]; then 
   print_warning "Este script não deve ser executado como root!"
   exit 1
fi

# 1. Instalar PostgreSQL localmente
print_status "Verificando instalação do PostgreSQL..."

if command -v psql &> /dev/null; then
    print_status "PostgreSQL já está instalado."
    psql --version
else
    print_status "Instalando PostgreSQL..."
    
    case $OS in
        Darwin)
            # macOS
            if command -v brew &> /dev/null; then
                brew install postgresql@15
                brew services start postgresql@15
            else
                print_error "Homebrew não encontrado. Instale o Homebrew primeiro."
                exit 1
            fi
            ;;
        Linux)
            # Ubuntu/Debian
            if [ -f /etc/debian_version ]; then
                sudo apt-get update
                sudo apt-get install -y postgresql postgresql-contrib
                sudo systemctl start postgresql
                sudo systemctl enable postgresql
            # Red Hat/CentOS/Fedora
            elif [ -f /etc/redhat-release ]; then
                sudo yum install -y postgresql postgresql-server postgresql-contrib
                sudo postgresql-setup initdb
                sudo systemctl start postgresql
                sudo systemctl enable postgresql
            else
                print_error "Distribuição Linux não suportada automaticamente."
                print_error "Por favor, instale o PostgreSQL manualmente."
                exit 1
            fi
            ;;
        *)
            print_error "Sistema operacional não suportado: $OS"
            exit 1
            ;;
    esac
fi

# 2. Verificar se o PostgreSQL está rodando
print_status "Verificando se o PostgreSQL está rodando..."

if pg_isready &> /dev/null; then
    print_status "PostgreSQL está rodando."
else
    print_error "PostgreSQL não está rodando. Tentando iniciar..."
    case $OS in
        Darwin)
            brew services start postgresql@15
            ;;
        Linux)
            sudo systemctl start postgresql
            ;;
    esac
    
    # Aguardar o PostgreSQL iniciar
    sleep 5
    
    if ! pg_isready &> /dev/null; then
        print_error "Não foi possível iniciar o PostgreSQL."
        exit 1
    fi
fi

# 3. Instalar e configurar pgvector
print_status "Instalando pgvector..."

# Verificar se já está instalado
if psql -U postgres -d postgres -c "SELECT * FROM pg_extension WHERE extname = 'vector';" &> /dev/null; then
    print_status "pgvector já está instalado."
else
    case $OS in
        Darwin)
            # macOS com Homebrew
            if command -v brew &> /dev/null; then
                # Clonar e compilar pgvector
                print_status "Clonando pgvector do GitHub..."
                TEMP_DIR=$(mktemp -d)
                cd $TEMP_DIR
                git clone --branch v0.5.1 https://github.com/pgvector/pgvector.git
                cd pgvector
                
                # Compilar e instalar
                print_status "Compilando pgvector..."
                make
                sudo make install
                
                cd - > /dev/null
                rm -rf $TEMP_DIR
            fi
            ;;
        Linux)
            # Ubuntu/Debian
            if [ -f /etc/debian_version ]; then
                sudo apt-get install -y postgresql-server-dev-all git make gcc
                
                # Clonar e compilar pgvector
                print_status "Clonando pgvector do GitHub..."
                TEMP_DIR=$(mktemp -d)
                cd $TEMP_DIR
                git clone --branch v0.5.1 https://github.com/pgvector/pgvector.git
                cd pgvector
                
                # Compilar e instalar
                print_status "Compilando pgvector..."
                make
                sudo make install
                
                cd - > /dev/null
                rm -rf $TEMP_DIR
            fi
            ;;
    esac
fi

# 4. Criar banco de dados de desenvolvimento
print_status "Criando banco de dados de desenvolvimento..."

# Nome do banco e usuário
DB_NAME="chat_system_dev"
DB_USER="chat_user"

# Criar usuário sem senha (desenvolvimento local)
print_status "Criando usuário do banco de dados..."
psql -U postgres <<EOF
-- Criar usuário se não existir
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_user WHERE usename = '$DB_USER') THEN
        CREATE USER $DB_USER;
    END IF;
END
\$\$;

-- Dar permissões ao usuário
ALTER USER $DB_USER CREATEDB;
EOF

# Criar banco de dados
print_status "Criando banco de dados $DB_NAME..."
psql -U postgres <<EOF
-- Criar banco se não existir
SELECT 'CREATE DATABASE $DB_NAME OWNER $DB_USER'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$DB_NAME')\gexec
EOF

# 5. Aplicar o esquema e criar extensão vector
print_status "Aplicando esquema do banco de dados..."

psql -U postgres -d $DB_NAME <<EOF
-- Criar extensão vector
CREATE EXTENSION IF NOT EXISTS vector;

-- Criar extensão para UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Criar tabela de interações de chat
CREATE TABLE IF NOT EXISTS chat_interactions (
    id SERIAL PRIMARY KEY,
    client_id UUID NOT NULL,
    sector VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    answer TEXT,
    operator_name VARCHAR(100),
    validated_by VARCHAR(20) DEFAULT 'pending',
    embedding vector(1536),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Criar índice para busca por embedding
CREATE INDEX IF NOT EXISTS idx_chat_embedding ON chat_interactions 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Criar índice para client_id
CREATE INDEX IF NOT EXISTS idx_chat_client_id ON chat_interactions(client_id);

-- Criar índice para sector
CREATE INDEX IF NOT EXISTS idx_chat_sector ON chat_interactions(sector);

-- Criar índice para created_at
CREATE INDEX IF NOT EXISTS idx_chat_created_at ON chat_interactions(created_at);

-- Criar função para atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS \$\$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
\$\$ language 'plpgsql';

-- Criar trigger para atualizar updated_at
DROP TRIGGER IF EXISTS update_chat_interactions_updated_at ON chat_interactions;
CREATE TRIGGER update_chat_interactions_updated_at 
BEFORE UPDATE ON chat_interactions 
FOR EACH ROW 
EXECUTE FUNCTION update_updated_at_column();

-- Dar permissões ao usuário
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
GRANT ALL ON ALL TABLES IN SCHEMA public TO $DB_USER;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO $DB_USER;
EOF

# 6. Configurar conexão sem senha (desenvolvimento local)
print_status "Configurando acesso sem senha para desenvolvimento local..."

# Criar arquivo .pgpass se não existir
PGPASS_FILE="$HOME/.pgpass"
if [ ! -f "$PGPASS_FILE" ]; then
    touch "$PGPASS_FILE"
    chmod 600 "$PGPASS_FILE"
fi

# Adicionar entrada para o usuário local
echo "localhost:5432:$DB_NAME:$DB_USER:" >> "$PGPASS_FILE"
echo "localhost:5432:*:postgres:" >> "$PGPASS_FILE"

# 7. Verificar instalação e funcionamento
print_status "Verificando instalação..."

# Testar conexão
if psql -U $DB_USER -d $DB_NAME -c "SELECT version();" &> /dev/null; then
    print_status "Conexão com o banco de dados OK!"
else
    print_error "Não foi possível conectar ao banco de dados."
    exit 1
fi

# Verificar se pgvector está funcionando
if psql -U $DB_USER -d $DB_NAME -c "SELECT vector_dims(ARRAY[1,2,3]::vector);" &> /dev/null; then
    print_status "pgvector está funcionando corretamente!"
else
    print_error "pgvector não está funcionando corretamente."
    exit 1
fi

# Criar arquivo .env com configurações
print_status "Criando arquivo .env com configurações..."

cat > .env <<EOF
# Configurações do Banco de Dados
DATABASE_URL=postgresql://$DB_USER@localhost:5432/$DB_NAME
DB_HOST=localhost
DB_PORT=5432
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=

# Configurações da API
API_V1_PREFIX=/api/v1
PROJECT_NAME=Chat System
DEBUG=True

# Configurações de Embeddings
EMBEDDING_MODEL=mock
EMBEDDING_DIMENSION=1536

# Configurações de Logging
LOG_LEVEL=INFO
EOF

print_status "Arquivo .env criado com sucesso!"

# Resumo final
echo ""
print_status "===================== CONFIGURAÇÃO CONCLUÍDA ====================="
print_status "Banco de dados: $DB_NAME"
print_status "Usuário: $DB_USER"
print_status "Host: localhost"
print_status "Porta: 5432"
print_status "pgvector: Instalado e configurado"
print_status "=================================================================="
echo ""
print_status "Para conectar ao banco de dados, use:"
echo "  psql -U $DB_USER -d $DB_NAME"
echo ""
print_status "As configurações foram salvas no arquivo .env"
print_status "Próximo passo: instalar as dependências Python com 'pip install -r requirements.txt'"
