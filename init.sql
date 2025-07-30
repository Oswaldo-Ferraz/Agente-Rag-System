-- Script de inicialização do banco de dados PostgreSQL
-- Este arquivo será executado automaticamente pelo docker-compose

-- Criar extensão pgvector
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
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Criar trigger para atualizar updated_at
DROP TRIGGER IF EXISTS update_chat_interactions_updated_at ON chat_interactions;
CREATE TRIGGER update_chat_interactions_updated_at 
BEFORE UPDATE ON chat_interactions 
FOR EACH ROW 
EXECUTE FUNCTION update_updated_at_column();

-- Inserir alguns dados de exemplo (opcional para desenvolvimento)
INSERT INTO chat_interactions (client_id, sector, message, embedding) VALUES
(
    uuid_generate_v4(),
    'suporte',
    'Olá, estou com problema no meu produto. Pode me ajudar?',
    array_fill(0.1, ARRAY[1536])::vector
),
(
    uuid_generate_v4(),
    'financeiro',
    'Preciso de ajuda com meu boleto vencido.',
    array_fill(0.2, ARRAY[1536])::vector
),
(
    uuid_generate_v4(),
    'vendas',
    'Gostaria de saber mais sobre seus produtos.',
    array_fill(0.3, ARRAY[1536])::vector
)
ON CONFLICT DO NOTHING;
