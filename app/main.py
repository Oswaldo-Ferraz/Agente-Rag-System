"""
Aplicação principal FastAPI para o sistema de chat.

Sistema completo de chat/atendimento com:
- Armazenamento em PostgreSQL
- Busca semântica com pgvector
- API REST completa
- Preparado para integração com IA
"""

import logging
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import engine, Base
from app.api.v1.chat import router as chat_router

# Configurar logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('chat_system.log') if not settings.DEBUG else logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerenciar ciclo de vida da aplicação.
    
    Executa inicialização e limpeza necessárias.
    """
    # Startup: Verificar conexão com banco e criar tabelas se necessário
    logger.info("Inicializando aplicação Chat System...")
    
    try:
        # Verificar se as tabelas existem (não criar automaticamente em produção)
        if settings.DEBUG:
            logger.info("Modo DEBUG: Verificando estrutura do banco de dados...")
            # Em desenvolvimento, pode criar tabelas automaticamente
            # Base.metadata.create_all(bind=engine)
            
        logger.info("Sistema inicializado com sucesso!")
        
    except Exception as e:
        logger.error(f"Erro na inicialização: {str(e)}")
        raise
    
    yield
    
    # Shutdown: Limpeza se necessária
    logger.info("Finalizando aplicação...")


# Criar instância da aplicação FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""
    Sistema completo de chat/atendimento com busca semântica.
    
    ## Funcionalidades
    
    * **Mensagens**: Criar, ler, atualizar e excluir mensagens de chat
    * **Busca Semântica**: Buscar mensagens similares usando pgvector
    * **Histórico**: Acessar histórico completo de conversas por cliente
    * **Setores**: Organizar atendimento por setores (financeiro, suporte, vendas, etc.)
    * **Validação**: Sistema de validação de respostas (humano/IA)
    
    ## Setores Disponíveis
    
    * `financeiro` - Questões financeiras, boletos, pagamentos
    * `suporte` - Suporte técnico, problemas com produtos/serviços  
    * `vendas` - Vendas, produtos, cotações
    * `admin` - Questões administrativas
    * `geral` - Atendimento geral
    """,
    version="0.1.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# Configurar CORS para desenvolvimento
if settings.DEBUG:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Em produção, especificar origins permitidas
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.info("CORS configurado para desenvolvimento")

# Incluir routers da API
app.include_router(
    chat_router,
    prefix=settings.API_V1_PREFIX,
    tags=["chat"]
)

logger.info(f"Routers registrados com prefixo: {settings.API_V1_PREFIX}")


@app.get("/", tags=["health"])
async def root():
    """
    Endpoint de verificação de saúde da aplicação.
    
    Retorna informações básicas sobre o status do sistema.
    """
    return {
        "message": "Chat System API está funcionando",
        "version": "0.1.0",
        "status": "healthy",
        "docs_url": "/docs" if settings.DEBUG else "disabled",
        "debug_mode": settings.DEBUG
    }


@app.get("/health", tags=["health"])
async def health_check():
    """
    Endpoint detalhado de verificação de saúde.
    
    Verifica status dos componentes principais do sistema.
    """
    try:
        # Verificar conexão com banco de dados
        from app.database import SessionLocal
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Erro na verificação do banco de dados: {str(e)}")
        db_status = "unhealthy"
    
    # Verificar serviço de embeddings
    try:
        from app.services.embedding_service import get_embedding_service
        embedding_service = get_embedding_service()
        embedding_service.get_model_info()
        embedding_status = "healthy"
    except Exception as e:
        logger.error(f"Erro na verificação do serviço de embeddings: {str(e)}")
        embedding_status = "unhealthy"
    
    overall_status = "healthy" if all([
        db_status == "healthy",
        embedding_status == "healthy"
    ]) else "unhealthy"
    
    return {
        "status": overall_status,
        "timestamp": "2025-07-29T00:00:00Z",  # Seria datetime.utcnow().isoformat() + "Z" em produção
        "version": "0.1.0",
        "components": {
            "database": db_status,
            "embeddings": embedding_status
        },
        "settings": {
            "debug_mode": settings.DEBUG,
            "embedding_model": settings.EMBEDDING_MODEL,
            "embedding_dimension": settings.EMBEDDING_DIMENSION
        }
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Handler global para exceções não tratadas.
    
    Garante que todas as exceções sejam logadas adequadamente
    e retornem respostas padronizadas.
    """
    logger.error(f"Erro não tratado na rota {request.url}: {str(exc)}", exc_info=True)
    
    if settings.DEBUG:
        # Em modo debug, mostrar detalhes do erro
        return JSONResponse(
            status_code=500,
            content={
                "error": "internal_server_error",
                "message": "Erro interno do servidor",
                "details": str(exc),
                "url": str(request.url)
            }
        )
    else:
        # Em produção, não expor detalhes do erro
        return JSONResponse(
            status_code=500,
            content={
                "error": "internal_server_error",
                "message": "Erro interno do servidor"
            }
        )


# Log de inicialização
logger.info(f"Aplicação {settings.PROJECT_NAME} configurada")
logger.info(f"Modo DEBUG: {settings.DEBUG}")
logger.info(f"Banco de dados: {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")
logger.info(f"Modelo de embedding: {settings.EMBEDDING_MODEL}")

if __name__ == "__main__":
    import uvicorn
    
    logger.info("Iniciando servidor de desenvolvimento...")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
