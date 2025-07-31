#!/usr/bin/env python3
"""
Script de diagnóstico N8N - Testa conectividade e simula requisições N8N
"""
import requests
import json
import time
import sys
from datetime import datetime

# URLs para testar
URLS_TO_TEST = [
    "http://localhost:8000",
    "http://127.0.0.1:8000", 
    "http://192.168.15.43:8000",
    "http://0.0.0.0:8000"  # Pode não funcionar, mas vamos testar
]

ENDPOINTS = [
    "/health",
    "/api/v1/messages/test"
]

# Payload para teste
TEST_PAYLOAD = {
    "client_id": "123e4567-e89b-12d3-a456-426614174000",
    "sector": "suporte", 
    "message": "Teste de conectividade do N8N"
}

def test_url_endpoint(base_url, endpoint, method="GET", payload=None):
    """Testa uma URL específica com timeout e headers similares ao N8N"""
    url = f"{base_url}{endpoint}"
    
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "n8n-diagnostic/1.0",
        "Accept": "application/json",
        "Connection": "keep-alive"
    }
    
    print(f"\n🔍 Testando: {method} {url}")
    print(f"   Headers: {headers}")
    if payload:
        print(f"   Payload: {json.dumps(payload)}")
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        else:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        print(f"   ✅ Status: {response.status_code}")
        print(f"   ⏱️  Tempo: {response.elapsed.total_seconds():.3f}s")
        print(f"   📦 Tamanho: {len(response.content)} bytes")
        
        try:
            json_response = response.json()
            print(f"   📋 JSON: {json.dumps(json_response, indent=2)}")
        except:
            print(f"   📄 Texto: {response.text[:200]}")
            
        return True, response.status_code, response.elapsed.total_seconds()
        
    except requests.exceptions.ConnectTimeout:
        print(f"   ❌ TIMEOUT de conexão (>10s)")
        return False, "TIMEOUT", 10
    except requests.exceptions.ConnectionError as e:
        print(f"   ❌ ERRO de conexão: {str(e)}")
        return False, "CONNECTION_ERROR", 0
    except requests.exceptions.Timeout:
        print(f"   ❌ TIMEOUT de resposta")
        return False, "RESPONSE_TIMEOUT", 10
    except Exception as e:
        print(f"   ❌ ERRO: {str(e)}")
        return False, "ERROR", 0

def main():
    print("🧪 N8N DIAGNOSTIC TOOL")
    print("=" * 50)
    print(f"🕒 Iniciado em: {datetime.now()}")
    print()
    
    results = []
    
    for base_url in URLS_TO_TEST:
        print(f"\n🌐 Testando base URL: {base_url}")
        print("-" * 40)
        
        # Teste 1: Health Check
        success, status, time_taken = test_url_endpoint(base_url, "/health", "GET")
        results.append({
            "url": f"{base_url}/health",
            "method": "GET", 
            "success": success,
            "status": status,
            "time": time_taken
        })
        
        # Teste 2: Endpoint N8N
        success, status, time_taken = test_url_endpoint(base_url, "/api/v1/messages/test", "POST", TEST_PAYLOAD)
        results.append({
            "url": f"{base_url}/api/v1/messages/test",
            "method": "POST",
            "success": success, 
            "status": status,
            "time": time_taken
        })
        
        time.sleep(1)  # Pausa entre testes
    
    # Resumo
    print("\n" + "=" * 50)
    print("📊 RESUMO DOS TESTES")
    print("=" * 50)
    
    successful_tests = [r for r in results if r["success"]]
    failed_tests = [r for r in results if not r["success"]]
    
    print(f"✅ Sucessos: {len(successful_tests)}/{len(results)}")
    print(f"❌ Falhas: {len(failed_tests)}/{len(results)}")
    
    if successful_tests:
        print("\n🎉 URLs FUNCIONANDO:")
        for test in successful_tests:
            print(f"   {test['method']} {test['url']} - {test['status']} ({test['time']:.3f}s)")
    
    if failed_tests:
        print("\n💥 URLs COM PROBLEMA:")
        for test in failed_tests:
            print(f"   {test['method']} {test['url']} - {test['status']}")
    
    # Recomendações
    print("\n🔧 RECOMENDAÇÕES PARA N8N:")
    print("-" * 30)
    
    working_urls = [t["url"].split("/")[2] for t in successful_tests if "/health" in t["url"]]
    if working_urls:
        print(f"✅ Use estas URLs no N8N:")
        for url in set(working_urls):
            print(f"   http://{url}")
    
    print(f"\n📋 Payload para N8N:")
    print(json.dumps(TEST_PAYLOAD, indent=2))
    
    print(f"\n🕒 Finalizado em: {datetime.now()}")

if __name__ == "__main__":
    main()
