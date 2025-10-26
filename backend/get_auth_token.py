#!/usr/bin/env python3
"""
Script utilitário para obter tokens de autenticação do Supabase sem frontend.
Demonstra diferentes métodos para autenticação durante desenvolvimento e testes.
"""

import asyncio
import json
from typing import Optional

import httpx
from supabase import create_client, Client
from app.utils.env import get_supabase_url, get_supabase_anon_key, get_supabase_service_key


class SupabaseAuthHelper:
    """Helper para autenticação com Supabase sem frontend."""
    
    def __init__(self):
        try:
            self.url = get_supabase_url()
            self.anon_key = get_supabase_anon_key()
            self.service_key = get_supabase_service_key()
            self.client: Client = create_client(self.url, self.anon_key)
        except ValueError as e:
            print(f"❌ ERRO DE CONFIGURAÇÃO: {str(e)}")
            print("\n📋 CONFIGURAÇÃO NECESSÁRIA:")
            print("1. Crie um arquivo .env ou .env.local na pasta backend/")
            print("2. Adicione as seguintes variáveis:")
            print("   SUPABASE_URL=https://seu-projeto.supabase.co")
            print("   SUPABASE_ANON_KEY=sua_chave_anonima")
            print("   SUPABASE_SERVICE_ROLE_KEY=sua_chave_service_role")
            print("\n💡 Use o arquivo .env.example como referência!")
            raise SystemExit(1)
    
    def sign_up_user(self, email: str, password: str) -> dict:
        """
        Cria um novo usuário e retorna o token de acesso.
        
        Args:
            email: Email do usuário
            password: Senha do usuário (mínimo 6 caracteres)
            
        Returns:
            Dict com informações do usuário e token
        """
        try:
            response = self.client.auth.sign_up({
                "email": email,
                "password": password
            })
            
            if response.user and response.session:
                return {
                    "success": True,
                    "user_id": response.user.id,
                    "email": response.user.email,
                    "access_token": response.session.access_token,
                    "refresh_token": response.session.refresh_token,
                    "expires_at": response.session.expires_at,
                    "message": "Usuário criado com sucesso!"
                }
            else:
                return {
                    "success": False,
                    "message": "Erro ao criar usuário. Verifique se o email já não está em uso."
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Erro: {str(e)}"
            }
    
    def sign_in_user(self, email: str, password: str) -> dict:
        """
        Autentica um usuário existente e retorna o token de acesso.
        
        Args:
            email: Email do usuário
            password: Senha do usuário
            
        Returns:
            Dict com informações do usuário e token
        """
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user and response.session:
                return {
                    "success": True,
                    "user_id": response.user.id,
                    "email": response.user.email,
                    "access_token": response.session.access_token,
                    "refresh_token": response.session.refresh_token,
                    "expires_at": response.session.expires_at,
                    "message": "Login realizado com sucesso!"
                }
            else:
                return {
                    "success": False,
                    "message": "Credenciais inválidas."
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Erro: {str(e)}"
            }
    
    async def test_token_with_api(self, token: str) -> dict:
        """
        Testa um token JWT fazendo uma requisição para a API local.
        
        Args:
            token: Token JWT para testar
            
        Returns:
            Dict com resultado do teste
        """
        try:
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {token}"}
                response = await client.post(
                    "http://localhost:8000/chat",
                    json={"message": "Teste de autenticação"},
                    headers=headers
                )
                
                if response.status_code == 200:
                    return {
                        "success": True,
                        "message": "Token válido! API respondeu com sucesso.",
                        "response": response.json()
                    }
                else:
                    return {
                        "success": False,
                        "message": f"Token inválido. Status: {response.status_code}",
                        "error": response.text
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "message": f"Erro ao testar token: {str(e)}"
            }
    
    def get_service_role_info(self) -> dict:
        """
        Retorna informações sobre o service role key.
        ATENÇÃO: Use apenas em desenvolvimento!
        
        Returns:
            Dict com informações do service role
        """
        return {
            "service_key": self.service_key,
            "warning": "⚠️  NUNCA use service_role em produção para autenticação de usuários!",
            "usage": "Use apenas para operações administrativas e testes."
        }


def print_separator(title: str):
    """Imprime um separador visual."""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")


def print_result(result: dict):
    """Imprime o resultado de forma formatada."""
    if result["success"]:
        print("✅ SUCESSO:")
        print(f"   {result['message']}")
        if "access_token" in result:
            print(f"   🔑 Token: {result['access_token'][:50]}...")
            print(f"   👤 User ID: {result['user_id']}")
            print(f"   📧 Email: {result['email']}")
    else:
        print("❌ ERRO:")
        print(f"   {result['message']}")


async def main():
    """Função principal para demonstrar o uso."""
    print("🚀 Supabase Auth Token Helper")
    print("Este script demonstra como obter tokens de autenticação sem frontend.")
    
    auth_helper = SupabaseAuthHelper()
    
    # Opções disponíveis
    print_separator("OPÇÕES DISPONÍVEIS")
    print("1. Criar novo usuário (sign up)")
    print("2. Fazer login com usuário existente")
    print("3. Testar token com a API")
    print("4. Ver informações do Service Role")
    print("5. Sair")
    
    while True:
        try:
            choice = input("\n🔹 Escolha uma opção (1-5): ").strip()
            
            if choice == "1":
                print_separator("CRIAR NOVO USUÁRIO")
                email = input("📧 Email: ").strip()
                password = input("🔒 Senha (min. 6 caracteres): ").strip()
                
                if len(password) < 6:
                    print("❌ Senha deve ter pelo menos 6 caracteres!")
                    continue
                
                result = auth_helper.sign_up_user(email, password)
                print_result(result)
                
                if result["success"]:
                    print(f"\n📋 COPIE ESTE TOKEN PARA USAR NA API:")
                    print(f"Bearer {result['access_token']}")
            
            elif choice == "2":
                print_separator("FAZER LOGIN")
                email = input("📧 Email: ").strip()
                password = input("🔒 Senha: ").strip()
                
                result = auth_helper.sign_in_user(email, password)
                print_result(result)
                
                if result["success"]:
                    print(f"\n📋 COPIE ESTE TOKEN PARA USAR NA API:")
                    print(f"Bearer {result['access_token']}")
            
            elif choice == "3":
                print_separator("TESTAR TOKEN")
                token = input("🔑 Cole o token JWT (sem 'Bearer '): ").strip()
                
                if not token:
                    print("❌ Token não pode estar vazio!")
                    continue
                
                print("🔄 Testando token com a API local...")
                result = await auth_helper.test_token_with_api(token)
                print_result(result)
            
            elif choice == "4":
                print_separator("SERVICE ROLE INFO")
                info = auth_helper.get_service_role_info()
                print(f"🔑 Service Key: {info['service_key'][:50]}...")
                print(f"⚠️  {info['warning']}")
                print(f"📝 {info['usage']}")
                
                print(f"\n📋 PARA USAR COMO SERVICE ROLE:")
                print(f"Bearer {info['service_key']}")
            
            elif choice == "5":
                print("\n👋 Até logo!")
                break
            
            else:
                print("❌ Opção inválida! Escolha entre 1-5.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Saindo...")
            break
        except Exception as e:
            print(f"❌ Erro inesperado: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())