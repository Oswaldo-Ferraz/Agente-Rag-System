"""
Schemas Pydantic para validação e serialização de dados de chat.

Este módulo contém os esquemas de dados para:
- Criação de mensagens
- Respostas da API
- Atualizações de mensagens  
- Validações customizadas
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, validator, root_validator
import logging

logger = logging.getLogger(__name__)


class ChatMessageBase(BaseModel):
    """Schema base para mensagens de chat."""
    
    client_id: UUID = Field(..., description="ID único do cliente")
    sector: Optional[str] = Field(default="geral", min_length=1, max_length=50, description="Setor do atendimento")
    tag: Optional[str] = Field(default="geral", max_length=100, description="Tag para categorização adicional")
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
    
    @validator('tag', pre=True, always=True)
    def validate_tag(cls, v):
        """Validar e normalizar tag. Se não fornecido ou vazio, usa 'geral'."""
        # Se valor não fornecido, None ou vazio após strip, usar 'geral'
        if v is None or (isinstance(v, str) and not v.strip()):
            v = "geral"
            logger.info("Tag não fornecida ou vazia, usando 'geral' como padrão")
        
        # Normalizar para minúsculo e remover espaços
        v = str(v).strip().lower()
        
        return v
    
    @validator('message')
    def validate_message(cls, v):
        """Validar se a mensagem não está vazia após trim."""
        if not v.strip():
            raise ValueError('Mensagem não pode estar vazia')
        return v.strip()


class ChatMessageCreate(BaseModel):
    """Schema para criação de novas mensagens."""
    
    client_id: UUID = Field(..., description="ID único do cliente")
    sector: str = Field(default="geral", max_length=50, description="Setor do atendimento")
    tag: Optional[str] = Field(default="geral", max_length=100, description="Tag para categorização adicional")
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
    
    @validator('tag', pre=True, always=True)
    def validate_tag(cls, v):
        """Validar e normalizar tag. Se não fornecido ou vazio, usa 'geral'."""
        # Se valor não fornecido, None ou vazio após strip, usar 'geral'
        if v is None or (isinstance(v, str) and not v.strip()):
            v = "geral"
            logger.info("Tag não fornecida ou vazia, usando 'geral' como padrão")
        
        # Normalizar para minúsculo e remover espaços
        v = str(v).strip().lower()
        
        return v
    
    @validator('message')
    def validate_message(cls, v):
        """Validar se a mensagem não está vazia após trim."""
        if not v.strip():
            raise ValueError('Mensagem não pode estar vazia')
        return v.strip()


class ChatMessageUpdate(BaseModel):
    """Schema para atualização de mensagens existentes."""
    
    answer: Optional[str] = Field(None, max_length=10000, description="Resposta do atendente")
    operator_name: Optional[str] = Field(None, max_length=100, description="Nome do operador")
    validated_by: Optional[str] = Field(None, description="Quem validou a resposta")
    
    @validator('answer')
    def validate_answer(cls, v):
        """Validar resposta se fornecida."""
        if v is not None:
            if not v.strip():
                raise ValueError('Resposta não pode estar vazia')
            return v.strip()
        return v
    
    @validator('validated_by')
    def validate_validated_by(cls, v):
        """Validar campo validated_by."""
        if v is not None:
            valid_values = ['human', 'ai', 'pending']
            if v not in valid_values:
                raise ValueError(f'validated_by deve ser um dos valores: {valid_values}')
        return v


class ChatMessageResponse(ChatMessageBase):
    """Schema para resposta da API com dados completos da mensagem."""
    
    id: int = Field(..., description="ID único da mensagem")
    answer: Optional[str] = Field(None, description="Resposta do atendente")
    operator_name: Optional[str] = Field(None, description="Nome do operador")
    validated_by: str = Field(default="pending", description="Status de validação")
    created_at: datetime = Field(..., description="Data/hora de criação")
    updated_at: datetime = Field(..., description="Data/hora da última atualização")
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ChatMessageSearch(BaseModel):
    """Schema para parâmetros de busca semântica."""
    
    query: str = Field(..., min_length=1, max_length=1000, description="Texto para busca semântica")
    client_id: Optional[UUID] = Field(None, description="Filtrar por cliente específico")
    sector: Optional[str] = Field(None, description="Filtrar por setor")
    limit: int = Field(default=10, ge=1, le=100, description="Número máximo de resultados")
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="Limite mínimo de similaridade")
    
    @validator('sector')
    def validate_sector(cls, v):
        """Validar setor para busca."""
        if v is not None:
            valid_sectors = ['financeiro', 'suporte', 'vendas', 'admin', 'geral']
            if v.lower() not in valid_sectors:
                logger.warning(f"Setor '{v}' não está na lista de setores válidos: {valid_sectors}")
            return v.lower()
        return v


class ChatMessageSearchResponse(ChatMessageResponse):
    """Schema para resposta de busca semântica com score de similaridade."""
    
    similarity_score: float = Field(..., description="Score de similaridade (0.0 a 1.0)")


class ChatMessageList(BaseModel):
    """Schema para listagem paginada de mensagens."""
    
    messages: List[ChatMessageResponse]
    total: int = Field(..., description="Total de mensagens encontradas")
    page: int = Field(..., description="Página atual")
    per_page: int = Field(..., description="Mensagens por página")
    has_next: bool = Field(..., description="Se há próxima página")
    has_prev: bool = Field(..., description="Se há página anterior")


class ErrorResponse(BaseModel):
    """Schema padrão para respostas de erro."""
    
    error: str = Field(..., description="Tipo do erro")
    message: str = Field(..., description="Mensagem descritiva do erro")
    details: Optional[dict] = Field(None, description="Detalhes adicionais do erro")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp do erro")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
