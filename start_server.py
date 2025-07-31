#!/usr/bin/env python3
"""
Script para iniciar o servidor FastAPI com configurações específicas para N8N
"""
import uvicorn
import socket
import os

if __name__ == "__main__":
    # Desabilitar IPv6 completamente
    socket.has_ipv6 = False
    
    # Forçar apenas IPv4
    os.environ['PREFER_IPV4'] = '1'
    
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
    
    print("🚀 Iniciando servidor FastAPI para N8N...")
    print(f"📡 Servidor disponível em: http://localhost:8000")
    print(f"📡 Servidor disponível em: http://127.0.0.1:8000")
    print(f"📚 Documentação em: http://localhost:8000/docs")
    print(f"❤️  Health check em: http://localhost:8000/health")
    print("🔧 IPv6 DESABILITADO para compatibilidade N8N")
    print("=" * 50)
    
    # Iniciar servidor
    uvicorn.run(**config)
