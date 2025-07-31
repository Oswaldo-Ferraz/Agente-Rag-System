-- Migração para adicionar campo 'tag' na tabela chat_interactions
-- Data: 31/07/2025

-- Adicionar coluna tag
ALTER TABLE chat_interactions 
ADD COLUMN tag VARCHAR(100) NOT NULL DEFAULT 'geral';

-- Criar índice para performance
CREATE INDEX idx_chat_interactions_tag ON chat_interactions(tag);

-- Comentários
COMMENT ON COLUMN chat_interactions.tag IS 'Tag para categorização adicional das mensagens';

-- Verificar estrutura atualizada
\d chat_interactions;
