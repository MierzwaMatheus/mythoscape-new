#!/usr/bin/env python3
"""
Script para testar a API com diferentes cenários de autenticação.
Demonstra como fazer requisições autenticadas e não autenticadas.
"""

import asyncio
import json
from typing import Optional

import httpx


class APIAuthTester:
    """Testador para diferentes cenários de autenticação da API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    async def test_health_endpoint(self) -> dict:
        """Testa o endpoint de health (público)."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/health")
                
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "response": response.json() if response.status_code == 200 else response.text
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def test_chat_without_auth(self) -> dict:
        """Testa o endpoint /chat sem autenticação."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat",
                    json={"message": "Olá! Teste sem autenticação."}
                )
                
                return {
                    "success": response.status_code == 200,
                    "status_code": response.status_code,
                    "response": response.json() if response.status_code == 200 else response.text
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def test_chat_with_invalid_token(self) -> dict:
        """Testa o endpoint /chat com token inválido."""
        try:
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": "Bearer token_invalido_123"}
                response = await client.post(
                    f"{self.base_url}/chat",
                    json={"message": "Teste com token inválido."},
                    headers=headers
                )
                
                return {
                    "success": response.status_code == 200,
                    "status_code": response.status_code,
                    "response": response.json() if response.status_code == 200 else response.text
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def test_chat_with_valid_token(self, token: str) -> dict:
        """Testa o endpoint /chat com token válido."""
        try:
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {token}"}
                response = await client.post(
                    f"{self.base_url}/chat",
                    json={"message": "Teste com token válido!"},
                    headers=headers
                )
                
                return {
                    "success": response.status_code == 200,
                    "status_code": response.status_code,
                    "response": response.json() if response.status_code == 200 else response.text
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def test_localhost_access(self) -> dict:
        """Testa se requisições do localhost são permitidas."""
        try:
            async with httpx.AsyncClient() as client:
                # Simula requisição do localhost
                response = await client.post(
                    f"{self.base_url}/chat",
                    json={"message": "Teste de acesso localhost."}
                )
                
                return {
                    "success": response.status_code == 200,
                    "status_code": response.status_code,
                    "response": response.json() if response.status_code == 200 else response.text,
                    "note": "Localhost deve ter acesso mesmo sem token"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


def print_test_result(test_name: str, result: dict):
    """Imprime o resultado de um teste de forma formatada."""
    print(f"\n🧪 {test_name}")
    print("-" * 50)
    
    if result["success"]:
        print("✅ PASSOU")
        if "status_code" in result:
            print(f"   Status: {result['status_code']}")
        if "response" in result:
            print(f"   Resposta: {json.dumps(result['response'], indent=2, ensure_ascii=False)}")
    else:
        print("❌ FALHOU")
        if "status_code" in result:
            print(f"   Status: {result['status_code']}")
        if "error" in result:
            print(f"   Erro: {result['error']}")
        if "response" in result:
            print(f"   Resposta: {result['response']}")
    
    if "note" in result:
        print(f"   📝 Nota: {result['note']}")


async def run_all_tests(token: Optional[str] = None):
    """Executa todos os testes de autenticação."""
    print("🚀 Iniciando testes de autenticação da API")
    print("=" * 60)
    
    tester = APIAuthTester()
    
    # Teste 1: Health endpoint (público)
    result = await tester.test_health_endpoint()
    print_test_result("Health Endpoint (Público)", result)
    
    # Teste 2: Chat sem autenticação
    result = await tester.test_chat_without_auth()
    print_test_result("Chat sem Autenticação", result)
    
    # Teste 3: Chat com token inválido
    result = await tester.test_chat_with_invalid_token()
    print_test_result("Chat com Token Inválido", result)
    
    # Teste 4: Chat com token válido (se fornecido)
    if token:
        result = await tester.test_chat_with_valid_token(token)
        print_test_result("Chat com Token Válido", result)
    else:
        print(f"\n🧪 Chat com Token Válido")
        print("-" * 50)
        print("⏭️  PULADO - Token não fornecido")
    
    # Teste 5: Acesso localhost
    result = await tester.test_localhost_access()
    print_test_result("Acesso Localhost", result)
    
    print("\n" + "=" * 60)
    print("🏁 Testes concluídos!")


async def interactive_mode():
    """Modo interativo para testes."""
    print("🔧 Modo Interativo - Teste de Autenticação da API")
    print("=" * 60)
    
    while True:
        print("\nOpções:")
        print("1. Executar todos os testes (sem token)")
        print("2. Executar todos os testes (com token)")
        print("3. Testar endpoint específico")
        print("4. Sair")
        
        choice = input("\n🔹 Escolha uma opção (1-4): ").strip()
        
        if choice == "1":
            await run_all_tests()
        
        elif choice == "2":
            token = input("🔑 Cole o token JWT (sem 'Bearer '): ").strip()
            if token:
                await run_all_tests(token)
            else:
                print("❌ Token não pode estar vazio!")
        
        elif choice == "3":
            print("\nEndpoints disponíveis:")
            print("1. /health")
            print("2. /chat (sem auth)")
            print("3. /chat (com token)")
            
            endpoint_choice = input("Escolha o endpoint (1-3): ").strip()
            tester = APIAuthTester()
            
            if endpoint_choice == "1":
                result = await tester.test_health_endpoint()
                print_test_result("Health Endpoint", result)
            
            elif endpoint_choice == "2":
                result = await tester.test_chat_without_auth()
                print_test_result("Chat sem Auth", result)
            
            elif endpoint_choice == "3":
                token = input("🔑 Cole o token JWT: ").strip()
                if token:
                    result = await tester.test_chat_with_valid_token(token)
                    print_test_result("Chat com Token", result)
                else:
                    print("❌ Token não pode estar vazio!")
        
        elif choice == "4":
            print("\n👋 Até logo!")
            break
        
        else:
            print("❌ Opção inválida!")


async def main():
    """Função principal."""
    import sys
    
    if len(sys.argv) > 1:
        # Modo não-interativo com token
        token = sys.argv[1]
        await run_all_tests(token)
    else:
        # Modo interativo
        await interactive_mode()


if __name__ == "__main__":
    asyncio.run(main())