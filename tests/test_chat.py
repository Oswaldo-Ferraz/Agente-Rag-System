"""
Testes básicos para o sistema de chat.

Este módulo contém testes para:
- Conexão com banco de dados
- CRUD básico de mensagens
- Validações de schema
- Busca semântica básica
"""

import pytest
import uuid
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.models.chat import ChatInteraction
from app.schemas.chat import ChatMessageCreate, ChatMessageUpdate
from app.services.chat_service import get_chat_service
from app.services.embedding_service import get_embedding_service
from app.utils.validators import ChatValidators

# Configurar banco de dados de teste
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_chat.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Criar tabelas de teste
Base.metadata.create_all(bind=engine)


def override_get_db():
    """Override da dependency do banco para usar banco de teste."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Override da dependency
app.dependency_overrides[get_db] = override_get_db

# Cliente de teste
client = TestClient(app)


class TestDatabaseConnection:
    """Testes de conexão com banco de dados."""
    
    def test_database_connection(self):
        """Testar conexão básica com o banco de dados."""
        db = TestingSessionLocal()
        try:
            # Executar query simples
            result = db.execute("SELECT 1")
            assert result.fetchone()[0] == 1
        finally:
            db.close()
    
    def test_table_creation(self):
        """Testar se as tabelas foram criadas corretamente."""
        db = TestingSessionLocal()
        try:
            # Verificar se a tabela chat_interactions existe
            result = db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='chat_interactions'"
            )
            assert result.fetchone() is not None
        finally:
            db.close()


class TestChatModels:
    """Testes dos modelos de dados."""
    
    def test_chat_interaction_creation(self):
        """Testar criação de ChatInteraction."""
        db = TestingSessionLocal()
        try:
            # Criar mensagem de teste
            test_message = ChatInteraction(
                client_id=uuid.uuid4(),
                sector="suporte",
                message="Mensagem de teste",
                embedding=[0.1, 0.2, 0.3] + [0.0] * 1533  # Mock embedding
            )
            
            db.add(test_message)
            db.commit()
            db.refresh(test_message)
            
            # Verificar se foi criada corretamente
            assert test_message.id is not None
            assert test_message.sector == "suporte"
            assert test_message.message == "Mensagem de teste"
            assert test_message.validated_by == "pending"
            assert test_message.created_at is not None
            
        finally:
            db.close()


class TestChatSchemas:
    """Testes dos schemas Pydantic."""
    
    def test_chat_message_create_valid(self):
        """Testar criação de schema válido."""
        client_id = uuid.uuid4()
        message_data = ChatMessageCreate(
            client_id=client_id,
            sector="financeiro",
            message="Preciso de ajuda com meu boleto"
        )
        
        assert message_data.client_id == client_id
        assert message_data.sector == "financeiro"
        assert message_data.message == "Preciso de ajuda com meu boleto"
    
    def test_chat_message_create_invalid_sector(self):
        """Testar validação de setor inválido."""
        client_id = uuid.uuid4()
        
        # Setor inválido deve ser normalizado pelo validator
        message_data = ChatMessageCreate(
            client_id=client_id,
            sector="FINANCEIRO",  # Maiúsculo deve ser normalizado
            message="Teste"
        )
        assert message_data.sector == "financeiro"
    
    def test_chat_message_update_valid(self):
        """Testar schema de atualização válido."""
        update_data = ChatMessageUpdate(
            answer="Resposta de teste",
            operator_name="João Silva",
            validated_by="human"
        )
        
        assert update_data.answer == "Resposta de teste"
        assert update_data.operator_name == "João Silva"
        assert update_data.validated_by == "human"


class TestChatValidators:
    """Testes dos validadores customizados."""
    
    def test_validate_uuid_valid(self):
        """Testar validação de UUID válido."""
        test_uuid = uuid.uuid4()
        assert ChatValidators.validate_uuid(test_uuid) is True
        assert ChatValidators.validate_uuid(str(test_uuid)) is True
    
    def test_validate_uuid_invalid(self):
        """Testar validação de UUID inválido."""
        assert ChatValidators.validate_uuid("invalid-uuid") is False
        assert ChatValidators.validate_uuid(123) is False
        assert ChatValidators.validate_uuid(None) is False
    
    def test_validate_sector_valid(self):
        """Testar validação de setor válido."""
        valid, normalized = ChatValidators.validate_sector("SUPORTE")
        assert valid is True
        assert normalized == "suporte"
        
        valid, normalized = ChatValidators.validate_sector("  financeiro  ")
        assert valid is True
        assert normalized == "financeiro"
    
    def test_validate_sector_invalid(self):
        """Testar validação de setor inválido."""
        valid, normalized = ChatValidators.validate_sector("setor_inexistente")
        assert valid is False
        assert normalized is None
    
    def test_validate_message_text_valid(self):
        """Testar validação de texto de mensagem válido."""
        valid, normalized = ChatValidators.validate_message_text("  Mensagem de teste  ")
        assert valid is True
        assert normalized == "Mensagem de teste"
    
    def test_validate_message_text_invalid(self):
        """Testar validação de texto de mensagem inválido."""
        # Texto vazio
        valid, normalized = ChatValidators.validate_message_text("   ")
        assert valid is False
        
        # Texto muito longo
        long_text = "x" * 10001
        valid, normalized = ChatValidators.validate_message_text(long_text)
        assert valid is False


class TestEmbeddingService:
    """Testes do serviço de embeddings."""
    
    def test_embedding_service_initialization(self):
        """Testar inicialização do serviço."""
        service = get_embedding_service()
        assert service is not None
        assert service.model_name == "mock"
        assert service.dimension == 1536
    
    def test_generate_embedding_valid(self):
        """Testar geração de embedding para texto válido."""
        service = get_embedding_service()
        embedding = service.generate_embedding("Teste de mensagem")
        
        assert isinstance(embedding, list)
        assert len(embedding) == 1536
        assert all(isinstance(x, float) for x in embedding)
    
    def test_generate_embedding_invalid(self):
        """Testar geração de embedding para texto inválido."""
        service = get_embedding_service()
        
        with pytest.raises(ValueError):
            service.generate_embedding("")
        
        with pytest.raises(ValueError):
            service.generate_embedding("   ")
    
    def test_calculate_similarity(self):
        """Testar cálculo de similaridade."""
        service = get_embedding_service()
        
        # Embeddings idênticos devem ter similaridade 1.0
        embedding1 = [1.0] * 1536
        embedding2 = [1.0] * 1536
        similarity = service.calculate_similarity(embedding1, embedding2)
        assert similarity == 1.0
    
    def test_batch_embeddings(self):
        """Testar geração de embeddings em lote."""
        service = get_embedding_service()
        texts = ["Primeira mensagem", "Segunda mensagem", "Terceira mensagem"]
        
        embeddings = service.generate_batch_embeddings(texts)
        
        assert len(embeddings) == 3
        assert all(len(emb) == 1536 for emb in embeddings)


class TestChatService:
    """Testes do serviço de chat."""
    
    def test_create_message(self):
        """Testar criação de mensagem."""
        db = TestingSessionLocal()
        chat_service = get_chat_service()
        
        try:
            message_data = ChatMessageCreate(
                client_id=uuid.uuid4(),
                sector="suporte",
                message="Mensagem de teste para o serviço"
            )
            
            created_message = chat_service.create_message(db, message_data)
            
            assert created_message.id is not None
            assert created_message.client_id == message_data.client_id
            assert created_message.sector == message_data.sector
            assert created_message.message == message_data.message
            assert created_message.embedding is not None
            
        finally:
            db.close()
    
    def test_get_message_by_id(self):
        """Testar busca de mensagem por ID."""
        db = TestingSessionLocal()
        chat_service = get_chat_service()
        
        try:
            # Criar mensagem primeiro
            message_data = ChatMessageCreate(
                client_id=uuid.uuid4(),
                sector="vendas",
                message="Mensagem para busca por ID"
            )
            
            created_message = chat_service.create_message(db, message_data)
            
            # Buscar por ID
            found_message = chat_service.get_message_by_id(db, created_message.id)
            
            assert found_message is not None
            assert found_message.id == created_message.id
            assert found_message.message == message_data.message
            
        finally:
            db.close()
    
    def test_update_message(self):
        """Testar atualização de mensagem."""
        db = TestingSessionLocal()
        chat_service = get_chat_service()
        
        try:
            # Criar mensagem primeiro
            message_data = ChatMessageCreate(
                client_id=uuid.uuid4(),
                sector="admin",
                message="Mensagem para atualização"
            )
            
            created_message = chat_service.create_message(db, message_data)
            
            # Atualizar mensagem
            update_data = ChatMessageUpdate(
                answer="Resposta de teste",
                operator_name="Operador Teste",
                validated_by="human"
            )
            
            updated_message = chat_service.update_message(db, created_message.id, update_data)
            
            assert updated_message is not None
            assert updated_message.answer == "Resposta de teste"
            assert updated_message.operator_name == "Operador Teste"
            assert updated_message.validated_by == "human"
            
        finally:
            db.close()


class TestAPIEndpoints:
    """Testes dos endpoints da API."""
    
    def test_root_endpoint(self):
        """Testar endpoint raiz."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
    
    def test_health_endpoint(self):
        """Testar endpoint de health check."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "components" in data
    
    def test_create_message_endpoint(self):
        """Testar endpoint de criação de mensagem."""
        message_data = {
            "client_id": str(uuid.uuid4()),
            "sector": "suporte",
            "message": "Teste via API"
        }
        
        response = client.post("/api/v1/messages/", json=message_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["client_id"] == message_data["client_id"]
        assert data["sector"] == message_data["sector"]
        assert data["message"] == message_data["message"]
        assert "id" in data
    
    def test_get_message_endpoint(self):
        """Testar endpoint de busca de mensagem."""
        # Criar mensagem primeiro
        message_data = {
            "client_id": str(uuid.uuid4()),
            "sector": "financeiro",
            "message": "Teste busca via API"
        }
        
        create_response = client.post("/api/v1/messages/", json=message_data)
        created_message = create_response.json()
        
        # Buscar mensagem
        response = client.get(f"/api/v1/messages/{created_message['id']}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == created_message["id"]
        assert data["message"] == message_data["message"]
    
    def test_get_nonexistent_message(self):
        """Testar busca de mensagem inexistente."""
        response = client.get("/api/v1/messages/99999")
        assert response.status_code == 404


# Fixture para limpeza do banco de teste
@pytest.fixture(autouse=True)
def cleanup_database():
    """Limpar banco de dados após cada teste."""
    yield
    # Limpar dados após cada teste
    db = TestingSessionLocal()
    try:
        db.query(ChatInteraction).delete()
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    # Executar testes
    pytest.main([__file__, "-v"])
