"""
API endpoints v1 para operações de chat/mensagens.

Este módulo implementa todos os endpoints REST para:
- Criar mensagens
- Buscar mensagens por ID
- Busca semântica
- Atualizar mensagens
- Histórico por cliente
- Listagem por setor
"""

import logging
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.security import get_api_key
from app.schemas.chat import (
    ChatMessageCreate, 
    ChatMessageResponse, 
    ChatMessageUpdate, 
    ChatMessageSearch,
    ChatMessageSearchResponse,
    ChatMessageList,
    ErrorResponse
)
from app.services.chat_service import get_chat_service

logger = logging.getLogger(__name__)

# Router para endpoints de chat
router = APIRouter(prefix="/messages", tags=["chat"])


def get_db():
    """
    Dependency para obter sessão do banco de dados.
    
    Yields:
        Session: Sessão do SQLAlchemy
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Erro na sessão do banco de dados: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


@router.get("/n8n-ping", response_model=dict, status_code=status.HTTP_200_OK)
async def n8n_ping():
    """
    Endpoint simples de ping para testar conectividade do N8N - sem parâmetros.
    """
    return {
        "status": "success",
        "message": "Pong! Servidor FastAPI está funcionando",
        "timestamp": "2025-07-30T03:15:00Z",
        "server": "FastAPI Chat System",
        "version": "1.0.0"
    }


@router.post("/test", response_model=dict, status_code=status.HTTP_200_OK)
async def test_n8n(message_data: ChatMessageCreate):
    """
    Endpoint de teste rápido para N8N - sem processamento de embedding.
    """
    try:
        return {
            "status": "success",
            "message": "N8N conectado com sucesso!",
            "received": {
                "client_id": str(message_data.client_id),
                "sector": message_data.sector,
                "message": message_data.message
            },
            "timestamp": "2025-07-30T00:00:00Z"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": "2025-07-30T00:00:00Z"
        }


@router.post("", response_model=ChatMessageResponse, status_code=status.HTTP_201_CREATED)
def create_message(
    message_data: ChatMessageCreate,
    db: Session = Depends(get_db),
    chat_service = Depends(get_chat_service),
    api_key: str = Depends(get_api_key)
):
    """
    Criar nova mensagem de chat.
    
    - **client_id**: UUID único do cliente
    - **sector**: Setor do atendimento (financeiro, suporte, vendas, admin, geral)
    - **message**: Conteúdo da mensagem (máximo 10.000 caracteres)
    
    A mensagem será automaticamente processada para gerar o embedding
    necessário para busca semântica.
    """
    try:
        logger.info(f"Criando nova mensagem para cliente {message_data.client_id}")
        
        # Criar mensagem usando o serviço
        new_message = chat_service.create_message(db, message_data)
        
        logger.info(f"Mensagem criada com sucesso: ID {new_message.id}")
        return new_message
        
    except ValueError as e:
        logger.warning(f"Dados inválidos na criação de mensagem: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Dados inválidos: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Erro interno ao criar mensagem: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.get(
    "/{message_id}",
    response_model=ChatMessageResponse,
    summary="Buscar mensagem por ID",
    description="Retorna uma mensagem específica pelo seu ID",
    responses={
        200: {"description": "Mensagem encontrada"},
        404: {"model": ErrorResponse, "description": "Mensagem não encontrada"},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor"}
    }
)
def get_message(
    message_id: int,
    db: Session = Depends(get_db),
    chat_service = Depends(get_chat_service),
    api_key: str = Depends(get_api_key)
):
    """
    Buscar mensagem específica por ID.
    
    - **message_id**: ID único da mensagem
    """
    try:
        logger.debug(f"Buscando mensagem ID: {message_id}")
        
        # Buscar mensagem usando o serviço
        message = chat_service.get_message_by_id(db, message_id)
        
        if not message:
            logger.warning(f"Mensagem não encontrada: ID {message_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Mensagem com ID {message_id} não encontrada"
            )
        
        logger.debug(f"Mensagem encontrada: ID {message.id}")
        return message
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.error(f"Erro interno ao buscar mensagem {message_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.put(
    "/{message_id}",
    response_model=ChatMessageResponse,
    summary="Atualizar mensagem",
    description="Atualiza uma mensagem existente (resposta, operador, validação)",
    responses={
        200: {"description": "Mensagem atualizada com sucesso"},
        404: {"model": ErrorResponse, "description": "Mensagem não encontrada"},
        400: {"model": ErrorResponse, "description": "Dados inválidos"},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor"}
    }
)
def update_message(
    message_id: int,
    update_data: ChatMessageUpdate,
    db: Session = Depends(get_db),
    chat_service = Depends(get_chat_service)
):
    """
    Atualizar mensagem existente.
    
    - **message_id**: ID da mensagem a ser atualizada
    - **answer**: Resposta do atendente (opcional)
    - **operator_name**: Nome do operador (opcional)
    - **validated_by**: Status de validação: 'human', 'ai' ou 'pending' (opcional)
    """
    try:
        logger.info(f"Atualizando mensagem ID: {message_id}")
        
        # Atualizar mensagem usando o serviço
        updated_message = chat_service.update_message(db, message_id, update_data)
        
        if not updated_message:
            logger.warning(f"Tentativa de atualizar mensagem inexistente: ID {message_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Mensagem com ID {message_id} não encontrada"
            )
        
        logger.info(f"Mensagem atualizada com sucesso: ID {message_id}")
        return updated_message
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except ValueError as e:
        logger.warning(f"Dados inválidos na atualização: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Dados inválidos: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Erro interno ao atualizar mensagem {message_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.post(
    "/search",
    response_model=List[ChatMessageSearchResponse],
    summary="Busca semântica",
    description="Realiza busca semântica nas mensagens usando pgvector",
    responses={
        200: {"description": "Resultados da busca semântica"},
        400: {"model": ErrorResponse, "description": "Parâmetros inválidos"},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor"}
    }
)
def semantic_search(
    search_params: ChatMessageSearch,
    db: Session = Depends(get_db),
    chat_service = Depends(get_chat_service)
):
    """
    Busca semântica nas mensagens usando similaridade vetorial.
    
    - **query**: Texto para busca semântica (obrigatório)
    - **client_id**: Filtrar por cliente específico (opcional)
    - **sector**: Filtrar por setor (opcional)
    - **limit**: Número máximo de resultados (1-100, padrão: 10)
    - **similarity_threshold**: Limite mínimo de similaridade (0.0-1.0, padrão: 0.7)
    
    Retorna mensagens ordenadas por relevância com score de similaridade.
    """
    try:
        logger.info(f"Iniciando busca semântica: '{search_params.query[:50]}...'")
        
        # Realizar busca semântica usando o serviço
        search_results = chat_service.semantic_search(db, search_params)
        
        # Converter resultados para o formato de resposta
        response_results = []
        for message, similarity_score in search_results:
            result = ChatMessageSearchResponse(
                **message.__dict__,
                similarity_score=similarity_score
            )
            response_results.append(result)
        
        logger.info(f"Busca semântica retornou {len(response_results)} resultados")
        return response_results
        
    except ValueError as e:
        logger.warning(f"Parâmetros inválidos na busca semântica: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Parâmetros inválidos: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Erro interno na busca semântica: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.get(
    "/client/{client_id}",
    response_model=ChatMessageList,
    summary="Histórico do cliente",
    description="Retorna histórico de mensagens de um cliente específico",
    responses={
        200: {"description": "Histórico do cliente"},
        400: {"model": ErrorResponse, "description": "Parâmetros inválidos"},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor"}
    }
)
def get_client_history(
    client_id: UUID,
    page: int = Query(1, ge=1, description="Número da página"),
    per_page: int = Query(20, ge=1, le=100, description="Mensagens por página"),
    db: Session = Depends(get_db),
    chat_service = Depends(get_chat_service)
):
    """
    Buscar histórico de mensagens de um cliente específico.
    
    - **client_id**: UUID do cliente
    - **page**: Número da página (padrão: 1)
    - **per_page**: Mensagens por página (1-100, padrão: 20)
    
    Retorna mensagens ordenadas da mais recente para a mais antiga.
    """
    try:
        logger.debug(f"Buscando histórico do cliente {client_id}, página {page}")
        
        # Calcular skip baseado na página
        skip = (page - 1) * per_page
        
        # Buscar mensagens do cliente
        messages, total = chat_service.get_messages_by_client(db, client_id, skip, per_page)
        
        # Calcular metadados de paginação
        total_pages = (total + per_page - 1) // per_page
        has_next = page < total_pages
        has_prev = page > 1
        
        response = ChatMessageList(
            messages=messages,
            total=total,
            page=page,
            per_page=per_page,
            has_next=has_next,
            has_prev=has_prev
        )
        
        logger.debug(f"Retornando {len(messages)} mensagens de {total} total para cliente {client_id}")
        return response
        
    except ValueError as e:
        logger.warning(f"Parâmetros inválidos no histórico do cliente: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Parâmetros inválidos: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Erro interno ao buscar histórico do cliente {client_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.get(
    "/sector/{sector}",
    response_model=ChatMessageList,
    summary="Mensagens por setor",
    description="Retorna mensagens filtradas por setor",
    responses={
        200: {"description": "Mensagens do setor"},
        400: {"model": ErrorResponse, "description": "Parâmetros inválidos"},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor"}
    }
)
def get_sector_messages(
    sector: str,
    page: int = Query(1, ge=1, description="Número da página"),
    per_page: int = Query(20, ge=1, le=100, description="Mensagens por página"),
    db: Session = Depends(get_db),
    chat_service = Depends(get_chat_service)
):
    """
    Buscar mensagens por setor.
    
    - **sector**: Nome do setor (financeiro, suporte, vendas, admin, geral)
    - **page**: Número da página (padrão: 1)
    - **per_page**: Mensagens por página (1-100, padrão: 20)
    
    Retorna mensagens ordenadas da mais recente para a mais antiga.
    """
    try:
        logger.debug(f"Buscando mensagens do setor {sector}, página {page}")
        
        # Validar setor
        valid_sectors = ['financeiro', 'suporte', 'vendas', 'admin', 'geral']
        if sector.lower() not in valid_sectors:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Setor inválido. Valores válidos: {valid_sectors}"
            )
        
        # Calcular skip baseado na página
        skip = (page - 1) * per_page
        
        # Buscar mensagens do setor
        messages, total = chat_service.get_messages_by_sector(db, sector, skip, per_page)
        
        # Calcular metadados de paginação
        total_pages = (total + per_page - 1) // per_page
        has_next = page < total_pages
        has_prev = page > 1
        
        response = ChatMessageList(
            messages=messages,
            total=total,
            page=page,
            per_page=per_page,
            has_next=has_next,
            has_prev=has_prev
        )
        
        logger.debug(f"Retornando {len(messages)} mensagens de {total} total para setor {sector}")
        return response
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.error(f"Erro interno ao buscar mensagens do setor {sector}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.get(
    "/recent",
    response_model=List[ChatMessageResponse],
    summary="Mensagens recentes",
    description="Retorna as mensagens mais recentes do sistema",
    responses={
        200: {"description": "Mensagens recentes"},
        400: {"model": ErrorResponse, "description": "Parâmetros inválidos"},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor"}
    }
)
def get_recent_messages(
    limit: int = Query(50, ge=1, le=100, description="Número máximo de mensagens"),
    db: Session = Depends(get_db),
    chat_service = Depends(get_chat_service)
):
    """
    Buscar mensagens mais recentes do sistema.
    
    - **limit**: Número máximo de mensagens (1-100, padrão: 50)
    
    Útil para dashboards e monitoramento em tempo real.
    """
    try:
        logger.debug(f"Buscando {limit} mensagens mais recentes")
        
        # Buscar mensagens recentes
        messages = chat_service.get_recent_messages(db, limit)
        
        logger.debug(f"Retornando {len(messages)} mensagens recentes")
        return messages
        
    except Exception as e:
        logger.error(f"Erro interno ao buscar mensagens recentes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.delete(
    "/{message_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir mensagem",
    description="Exclui uma mensagem do sistema",
    responses={
        204: {"description": "Mensagem excluída com sucesso"},
        404: {"model": ErrorResponse, "description": "Mensagem não encontrada"},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor"}
    }
)
def delete_message(
    message_id: int,
    db: Session = Depends(get_db),
    chat_service = Depends(get_chat_service)
):
    """
    Excluir mensagem do sistema.
    
    - **message_id**: ID da mensagem a ser excluída
    
    **Atenção**: Esta operação é irreversível.
    """
    try:
        logger.info(f"Excluindo mensagem ID: {message_id}")
        
        # Tentar excluir mensagem
        deleted = chat_service.delete_message(db, message_id)
        
        if not deleted:
            logger.warning(f"Tentativa de excluir mensagem inexistente: ID {message_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Mensagem com ID {message_id} não encontrada"
            )
        
        logger.info(f"Mensagem excluída com sucesso: ID {message_id}")
        return  # 204 No Content
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.error(f"Erro interno ao excluir mensagem {message_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )
