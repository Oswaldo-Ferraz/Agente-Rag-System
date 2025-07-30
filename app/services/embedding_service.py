"""
Serviço de Embeddings com suporte a HuggingFace (principal) e OpenAI (fallback)
"""
import logging
import random
from typing import List, Optional
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Configuração de logging
logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self, model_type: str = "mock", fallback_type: str = "openai", 
                 huggingface_model: str = "neuralmind/bert-base-portuguese-cased",
                 openai_api_key: str = ""):
        """
        Inicializa o serviço de embeddings com fallback automático
        
        Args:
            model_type: Tipo do modelo principal ('huggingface', 'openai', 'mock')
            fallback_type: Tipo do modelo de fallback ('openai', 'mock')
            huggingface_model: Nome do modelo HuggingFace
            openai_api_key: Chave da API OpenAI
        """
        self.model_type = model_type
        self.fallback_type = fallback_type
        self.huggingface_model = huggingface_model
        self.openai_api_key = openai_api_key
        
        # Modelos carregados sob demanda
        self._hf_model = None
        self._openai_client = None
        
        logger.info(f"EmbeddingService inicializado - Principal: {model_type}, Fallback: {fallback_type}")
    
    def _load_huggingface_model(self):
        """Carrega o modelo HuggingFace sob demanda"""
        if self._hf_model is None:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info(f"Carregando modelo HuggingFace: {self.huggingface_model}")
                self._hf_model = SentenceTransformer(self.huggingface_model)
                logger.info("Modelo HuggingFace carregado com sucesso")
            except Exception as e:
                logger.error(f"Erro ao carregar modelo HuggingFace: {e}")
                raise
        return self._hf_model
    
    def _load_openai_client(self):
        """Carrega o cliente OpenAI sob demanda"""
        if self._openai_client is None:
            try:
                import openai
                logger.info("Configurando cliente OpenAI")
                self._openai_client = openai.OpenAI(api_key=self.openai_api_key)
                logger.info("Cliente OpenAI configurado com sucesso")
            except Exception as e:
                logger.error(f"Erro ao configurar cliente OpenAI: {e}")
                raise
        return self._openai_client
    
    def _generate_huggingface_embedding(self, text: str) -> List[float]:
        """Gera embedding usando HuggingFace"""
        try:
            model = self._load_huggingface_model()
            embedding = model.encode(text, convert_to_tensor=False)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Erro ao gerar embedding HuggingFace: {e}")
            raise
    
    def _generate_openai_embedding(self, text: str) -> List[float]:
        """Gera embedding usando OpenAI"""
        try:
            client = self._load_openai_client()
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Erro ao gerar embedding OpenAI: {e}")
            raise
    
    def _generate_mock_embedding(self, text: str) -> List[float]:
        """Gera embedding mock para desenvolvimento"""
        # Set seed baseado no hash do texto para consistência
        random.seed(hash(text) % 2**32)
        return [random.uniform(-1, 1) for _ in range(1536)]
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Gera embedding para um texto com fallback automático
        
        Args:
            text: Texto para gerar embedding
            
        Returns:
            Lista com valores do embedding
        """
        if not text or not text.strip():
            logger.warning("Texto vazio fornecido para embedding")
            return [0.0] * 1536
        
        # Tenta o modelo principal
        try:
            if self.model_type == "huggingface":
                logger.debug("Gerando embedding com HuggingFace")
                return self._generate_huggingface_embedding(text)
            elif self.model_type == "openai":
                logger.debug("Gerando embedding com OpenAI")
                return self._generate_openai_embedding(text)
            elif self.model_type == "mock":
                logger.debug("Gerando embedding mock")
                return self._generate_mock_embedding(text)
        except Exception as e:
            logger.warning(f"Falha no modelo principal {self.model_type}: {e}")
            
            # Tenta o fallback
            try:
                logger.info(f"Tentando fallback para {self.fallback_type}")
                if self.fallback_type == "openai":
                    return self._generate_openai_embedding(text)
                elif self.fallback_type == "mock":
                    return self._generate_mock_embedding(text)
            except Exception as fallback_error:
                logger.error(f"Falha no fallback {self.fallback_type}: {fallback_error}")
                
                # Último recurso: mock
                logger.warning("Usando embedding mock como último recurso")
                return self._generate_mock_embedding(text)
        
        # Fallback final
        logger.error("Todos os métodos falharam, retornando embedding zero")
        return [0.0] * 1536
    
    def generate_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Gera embeddings em lote para múltiplos textos
        
        Args:
            texts: Lista de textos
            
        Returns:
            Lista de embeddings
        """
        if not texts:
            return []
        
        logger.info(f"Gerando {len(texts)} embeddings em lote")
        
        # Para HuggingFace, podemos usar processamento em lote
        if self.model_type == "huggingface":
            try:
                model = self._load_huggingface_model()
                embeddings = model.encode(texts, convert_to_tensor=False)
                return embeddings.tolist()
            except Exception as e:
                logger.warning(f"Falha no batch HuggingFace: {e}")
        
        # Para outros modelos ou fallback, processa individualmente
        embeddings = []
        for text in texts:
            embeddings.append(self.generate_embedding(text))
        
        return embeddings
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calcula similaridade coseno entre dois embeddings
        
        Args:
            embedding1: Primeiro embedding
            embedding2: Segundo embedding
            
        Returns:
            Similaridade coseno (0-1)
        """
        try:
            # Converte para arrays numpy
            emb1 = np.array(embedding1).reshape(1, -1)
            emb2 = np.array(embedding2).reshape(1, -1)
            
            # Calcula similaridade coseno
            similarity = cosine_similarity(emb1, emb2)[0][0]
            
            # Garante que o resultado esteja entre 0 e 1
            return max(0.0, min(1.0, similarity))
            
        except Exception as e:
            logger.error(f"Erro ao calcular similaridade: {e}")
            return 0.0
    
    def get_model_info(self) -> dict:
        """
        Retorna informações sobre os modelos configurados
        
        Returns:
            Dicionário com informações dos modelos
        """
        return {
            "primary_model": self.model_type,
            "fallback_model": self.fallback_type,
            "huggingface_model": self.huggingface_model,
            "openai_configured": bool(self.openai_api_key),
            "embedding_dimension": 1536
        }


# Instância global do serviço
embedding_service: Optional[EmbeddingService] = None

def get_embedding_service() -> EmbeddingService:
    """
    Retorna a instância global do serviço de embeddings
    Cria uma nova se não existir
    """
    global embedding_service
    
    if embedding_service is None:
        from app.config import settings
        
        embedding_service = EmbeddingService(
            model_type=settings.EMBEDDING_MODEL,
            fallback_type=settings.EMBEDDING_FALLBACK,
            huggingface_model=settings.HUGGINGFACE_MODEL_NAME,
            openai_api_key=settings.OPENAI_API_KEY
        )
    
    return embedding_service
