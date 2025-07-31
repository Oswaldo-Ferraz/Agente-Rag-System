#!/bin/bash

# Script de inicialização para Codespace
# Configura PostgreSQL e inicia os serviços necessários

echo "🚀 Iniciando configuração do Agente IA RAG Professional..."

# Instalar PostgreSQL e extensões
sudo apt-get update
sudo apt-get install -y postgresql postgresql-contrib

# Iniciar PostgreSQL
sudo service postgresql start

# Configurar usuário e banco
sudo -u postgres psql -c "CREATE USER chat_user WITH PASSWORD 'codespace_password';"
sudo -u postgres psql -c "CREATE DATABASE chat_system_dev OWNER chat_user;"
sudo -u postgres psql -c "ALTER USER chat_user CREATEDB;"

# Instalar pgvector (se disponível)
sudo -u postgres psql -d chat_system_dev -c "CREATE EXTENSION IF NOT EXISTS vector;"

# Configurar variáveis de ambiente para o banco
export DATABASE_URL="postgresql://chat_user:codespace_password@localhost:5432/chat_system_dev"
export DB_HOST="localhost"
export DB_PORT="5432"
export DB_NAME="chat_system_dev"
export DB_USER="chat_user"
export DB_PASSWORD="codespace_password"

echo "✅ PostgreSQL configurado com sucesso!"

# Executar script de inicialização do banco se existir
if [ -f "init.sql" ]; then
    echo "📊 Executando script de inicialização..."
    sudo -u postgres psql -d chat_system_dev -f init.sql
    echo "✅ Banco inicializado!"
fi

# Instalar dependências Python se não estiverem instaladas
if [ -f "requirements.txt" ]; then
    echo "🐍 Instalando dependências Python..."
    pip install -r requirements.txt
    echo "✅ Dependências instaladas!"
fi

echo "🎉 Configuração completa! Execute 'python3 start_server.py' para iniciar."
