"""
Validadores customizados para o sistema de chat.

Este módulo contém validadores para:
- UUIDs
- Textos e mensagens
- Setores válidos
- Parâmetros de paginação
- Embeddings
"""

import re
import logging
from typing import Optional, List, Any
from uuid import UUID
from datetime import datetime

logger = logging.getLogger(__name__)


class ChatValidators:
    """Classe com validadores específicos para o sistema de chat."""
    
    # Setores válidos do sistema
    VALID_SECTORS = ['financeiro', 'suporte', 'vendas', 'admin', 'geral']
    
    # Status de validação válidos
    VALID_VALIDATION_STATUS = ['human', 'ai', 'pending']
    
    # Limites de tamanho
    MAX_MESSAGE_LENGTH = 10000
    MAX_ANSWER_LENGTH = 10000
    MAX_OPERATOR_NAME_LENGTH = 100
    MAX_SECTOR_LENGTH = 50
    
    @staticmethod
    def validate_uuid(value: Any) -> bool:
        """
        Validar se um valor é um UUID válido.
        
        Args:
            value: Valor a ser validado
            
        Returns:
            True se for UUID válido, False caso contrário
        """
        try:
            if isinstance(value, str):
                UUID(value)
                return True
            elif isinstance(value, UUID):
                return True
            else:
                return False
        except (ValueError, TypeError):
            logger.debug(f"UUID inválido: {value}")
            return False
    
    @staticmethod
    def validate_sector(sector: str) -> tuple[bool, Optional[str]]:
        """
        Validar se um setor é válido.
        
        Args:
            sector: Nome do setor a ser validado
            
        Returns:
            Tupla (é_válido, setor_normalizado)
        """
        if not isinstance(sector, str):
            return False, None
        
        sector_normalized = sector.strip().lower()
        
        if not sector_normalized:
            return False, None
        
        if sector_normalized in ChatValidators.VALID_SECTORS:
            return True, sector_normalized
        else:
            logger.warning(f"Setor inválido: {sector}. Setores válidos: {ChatValidators.VALID_SECTORS}")
            return False, None
    
    @staticmethod
    def validate_message_text(text: str, max_length: int = MAX_MESSAGE_LENGTH) -> tuple[bool, Optional[str]]:
        """
        Validar texto de mensagem.
        
        Args:
            text: Texto a ser validado
            max_length: Comprimento máximo permitido
            
        Returns:
            Tupla (é_válido, texto_normalizado)
        """
        if not isinstance(text, str):
            return False, None
        
        text_normalized = text.strip()
        
        if not text_normalized:
            logger.debug("Texto da mensagem está vazio")
            return False, None
        
        if len(text_normalized) > max_length:
            logger.warning(f"Texto muito longo: {len(text_normalized)} > {max_length}")
            return False, None
        
        # Verificar se contém apenas caracteres válidos
        if ChatValidators._contains_invalid_characters(text_normalized):
            logger.warning("Texto contém caracteres inválidos")
            return False, None
        
        return True, text_normalized
    
    @staticmethod
    def validate_operator_name(name: Optional[str]) -> tuple[bool, Optional[str]]:
        """
        Validar nome do operador.
        
        Args:
            name: Nome do operador (pode ser None)
            
        Returns:
            Tupla (é_válido, nome_normalizado)
        """
        if name is None:
            return True, None
        
        if not isinstance(name, str):
            return False, None
        
        name_normalized = name.strip()
        
        if not name_normalized:
            return True, None  # Nome vazio é válido (opcional)
        
        if len(name_normalized) > ChatValidators.MAX_OPERATOR_NAME_LENGTH:
            logger.warning(f"Nome do operador muito longo: {len(name_normalized)}")
            return False, None
        
        # Verificar formato do nome (apenas letras, espaços e alguns caracteres especiais)
        if not re.match(r'^[a-zA-ZÀ-ÿ\s\-\.\_]+$', name_normalized):
            logger.warning(f"Nome do operador com formato inválido: {name_normalized}")
            return False, None
        
        return True, name_normalized
    
    @staticmethod
    def validate_validation_status(status: Optional[str]) -> tuple[bool, Optional[str]]:
        """
        Validar status de validação.
        
        Args:
            status: Status a ser validado
            
        Returns:
            Tupla (é_válido, status_normalizado)
        """
        if status is None:
            return True, 'pending'  # Default value
        
        if not isinstance(status, str):
            return False, None
        
        status_normalized = status.strip().lower()
        
        if status_normalized in ChatValidators.VALID_VALIDATION_STATUS:
            return True, status_normalized
        else:
            logger.warning(f"Status de validação inválido: {status}. Valores válidos: {ChatValidators.VALID_VALIDATION_STATUS}")
            return False, None
    
    @staticmethod
    def validate_pagination_params(page: int, per_page: int) -> tuple[bool, str]:
        """
        Validar parâmetros de paginação.
        
        Args:
            page: Número da página
            per_page: Itens por página
            
        Returns:
            Tupla (é_válido, mensagem_erro)
        """
        if not isinstance(page, int) or page < 1:
            return False, "Página deve ser um número inteiro maior que 0"
        
        if not isinstance(per_page, int) or per_page < 1:
            return False, "Items por página deve ser um número inteiro maior que 0"
        
        if per_page > 100:
            return False, "Máximo de 100 itens por página"
        
        return True, ""
    
    @staticmethod
    def validate_similarity_threshold(threshold: float) -> tuple[bool, str]:
        """
        Validar threshold de similaridade.
        
        Args:
            threshold: Valor do threshold (0.0 a 1.0)
            
        Returns:
            Tupla (é_válido, mensagem_erro)
        """
        if not isinstance(threshold, (int, float)):
            return False, "Threshold deve ser um número"
        
        if threshold < 0.0 or threshold > 1.0:
            return False, "Threshold deve estar entre 0.0 e 1.0"
        
        return True, ""
    
    @staticmethod
    def validate_embedding(embedding: List[float], expected_dimension: int = 1536) -> tuple[bool, str]:
        """
        Validar embedding vector.
        
        Args:
            embedding: Lista de floats representando o embedding
            expected_dimension: Dimensão esperada do embedding
            
        Returns:
            Tupla (é_válido, mensagem_erro)
        """
        if not isinstance(embedding, list):
            return False, "Embedding deve ser uma lista"
        
        if len(embedding) != expected_dimension:
            return False, f"Embedding deve ter {expected_dimension} dimensões, recebido: {len(embedding)}"
        
        # Verificar se todos os elementos são números
        for i, value in enumerate(embedding):
            if not isinstance(value, (int, float)):
                return False, f"Elemento {i} do embedding não é um número: {value}"
            
            # Verificar se o valor é finito
            if not (-1e10 <= value <= 1e10):  # Reasonable bounds
                return False, f"Elemento {i} do embedding fora dos limites: {value}"
        
        return True, ""
    
    @staticmethod
    def validate_search_query(query: str) -> tuple[bool, Optional[str]]:
        """
        Validar query de busca semântica.
        
        Args:
            query: Texto da query
            
        Returns:
            Tupla (é_válido, query_normalizada)
        """
        if not isinstance(query, str):
            return False, None
        
        query_normalized = query.strip()
        
        if not query_normalized:
            return False, None
        
        if len(query_normalized) > 1000:  # Limite para queries
            logger.warning(f"Query muito longa: {len(query_normalized)}")
            return False, None
        
        # Verificar se não é só espaços ou caracteres especiais
        if not re.search(r'[a-zA-ZÀ-ÿ0-9]', query_normalized):
            logger.warning("Query não contém caracteres alfanuméricos")
            return False, None
        
        return True, query_normalized
    
    @staticmethod
    def validate_date_range(start_date: Optional[datetime], end_date: Optional[datetime]) -> tuple[bool, str]:
        """
        Validar range de datas.
        
        Args:
            start_date: Data de início (opcional)
            end_date: Data de fim (opcional)
            
        Returns:
            Tupla (é_válido, mensagem_erro)
        """
        if start_date is None and end_date is None:
            return True, ""
        
        if start_date is not None and not isinstance(start_date, datetime):
            return False, "Data de início deve ser um datetime"
        
        if end_date is not None and not isinstance(end_date, datetime):
            return False, "Data de fim deve ser um datetime"
        
        if start_date and end_date and start_date > end_date:
            return False, "Data de início deve ser anterior à data de fim"
        
        # Verificar se as datas não são muito antigas ou futuras
        now = datetime.now()
        
        if start_date and (now - start_date).days > 365 * 5:  # 5 anos
            return False, "Data de início muito antiga (máximo 5 anos)"
        
        if end_date and end_date > now:
            return False, "Data de fim não pode ser futura"
        
        return True, ""
    
    @staticmethod
    def _contains_invalid_characters(text: str) -> bool:
        """
        Verificar se o texto contém caracteres inválidos.
        
        Args:
            text: Texto a ser verificado
            
        Returns:
            True se contém caracteres inválidos
        """
        # Lista de caracteres que não são permitidos
        invalid_chars = ['\x00', '\x01', '\x02', '\x03', '\x04', '\x05', '\x06', '\x07', 
                        '\x08', '\x0b', '\x0c', '\x0e', '\x0f', '\x10', '\x11', '\x12', 
                        '\x13', '\x14', '\x15', '\x16', '\x17', '\x18', '\x19', '\x1a', 
                        '\x1b', '\x1c', '\x1d', '\x1e', '\x1f', '\x7f']
        
        return any(char in text for char in invalid_chars)


