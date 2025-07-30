#!/usr/bin/env python3
"""
Script para criar o banco de dados e tabelas
"""
import logging
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurações do banco
DATABASE_URL = "postgresql://postgres:postgres123@localhost:5432/chat_system_dev"

def create_database_and_tables():
    """Criar banco de dados e tabelas"""
    try:
        # Conectar ao banco
        logger.info("Conectando ao PostgreSQL...")
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Testar conexão
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            logger.info(f"✅ Conectado ao PostgreSQL: {version}")
            
            # Ativar extensão pgvector
            logger.info("Ativando extensão pgvector...")
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            conn.commit()
            logger.info("✅ Extensão pgvector ativada")
            
            # Criar tabela chat_interactions
            logger.info("Criando tabela chat_interactions...")
            create_table_sql = text("""
                CREATE TABLE IF NOT EXISTS chat_interactions (
                    id SERIAL PRIMARY KEY,
                    client_id UUID NOT NULL,
                    sector VARCHAR(50) NOT NULL,
                    message TEXT NOT NULL,
                    answer TEXT,
                    operator_name VARCHAR(100),
                    validated_by VARCHAR(20) DEFAULT 'pending',
                    embedding vector(768),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.execute(create_table_sql)
            conn.commit()
            logger.info("✅ Tabela chat_interactions criada")
            
            # Criar índices
            logger.info("Criando índices...")
            indices_sql = [
                "CREATE INDEX IF NOT EXISTS idx_chat_client_id ON chat_interactions(client_id);",
                "CREATE INDEX IF NOT EXISTS idx_chat_sector ON chat_interactions(sector);",
                "CREATE INDEX IF NOT EXISTS idx_chat_created_at ON chat_interactions(created_at);",
                "CREATE INDEX IF NOT EXISTS idx_chat_embedding ON chat_interactions USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);"
            ]
            
            for idx_sql in indices_sql:
                conn.execute(text(idx_sql))
            conn.commit()
            logger.info("✅ Índices criados")
            
            # Verificar tabela criada
            result = conn.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'chat_interactions'
                ORDER BY ordinal_position;
            """))
            
            columns = result.fetchall()
            logger.info("📊 Estrutura da tabela:")
            for col in columns:
                logger.info(f"  - {col[0]}: {col[1]}")
            
            logger.info("🎉 Banco de dados configurado com sucesso!")
            return True
            
    except OperationalError as e:
        logger.error(f"❌ Erro de conexão: {e}")
        logger.error("Verifique se o PostgreSQL está rodando na porta 5432")
        return False
    except Exception as e:
        logger.error(f"❌ Erro ao criar banco: {e}")
        return False

if __name__ == "__main__":
    success = create_database_and_tables()
    sys.exit(0 if success else 1)
