#!/usr/bin/env python3
"""
Script para iniciar o servidor FastAPI com configurações específicas para N8N e Codespace
"""
import uvicorn
import socket
import os

def detect_environment():
    """Detecta se está rodando no Codespace ou localmente"""
    return 'CODESPACES' in os.environ

if __name__ == "__main__":
    # Detectar ambiente
    is_codespace = detect_environment()
    
    # Desabilitar IPv6 completamente
    socket.has_ipv6 = False
    
    # Forçar apenas IPv4
    os.environ['PREFER_IPV4'] = '1'
    
    # Configurar arquivo .env baseado no ambiente
    if is_codespace and os.path.exists('.env.codespace'):
        os.environ.setdefault('ENV_FILE', '.env.codespace')
        print("🌐 Detectado ambiente Codespace - usando .env.codespace")
    
    # Configurações do servidor
    config = {
        "app": "app.main:app",
        "host": "0.0.0.0",  # Todas as interfaces IPv4
        "port": 8000,
        "reload": False,  # Desabilitar reload para estabilidade
        "log_level": "info",
        "access_log": True,
        "loop": "asyncio",  # Força loop asyncio
    }
    
    print("🚀 Iniciando servidor FastAPI...")
    if is_codespace:
        print("🌐 Ambiente: GitHub Codespace")
        codespace_name = os.environ.get('CODESPACE_NAME', 'unknown')
        print(f"📡 URL pública: https://{codespace_name}-8000.app.github.dev")
        print(f"📚 Documentação: https://{codespace_name}-8000.app.github.dev/docs")
        print(f"❤️  Health check: https://{codespace_name}-8000.app.github.dev/health")
        print(f"🔑 API Key: agente-ia-rag-professional-key-2025")
    else:
        print(f"📡 Servidor disponível em: http://localhost:8000")
        print(f"📡 Servidor disponível em: http://127.0.0.1:8000")
        print(f"📚 Documentação em: http://localhost:8000/docs")
        print(f"❤️  Health check em: http://localhost:8000/health")
    print("🔧 IPv6 DESABILITADO para compatibilidade N8N")
    print("=" * 50)
    
    # Iniciar servidor
    uvicorn.run(**config)