class DataSanitizer:
    """Classe para sanitização de dados de entrada."""
    
    @staticmethod
    def sanitize_text(text: str) -> str:
        """
        Sanitizar texto removendo caracteres perigosos.
        
        Args:
            text: Texto a ser sanitizado
            
        Returns:
            Texto sanitizado
        """
        if not isinstance(text, str):
            return ""
        
        # Remover caracteres de controle
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
        
        # Normalizar espaços em branco
        text = re.sub(r'\s+', ' ', text)
        
        # Remover espaços no início e fim
        text = text.strip()
        
        return text
    
    @staticmethod
    def sanitize_html(text: str) -> str:
        """
        Remover tags HTML básicas do texto.
        
        Args:
            text: Texto que pode conter HTML
            
        Returns:
            Texto sem tags HTML
        """
        if not isinstance(text, str):
            return ""
        
        # Remover tags HTML básicas
        text = re.sub(r'<[^>]+>', '', text)
        
        # Decodificar entidades HTML básicas
        html_entities = {
            '&amp;': '&',
            '&lt;': '<',
            '&gt;': '>',
            '&quot;': '"',
            '&#39;': "'",
            '&nbsp;': ' '
        }
        
        for entity, char in html_entities.items():
            text = text.replace(entity, char)
        
        return text.strip()
    
    @staticmethod
    def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
        """
        Truncar texto se necessário.
        
        Args:
            text: Texto a ser truncado
            max_length: Comprimento máximo
            suffix: Sufixo a adicionar se truncado
            
        Returns:
            Texto truncado se necessário
        """
        if not isinstance(text, str) or len(text) <= max_length:
            return text
        
        return text[:max_length - len(suffix)] + suffix
