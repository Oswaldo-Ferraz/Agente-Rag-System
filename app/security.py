"""
Sistema de autenticação por API Key para o Chat System.

Implementa verificação de API Key via header Authorization.
"""

from fastapi import HTTPException, Security, status
from fastapi.security.api_key import APIKeyHeader
from app.config import settings

# Configurar header de API Key
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def get_api_key(api_key: str = Security(api_key_header)) -> str:
    """
    Validar API Key fornecida no header.
    
    Args:
        api_key: API Key fornecida no header X-API-Key
        
    Returns:
        str: API Key validada
        
    Raises:
        HTTPException: Se API Key for inválida ou não fornecida
    """
    if api_key == settings.API_KEY:
        return api_key
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="API Key inválida ou não fornecida. Use o header X-API-Key.",
        headers={"WWW-Authenticate": "X-API-Key"},
    )

def get_api_key_optional(api_key: str = Security(api_key_header)) -> str | None:
    """
    Validar API Key opcional (para endpoints públicos com controle).
    
    Args:
        api_key: API Key fornecida no header X-API-Key
        
    Returns:
        str | None: API Key validada ou None se não fornecida
    """
    if not api_key:
        return None
        
    if api_key == settings.API_KEY:
        return api_key
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="API Key inválida. Use o header X-API-Key.",
        headers={"WWW-Authenticate": "X-API-Key"},
    )
