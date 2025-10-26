"""Middleware de autenticação JWT para validação de tokens Supabase."""

import jwt
from typing import Optional
from fastapi import HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError

from app.services.supabase import get_supabase_client


class JWTBearer(HTTPBearer):
    """Classe para validação de tokens JWT do Supabase."""
    
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)
    
    async def __call__(self, request: Request) -> Optional[str]:
        """
        Valida o token JWT presente no header Authorization.
        
        Args:
            request: Requisição HTTP do FastAPI
            
        Returns:
            Token JWT validado ou None se inválido
            
        Raises:
            HTTPException: Se o token for inválido ou expirado
        """
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de autorização não fornecido",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not credentials.scheme == "Bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Esquema de autenticação inválido. Use Bearer token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        token = credentials.credentials
        
        if not self._verify_jwt_token(token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token JWT inválido ou expirado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return token
    
    def _verify_jwt_token(self, token: str) -> bool:
        """
        Verifica se o token JWT é válido usando o Supabase.
        
        Args:
            token: Token JWT a ser validado
            
        Returns:
            True se o token for válido, False caso contrário
        """
        try:
            # Obtém o cliente Supabase
            supabase = get_supabase_client()
            
            # Verifica o token usando o Supabase Auth
            user_response = supabase.auth.get_user(token)
            
            # Se chegou até aqui, o token é válido
            return user_response.user is not None
            
        except Exception as e:
            # Log do erro para debugging (em produção, use logging adequado)
            print(f"Erro na validação do token: {str(e)}")
            return False


def get_current_user_id(token: str) -> str:
    """
    Extrai o ID do usuário do token JWT validado.
    
    Args:
        token: Token JWT válido
        
    Returns:
        ID do usuário extraído do token
        
    Raises:
        HTTPException: Se não conseguir extrair o ID do usuário
    """
    try:
        # Decodifica o token sem verificar a assinatura (já foi verificado)
        payload = jwt.decode(token, options={"verify_signature": False})
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="ID do usuário não encontrado no token"
            )
        
        return user_id
        
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token JWT malformado"
        )


def is_localhost_request(request: Request) -> bool:
    """
    Verifica se a requisição vem do localhost (para desenvolvimento).
    
    Args:
        request: Requisição HTTP do FastAPI
        
    Returns:
        True se a requisição vem do localhost
    """
    client_host = request.client.host if request.client else None
    return client_host in ["127.0.0.1", "localhost", "::1"]


# Instância global do validador JWT
jwt_bearer = JWTBearer()