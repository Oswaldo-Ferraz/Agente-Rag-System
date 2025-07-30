"""
Serviço CRUD para operações de chat/mensagens.

Este módulo implementa todas as operações de banco de dados relacionadas
às mensagens de chat, incluindo busca semântica com pgvector.
"""

import logging
from datetime import datetime
from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import text, and_, or_, desc
from sqlalchemy.exc import SQLAlchemyError

from app.models.chat import ChatInteraction
from app.schemas.chat import ChatMessageCreate, ChatMessageUpdate, ChatMessageSearch
from app.services.embedding_service import get_embedding_service

logger = logging.getLogger(__name__)


class ChatService:
    """
    Serviço para operações CRUD de mensagens de chat.
    
    Implementa todas as operações necessárias para gerenciar mensagens,
    incluindo busca semântica usando pgvector.
    """
    
    def __init__(self):
        """Inicializar o serviço de chat."""
        self.embedding_service = get_embedding_service()
        logger.info("ChatService inicializado")
    
    def create_message(self, db: Session, message_data: ChatMessageCreate) -> ChatInteraction:
        """
        Criar nova mensagem de chat.
        
        Args:
            db: Sessão do banco de dados
            message_data: Dados da mensagem a ser criada
            
        Returns:
            ChatInteraction: Mensagem criada
            
        Raises:
            Exception: Para erros de banco de dados ou embedding
        """
        try:
            logger.info(f"Criando nova mensagem para cliente {message_data.client_id}")
            
            # Gerar embedding para a mensagem
            embedding = self.embedding_service.generate_embedding(message_data.message)
            logger.debug(f"Embedding gerado com {len(embedding)} dimensões")
            
            # Criar registro no banco
            db_message = ChatInteraction(
                client_id=message_data.client_id,
                sector=message_data.sector,
                message=message_data.message,
                embedding=embedding
            )
            
            db.add(db_message)
            db.commit()
            db.refresh(db_message)
            
            logger.info(f"Mensagem criada com ID: {db_message.id}")
            return db_message
            
        except SQLAlchemyError as e:
            logger.error(f"Erro de banco de dados ao criar mensagem: {str(e)}")
            db.rollback()
            raise Exception(f"Erro ao salvar mensagem no banco de dados: {str(e)}")
        except Exception as e:
            logger.error(f"Erro inesperado ao criar mensagem: {str(e)}")
            db.rollback()
            raise Exception(f"Erro interno ao criar mensagem: {str(e)}")
    
    def get_message_by_id(self, db: Session, message_id: int) -> Optional[ChatInteraction]:
        """
        Buscar mensagem por ID.
        
        Args:
            db: Sessão do banco de dados
            message_id: ID da mensagem
            
        Returns:
            ChatInteraction ou None se não encontrada
        """
        try:
            logger.debug(f"Buscando mensagem com ID: {message_id}")
            
            message = db.query(ChatInteraction).filter(ChatInteraction.id == message_id).first()
            
            if message:
                logger.debug(f"Mensagem encontrada: ID {message.id}")
            else:
                logger.debug(f"Mensagem não encontrada: ID {message_id}")
            
            return message
            
        except SQLAlchemyError as e:
            logger.error(f"Erro de banco de dados ao buscar mensagem {message_id}: {str(e)}")
            raise Exception(f"Erro ao buscar mensagem: {str(e)}")
    
    def update_message(self, db: Session, message_id: int, update_data: ChatMessageUpdate) -> Optional[ChatInteraction]:
        """
        Atualizar mensagem existente.
        
        Args:
            db: Sessão do banco de dados
            message_id: ID da mensagem a ser atualizada
            update_data: Dados para atualização
            
        Returns:
            ChatInteraction atualizada ou None se não encontrada
            
        Raises:
            Exception: Para erros de banco de dados
        """
        try:
            logger.info(f"Atualizando mensagem ID: {message_id}")
            
            # Buscar mensagem existente
            db_message = self.get_message_by_id(db, message_id)
            if not db_message:
                logger.warning(f"Tentativa de atualizar mensagem inexistente: {message_id}")
                return None
            
            # Aplicar atualizações apenas nos campos fornecidos
            update_fields = update_data.dict(exclude_unset=True)
            
            for field, value in update_fields.items():
                if hasattr(db_message, field):
                    setattr(db_message, field, value)
                    logger.debug(f"Campo {field} atualizado para: {value}")
            
            # O campo updated_at é atualizado automaticamente pelo trigger do banco
            
            db.commit()
            db.refresh(db_message)
            
            logger.info(f"Mensagem {message_id} atualizada com sucesso")
            return db_message
            
        except SQLAlchemyError as e:
            logger.error(f"Erro de banco de dados ao atualizar mensagem {message_id}: {str(e)}")
            db.rollback()
            raise Exception(f"Erro ao atualizar mensagem: {str(e)}")
    
    def get_messages_by_client(
        self, 
        db: Session, 
        client_id: UUID, 
        skip: int = 0, 
        limit: int = 100
    ) -> Tuple[List[ChatInteraction], int]:
        """
        Buscar mensagens de um cliente específico com paginação.
        
        Args:
            db: Sessão do banco de dados
            client_id: ID do cliente
            skip: Número de registros para pular
            limit: Limite de registros por página
            
        Returns:
            Tupla com (lista de mensagens, total de mensagens)
        """
        try:
            logger.debug(f"Buscando mensagens do cliente {client_id}, skip={skip}, limit={limit}")
            
            # Buscar mensagens com paginação
            query = db.query(ChatInteraction).filter(ChatInteraction.client_id == client_id)
            
            total = query.count()
            messages = query.order_by(desc(ChatInteraction.created_at)).offset(skip).limit(limit).all()
            
            logger.debug(f"Encontradas {len(messages)} mensagens de {total} total para cliente {client_id}")
            return messages, total
            
        except SQLAlchemyError as e:
            logger.error(f"Erro ao buscar mensagens do cliente {client_id}: {str(e)}")
            raise Exception(f"Erro ao buscar mensagens do cliente: {str(e)}")
    
    def semantic_search(
        self, 
        db: Session, 
        search_params: ChatMessageSearch
    ) -> List[Tuple[ChatInteraction, float]]:
        """
        Realizar busca semântica usando pgvector.
        
        Args:
            db: Sessão do banco de dados
            search_params: Parâmetros da busca semântica
            
        Returns:
            Lista de tuplas (mensagem, score_similaridade)
            
        Raises:
            Exception: Para erros na busca semântica
        """
        try:
            logger.info(f"Iniciando busca semântica para: '{search_params.query[:50]}...'")
            
            # Gerar embedding para a query
            query_embedding = self.embedding_service.generate_embedding(search_params.query)
            logger.debug(f"Embedding da query gerado com {len(query_embedding)} dimensões")
            
            # Construir query SQL para busca por similaridade
            base_query = db.query(
                ChatInteraction,
                text("1 - (embedding <=> :query_embedding) as similarity_score")
            ).filter(
                ChatInteraction.embedding.isnot(None)
            )
            
            # Aplicar filtros opcionais
            if search_params.client_id:
                base_query = base_query.filter(ChatInteraction.client_id == search_params.client_id)
                logger.debug(f"Filtro por cliente aplicado: {search_params.client_id}")
            
            if search_params.sector:
                base_query = base_query.filter(ChatInteraction.sector == search_params.sector)
                logger.debug(f"Filtro por setor aplicado: {search_params.sector}")
            
            # Aplicar filtro de similaridade mínima e ordenar por relevância
            base_query = base_query.filter(
                text("1 - (embedding <=> :query_embedding) >= :threshold")
            ).order_by(
                text("embedding <=> :query_embedding")
            ).limit(search_params.limit)
            
            # Executar query
            results = base_query.params(
                query_embedding=query_embedding,
                threshold=search_params.similarity_threshold
            ).all()
            
            # Converter resultados para formato esperado
            search_results = [(message, float(score)) for message, score in results]
            
            logger.info(f"Busca semântica retornou {len(search_results)} resultados")
            return search_results
            
        except SQLAlchemyError as e:
            logger.error(f"Erro de banco de dados na busca semântica: {str(e)}")
            raise Exception(f"Erro na busca semântica: {str(e)}")
        except Exception as e:
            logger.error(f"Erro inesperado na busca semântica: {str(e)}")
            raise Exception(f"Erro interno na busca semântica: {str(e)}")
    
    def get_messages_by_sector(
        self, 
        db: Session, 
        sector: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> Tuple[List[ChatInteraction], int]:
        """
        Buscar mensagens por setor com paginação.
        
        Args:
            db: Sessão do banco de dados
            sector: Setor para filtrar
            skip: Número de registros para pular
            limit: Limite de registros por página
            
        Returns:
            Tupla com (lista de mensagens, total de mensagens)
        """
        try:
            logger.debug(f"Buscando mensagens do setor {sector}, skip={skip}, limit={limit}")
            
            query = db.query(ChatInteraction).filter(ChatInteraction.sector == sector.lower())
            
            total = query.count()
            messages = query.order_by(desc(ChatInteraction.created_at)).offset(skip).limit(limit).all()
            
            logger.debug(f"Encontradas {len(messages)} mensagens de {total} total para setor {sector}")
            return messages, total
            
        except SQLAlchemyError as e:
            logger.error(f"Erro ao buscar mensagens do setor {sector}: {str(e)}")
            raise Exception(f"Erro ao buscar mensagens do setor: {str(e)}")
    
    def delete_message(self, db: Session, message_id: int) -> bool:
        """
        Excluir mensagem (soft delete ou hard delete).
        
        Args:
            db: Sessão do banco de dados
            message_id: ID da mensagem a ser excluída
            
        Returns:
            True se excluída com sucesso, False se não encontrada
            
        Raises:
            Exception: Para erros de banco de dados
        """
        try:
            logger.info(f"Excluindo mensagem ID: {message_id}")
            
            db_message = self.get_message_by_id(db, message_id)
            if not db_message:
                logger.warning(f"Tentativa de excluir mensagem inexistente: {message_id}")
                return False
            
            # Por enquanto fazendo hard delete - pode ser alterado para soft delete
            db.delete(db_message)
            db.commit()
            
            logger.info(f"Mensagem {message_id} excluída com sucesso")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Erro de banco de dados ao excluir mensagem {message_id}: {str(e)}")
            db.rollback()
            raise Exception(f"Erro ao excluir mensagem: {str(e)}")
    
    def get_recent_messages(
        self, 
        db: Session, 
        limit: int = 50
    ) -> List[ChatInteraction]:
        """
        Buscar mensagens mais recentes.
        
        Args:
            db: Sessão do banco de dados
            limit: Número máximo de mensagens para retornar
            
        Returns:
            Lista das mensagens mais recentes
        """
        try:
            logger.debug(f"Buscando {limit} mensagens mais recentes")
            
            messages = db.query(ChatInteraction)\
                        .order_by(desc(ChatInteraction.created_at))\
                        .limit(limit)\
                        .all()
            
            logger.debug(f"Retornadas {len(messages)} mensagens recentes")
            return messages
            
        except SQLAlchemyError as e:
            logger.error(f"Erro ao buscar mensagens recentes: {str(e)}")
            raise Exception(f"Erro ao buscar mensagens recentes: {str(e)}")


# Instância global do serviço (singleton)
_chat_service: Optional[ChatService] = None


def get_chat_service() -> ChatService:
    """
    Obter instância singleton do serviço de chat.
    
    Returns:
        Instância do ChatService
    """
    global _chat_service
    
    if _chat_service is None:
        _chat_service = ChatService()
    
    return _chat_service
