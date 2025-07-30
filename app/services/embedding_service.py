"""
Serviço de geração de embeddings para busca semântica.

Este módulo implementa a geração de embeddings usando um modelo mock
que será posteriormente substituído por um modelo real de IA.
"""

import logging
import numpy as np
from typing import List, Optional
from app.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Serviço para geração de embeddings de texto.
    
    Implementação inicial usa embeddings mock para desenvolvimento.
    Preparado para integração futura com modelos reais (OpenAI, HuggingFace, etc.).
    """
    
    def __init__(self):
        """Inicializar o serviço de embeddings."""
        self.model_name = settings.EMBEDDING_MODEL
        self.dimension = settings.EMBEDDING_DIMENSION
        logger.info(f"Inicializando EmbeddingService com modelo: {self.model_name}, dimensão: {self.dimension}")
        
        # Para desenvolvimento, usar embeddings mock
        if self.model_name == "mock":
            self._initialize_mock_embeddings()
        else:
            # Aqui seria a inicialização de modelos reais
            raise NotImplementedError(f"Modelo {self.model_name} ainda não implementado")
    
    def _initialize_mock_embeddings(self):
        """Inicializar sistema de embeddings mock para desenvolvimento."""
        logger.info("Usando embeddings mock para desenvolvimento")
        
        # Banco de dados simulado de embeddings para palavras comuns
        self.mock_embeddings = {
            "boleto": self._generate_mock_embedding("boleto"),
            "pagamento": self._generate_mock_embedding("pagamento"),
            "fatura": self._generate_mock_embedding("fatura"),
            "cobrança": self._generate_mock_embedding("cobrança"),
            "suporte": self._generate_mock_embedding("suporte"),
            "problema": self._generate_mock_embedding("problema"),
            "erro": self._generate_mock_embedding("erro"),
            "dúvida": self._generate_mock_embedding("dúvida"),
            "ajuda": self._generate_mock_embedding("ajuda"),
            "vendas": self._generate_mock_embedding("vendas"),
            "produto": self._generate_mock_embedding("produto"),
            "serviço": self._generate_mock_embedding("serviço"),
        }
    
    def _generate_mock_embedding(self, seed_text: str) -> List[float]:
        """
        Gerar embedding mock baseado em um texto seed.
        
        Args:
            seed_text: Texto base para gerar o embedding
            
        Returns:
            Lista de floats representando o embedding
        """
        # Usar hash do texto como seed para reprodutibilidade
        np.random.seed(hash(seed_text) % (2**32))
        
        # Gerar vetor aleatório normalizado
        embedding = np.random.normal(0, 1, self.dimension)
        
        # Normalizar para magnitude unitária
        embedding = embedding / np.linalg.norm(embedding)
        
        return embedding.tolist()
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Gerar embedding para um texto.
        
        Args:
            text: Texto para gerar embedding
            
        Returns:
            Lista de floats representando o embedding
            
        Raises:
            ValueError: Se o texto estiver vazio
            Exception: Para erros na geração do embedding
        """
        if not text or not text.strip():
            raise ValueError("Texto não pode estar vazio")
        
        text = text.strip().lower()
        
        try:
            if self.model_name == "mock":
                return self._generate_mock_embedding_for_text(text)
            else:
                # Aqui seria a chamada para modelos reais
                raise NotImplementedError(f"Modelo {self.model_name} não implementado")
                
        except Exception as e:
            logger.error(f"Erro ao gerar embedding para texto '{text[:50]}...': {str(e)}")
            raise Exception(f"Falha na geração do embedding: {str(e)}")
    
    def _generate_mock_embedding_for_text(self, text: str) -> List[float]:
        """
        Gerar embedding mock inteligente baseado no conteúdo do texto.
        
        Args:
            text: Texto para análise
            
        Returns:
            Embedding mock que considera similaridade semântica básica
        """
        # Procurar por palavras-chave conhecidas
        words = text.split()
        found_embeddings = []
        
        for word in words:
            if word in self.mock_embeddings:
                found_embeddings.append(np.array(self.mock_embeddings[word]))
        
        if found_embeddings:
            # Fazer média dos embeddings encontrados
            base_embedding = np.mean(found_embeddings, axis=0)
            
            # Adicionar pequeno ruído baseado no texto completo
            np.random.seed(hash(text) % (2**32))
            noise = np.random.normal(0, 0.1, self.dimension)
            
            final_embedding = base_embedding + noise
        else:
            # Se não encontrou palavras-chave, gerar baseado no hash do texto
            final_embedding = self._generate_mock_embedding(text)
            final_embedding = np.array(final_embedding)
        
        # Normalizar
        final_embedding = final_embedding / np.linalg.norm(final_embedding)
        
        return final_embedding.tolist()
    
    def generate_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Gerar embeddings para uma lista de textos.
        
        Args:
            texts: Lista de textos para gerar embeddings
            
        Returns:
            Lista de embeddings correspondentes
            
        Raises:
            ValueError: Se a lista estiver vazia
        """
        if not texts:
            raise ValueError("Lista de textos não pode estar vazia")
        
        logger.info(f"Gerando embeddings para {len(texts)} textos")
        
        embeddings = []
        for i, text in enumerate(texts):
            try:
                embedding = self.generate_embedding(text)
                embeddings.append(embedding)
            except Exception as e:
                logger.error(f"Erro ao gerar embedding para texto {i}: {str(e)}")
                # Em caso de erro, usar embedding zero para não quebrar o batch
                embeddings.append([0.0] * self.dimension)
        
        return embeddings
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calcular similaridade de cosseno entre dois embeddings.
        
        Args:
            embedding1: Primeiro embedding
            embedding2: Segundo embedding
            
        Returns:
            Similaridade de cosseno (0.0 a 1.0)
            
        Raises:
            ValueError: Se os embeddings têm dimensões diferentes
        """
        if len(embedding1) != len(embedding2):
            raise ValueError("Embeddings devem ter a mesma dimensão")
        
        # Converter para arrays numpy
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        # Calcular similaridade de cosseno
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        
        # Normalizar para range 0-1
        similarity = (similarity + 1) / 2
        
        return float(similarity)
    
    def get_model_info(self) -> dict:
        """
        Obter informações sobre o modelo atual.
        
        Returns:
            Dicionário com informações do modelo
        """
        return {
            "model_name": self.model_name,
            "dimension": self.dimension,
            "is_mock": self.model_name == "mock",
            "status": "ready"
        }


# Instância global do serviço (singleton)
_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service() -> EmbeddingService:
    """
    Obter instância singleton do serviço de embeddings.
    
    Returns:
        Instância do EmbeddingService
    """
    global _embedding_service
    
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    
    return _embedding_service
